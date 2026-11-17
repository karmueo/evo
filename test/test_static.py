"""Regression tests for static evaluation and its CLI."""

import csv
import json
from pathlib import Path

import numpy as np
import pytest
import yaml

from evo import EvoException
from evo.cli import entry_points, static, static_parser
from evo.core.static import (
    StaticAnalysisConfig as Config,
    StaticAnalysisException,
    analyze_static,
    detect_static_intervals,
)
from evo.core.trajectory import PoseTrajectory3D
from evo.tools import file_interface
from evo.tools.settings import SETTINGS


def stops(positions, angles=None, epoch=0.0):
    positions = np.asarray(positions, dtype=float)
    samples_per_stop = 5
    xyz = np.repeat(positions, samples_per_stop, axis=0)
    theta = (
        np.deg2rad(
            np.repeat(
                angles if angles is not None else np.zeros(len(positions)),
                samples_per_stop,
            )
        )
        / 2
    )
    quats = np.column_stack(
        (np.cos(theta), np.zeros((len(xyz), 2)), np.sin(theta))
    )
    timestamps = np.concatenate(
        [
            i * 3.0 + np.linspace(0.0, 2.0, samples_per_stop)
            for i in range(len(positions))
        ]
    )
    return PoseTrajectory3D(xyz, quats, timestamps + epoch)


def test_closure_translation_rotation_and_no_alignment():
    traj = stops([[0, 0, 0], [0.005, 0, 0]], [90, 92])
    result = analyze_static(traj, Config(closure=True))
    assert result.closure is not None
    assert result.closure["euclidean_distance"] == pytest.approx(5)
    assert result.closure["rotation_angle_deg"] == pytest.approx(2)
    assert result.closure["delta_xyz"] == pytest.approx([5, 0, 0])
    assert result.closure["abs_delta_xyz"] == pytest.approx([5, 0, 0])
    same = analyze_static(stops([[0, 0, 0], [0, 0, 0]]), Config(closure=True))
    assert same.closure is not None
    assert same.closure["euclidean_distance"] == pytest.approx(0)


@pytest.mark.parametrize(
    "mode,expected_deltas,expected_euclideans",
    [
        ("origin", [[100, 0, 0], [200, 0, 0]], [100, 200]),
        ("consecutive", [[100, 0, 0], [100, 0, 0]], [100, 100]),
    ],
)
def test_reference_modes(mode, expected_deltas, expected_euclideans):
    result = analyze_static(
        stops([[0, 0, 0], [0.1, 0, 0], [0.2, 0, 0]]),
        Config(reference_mode=mode),
    )
    assert [d["delta_xyz"] for d in result.distances] == [
        pytest.approx(vec) for vec in expected_deltas
    ]
    assert [d["euclidean_distance"] for d in result.distances] == [
        pytest.approx(val) for val in expected_euclideans
    ]
    assert result.summary["euclidean_distance_mean"] == pytest.approx(
        np.mean(expected_euclideans)
    )


def test_distances_xyz_and_units():
    traj = stops([[0, 0, 0], [0.03, -0.04, 0.12]])
    result = analyze_static(traj)
    dist = result.distances[0]
    assert dist["delta_xyz"] == pytest.approx([30, -40, 120])
    assert dist["abs_delta_xyz"] == pytest.approx([30, 40, 120])
    assert dist["euclidean_distance"] == pytest.approx(130)
    meters = analyze_static(traj, Config(unit="m"))
    assert meters.distances[0]["delta_xyz"] == pytest.approx(
        [0.03, -0.04, 0.12]
    )
    assert meters.distances[0]["abs_delta_xyz"] == pytest.approx(
        [0.03, 0.04, 0.12]
    )
    assert meters.distances[0]["euclidean_distance"] == pytest.approx(0.13)


def test_jitter_and_quaternion_sign():
    traj = stops([[0, 0, 0]])
    traj.positions_xyz[:, 0] = [-0.001, 0, 0.001, 0, 0]
    traj.orientations_quat_wxyz[1] *= -1
    result = analyze_static(traj)
    segment = result.segments[0]
    assert segment["position_rms"] == pytest.approx(np.sqrt(2 / 5))
    assert segment["position_std"] == pytest.approx([np.sqrt(2 / 5), 0, 0])
    assert segment["position_max"] == pytest.approx(1)
    assert segment["angle_max_deg"] == pytest.approx(0)
    assert segment["duration"] == pytest.approx(2.0)


def test_angular_jitter():
    traj = stops([[0, 0, 0]])
    theta = np.deg2rad([-1, 0, 1, 0, 0]) / 2
    traj.orientations_quat_wxyz[:] = np.column_stack(
        (np.cos(theta), np.zeros((5, 2)), np.sin(theta))
    )
    segment = analyze_static(
        traj, Config(angular_speed_threshold=2.0)
    ).segments[0]
    assert segment["angle_rms_deg"] == pytest.approx(np.sqrt(2 / 5))
    assert segment["angle_max_deg"] == pytest.approx(1)


