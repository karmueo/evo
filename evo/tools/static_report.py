"""Static analysis text, table and figure reports (GPL v3 or later)."""

from collections.abc import Sequence
import csv
import json
import os
from pathlib import Path
from typing import Any

import numpy as np

from evo.core.static import StaticAnalysisResult, _angles
from evo.core.trajectory import PoseTrajectory3D
from evo.core.transformations import quaternion_matrix
from evo.tools import user


def _normalize_results(
    results: StaticAnalysisResult | Sequence[StaticAnalysisResult],
) -> list[StaticAnalysisResult]:
    if isinstance(results, StaticAnalysisResult):
        return [results]
    return list(results)


def _format_single_report(
    result: StaticAnalysisResult, include_header: bool = True
) -> list[str]:
    unit = result.config.unit
    lines: list[str] = []
    if include_header:
        lines.append(f"Static trajectory analysis ({unit}, angles in deg)")
    if result.source:
        lines.append(f"Trajectory: {result.source}")
    for segment in result.segments:
        pos_text = ", ".join(f"{v:.6f}" for v in segment["position"])
        lines.append(
            f"Stop {segment['index']}: {segment['start_relative']:.3f}"
            f"..{segment['end_relative']:.3f}s "
            f"({segment['duration']:.3f}s, {segment['sample_count']} poses); "
            f"position [{pos_text}] {unit}; "
            f"position RMS {segment['position_rms']:.6f} {unit}, "
            f"angle RMS {segment['angle_rms_deg']:.6f} deg"
        )
    pairs: list[tuple[str, dict[str, Any]]] = [
        ("Distance", d) for d in result.distances
    ]
    if result.closure is not None:
        pairs.append(("Closure", result.closure))
    for kind, dist in pairs:
        delta_text = ", ".join(f"{v:+.6f}" for v in dist["delta_xyz"])
        abs_text = ", ".join(f"{v:.6f}" for v in dist["abs_delta_xyz"])
        lines.append(
            f"{kind} {dist['reference_index']} -> {dist['index']}: "
            f"dXYZ [{delta_text}] {unit}; "
            f"|dXYZ| [{abs_text}] {unit}; "
            f"Euclidean distance {dist['euclidean_distance']:.6f} {unit}; "
            f"rotation angle {dist['rotation_angle_deg']:.6f} deg"
        )
    for key, value in result.summary.items():
        lines.append(f"{key}: {value:.6f} {unit}")
    return lines


def format_report(
    results: StaticAnalysisResult | Sequence[StaticAnalysisResult],
) -> str:
    items = _normalize_results(results)
    if not items:
        return ""
    unit = items[0].config.unit
    lines = [f"Static trajectory analysis ({unit}, angles in deg)"]
    for idx, result in enumerate(items):
        if idx > 0:
            lines.append("")
        lines.extend(_format_single_report(result, include_header=False))
    return "\n".join(lines)


def save_json(
    results: StaticAnalysisResult | Sequence[StaticAnalysisResult],
    path: str,
    confirm_overwrite: bool = True,
) -> None:
    if confirm_overwrite and not user.check_and_confirm_overwrite(path):
        return
    items = _normalize_results(results)
    payload: dict[str, Any]
    if len(items) == 1:
        payload = items[0].to_dict()
    else:
        payload = {
            "config": items[0].to_dict()["config"] if items else {},
            "trajectories": [item.to_dict() for item in items],
        }
    with open(path, "w", encoding="utf-8") as output:
        json.dump(
            payload,
            output,
            ensure_ascii=False,
            indent=2,
            allow_nan=False,
        )
        output.write("\n")


