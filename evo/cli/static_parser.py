"""Argument parser for static trajectory evaluation (GPL v3 or later)."""

import argparse


def parser() -> argparse.ArgumentParser:
    main = argparse.ArgumentParser(description="Static trajectory evaluation")
    sub = main.add_subparsers(dest="subcommand", required=True)
    tum = sub.add_parser("tum", help="TUM trajectory (positions in meters)")
    tum.add_argument(
        "trajectories",
        nargs="+",
        metavar="trajectory",
        help="one or more estimated TUM trajectory files",
    )
    tum.add_argument(
        "--reference_mode", choices=("origin", "consecutive"), default="origin"
    )
    tum.add_argument(
        "--unit",
        choices=("mm", "m"),
        default="mm",
        help="output position and distance unit; TUM input positions remain meters",
    )
    tum.add_argument(
        "--closure",
        action="store_true",
        help="evaluate distance between first and last detected stops",
    )
    for name, value, help_text in (
        ("window", 0.5, "detection window duration (s)"),
        (
            "speed_threshold",
            0.008,
            "window translation motion rate limit (m/s)",
        ),
        (
            "angular_speed_threshold",
            1.0,
            "window angular motion rate limit (deg/s)",
        ),
        ("min_duration", 2.0, "minimum detected stop duration (s)"),
        ("max_gap", 0.5, "maximum timestamp gap within a detected stop (s)"),
    ):
        tum.add_argument(
            "--" + name, type=float, default=value, help=help_text
        )
    tum.add_argument(
        "-c",
        "--config",
        help="YAML parameters (override command line arguments)",
    )
    tum.add_argument(
        "--labels",
        nargs="+",
        help="optional display labels for input trajectories in plots",
    )
    for name in ("save_json", "save_csv", "save_plot", "logfile"):
        tum.add_argument("--" + name, help="output file path")
    for name in ("plot", "verbose", "silent", "debug", "no_warnings"):
        tum.add_argument("--" + name, action="store_true")
    return main
