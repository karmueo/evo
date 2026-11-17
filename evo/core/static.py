"""Static trajectory evaluation in the trajectory's world coordinate axes.

This file is part of evo (github.com/MichaelGrupp/evo).
Copyright evo authors. Licensed under the GNU GPL v3 or later.
"""

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from evo import EvoException
from evo.core.trajectory import PoseTrajectory3D
from evo.core.transformations import quaternion_matrix


class StaticAnalysisException(EvoException):
    pass


@dataclass
class StaticAnalysisConfig:
    reference_mode: str = "origin"
    unit: str = "mm"
    closure: bool = False
    window: float = 0.5
    speed_threshold: float = 0.008
    angular_speed_threshold: float = 1.0
    min_duration: float = 2.0
    max_gap: float = 0.5

    def validate(self) -> None:
        for name, choices in (
            ("unit", ("m", "mm")),
            ("reference_mode", ("origin", "consecutive")),
        ):
            if getattr(self, name) not in choices:
                raise StaticAnalysisException(
                    f"Invalid {name}: {getattr(self, name)}"
                )
        for name in ("window", "min_duration", "max_gap"):
            value = getattr(self, name)
            if (
                not isinstance(value, (int, float))
                or not np.isfinite(value)
                or value <= 0
            ):
                raise StaticAnalysisException(
                    f"{name} must be finite and positive"
                )
        for name in ("speed_threshold", "angular_speed_threshold"):
            value = getattr(self, name)
            if (
                not isinstance(value, (int, float))
                or not np.isfinite(value)
                or value < 0
            ):
                raise StaticAnalysisException(
                    f"{name} must be finite and nonnegative"
                )


@dataclass(frozen=True)
class StaticInterval:
    """Half-open sample indices; reported timestamps include both endpoints."""

    start: int
    stop: int


@dataclass
class StaticAnalysisResult:
    config: StaticAnalysisConfig
    segments: list[dict[str, Any]]
    distances: list[dict[str, Any]]
    closure: dict[str, Any] | None
    summary: dict[str, float]
    source: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _validate_trajectory(traj: PoseTrajectory3D) -> None:
    if not isinstance(traj, PoseTrajectory3D) or traj.num_poses < 2:
        raise StaticAnalysisException(
            "At least two timestamped poses are required"
        )
    if not all(
        np.isfinite(a).all()
        for a in (
            traj.positions_xyz,
            traj.orientations_quat_wxyz,
            traj.timestamps,
        )
    ):
        raise StaticAnalysisException("Trajectory contains non-finite values")
    valid, details = traj.check()
    if not valid:
        raise StaticAnalysisException(f"Invalid trajectory: {details}")


def _angles(reference: np.ndarray, rotations: np.ndarray) -> np.ndarray:
    # atan2 avoids the loss of precision of acos(trace) near zero angle.
    relative = np.einsum("ji,njk->nik", reference, rotations)
    skew = np.column_stack(
        (
            relative[:, 2, 1] - relative[:, 1, 2],
            relative[:, 0, 2] - relative[:, 2, 0],
            relative[:, 1, 0] - relative[:, 0, 1],
        )
    )
    sine = np.linalg.norm(skew, axis=1) / 2
    cosine = np.clip((np.trace(relative, axis1=1, axis2=2) - 1) / 2, -1, 1)
    return np.degrees(np.arctan2(sine, cosine))


def detect_static_intervals(
    traj: PoseTrajectory3D, config: StaticAnalysisConfig | None = None
) -> list[StaticInterval]:
    """Merge stable trailing windows without crossing timestamp gaps.

    Window motion rates use maximum displacement from the window's first
    pose, rather than accumulated path length, so pose noise is not summed.
    Thresholds are in m/s and degrees/s, independently of report units.
    """
    config = config or StaticAnalysisConfig()
    config.validate()
    _validate_trajectory(traj)
    times = traj.timestamps - traj.timestamps[0]
    positions = traj.positions_xyz
    rotations = np.array([p[:3, :3] for p in traj.poses_se3])
    candidates: list[StaticInterval] = []
    block_start = 0
    for end in range(1, len(times)):
        if times[end] - times[end - 1] > config.max_gap:
            block_start = end
        start = (
            int(
                np.searchsorted(
                    times, times[end] - config.window, side="right"
                )
            )
            - 1
        )
        if start < block_start or start >= end:
            continue
        duration = times[end] - times[start]
        translation = np.linalg.norm(
            positions[start : end + 1] - positions[start], axis=1
        ).max()
        angle = _angles(rotations[start], rotations[start : end + 1]).max()
        if (
            translation <= config.speed_threshold * duration + 1e-12
            and angle <= config.angular_speed_threshold * duration + 1e-8
        ):
            if candidates and start < candidates[-1].stop:
                candidates[-1] = StaticInterval(candidates[-1].start, end + 1)
            else:
                candidates.append(StaticInterval(start, end + 1))
    return [
        interval
        for interval in candidates
        if times[interval.stop - 1] - times[interval.start]
        >= config.min_duration - 1e-12
    ]


