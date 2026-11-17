"""CLI for static trajectory evaluation (GPL v3 or later)."""

import argparse
import logging
from dataclasses import fields

from evo.core.static import StaticAnalysisConfig, analyze_static
from evo.tools import file_interface, log
from evo.tools.static_report import format_report, save_csv, save_json

CONFIG_FORMAT = "yaml"

logger = logging.getLogger(__name__)


def run(args: argparse.Namespace) -> None:
    log.configure_logging(
        args.verbose, args.silent, args.debug, local_logfile=args.logfile
    )
    config = StaticAnalysisConfig(
        **{f.name: getattr(args, f.name) for f in fields(StaticAnalysisConfig)}
    )
    trajectories = [
        file_interface.read_tum_trajectory_file(path)
        for path in args.trajectories
    ]
    results = [analyze_static(traj, config) for traj in trajectories]
    logger.info(format_report(results))
    if args.save_json:
        save_json(
            results, args.save_json, confirm_overwrite=not args.no_warnings
        )
    if args.save_csv:
        save_csv(
            results, args.save_csv, confirm_overwrite=not args.no_warnings
        )
    if args.plot or args.save_plot:
        from evo.tools.static_report import plot_report

        plots = plot_report(
            trajectories, results, labels=getattr(args, "labels", None)
        )
        try:
            if args.save_plot:
                plots.export(
                    args.save_plot, confirm_overwrite=not args.no_warnings
                )
            if args.plot:
                plots.show()
        finally:
            plots.close()
