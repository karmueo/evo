"""读取静态分析配置与单条轨迹，并生成报告（GPL v3 或更高版本）。"""

import argparse
import logging
import re
from dataclasses import fields

from evo.core.static import (
    StaticAnalysisConfig,
    StaticAnalysisException,
    analyze_static,
)
from evo.tools import file_interface, log
from evo.tools.static_report import format_report, save_csv, save_json

CONFIG_FORMAT = "yaml"

logger = logging.getLogger(__name__)


def _manual_intervals(
    args: argparse.Namespace,
) -> dict[str, tuple[float, float]]:
    """从合并后的参数提取启用的区间，配置结构错误时抛出异常。"""
    intervals: dict[str, tuple[float, float]] = {}
    for name, section in vars(args).items():
        if not re.fullmatch(r"static_[0-9]+", name):
            continue
        if not isinstance(section, dict):
            raise StaticAnalysisException(f"{name} must be a YAML mapping")
        enabled = section.get("enable", True)
        if not isinstance(enabled, bool):
            raise StaticAnalysisException(f"{name}.enable must be a boolean")
        if not enabled:
            continue
        for field in ("start_time", "end_time"):
            if field not in section:
                raise StaticAnalysisException(f"{name}.{field} is required")
        intervals[name] = (section["start_time"], section["end_time"])
    return intervals


def run(args: argparse.Namespace) -> None:
    """分析一条 TUM 轨迹并按参数输出报告，配置无效时抛出异常。"""
    log.configure_logging(
        args.verbose, args.silent, args.debug, local_logfile=args.logfile
    )
    config = StaticAnalysisConfig(
        **{f.name: getattr(args, f.name) for f in fields(StaticAnalysisConfig)}
    )
    if not isinstance(args.trajectory, str) or not args.trajectory:
        raise StaticAnalysisException("Expected one TUM trajectory path")
    labels = getattr(args, "labels", None)
    if labels is not None and (
        not isinstance(labels, list)
        or len(labels) != 1
        or not isinstance(labels[0], str)
    ):
        raise StaticAnalysisException("Expected one trajectory label")
    intervals = _manual_intervals(args)
    traj = file_interface.read_tum_trajectory_file(args.trajectory)
    result = analyze_static(traj, config, manual_intervals=intervals)
    logger.info(format_report(result))
    if args.save_json:
        save_json(
            result, args.save_json, confirm_overwrite=not args.no_warnings
        )
    if args.save_csv:
        save_csv(result, args.save_csv, confirm_overwrite=not args.no_warnings)
    if args.plot or args.save_plot:
        from evo.tools.static_report import plot_report

        plots = plot_report(traj, result, labels=labels)
        try:
            if args.save_plot:
                plots.export(
                    args.save_plot, confirm_overwrite=not args.no_warnings
                )
            if args.plot:
                plots.show()
        finally:
            plots.close()