def test_detect_noisy_stops_and_movement():
    times = np.arange(0, 8.01, 0.05)
    x = np.clip((times - 2) / 2, 0, 1) * 0.1
    xyz = np.column_stack((x, np.zeros((len(times), 2))))
    xyz[:, 1] = 0.0001 * np.sin(times * 30)
    traj = PoseTrajectory3D(xyz, np.tile([1, 0, 0, 0], (len(times), 1)), times)
    intervals = detect_static_intervals(traj)
    assert len(intervals) == 2
    assert times[intervals[0].stop - 1] <= 2.1
    assert times[intervals[1].start] >= 3.9
    result = analyze_static(traj)
    assert result.distances[0]["euclidean_distance"] == pytest.approx(
        100, abs=1.0
    )


def test_rotation_short_stops_and_gaps():
    times = np.arange(0, 3.01, 0.05)
    theta = np.deg2rad(times * 10) / 2
    quats = np.column_stack(
        (np.cos(theta), np.zeros((len(times), 2)), np.sin(theta))
    )
    assert (
        detect_static_intervals(
            PoseTrajectory3D(np.zeros((len(times), 3)), quats, times)
        )
        == []
    )
    short = PoseTrajectory3D(
        np.zeros((3, 3)), np.tile([1, 0, 0, 0], (3, 1)), [0, 0.2, 0.4]
    )
    assert detect_static_intervals(short) == []
    gap_times = np.r_[np.arange(0, 2.01, 0.1), np.arange(5, 7.01, 0.1)]
    gap = PoseTrajectory3D(
        np.zeros((len(gap_times), 3)),
        np.tile([1, 0, 0, 0], (len(gap_times), 1)),
        gap_times,
    )
    assert len(detect_static_intervals(gap)) == 2


@pytest.mark.parametrize(
    "field,value",
    [
        ("timestamps", [0, 0, 1, 1.5, 2]),
        ("timestamps", [0, 2, 1, 1.5, 2.5]),
        ("timestamps", [0, 0.5, 1, 1.5, np.inf]),
        ("positions_xyz", np.full((5, 3), np.nan)),
        ("orientations_quat_wxyz", np.zeros((5, 4))),
    ],
)
def test_invalid_trajectory(field, value):
    traj = stops([[0, 0, 0]])
    getattr(traj, field)[:] = value
    with pytest.raises(StaticAnalysisException):
        analyze_static(traj)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"unit": "cm"},
        {"reference_mode": "invalid"},
        {"window": 0},
        {"min_duration": -1},
        {"speed_threshold": -1},
        {"max_gap": np.nan},
        {"closure": True},
    ],
)
def test_invalid_config(kwargs):
    with pytest.raises(StaticAnalysisException):
        analyze_static(stops([[0, 0, 0]]), Config(**kwargs))


def test_cli_single_and_multi_trajectory_exports_and_plots(
    tmp_path: Path, monkeypatch
):
    monkeypatch.setitem(SETTINGS, "plot_backend", "Agg")
    monkeypatch.setitem(SETTINGS, "plot_split", False)
    traj1 = tmp_path / "traj1.txt"
    traj2 = tmp_path / "traj2.txt"
    file_interface.write_tum_trajectory_file(
        traj1, stops([[0, 0, 0], [0.1, 0, 0], [0, 0, 0]])
    )
    file_interface.write_tum_trajectory_file(
        traj2, stops([[0, 0, 0], [0, 0.2, 0]])
    )
    config = tmp_path / "experiment.yaml"
    config.write_text(
        yaml.safe_dump(
            {
                "unit": "mm",
                "reference_mode": "consecutive",
            }
        ),
        encoding="utf-8",
    )
    args = static_parser.parser().parse_args(
        [
            "tum",
            str(traj1),
            str(traj2),
            "--config",
            str(config),
            "--unit",
            "m",
            "--closure",
            "--no_warnings",
            "--save_json",
            str(tmp_path / "report.json"),
            "--save_csv",
            str(tmp_path / "report.csv"),
            "--save_plot",
            str(tmp_path / "report.pdf"),
        ]
    )
    static.run(entry_points.merge_config(args, static.CONFIG_FORMAT))
    report = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert report["config"]["unit"] == "mm"
    assert len(report["trajectories"]) == 2
    first = report["trajectories"][0]
    second = report["trajectories"][1]
    assert first["closure"]["euclidean_distance"] == pytest.approx(0)
    assert first["summary"]["euclidean_distance_mean"] == pytest.approx(100)
    assert second["distances"][0]["delta_xyz"] == pytest.approx([0, 200, 0])
    assert second["distances"][0]["abs_delta_xyz"] == pytest.approx(
        [0, 200, 0]
    )
    assert second["distances"][0]["euclidean_distance"] == pytest.approx(200)
    with (tmp_path / "report.csv").open(
        newline="", encoding="utf-8"
    ) as source:
        rows = list(csv.DictReader(source))
    assert len(rows) == 7
    assert rows[0]["source"] == str(traj1)
    assert rows[3]["type"] == "closure"
    assert rows[4]["source"] == str(traj2)
    assert rows[0]["euclidean_distance"] == ""
    assert float(rows[1]["euclidean_distance"]) == pytest.approx(100)
    assert (tmp_path / "report.pdf").stat().st_size > 1000