def save_csv(
    results: StaticAnalysisResult | Sequence[StaticAnalysisResult],
    path: str,
    confirm_overwrite: bool = True,
) -> None:
    if confirm_overwrite and not user.check_and_confirm_overwrite(path):
        return
    items = _normalize_results(results)
    rows: list[dict[str, Any]] = []

    def flatten(data: dict[str, Any]) -> dict[str, Any]:
        row = {}
        for key, value in data.items():
            if isinstance(value, list):
                axes = (
                    ("w", "x", "y", "z")
                    if len(value) == 4
                    else ("x", "y", "z")
                )
                row.update(
                    {f"{key}_{axis}": v for axis, v in zip(axes, value)}
                )
            else:
                row[key] = value
        return row

    for result in items:
        distances = {d["index"]: d for d in result.distances}
        for segment in result.segments:
            rows.append(
                {
                    "source": result.source or "",
                    "type": "stop",
                    "unit": result.config.unit,
                    **flatten(segment),
                    **flatten(distances.get(segment["index"], {})),
                }
            )
        if result.closure is not None:
            rows.append(
                {
                    "source": result.source or "",
                    "type": "closure",
                    "unit": result.config.unit,
                    **flatten(result.closure),
                }
            )
    names = list(dict.fromkeys(key for row in rows for key in row))
    with open(path, "w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=names)
        writer.writeheader()
        writer.writerows(rows)


def _configure_chinese_font() -> None:
    from matplotlib import font_manager, pyplot as plt

    preferred = [
        "Noto Sans CJK SC",
        "WenQuanYi Zen Hei",
        "SimHei",
        "Microsoft YaHei",
        "PingFang SC",
        "Droid Sans Fallback",
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    selected = [name for name in preferred if name in available]
    if selected:
        current = list(plt.rcParams.get("font.sans-serif", []))
        plt.rcParams["font.sans-serif"] = selected + [
            f for f in current if f not in selected
        ]
    plt.rcParams["axes.unicode_minus"] = False


def _trajectory_labels(
    traj_list: Sequence[PoseTrajectory3D],
    res_list: Sequence[StaticAnalysisResult],
    labels: Sequence[str] | None = None,
) -> list[str]:
    if labels is not None:
        if len(labels) != len(traj_list):
            raise ValueError(
                f"Expected {len(traj_list)} labels, got {len(labels)}"
            )
        return list(labels)
    sources = [
        res.source or traj.name or f"轨迹 {idx + 1}"
        for idx, (traj, res) in enumerate(zip(traj_list, res_list))
    ]
    if len(sources) == 1:
        src = sources[0]
        return [Path(src).name if "/" in src or "\\" in src else src]
    try:
        parents = [str(Path(s).parent) for s in sources]
        common = os.path.commonpath(parents)
        derived = [
            os.path.relpath(s, common) if common else Path(s).name
            for s in sources
        ]
    except ValueError:
        derived = [Path(s).name for s in sources]
    counts: dict[str, int] = {}
    for item in derived:
        counts[item] = counts.get(item, 0) + 1
    if any(c > 1 for c in counts.values()):
        return [f"#{idx + 1} {item}" for idx, item in enumerate(derived)]
    return derived


def _plot_single(
    collection: Any,
    traj: PoseTrajectory3D,
    result: StaticAnalysisResult,
    prefix: str = "",
    label: str = "",
) -> None:
    from matplotlib import pyplot as plt

    _configure_chinese_font()
    unit = result.config.unit
    scale = 1000.0 if unit == "mm" else 1.0
    times = traj.timestamps - traj.timestamps[0]
    fig, axes = plt.subplots(3, 1, sharex=True, layout="constrained")
    for i, axis in enumerate(axes):
        axis.plot(
            times,
            (traj.positions_xyz[:, i] - traj.positions_xyz[0, i]) * scale,
        )
        for segment in result.segments:
            axis.axvspan(
                segment["start_relative"], segment["end_relative"], alpha=0.2
            )
            axis.text(segment["start_relative"], 0, str(segment["index"]))
        axis.set_ylabel(f"{'XYZ'[i]} 相对位移 ({unit})")
    axes[-1].set_xlabel("轨迹起始时间 (s)")
    title_intervals = f"{label} - 静止区间检测" if label else "静止区间检测"
    fig.suptitle(title_intervals)
    collection.add_figure(f"{prefix}intervals", fig)

    fig, axes = plt.subplots(2, 1, sharex=True, layout="constrained")
    for segment in result.segments:
        start, stop = segment["start_index"], segment["stop_index"]
        sl = slice(start, stop)
        center = np.array(segment["position"])
        axes[0].plot(
            times[sl],
            np.linalg.norm(traj.positions_xyz[sl] * scale - center, axis=1),
            label=f"停靠点 {segment['index']}",
        )
        rotation = quaternion_matrix(segment["quaternion_wxyz"])[:3, :3]
        angles = _angles(
            rotation, np.array([p[:3, :3] for p in traj.poses_se3[sl]])
        )
        axes[1].plot(times[sl], angles)
    axes[0].set_ylabel(f"位置残差 ({unit})")
    axes[0].legend()
    axes[1].set_ylabel("旋转残差 (deg)")
    axes[1].set_xlabel("轨迹起始时间 (s)")
    title_stability = f"{label} - 静止段稳定性" if label else "静止段稳定性"
    fig.suptitle(title_stability)
    collection.add_figure(f"{prefix}stability", fig)

    distances = list(result.distances)
    tick_labels = [
        f"{d['reference_index']}->{d['index']}" for d in result.distances
    ]
    if result.closure is not None:
        distances.append(result.closure)
        tick_labels.append("闭合误差")
    if distances:
        fig, axes = plt.subplots(2, 1, sharex=True, layout="constrained")
        x = np.arange(len(distances))
        decimals = 3 if unit == "m" else 2
        series: list[tuple[list[float], Any]] = []
        for i, axis_name in enumerate("XYZ"):
            vals = [float(d["abs_delta_xyz"][i]) for d in distances]
            (line,) = axes[0].plot(
                x,
                vals,
                marker="o",
                label=f"|d{axis_name}|",
            )
            series.append((vals, line.get_color()))
        euc_vals = [float(d["euclidean_distance"]) for d in distances]
        (euc_line,) = axes[0].plot(
            x,
            euc_vals,
            marker="o",
            color="gold",
            label="欧氏距离",
        )
        series.append((euc_vals, euc_line.get_color()))

        all_vals = [v for vals, _ in series for v in vals]
        y_min = min(all_vals)
        y_span = max(all_vals) - y_min or 1.0
        for x_idx in range(len(distances)):
            items = sorted(
                ((vals[x_idx], color) for vals, color in series),
                key=lambda item: item[0],
            )
            approx_pts = [((v - y_min) / y_span) * 140.0 for v, _ in items]
            placed = list(approx_pts)
            for k in range(1, len(placed)):
                if placed[k] - placed[k - 1] < 11.0:
                    placed[k] = placed[k - 1] + 11.0
            for (val, color), orig, adj in zip(items, approx_pts, placed):
                axes[0].annotate(
                    f"{val:.{decimals}f}",
                    xy=(x_idx, val),
                    xytext=(6, adj - orig),
                    textcoords="offset points",
                    ha="left",
                    va="center",
                    fontsize=8,
                    color=color,
                )

        axes[0].margins(y=0.18)
        axes[0].set_xlim(-0.35, len(distances) - 0.35)
        axes[0].set_ylabel(f"距离 ({unit})")
        axes[0].legend(
            ncol=4,
            loc="lower center",
            bbox_to_anchor=(0.5, 1.02),
            frameon=True,
        )

        rot_vals = [float(d["rotation_angle_deg"]) for d in distances]
        axes[1].plot(x, rot_vals, marker="o")
        for x_idx, angle in enumerate(rot_vals):
            axes[1].annotate(
                f"{angle:.2f}°",
                xy=(x_idx, angle),
                xytext=(0, 6),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=8,
            )
        axes[1].margins(y=0.22)
        axes[1].set_ylabel("旋转角 (deg)")
        axes[1].set_xticks(x, tick_labels)
        axes[1].set_xlabel("停靠点对")
        title_distances = (
            f"{label} - 停靠点间距离与旋转" if label else "停靠点间距离与旋转"
        )
        fig.suptitle(title_distances)
        collection.add_figure(f"{prefix}distances", fig)


def plot_report(
    trajectories: PoseTrajectory3D | Sequence[PoseTrajectory3D],
    results: StaticAnalysisResult | Sequence[StaticAnalysisResult],
    labels: Sequence[str] | None = None,
):
    from evo.tools import plot

    _configure_chinese_font()
    traj_list = (
        [trajectories]
        if isinstance(trajectories, PoseTrajectory3D)
        else list(trajectories)
    )
    res_list = _normalize_results(results)
    traj_labels = _trajectory_labels(traj_list, res_list, labels=labels)
    collection = plot.PlotCollection("静态轨迹分析")
    multi = len(traj_list) > 1
    for idx, (traj, res, label) in enumerate(
        zip(traj_list, res_list, traj_labels)
    ):
        if multi:
            safe_label = label.replace("/", "_").replace("\\", "_")
            prefix = f"{idx}_{safe_label}_"
        else:
            prefix = ""
        _plot_single(collection, traj, res, prefix=prefix, label=label)
    return collection
