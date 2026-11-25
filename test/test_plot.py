"""验证公共绘图模块的交互显示和轨迹端点标记。"""

import sys
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pytest

from evo.tools.settings import SETTINGS


@pytest.mark.parametrize(
    ("backend", "tabbed_window"),
    [("qtagg", "tabbed_qt_window"), ("tkagg", "tabbed_tk_window")],
)
def test_show_uses_pyplot_in_interactive_mode(
    monkeypatch: pytest.MonkeyPatch, backend: str, tabbed_window: str
) -> None:
    """验证切换到交互后端后，图表由 Matplotlib 非阻塞显示。"""
    from matplotlib.figure import Figure

    monkeypatch.setitem(SETTINGS, "plot_backend", "Agg")
    monkeypatch.setitem(SETTINGS, "plot_split", False)

    from evo.tools import plot

    monkeypatch.setattr(plot.mpl, "get_backend", lambda: backend)
    plots = plot.PlotCollection()
    plots.add_figure("trajectory", Figure())

    with (
        plot.plt.ion(),
        patch.object(plot.plt, "show") as show,
        patch.object(plots, tabbed_window) as show_tabbed,
    ):
        plots.show()

    show.assert_called_once_with()
    show_tabbed.assert_not_called()


@pytest.mark.parametrize("backend", ["qtagg", "tkagg"])
@pytest.mark.parametrize("command", ["static", "ape", "rpe"])
def test_cli_keeps_interactive_figures_open(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, backend: str, command: str
) -> None:
    """验证命令返回后，非阻塞显示的图表仍由 pyplot 管理。"""
    from evo.cli import entry_points

    monkeypatch.setitem(SETTINGS, "plot_backend", "Agg")
    monkeypatch.setitem(SETTINGS, "plot_split", False)

    from evo.tools import plot

    # 用 Agg 创建图表，只模拟交互后端的非阻塞显示，不需要桌面会话。
    monkeypatch.setattr(plot.mpl, "get_backend", lambda: backend)
    path = tmp_path / "stationary.tum"
    path.write_text(
        "".join(f"{i / 4} 0 0 0 0 0 0 1\n" for i in range(12)),
        encoding="utf-8",
    )
    trajectories = [str(path)] if command == "static" else [str(path)] * 2
    monkeypatch.setattr(
        sys, "argv", [f"evo_{command}", "tum", *trajectories, "--plot"]
    )

    existing = set(plot.plt.get_fignums())
    try:
        with plot.plt.ion(), patch.object(plot.plt, "show") as show:
            getattr(entry_points, command)()
        show.assert_called_once()
        assert set(plot.plt.get_fignums()) - existing
    finally:
        for number in set(plot.plt.get_fignums()) - existing:
            plot.plt.close(number)


@pytest.mark.parametrize("plot_mode", ["xz", "xyz"])
def test_trajectory_endpoint_markers(plot_mode: str) -> None:
    """验证二维和三维渲染中，带描边的端点标记绘制在轨迹上方。"""
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.figure import Figure

    from evo.core.trajectory import PosePath3D
    from evo.tools import plot

    end_pose = np.eye(4)
    end_pose[:3, 3] = [1, 2, 3]
    path = PosePath3D(poses_se3=[np.eye(4), end_pose])
    mode = plot.PlotMode(plot_mode)
    fig = Figure()
    canvas = FigureCanvasAgg(fig)
    ax = plot.prepare_axis(fig, mode)

    plot.traj_colormap(
        ax,
        path,
        [0.0, 1.0],
        mode,
        min_map=0.0,
        max_map=1.0,
        fig=fig,
        plot_start_end_markers=True,
    )
    canvas.draw()

    start, end = ax.get_lines()
    assert start.get_marker() == "o"
    assert start.get_fillstyle() == "none"
    assert end.get_marker() == "x"
    for marker in (start, end):
        assert marker.get_markersize() >= 10
        assert marker.get_zorder() > ax.collections[0].get_zorder()
        assert marker.get_path_effects()