def test_identical_nonidentity_rotation_and_half_turn():
    same = analyze_static(
        stops([[0, 0, 0], [0, 0, 0]], [47, 47]), Config(closure=True)
    )
    assert same.closure is not None
    assert same.closure["rotation_angle_deg"] == pytest.approx(0, abs=1e-10)
    half_turn = analyze_static(
        stops([[0, 0, 0], [0, 0, 0]], [0, 180]), Config(closure=True)
    )
    assert half_turn.closure is not None
    assert half_turn.closure["rotation_angle_deg"] == pytest.approx(180)


@pytest.mark.parametrize(
    "mode,second_delta,second_euclidean",
    [
        ("origin", [0, 0, 0], 0),
        ("consecutive", [-100, 0, 0], 100),
    ],
)
def test_repository_examples(mode, second_delta, second_euclidean):
    root = Path(__file__).resolve().parents[1] / "examples" / "static_analysis"
    config = Config(
        **yaml.safe_load((root / f"{mode}.yaml").read_text(encoding="utf-8")),
        closure=True,
    )
    result = analyze_static(
        file_interface.read_tum_trajectory_file(root / "trajectory.tum"),
        config,
    )
    assert len(result.segments) == 3
    assert result.distances[0]["delta_xyz"] == pytest.approx([100, 0, 0])
    assert result.distances[0]["euclidean_distance"] == pytest.approx(100)
    assert result.distances[1]["delta_xyz"] == pytest.approx(second_delta)
    assert result.distances[1]["euclidean_distance"] == pytest.approx(
        second_euclidean
    )
    assert result.closure is not None
    assert result.closure["euclidean_distance"] == pytest.approx(0)


@pytest.mark.parametrize("suffix", ["yaml", "yml"])
def test_yaml_config_comments_booleans_and_settings(
    tmp_path, monkeypatch, suffix
):
    monkeypatch.setitem(SETTINGS, "plot_split", False)
    config = tmp_path / f"experiment.{suffix}"
    config.write_text(
        "# YAML config with Unicode: 静止分析\n"
        "unit: m\n"
        "closure: true\n"
        "plot_split: true\n"
        "min_duration: 2.5\n",
        encoding="utf-8",
    )
    args = static_parser.parser().parse_args(
        ["tum", "trajectory.tum", "--config", str(config)]
    )
    merged = entry_points.merge_config(args, static.CONFIG_FORMAT)
    assert merged.unit == "m"
    assert merged.closure is True
    assert merged.min_duration == pytest.approx(2.5)
    assert SETTINGS.plot_split is True


@pytest.mark.parametrize(
    "content",
    [
        "",
        "null",
        "- unit\n- mm",
        "unit: [",
        "1: mm",
        "!!python/object/apply:os.system ['echo unsafe']",
    ],
)
def test_invalid_yaml_config(tmp_path, content):
    config = tmp_path / "invalid.yaml"
    config.write_text(content, encoding="utf-8")
    args = static_parser.parser().parse_args(
        ["tum", "trajectory.tum", "--config", str(config)]
    )
    with pytest.raises(EvoException, match="YAML config"):
        entry_points.merge_config(args, static.CONFIG_FORMAT)


def test_other_commands_keep_json_config(tmp_path):
    from evo.cli import traj_parser

    config = tmp_path / "trajectory.json"
    config.write_text(json.dumps({"plot": True}))
    args = traj_parser.parser().parse_args(
        ["tum", "trajectory.tum", "--config", str(config)]
    )
    assert entry_points.merge_config(args).plot is True


def test_cli_invalid_yaml_reports_error(tmp_path, monkeypatch, capsys):
    config = tmp_path / "invalid.yaml"
    config.write_text("unit: [", encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["evo_static", "tum", "trajectory.tum", "--config", str(config)],
    )
    with pytest.raises(SystemExit) as exc:
        entry_points.launch(static, static_parser.parser())
    assert exc.value.code == 2
    error = capsys.readouterr().err
    assert "Invalid YAML config" in error
    assert "Traceback" not in error


