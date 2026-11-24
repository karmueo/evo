"""验证公共绘图模块在交互模式下的显示行为。"""

from unittest.mock import patch

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
