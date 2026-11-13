# 仓库贡献指南

## 项目结构与模块组织

evo 提供 Python 库和命令行工具，用于评估里程计与 SLAM 轨迹。

- `evo/core/`：轨迹模型、几何运算、时间同步、过滤器和评估指标。
- `evo/tools/`：文件读写、绘图、配置和集成辅助工具。
- `evo/cli/`：命令入口与参数处理；指标计算流程还包括 `evo/main_ape.py` 和 `evo/main_rpe.py`。
- `test/`：单元测试和命令行冒烟测试；`data/` 存放轨迹测试数据，`cfg/` 存放测试配置。
- `doc/` 与 `doc/assets/`：文档和图片等资源；`examples/`、`notebooks/` 和 `contrib/` 提供使用示例与补充工具。

## 构建、测试与开发命令

使用 Python 3.11 或更高版本，在独立环境中开发。以下命令均在仓库根目录执行。

- `pixi install`：安装项目配置的开发环境。
- `pixi run test`：通过 `pytest -sv` 运行测试套件。
- `pixi run fmt`：使用 Black 格式化代码。
- `pixi run mypy`：执行静态类型检查。
- `pixi run black --check .`：检查格式，不修改文件。
- `pixi run hatch build`：构建源码包和 wheel 包，输出至 `dist/`。
- `pixi run evo_ape --help`：查看本地命令行工具的帮助。

也可在虚拟环境中执行 `python -m pip install --editable .`，以可编辑模式安装项目；开发工具需另行安装。

## 代码风格与命名约定

使用四个空格缩进，函数和模块采用 `snake_case`，类采用 `PascalCase`。Black 的行宽设为 79 个字符，遵循 `pyproject.toml` 中的排除规则。参照相邻代码添加类型注解，确保 mypy 检查通过。保留已有许可证文件头，并在文档字符串或注释中说明数值计算的前提假设。

## 测试规范

使用 pytest 运行测试，许多单元测试基于 `unittest.TestCase`。单元测试文件命名为 `test_*.py`，测试方法命名为 `test_*`。修复缺陷时补充回归测试，尽量复用 `test/helpers.py` 和现有测试数据。可先执行 `pixi run pytest -sv test/test_sync.py` 验证相关模块，提交前再运行完整套件。项目未配置数值化的覆盖率门槛。

## 提交与合并请求规范

近期提交使用简短的英文祈使句标题，例如 `Fix result merge strategy`，有时附带 PR 编号。沿用该风格，无须强制添加 Conventional Commits 前缀。每次提交应围绕一个明确的改动。

PR 应说明解决的问题、变更后的行为、关联议题及已执行的验证。涉及绘图变化时，按需附上前后对比图。遵循 `.github/pull_request_template.md`；由编码代理创建的 PR 还需满足其中的代理身份披露和诗句要求。确保格式检查、类型检查和测试均通过，与 CI 要求保持一致。