def test_plot_report_chinese_and_distinct_labels(tmp_path: Path, monkeypatch):
    from evo.tools.static_report import plot_report

    monkeypatch.setitem(SETTINGS, "plot_backend", "Agg")
    monkeypatch.setitem(SETTINGS, "plot_split", False)
    trajs = []
    results = []
    for name in ("test1", "test2"):
        path = tmp_path / name / "trajectory_imu.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        traj = stops([[0, 0, 0], [0.1, 0, 0]])
        file_interface.write_tum_trajectory_file(path, traj)
        loaded = file_interface.read_tum_trajectory_file(path)
        trajs.append(loaded)
        results.append(analyze_static(loaded, Config(closure=True)))

    collection = plot_report(trajs, results)
    try:
        assert len(collection.figures) == 6
        titles = [
            fig._suptitle.get_text() for fig in collection.figures.values()
        ]
        assert any("test1/trajectory_imu.txt" in t for t in titles)
        assert any("test2/trajectory_imu.txt" in t for t in titles)
        assert all(
            any(
                k in t
                for k in ("静止区间检测", "静止段稳定性", "停靠点间距离与旋转")
            )
            for t in titles
        )
        first_intervals = next(
            fig
            for k, fig in collection.figures.items()
            if k.endswith("_intervals")
        )
        assert first_intervals.axes[-1].get_xlabel() == "轨迹起始时间 (s)"
        first_stability = next(
            fig
            for k, fig in collection.figures.items()
            if k.endswith("_stability")
        )
        assert "位置残差" in first_stability.axes[0].get_ylabel()
        assert "旋转残差" in first_stability.axes[1].get_ylabel()
        first_distances = next(
            fig
            for k, fig in collection.figures.items()
            if k.endswith("_distances")
        )
        assert first_distances.axes[-1].get_xlabel() == "停靠点对"
        euc_line = next(
            line
            for line in first_distances.axes[0].lines
            if line.get_label() == "欧氏距离"
        )
        assert euc_line.get_color() == "gold"
        assert len(first_distances.axes[0].texts) == 8
        assert len(first_distances.axes[1].texts) == 2
        out_pdf = tmp_path / "out.pdf"
        collection.export(str(out_pdf), confirm_overwrite=False)
        assert out_pdf.stat().st_size > 1000
    finally:
        collection.close()

    custom = plot_report(trajs, results, labels=["测试A", "测试B"])
    try:
        titles = [fig._suptitle.get_text() for fig in custom.figures.values()]
        assert any(t.startswith("测试A - ") for t in titles)
        assert any(t.startswith("测试B - ") for t in titles)
    finally:
        custom.close()


@pytest.mark.parametrize("closure", [False, True])
@pytest.mark.parametrize(
    "mode,expected_xyz,expected_angles,expected_labels",
    [
        (
            "origin",
            [[30, 40, 120], [1, 2, 2]],
            [10, 1],
            ["0->1", "0->2"],
        ),
        (
            "consecutive",
            [[30, 40, 120], [29, 42, 122]],
            [10, 9],
            ["0->1", "1->2"],
        ),
    ],
)
def test_plot_report_preserves_distances_with_optional_closure(
    monkeypatch, closure, mode, expected_xyz, expected_angles, expected_labels
):
    from evo.tools.static_report import plot_report

    monkeypatch.setitem(SETTINGS, "plot_backend", "Agg")
    traj = stops(
        [[0, 0, 0], [0.03, -0.04, 0.12], [0.001, 0.002, -0.002]],
        angles=[0, 10, 1],
    )
    result = analyze_static(traj, Config(reference_mode=mode, closure=closure))
    if closure:
        expected_xyz = expected_xyz + [[1, 2, 2]]
        expected_angles = expected_angles + [1]
        expected_labels = expected_labels + ["闭合误差"]

    collection = plot_report(traj, result)
    try:
        distance_axis, rotation_axis = collection.figures["distances"].axes
        assert [
            tick.get_text() for tick in rotation_axis.get_xticklabels()
        ] == expected_labels
        np.testing.assert_allclose(
            [line.get_ydata() for line in distance_axis.lines[:3]],
            np.array(expected_xyz).T,
        )
        euclidean = next(
            line
            for line in distance_axis.lines
            if line.get_label() == "欧氏距离"
        )
        np.testing.assert_allclose(
            euclidean.get_ydata(), np.linalg.norm(expected_xyz, axis=1)
        )
        np.testing.assert_allclose(
            rotation_axis.lines[0].get_ydata(), expected_angles
        )
        assert len(result.distances) == 2
    finally:
        collection.close()
