# evo

***用于评估里程计与 SLAM 的 Python 软件包***

| Linux / macOS / Windows / ROS / ROS2 |
| :---: |
| [![CI](https://github.com/MichaelGrupp/evo/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/MichaelGrupp/evo/actions/workflows/ci.yml) |

本软件包提供命令行工具和一个小型库，用于处理、评估和比较里程计及 SLAM 算法输出的轨迹。

支持的轨迹格式：

* TUM 轨迹文件
* KITTI 位姿文件
* EuRoC MAV（.csv 真值文件和 TUM 轨迹文件）
* 包含 `geometry_msgs/PoseStamped`、`geometry_msgs/TransformStamped`、`geometry_msgs/PoseWithCovarianceStamped`、`geometry_msgs/PointStamped` 或 `nav_msgs/Odometry` 话题，或包含 [TF 消息](https://github.com/MichaelGrupp/evo/wiki/Formats#bag---ros-bagfile)的 ROS 和 ROS2 bag 文件

有关格式的更多信息，请参阅[这里](https://github.com/MichaelGrupp/evo/wiki/Formats)。

<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_map.png" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_map.png" alt="evo" height="175" border="5" />
</a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/markers.png" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/markers.png" alt="evo" height="175" border="5" />
</a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/map_tile_osm.png" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/map_tile_osm.png" alt="evo" height="175" border="5" />
</a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_rerun.gif" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_rerun.gif" alt="evo" height="175" border="5" />
</a>

---

## 为什么选择 evo？

与其他公开的基准评测工具相比，evo 有以下优势：

* 使用通用工具处理不同格式
* 提供轨迹关联、对齐以及单目 SLAM 尺度调整等算法选项
* 提供灵活的输出、[绘图](https://github.com/MichaelGrupp/evo/wiki/Plotting)、[可视化](https://github.com/MichaelGrupp/evo/wiki/Rerun-integration)和导出选项（例如 LaTeX 图表或 Excel 表格）
* 功能强大且可配置的命令行界面，涵盖多种使用场景
* 模块化的 `core` 和 `tools` 库，便于自定义扩展
* 比其他成熟的 Python 工具更快（[详见这里](https://github.com/MichaelGrupp/evo/blob/master/doc/performance.md)）

**它不是什么：**针对特定数据集的某个评估协议的完全复现。

---

## 安装与升级

如果你熟悉[这些](https://xkcd.com/1987/#)，安装就很简单。

最新版 evo 支持 **Python 3.11 及以上版本**。

请仅在合适的环境中使用 `pip`（例如 `uv`/`uvx`、`pipx`、`venv`、Pixi 或传统的[虚拟环境](https://github.com/MichaelGrupp/evo/blob/master/doc/install_in_virtualenv.md)）。
> ⚠️ ☠️☠️☠️ ⚠️
>
> 无论如何，请勿使用 `pip install --user`、任何带 `--break-system-packages` 的命令，或者最糟糕的 `sudo pip install`。

### 从 PyPI 安装
如果只想使用最新发布版本的命令行工具，最简单的方法是运行：
```bash
pip install evo
```
这会从 [PyPI](https://pypi.org/project/evo/) 下载软件包及其依赖，并进行安装或升级。你也可以通过 https://libraries.io/pypi/evo 订阅新版本。

升级到新版本：`pip install --upgrade evo`

### 从源码安装

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，然后在当前项目根目录（包含 `pyproject.toml` 的目录）下运行：

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install --editable .
evo_ape --help
```

上述命令会在项目根目录创建 `.venv` 虚拟环境，并将当前项目及其依赖安装到该环境中。`--editable` 表示以可编辑模式安装，修改源码后无需重新安装；`evo_ape --help` 用于验证命令行工具是否可用。

Windows PowerShell 的激活命令为 `.venv\Scripts\Activate.ps1`。每次打开新终端后，需重新激活环境才能直接使用 `evo_ape` 等命令；使用完毕后运行 `deactivate` 退出环境。

### Pixi

如果需要隔离的开发环境，[Pixi](https://prefix.dev) 是一个易用的选择。已有环境中可运行 `pixi add evo`；也可以克隆本仓库，然后运行 `pixi shell` 进入开发环境。

### Tab 补全

通过 [argcomplete](https://github.com/kislyuk/argcomplete/) 软件包支持 Tab 补全。安装后运行 `activate-global-python-argcomplete` 即可使用。

### 依赖项

**Python 软件包**

evo 的必需依赖会在使用 pip 安装时***自动解析并安装***。
详细信息请参阅 `pyproject.toml` 文件。

**PyQt6（可选）**

[PyQt6](https://pypi.org/project/PyQt6/) 可通过 matplotlib 的 “*qtagg*” 后端为绘图提供增强的图形界面（否则使用 “*TkAgg*”）。如果安装本软件包时已安装 PyQt6，它将作为默认后端（参见 `evo_config show`）。若要在之后更改绘图后端，请运行 `evo_config set plot_backend qtagg`。

如果安装 tkinter 时遇到问题，可以尝试 PyQt6。

**ROS（可选）**

部分 ROS 相关功能需要安装 ROS，详见[这里](http://www.ros.org/)。本软件包使用 ROS Lyrical 进行测试。

> 得益于随 evo 一起安装的 [rosbags](https://pypi.org/project/rosbags/) 软件包，即使没有安装相应的 ROS 发行版，也可以读取 ROS 1 和 ROS 2 的 bag 文件。（读取 `/tf` 话题除外，因为它需要 ROS 提供的缓冲区实现。）

**contextily（可选）**

在地理参考数据的图中[添加地图瓦片](https://github.com/MichaelGrupp/evo/wiki/Plotting#geographic-map-tiles)需要安装 [contextily](https://contextily.readthedocs.io/en/latest/index.html)。

**Rerun（可选）**

也可以将数据发送到 [Rerun](https://rerun.io/) 查看器。只需运行 `pip install rerun-sdk`，并在命令中添加 `--rerun`。更多详情请参阅相关的 [Wiki 页面](https://github.com/MichaelGrupp/evo/wiki/Rerun-integration)。

<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_rerun.gif" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_rerun.gif" alt="evo" width="350" border="5" />
</a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_rerun.gif" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_rerun.gif" alt="evo" width="350" border="5" />
</a>

---

## 命令行界面

激活安装 evo 的虚拟环境后，可以在命令行中调用以下工具：

**评估指标：**

* `evo_ape` - 绝对位姿误差
* `evo_rpe` - 相对位姿误差

**工具：**

* `evo_traj` - 分析、绘制或导出一条或多条轨迹
* `evo_res` - 比较 `evo_ape` 或 `evo_rpe` 生成的一个或多个结果文件
* `evo_config` - 管理全局设置和配置文件

在命令后添加 `--help` 可查看选项，例如 `evo_ape --help`。类 UNIX 系统支持命令行参数的 Tab 补全。

**更多文档**
请参阅 [GitHub Wiki](https://github.com/MichaelGrupp/evo/wiki)。

---

## 使用示例

源码目录的 `test/data` 中包含一些示例轨迹。


### 1. 绘制多条轨迹

  这里使用 `evo_traj` 绘制两个 KITTI 位姿文件和真值轨迹：
  ```
  cd test/data
  evo_traj kitti KITTI_00_ORB.txt KITTI_00_SPTAM.txt --ref=KITTI_00_gt.txt -p --plot_mode=xz
  ```

  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo_xyz.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo_xyz.png" alt="evo" height="200" border="5" />
  </a>

### 2. 计算轨迹评估指标

  下面使用 `evo_ape` 计算 ORB-SLAM 和 S-PTAM 两条轨迹的绝对位姿误差（`KITTI_00_gt.txt` 是参考真值），绘制结果，并分别保存为供 `evo_res` 使用的 .zip 文件：

  *第一条轨迹（ORB Stereo）：*

  ```
  mkdir results
  evo_ape kitti KITTI_00_gt.txt KITTI_00_ORB.txt -va --plot --plot_mode xz --save_results results/ORB.zip
  ```

  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_raw.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_raw.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_map.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_map.png" alt="evo" height="200" border="5" />
  </a>

  *第二条轨迹（S-PTAM）：*

  ```
  evo_ape kitti KITTI_00_gt.txt KITTI_00_SPTAM.txt -va --plot --plot_mode xz --save_results results/SPTAM.zip
  ```

  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_raw.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_raw.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_map.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_map.png" alt="evo" height="200" border="5" />
  </a>


### 3. 处理多个评估结果

  `evo_res` 可用于比较多个评估结果文件，例如：
  * 输出信息和统计数据（默认）
  * 绘制结果
  * 将统计数据保存为表格

  这里使用上述结果生成图表和表格：
  ```
  evo_res results/*.zip -p --save_table results/table.csv
  ```

  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_raw.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_raw.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_dist.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_dist.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_stats.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_stats.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_box.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_box.png" alt="evo" height="200" border="5" />
  </a>
  <a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_violin.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/res_violin.png" alt="evo" height="200" border="5" />
  </a>

---

## IPython / Jupyter 资源

要查看交互式源码文档，请打开仓库 `notebooks` 目录中的 [Jupyter notebook](http://jupyter.readthedocs.io/en/latest/install.html) 文件 `metrics_tutorial.ipynb`。有关 Jupyter notebook 的更多信息，请参阅[这里](https://github.com/MichaelGrupp/evo/blob/master/doc/jupyter_notebook.md)。

如果已安装 IPython，可以使用 `evo_ipython` 命令启动加载了 evo 自定义配置的 IPython shell。

---

## 社区贡献的实用工具

仓库的 `contrib/` 目录收录了一些用于特定场景的“非官方”脚本。它们不随软件包发布，因此也不会在持续集成中定期测试。

---

## 遇到问题
*“😱，这个 💩 软件怎么不能按我的要求工作！！！”*

**排查步骤：**
* 在命令后添加 `-h` / `--help`
* 查阅 [Wiki](https://github.com/MichaelGrupp/evo/wiki)
* 查看[已关闭的议题](https://github.com/MichaelGrupp/evo/issues?q=is%3Aissue+is%3Aclosed)
* 创建[新议题](https://github.com/MichaelGrupp/evo/issues)

---

## 参与贡献

欢迎贡献补丁，建议通过 pull request 提交。

## 许可证

[GPL-3.0 或更高版本](https://www.gnu.org/licenses/gpl-3.0.html)

如果你在研究中使用本软件包，欢迎在脚注中附上本仓库链接：`github.com/MichaelGrupp/evo`。

或者，使用以下 BibTeX 条目引用：
```
@misc{grupp2017evo,
  title={evo: Python package for the evaluation of odometry and SLAM.},
  author={Grupp, Michael},
  howpublished={\url{https://github.com/MichaelGrupp/evo}},
  year={2017}
}
```