def analyze_static(
    traj: PoseTrajectory3D, config: StaticAnalysisConfig | None = None
) -> StaticAnalysisResult:
    """Evaluate automatically detected static stops using equal sample weights.

    Positions internally remain in meters; report positions and inter-stop
    distances use config.unit. No coordinate alignment or scaling is applied.
    """
    config = config or StaticAnalysisConfig()
    config.validate()
    _validate_trajectory(traj)
    intervals = detect_static_intervals(traj, config)
    if not intervals:
        raise StaticAnalysisException(
            "No static intervals found; adjust detection thresholds"
        )
    if config.closure and len(intervals) < 2:
        raise StaticAnalysisException(
            "Closure evaluation requires at least two static intervals"
        )
    scale = 1000.0 if config.unit == "mm" else 1.0
    segments: list[dict[str, Any]] = []
    means: list[np.ndarray] = []
    rotations: list[np.ndarray] = []
    for index, interval in enumerate(intervals):
        sl = slice(interval.start, interval.stop)
        xyz = traj.positions_xyz[sl]
        mean = xyz.mean(axis=0)
        quats = traj.orientations_quat_wxyz[sl]
        # Markley mean is invariant to quaternion sign and uses no new dependency.
        _, vectors = np.linalg.eigh(quats.T @ quats)
        quat = vectors[:, -1]
        if quat[0] < 0:
            quat = -quat
        rotation = quaternion_matrix(quat)[:3, :3]
        angular = _angles(
            rotation, np.array([p[:3, :3] for p in traj.poses_se3[sl]])
        )
        residual = np.linalg.norm(xyz - mean, axis=1) * scale
        means.append(mean * scale)
        rotations.append(rotation)
        start_time = float(traj.timestamps[interval.start])
        end_time = float(traj.timestamps[interval.stop - 1])
        segments.append(
            {
                "index": index,
                "start_index": interval.start,
                "stop_index": interval.stop,
                "start_time": start_time,
                "end_time": end_time,
                "duration": end_time - start_time,
                "start_relative": float(start_time - traj.timestamps[0]),
                "end_relative": float(end_time - traj.timestamps[0]),
                "sample_count": interval.stop - interval.start,
                "position": (mean * scale).tolist(),
                "quaternion_wxyz": quat.tolist(),
                "position_std": (xyz.std(axis=0) * scale).tolist(),
                "position_rms": float(np.sqrt(np.mean(residual**2))),
                "position_max": float(residual.max()),
                "angle_rms_deg": float(np.sqrt(np.mean(angular**2))),
                "angle_max_deg": float(angular.max()),
            }
        )

    def measure_distance(first: int, last: int) -> dict[str, Any]:
        delta = means[last] - means[first]
        abs_delta = np.abs(delta)
        euclidean = float(np.linalg.norm(delta))
        return {
            "reference_index": first,
            "index": last,
            "delta_xyz": delta.tolist(),
            "abs_delta_xyz": abs_delta.tolist(),
            "euclidean_distance": euclidean,
            "rotation_angle_deg": float(
                _angles(rotations[first], np.array([rotations[last]]))[0]
            ),
        }

    distances = [
        measure_distance(
            0 if config.reference_mode == "origin" else i - 1,
            i,
        )
        for i in range(1, len(intervals))
    ]
    closure = (
        measure_distance(0, len(intervals) - 1) if config.closure else None
    )
    summary: dict[str, float] = {}
    if distances:
        values = np.array([row["euclidean_distance"] for row in distances])
        summary = {
            "euclidean_distance_mean": float(np.mean(values)),
            "euclidean_distance_min": float(values.min()),
            "euclidean_distance_max": float(values.max()),
        }
    return StaticAnalysisResult(
        config, segments, distances, closure, summary, traj.name
    )
