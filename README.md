# evo

[![CI](https://github.com/MichaelGrupp/evo/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/MichaelGrupp/evo/actions/workflows/ci.yml)

evo 是用于处理、评估和比较里程计及 SLAM 轨迹的 Python 软件包，支持 Linux、macOS 和 Windows。需要 Python 3.11 或更高版本；以下安装命令应在合适的隔离环境中运行，源码安装和示例从仓库根目录开始。必需依赖及可选组件见 [pyproject.toml](pyproject.toml)。支持 TUM、KITTI、EuRoC MAV 及 ROS/ROS2 bag 等格式，详见[格式说明](https://github.com/MichaelGrupp/evo/wiki/Formats)。读取 bag 的 `/tf` 话题需要 ROS；其他受支持的话题可通过依赖 rosbags 读取。

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

<a id="为什么选择-evo"></a>

## 安装

以下安装命令统一使用 [uv](https://docs.astral.sh/uv/getting-started/installation/)，请先创建并激活虚拟环境（见[从源码安装](#从源码安装)中的环境准备命令）。`uv venv` 默认不安装 `pip`；使用 `uv pip install` 可直接向虚拟环境安装软件包，避免调用系统 `pip`。

### 从源码安装

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)，在仓库根目录执行：

```bash
# 创建 Python 3.11 虚拟环境
uv venv \
  --python 3.11 \
  .venv
```

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `--python` | 选择 Python 版本 | 输入值 | 默认依赖环境；此处指定 `3.11` |
| 路径 | 指定虚拟环境位置 | 输出目录 | 此处为 `.venv`；其他默认行为待确认 |

```bash
# 激活虚拟环境
source .venv/bin/activate
```

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| 文件路径 | 指定当前 shell 执行的激活脚本 | 输入文件 | 必填；此处为 `.venv/bin/activate` |

```bash
# 以可编辑模式安装当前项目
uv pip install \
  --editable .
```

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `--editable` | 以可编辑模式安装项目 | 输入目录 | 默认不启用；此处使用当前目录 `.` |

```bash
# 查看 APE 工具帮助
evo_ape \
  --help
```

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `-h`, `--help` | 显示帮助并退出 | 行为控制项 | 默认不启用；具体格式的参数见下方示例和 [解析器](evo/cli/ape_parser.py) |

新终端需重新激活环境；使用完毕后可运行 `deactivate` 退出。Pixi 用户可在已有环境中执行 `pixi add evo`，或在仓库中执行 `pixi shell`。

<a id="pixi"></a>
<a id="tab-补全"></a>
<a id="依赖项"></a>

### 可选组件

安装 [PyQt6](https://pypi.org/project/PyQt6/) 可使用 `qtagg` 绘图后端；安装 [contextily](https://contextily.readthedocs.io/) 可在地理参考数据图中添加地图瓦片。ROS 相关功能的条件见[格式说明](https://github.com/MichaelGrupp/evo/wiki/Formats)。安装 [argcomplete](https://github.com/kislyuk/argcomplete/) 后，可按其说明启用 Tab 补全。

```bash
# 设置绘图后端
evo_config set \
  plot_backend \
  qtagg
```

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `params` | 设置参数名称及值 | 输入值 | 按需指定；此处为 `plot_backend qtagg`，默认后端依赖环境，见[设置模板](evo/tools/settings_template.py) |
| `-c`, `--config` | 指定配置文件 | 输入兼输出文件 | 默认使用软件包设置 |
| `-m`, `--merge` | 合并其他配置文件 | 输入文件 | 默认未设置 |
| `--soft` | 合并时不覆盖 | 行为控制项 | 默认不启用 |
| `--no_color` | 禁用彩色输出 | 行为控制项 | 默认不启用 |

```bash
# 安装 Rerun 查看器依赖
uv pip install \
  rerun-sdk
```

参数说明同上方 `uv pip install`；请在安装 evo 的同一虚拟环境中执行。安装后可在支持的 evo 命令中添加 `--rerun`，详见 [Rerun 集成](https://github.com/MichaelGrupp/evo/wiki/Rerun-integration)。

<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_rerun.gif" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_rerun.gif" alt="evo" width="350" border="5" />
</a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_rerun.gif" target="_blank">
  <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_rerun.gif" alt="evo" width="350" border="5" />
</a>

## 命令行界面

激活环境后可使用 `evo_ape`、`evo_rpe`、`evo_traj`、`evo_res`、`evo_static` 和 `evo_config`。更多选项见各命令的 `--help` 及 [Wiki](https://github.com/MichaelGrupp/evo/wiki)。

`evo_traj`、`evo_ape` 和 `evo_rpe` 支持以下格式子命令，依据：[轨迹解析器](evo/cli/traj_parser.py)、[APE 解析器](evo/cli/ape_parser.py)和 [RPE 解析器](evo/cli/rpe_parser.py)。子命令必须显式指定；本文示例统一使用 `tum`。

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `tum` | 读取 TUM 轨迹 | 输入文件 | 无默认子命令；每行 `timestamp tx ty tz qx qy qz qw` |
| `kitti` | 读取 KITTI 位姿 | 输入文件 | 无默认子命令；每行 3×4 位姿矩阵展开为 12 个数，无时间戳 |
| `euroc` | 读取 EuRoC MAV 真值 | 输入文件 | 无默认子命令；真值为 CSV，APE/RPE 的估计轨迹为 TUM 格式 |
| `bag` | 读取 ROS 1 bag | 输入文件及话题名称 | 无默认子命令；轨迹工具选择轨迹话题，APE/RPE 指定参考和估计话题 |
| `bag2` | 读取 ROS 2 bag | 输入文件或目录及话题名称 | 无默认子命令；轨迹工具选择轨迹话题，APE/RPE 指定参考和估计话题 |
| `mcap` | 读取 MCAP | 输入文件及话题名称 | `bag2` 的别名 |

## 使用示例

以下命令均从仓库根目录执行。前三节使用 [test/data](test/data) 的 Freiburg TUM 数据，依次绘制轨迹、计算两组 APE 并比较结果。首次运行时 `results` 目录应尚未创建。配图使用原版 KITTI 示例，展示各类图表的形式。

### 1. 绘制多条轨迹

```bash
# 激活虚拟环境
source .venv/bin/activate

mkdir -p output

# 绘制两条 TUM 轨迹及参考轨迹
evo_traj tum \
  test/data/freiburg1_xyz-ORB_kf_mono.txt \
  test/data/freiburg1_xyz-rgbdslam.txt \
  --ref=test/data/freiburg1_xyz-groundtruth.txt \
  --save_plot=output/evo_traj.pdf \
  --plot_mode=xyz \
  --plot_relative_time \
  -a
```

以下为 `tum` 子命令参数；依据：[traj_parser.py](evo/cli/traj_parser.py)。未设置的可选值默认为空，开关默认关闭。

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `traj_files` | 待处理的轨迹文件 | 输入文件 | 必填，一个或多个 TUM 文件 |
| `--ref` | 参考轨迹 | 输入文件 | 未设置 |
| `-f`, `--full_check` | 执行全部检查并输出统计 | 行为控制项 | 默认关闭 |
| `-s`, `--correct_scale` | 校正尺度，需参考轨迹 | 行为控制项 | 默认关闭 |
| `--n_to_align` | 对齐使用的起始位姿数 | 输入值 | 默认 `-1`（全部）；整数 |
| `--sync` | 按时间戳关联，需参考轨迹 | 行为控制项 | 默认关闭 |
| `--transform_left`, `--transform_right` | 左乘或右乘变换 | 输入文件 | 未设置 |
| `--propagate_transform`, `--invert_transform` | 传播右乘变换或取逆 | 行为控制项 | 默认关闭 |
| `--t_offset`, `--t_max_diff` | 时间偏移及最大时间差 | 输入值 | 分别默认 `0.0`、`0.01`；浮点数 |
| `--sync_method` | 时间同步方法 | 输入值 | 默认 `nearest_time`；支持 `nearest_time`、`interpolation` |
| `--merge` | 合并轨迹 | 行为控制项 | 默认关闭 |
| `--project_to_plane` | 投影到平面 | 输入值 | 未设置；`xy`、`xz`、`yz` |
| `--downsample` | 限制位姿数量 | 输入值 | 未设置；整数 |
| `--motion_filter` | 按距离和角度过滤 | 输入值 | 未设置；两个浮点数，角度单位为度 |
| `-a`, `--align`; `--align_origin` | 对齐轨迹或原点 | 行为控制项 | 默认关闭；两者互斥 |
| `-p`, `--plot`; `--plot_relative_time` | 显示图窗或使用相对时间 | 行为控制项 | 默认关闭 |
| `--plot_mode` | 图的投影轴 | 输入值 | 默认由 `plot_mode_default` 设置；`xy`、`xz`、`yx`、`yz`、`zx`、`zy`、`xyz` |
| `--ros_map_yaml`, `--map_tile` | 选择 ROS 地图或地图瓦片 | 输入文件或值 | 未设置；瓦片需地理参考位姿和 contextily |
| `--save_plot`, `--save_table`, `--logfile` | 保存图、统计表或日志 | 输出文件 | 未设置 |
| `--rerun`, `--rerun_rec_id` | 发送可视化数据及指定记录 ID | 行为控制项、输入值 | 默认关闭；ID 未设置 |
| `--save_as_tum`, `--save_as_kitti`, `--save_as_bag`, `--save_as_bag2` | 按指定格式导出 | 行为控制项 | 默认关闭 |
| `--no_warnings`, `-v`, `--verbose`, `--show_full_names`, `--silent`, `--debug` | 控制警告、输出详略及名称 | 行为控制项 | 默认关闭 |
| `-c`, `--config` | 加载优先于命令行参数的配置 | 输入文件 | 未设置；JSON |
| `-h`, `--help` | 显示帮助 | 行为控制项 | 默认关闭 |

<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo.png" alt="evo" height="200" border="5" />
  </a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo_xyz.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/traj_demo_xyz.png" alt="evo" height="200" border="5" />
  </a>

### 2. 计算轨迹评估指标

```bash
# 创建结果目录
mkdir \
  results
```

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| 目录 | 指定要创建的目录 | 输出目录 | 必填；此处为 `results` |

```bash
# 对齐并校正单目尺度，计算和保存 ORB 轨迹的绝对位姿误差
evo_ape tum \
  test/data/freiburg1_xyz-groundtruth.txt \
  test/data/freiburg1_xyz-ORB_kf_mono.txt \
  -vas \
  --plot_mode xyz \
  --save_results results/ORB.zip
```

以下为 `tum` 子命令参数；依据：[ape_parser.py](evo/cli/ape_parser.py)。未设置的可选值默认为空，开关默认关闭。

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `ref_file`, `est_file` | 参考轨迹与估计轨迹 | 输入文件 | 均必填；TUM 文件 |
| `--t_max_diff` | 设置时间关联的最大时间差 | 输入值 | 默认 `0.01` 秒；浮点数 |
| `--t_offset` | 设置估计轨迹的时间偏移 | 输入值 | 默认 `0.0` 秒；浮点数 |
| `--sync_method` | 选择时间同步方法 | 输入值 | 默认 `nearest_time`；支持 `nearest_time`、`interpolation` |
| `--t_start` | 保留不早于该时间的轨迹数据 | 输入值 | 默认未设置；浮点时间戳，单位秒 |
| `--t_end` | 保留不晚于该时间的轨迹数据 | 输入值 | 默认未设置；浮点时间戳，单位秒 |
| `-r`, `--pose_relation` | 选择误差类型 | 输入值 | 默认 `trans_part`；`full`、`trans_part`、`rot_part`、`angle_deg`、`angle_rad`、`point_distance` |
| `-s`, `--correct_scale` | 校正尺度 | 行为控制项 | 默认关闭 |
| `--n_to_align` | 对齐使用的起始位姿数 | 输入值 | 默认 `-1`（全部）；整数 |
| `--change_unit` | 更改指标输出单位 | 输入值 | 未设置；支持的单位见 [units.py](evo/core/units.py) |
| `--project_to_plane`, `--downsample`, `--motion_filter` | 投影、降采样或过滤 | 输入值 | 默认及支持值见上方 `evo_traj` 表 |
| `-a`, `--align`; `--align_origin` | 对齐轨迹或原点 | 行为控制项 | 默认关闭；两者互斥 |
| `-p`, `--plot`; `--plot_full_ref` | 显示图窗或完整参考轨迹 | 行为控制项 | 默认关闭 |
| `--plot_mode` | 图的投影轴 | 输入值 | 默认及支持值见上方 `evo_traj` 表 |
| `--plot_x_dimension` | 原始误差图的横轴 | 输入值 | 默认 `seconds`，无时间戳时为 `index`；支持 `index`、`seconds`、`distances` |
| `--plot_colormap_min`, `--plot_colormap_max` | 色图上下限 | 输入值 | 默认使用误差最小值、最大值；浮点数 |
| `--plot_colormap_max_percentile` | 以百分位指定色图上限 | 输入值 | 未设置；浮点数，覆盖 `--plot_colormap_max` |
| `--ros_map_yaml`, `--map_tile`, `--save_plot`, `--rerun`, `--rerun_rec_id`, `--logfile` | 地图、图、Rerun 和日志选项 | 输入文件或值、输出文件、行为控制项 | 默认及条件见上方 `evo_traj` 表 |
| `--save_results` | 保存评估结果 | 输出文件 | 未设置；ZIP 路径 |
| `--no_warnings`, `-v`, `--verbose`, `--silent`, `--debug`, `-c`, `--config`, `-h`, `--help` | 控制输出、配置和帮助 | 行为控制项、输入文件 | 默认及条件见上方 `evo_traj` 表 |

<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_raw.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_raw.png" alt="evo" height="200" border="5" />
  </a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_map.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_ORB_map.png" alt="evo" height="200" border="5" />
  </a>

```bash
# 计算并保存 RGB-D SLAM 轨迹的绝对位姿误差
evo_ape tum \
  test/data/freiburg1_xyz-groundtruth.txt \
  test/data/freiburg1_xyz-rgbdslam.txt \
  -va \
  --plot \
  --plot_mode xz \
  --save_results results/RGBDSLAM.zip
```

<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_raw.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_raw.png" alt="evo" height="200" border="5" />
  </a>
<a href="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_map.png" target="_blank">
    <img src="https://raw.githubusercontent.com/MichaelGrupp/evo/master/doc/assets/ape_demo_S-PTAM_map.png" alt="evo" height="200" border="5" />
  </a>

### 3. 处理多个评估结果

两组结果使用相同的平移 APE 指标，ORB 额外进行了尺度校正。比较时用 `--ignore_title` 跳过由对齐方式产生的标题差异。

```bash
# 比较结果并保存统计表
evo_res \
  results/*.zip \
  -p \
  --ignore_title \
  --save_table results/table.csv
```

依据：[res_parser.py](evo/cli/res_parser.py)。

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `result_files` | 指定结果文件 | 输入文件 | 必填，一个或多个文件；示例通配符由 shell 展开 |
| `--merge`, `--use_rel_time`, `--use_filenames`, `--ignore_title` | 合并结果或调整时间、标签及标题 | 行为控制项 | 默认关闭 |
| `-p`, `--plot`, `--plot_markers` | 显示图窗或圆形标记 | 行为控制项 | 默认关闭 |
| `--save_plot`, `--save_table`, `--logfile` | 保存图、表或日志 | 输出文件 | 未设置 |
| `--rerun`, `--rerun_rec_id` | 发送可视化数据及指定记录 ID | 行为控制项、输入值 | 默认关闭；ID 未设置 |
| `--no_warnings`, `-v`, `--verbose`, `--silent`, `--debug`, `-c`, `--config`, `-h`, `--help` | 控制输出、配置和帮助 | 行为控制项、输入文件 | 默认及条件见上方 `evo_traj` 表 |

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

### 4. 轨迹静态分析

`evo_static` 每次分析一条 TUM 轨迹，支持自动检测或手动指定静止段。它评估段内位姿抖动，计算各静止段平均位姿之间的欧氏距离、$x, y, z$ 坐标差及可选的首尾位姿距离。

#### 手动指定静止段

用相对时间绘制待分析的单条轨迹，从时间轴读取各静止段的起点和终点。

```bash
evo_traj tum examples/static_analysis/trajectory.tum --plot --plot_relative_time
```

在传给 `--config` 的 YAML 中填写一个或多个顶层区间。以下配置选取 OpenVINS 示例轨迹两次停靠中的稳定时段。

```yaml
static_0:
  enable: true
  start_time: 15.0
  end_time: 20.0
static_1:
  enable: true
  start_time: 50.0
  end_time: 60.0
```

`start_time` 和 `end_time` 以轨迹首帧为零点，单位为秒。两端都计入区间，且须满足 `0 ≤ start_time < end_time ≤ 轨迹时长`，至少覆盖一帧。省略 `enable` 时默认启用。只要有启用的手动段，命令就按时间顺序用这些段的平均位姿计算距离。全部关闭或省略所有手动段时，命令使用自动检测。[origin.yaml](examples/static_analysis/origin.yaml) 启用手动段并以首段为基准，[consecutive.yaml](examples/static_analysis/consecutive.yaml) 使用自动检测并以前一段为基准。

#### 计算距离

```bash
mkdir -p output

# 用手动静止段计算段间距离并保存报告
evo_static tum \
  examples/static_analysis/trajectory.tum \
  --config examples/static_analysis/origin.yaml \
  --save_plot output/static_report.pdf \
  --plot
```

YAML 中已设置的键覆盖同名命令行设置，未设置的键保留命令行值。参数依据：[参数定义](evo/cli/static_parser.py)、[配置校验](evo/core/static.py)、[配置合并](evo/cli/entry_points.py)。表中的 `/` 后为对应 YAML 键。

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `trajectory`（位置参数） | 单条 TUM 轨迹路径 | 输入文件 | 必填 |
| `-c`、`--config` | 指定 YAML 配置 | 输入文件 | 未设置；顶层须为字符串键的映射 |
| `--reference_mode` / `reference_mode` | 指定距离基准点 | 输入值 | 默认 `origin`，首次静止点；支持 `consecutive`，上一次静止点 |
| `--unit` / `unit` | 指定位置和距离结果的单位 | 输入值 | 默认 `mm`；支持 `m`；不改变 TUM 输入单位 |
| `--closure` / `closure` | 计算首末静止段平均位姿之间的距离 | 行为控制项 | 默认 `false`，启用时至少需要两段静止区间 |
| `--window` / `window` | 自动检测窗口时长 | 输入值 | 默认 `0.5` 秒；有限正数 |
| `--speed_threshold` / `speed_threshold` | 平移窗口运动率上限 | 输入值 | 默认 `0.008` m/s；有限非负数，不随 `unit` 改变 |
| `--angular_speed_threshold` / `angular_speed_threshold` | 旋转窗口运动率上限 | 输入值 | 默认 `1.0` 度/秒；有限非负数 |
| `--min_duration` / `min_duration` | 自动区间最短持续时间 | 输入值 | 默认 `2.0` 秒；有限正数 |
| `--max_gap` / `max_gap` | 自动区间内相邻采样最大间隔，超出则分开检测 | 输入值 | 默认 `0.5` 秒；有限正数 |
| `static_0`、`static_1` 等 | 手动指定静止段 | YAML 配置项 | 可选，每段包含开关及相对时间 |
| `--labels` / `labels` | 为图表指定轨迹标签 | 输入值 | 可选，命令行接受一个标签，YAML 使用只含一个标签的列表 |
| `--plot` / `plot` | 交互显示图表 | 行为控制项（非输入输出） | 默认 `false`；需可用的图形显示环境 |
| `--save_json` / `save_json` | 指定 JSON 报告路径 | 输出文件 | 未设置，不保存 |
| `--save_csv` / `save_csv` | 指定 CSV 表格路径 | 输出文件 | 未设置，不保存 |
| `--save_plot` / `save_plot` | 指定图表导出路径 | 输出文件 | 未设置，不保存；PDF 默认合并为多页，其他格式或启用 `plot_split` 时按图名拆分 |
| `--no_warnings` / `no_warnings` | 跳过覆盖已有报告、表格和图表的确认 | 行为控制项（非输入输出） | 默认 `false`；启用后直接覆盖 |
| `--verbose` / `verbose` | 显示调试级别日志 | 行为控制项（非输入输出） | 默认 `false` |
| `--debug` / `debug` | 显示调试日志及详细日志头 | 行为控制项（非输入输出） | 默认 `false` |
| `--silent` / `silent` | 终端仅显示警告及错误 | 行为控制项（非输入输出） | 默认 `false`；`verbose` 或 `debug` 启用时优先显示调试日志 |
| `--logfile` / `logfile` | 指定本地日志路径 | 输出文件 | 未设置，不额外写入本地日志；全局日志由 evo 设置控制 |
| `-h`、`--help` | 显示帮助并退出 | 行为控制项（非输入输出） | 默认不启用；主命令与 `tum` 子命令均支持 |

JSON 包含配置、数据源、静止段、段间距离、可选首尾距离和汇总。CSV 每段一行（`type=stop`），首尾评估追加 `type=closure` 行。`stop_index` 是切片结束索引。位置与距离单位由 `unit` 指定，姿态为度，时间为秒。

使用 `--plot` 或 `--save_plot` 时，报告包含三维估计轨迹、静止区间、段内残差和段间距离。三维图用彩色标记显示静止段的 XYZ 平均位置，最后一个静止点用 X，其余用圆点。坐标完全重合时，按标记从大到小叠画。分图导出时，三维图的文件名以 `_trajectory_3d` 结尾，例如 `static_report_trajectory_3d.png`。详见[报告实现](evo/tools/static_report.py)。



#### Python 调用

在仓库根目录运行下列 Python 代码；示例自动检测静止段，计算段间距离并启用首尾评估。

```python
# 读取 TUM 轨迹，分析静止段及距离并打印字典报告
from evo.core.static import StaticAnalysisConfig, analyze_static
from evo.tools.file_interface import read_tum_trajectory_file

traj = read_tum_trajectory_file("examples/static_analysis/trajectory.tum")
report = analyze_static(traj, StaticAnalysisConfig(closure=True))
print(report.to_dict())
```

接口依据：[轨迹读取](evo/tools/file_interface.py)、[静态分析配置与结果](evo/core/static.py)。

| 支持的参数／配置项 | 参数作用 | 输入/输出 | 默认值/支持的值 |
| --- | --- | --- | --- |
| `read_tum_trajectory_file(file_path)` 的 `file_path` | 指定 TUM 数据源 | 输入文件或可读文件句柄；返回 `PoseTrajectory3D` | 必填，无默认值 |
| `StaticAnalysisConfig(...)` 的配置字段 | 设置距离基准、单位、首尾评估和检测参数 | 输入值 | 均可省略；字段名、默认值及范围见 CLI 首表中 `reference_mode` 至 `max_gap` 的对应 YAML 键；开关使用 Python 布尔值 |
| `analyze_static(traj, config=None)` 的 `traj` | 提供带时间戳的轨迹 | 输入值 | 必填，无默认值；`PoseTrajectory3D`，满足概述中的数据要求 |
| `analyze_static(...)` 的 `config` | 提供分析配置 | 输入值；返回 `StaticAnalysisResult` | 默认 `None`，使用 `StaticAnalysisConfig()` |
| `analyze_static(...)` 的 `manual_intervals` | 按名称传入相对时间区间 | 关键字参数，如 `{"static_0": (0.0, 2.0)}` | 默认 `None`，使用自动检测 |
| 无（`report.to_dict()`） | 无需配置 | 输出字典 | 不适用；包含配置、数据源、静止段、段间距离、可选首尾距离和汇总 |
| `print(...)` 的位置参数 | 提供要显示的报告字典 | 输入值；输出到标准输出 | 示例显式传入 `report.to_dict()`，不写报告文件 |

## IPython / Jupyter 资源

可打开 `notebooks/metrics_tutorial.ipynb`；有关环境准备见 [Jupyter 说明](doc/jupyter_notebook.md)。安装 IPython 后可使用 `evo_ipython` 启动 evo 配置的 shell。

## 社区贡献的实用工具

`contrib/` 中的非官方脚本不随软件包发布，也不在持续集成中定期测试。

## 遇到问题

查看命令帮助、[Wiki](https://github.com/MichaelGrupp/evo/wiki) 和[已关闭议题](https://github.com/MichaelGrupp/evo/issues?q=is%3Aissue+is%3Aclosed)，或创建[新议题](https://github.com/MichaelGrupp/evo/issues)。

## 参与贡献

欢迎通过 pull request 贡献补丁。

## 许可证

[GPL-3.0 或更高版本](https://www.gnu.org/licenses/gpl-3.0.html)。研究中可引用本仓库或使用以下条目：

```bibtex
@misc{grupp2017evo,
  title={evo: Python package for the evaluation of odometry and SLAM.},
  author={Grupp, Michael},
  howpublished={\url{https://github.com/MichaelGrupp/evo}},
  year={2017}
}
```
