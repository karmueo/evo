"""Tests for labeled Rerun statistics charts."""

import argparse
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

pytest.importorskip("rerun")

from evo.cli import res
from evo.core.result import Result
from evo.tools import pandas_bridge, rerun_bridge
from evo.tools.settings import SETTINGS


class StatisticsChartTest(unittest.TestCase):
    def test_result_comparison_views_display_statistics_images(self):
        keys = ["ORB", "RGBDSLAM"]
        frames = []
        for key in keys:
            result = Result()
            result.info.update(est_name=key, title="APE", label="APE (m)")
            result.stats["rmse"] = 0.04
            result.np_arrays["error_array"] = np.array([0.02, 0.05])
            frames.append(pandas_bridge.result_to_df(result))
        df = pd.concat(frames, axis="columns")

        with (
            patch.dict(SETTINGS, plot_statistics=["rmse"]),
            patch.object(rerun_bridge, "connect_or_spawn"),
            patch.object(rerun_bridge, "send_scalars"),
            patch.object(rerun_bridge.rr, "init"),
            patch.object(rerun_bridge.rr, "send_blueprint") as send_blueprint,
            patch.object(rerun_bridge.rr, "log") as log,
        ):
            res.send_to_rerun(
                argparse.Namespace(rerun_rec_id=None), df, keys, None, "APE"
            )

        send_blueprint.assert_called_once()
        blueprint = send_blueprint.call_args.args[0]
        views = blueprint.root_container.contents[1].contents
        self.assertEqual(len(views), len(keys))
        self.assertEqual(log.call_count, len(keys))
        for key, view, logged in zip(keys, views, log.call_args_list):
            with self.subTest(key=key):
                self.assertEqual(view.class_identifier, "2D")
                self.assertEqual(view.name, f"Statistics {key}")
                self.assertEqual(view.origin, f"/evo_res/statistics/{key}")
                self.assertEqual(view.contents, ["$origin"])
                self.assertEqual(f"/{logged.args[0]}", view.origin)
                self.assertIsInstance(logged.args[1], rerun_bridge.rr.Image)
                self.assertTrue(logged.kwargs["static"])

    def test_metric_labels_and_values(self):
        stats = {
            "max": 0.16,
            "min": 0.002,
            "std": 0.019,
            "mean": 0.041,
            "median": 0.042,
            "rmse": 0.045,
            "sse": 9.28,
        }
        with patch.dict(
            SETTINGS,
            plot_statistics=["rmse", "median", "mean", "std", "min", "max"],
        ):
            figure = rerun_bridge._statistics_figure(stats, "APE (m)")
        assert figure is not None
        ax = figure.axes[0]
        self.assertEqual(
            [tick.get_text() for tick in ax.get_xticklabels()],
            ["RMSE", "Median", "Mean", "Std", "Min", "Max"],
        )
        np.testing.assert_allclose(
            [bar.get_height() for bar in ax.patches],
            [0.045, 0.042, 0.041, 0.019, 0.002, 0.16],
        )
        self.assertEqual(ax.get_ylabel(), "APE (m)")
        self.assertGreater(ax.get_ylim()[1], stats["max"] * 1.1)

    def test_configured_order_and_missing_statistics(self):
        with patch.dict(SETTINGS, plot_statistics=["max", "missing", "rmse"]):
            figure = rerun_bridge._statistics_figure(
                {"rmse": 0.04, "max": 0.16}, "RPE (deg)"
            )
        assert figure is not None
        ax = figure.axes[0]
        self.assertEqual(
            [tick.get_text() for tick in ax.get_xticklabels()],
            ["Max", "RMSE"],
        )
        self.assertEqual(ax.get_ylabel(), "RPE (deg)")

    def test_statistics_are_logged_as_static_image(self):
        with (
            patch.dict(SETTINGS, plot_statistics=["rmse"]),
            patch.object(rerun_bridge.rr, "log") as log,
        ):
            rerun_bridge.send_statistics_bar_chart(
                "evo_ape/error/statistics", {"rmse": 0.04}, "APE (m)"
            )
        log.assert_called_once()
        self.assertEqual(log.call_args.args[0], "evo_ape/error/statistics")
        self.assertIsInstance(log.call_args.args[1], rerun_bridge.rr.Image)
        self.assertTrue(log.call_args.kwargs["static"])

    def test_disabled_or_missing_statistics_do_not_log(self):
        for names in ([], ["missing"]):
            with (
                self.subTest(names=names),
                patch.dict(SETTINGS, plot_statistics=names),
                patch.object(rerun_bridge.rr, "log") as log,
            ):
                rerun_bridge.send_statistics_bar_chart(
                    "evo_ape/error/statistics", {"rmse": 0.04}
                )
                log.assert_not_called()
