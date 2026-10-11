# Manipulation Learning Lab

**语言 / Language：** 简体中文 | [English](README.en.md)

## 从示教数据学习机器人操作

### 1. 实验概览

本实验使用人类示教数据，训练仿真中的 Panda 机械臂抓起罐子并放入目标料箱。你将检查数据、训练两组 Behavior Cloning（BC，行为克隆）策略、在相同条件下比较评测结果，并结合视频和状态记录解释一次真实失败。

**适用对象：** 具备 Python 和机器学习基础的研究生。**预计时间：** 教师准备好服务器、数据集和参考案例后，核心作业需要 2–3 小时。环境安装和数据下载不计入课堂时间。无需机器人硬件。

本实验沿用已经验证的 **robosuite + robomimic + MuJoCo** 流程，不依赖其他项目、已有 Conda 环境或私有模型。所有实验指标均来自实际训练和仿真执行。

### 2. 学习目标

完成实验后，你应能够：

- 检查 Demonstration Dataset（示教数据集），区分 Observation（观测）与 Action（动作）。
- 解释 Behavior Cloning：根据观测预测专家动作。
- 训练 Policy（策略），使用验证集选择 Checkpoint（模型检查点）。
- 解释 Closed-loop Inference（闭环推理）：每执行一次动作，都根据新的观测决定下一步动作。
- 设计 Controlled Experiment（受控对照实验），理解评测结果及其泛化结论的边界。
- 结合视频和状态曲线定位失败，区分观察到的事实与原因假设。

### 3. 任务说明

任务为 **robosuite PickPlaceCan**，使用 **Panda** 机械臂和平行夹爪。官方 robomimic **v1.5 Can / proficient-human / low-dimensional** 数据集包含 200 条人类示教、23,207 个控制步。按完整轨迹固定划分为 160 条训练数据、20 条验证数据和 20 条测试数据。测试集不参与模型权重选择。

| 项目 | 含义 |
|---|---|
| Policy 的 Observation：16 维 | 末端执行器在世界坐标系中的位置（3）、xyzw 四元数（4）、两个夹爪关节位置（2），以及罐子的世界位置和 xyzw 四元数（7） |
| Action：7 维 | 世界坐标系中的平移增量（3）、轴角旋转增量（3）、夹爪命令（1） |
| 坐标系与动作单位 | 世界坐标系，Z 轴向上；位置单位为米；动作归一化到 [-1, 1]，平移上限为 ±0.05 m，旋转上限为 ±0.5 rad |
| 夹爪命令 | 正值闭合，负值张开；命令无量纲，测得的开口单位为米 |
| 时间 | 控制频率为 20 Hz；使用控制步编号，不虚构采集时间戳 |
| 学生模型 | 现有的确定性 BC 多层感知机，含三个各 256 单元的隐藏层；Observation 归一化仅使用训练数据 |

现有观测适配器从数据集中 14 维的物体向量读取 `object[7:14]`。这一处理避免恢复仿真状态时已知的相对传感器缓存不一致问题，保持训练和推理输入一致。

评测同时报告环境自身的成功标记和 **stable released placement（松开夹爪后的稳定放置）**：罐子位于目标区域内并留有半径余量，夹爪已张开且不再接触罐子；继续执行 Policy，在 20 个控制间隔（1 秒）内保持位移 ≤0.01 m、速度 ≤0.05 m/s。具体阈值见 [评测配置](configs/evaluation.yaml)。这是课堂使用的放置判据，不能证明任意朝向下物体网格的每一点都位于料箱内。

**Position Shift Test（初始位置偏移测试）** 在符合条件的测试初始状态上，沿世界 X 轴增加 0.04 m，且偏移后仍位于源料箱内。它**不等同于经过严格验证的 OOD（分布外）测试**：偏移位置可能与训练数据覆盖范围重叠，二维位置图也不能代表完整的输入分布。

### 4. 安装环境

除非另有说明，以下命令均在仓库根目录执行。已测试的平台为 Linux x86-64。Python/CUDA 依赖和实验输出至少需要 15 GB 可用磁盘空间；课堂服务器还需为各组预留额外空间，见 [服务器部署说明](docs/server_setup.md)。

管理员在 Ubuntu 22.04/24.04 上安装系统依赖：

```bash
sudo apt-get update
sudo apt-get install -y git curl build-essential libosmesa6 libgl1 libegl1 libglib2.0-0
```

OSMesa 可在没有显示器或 GPU 的情况下完成渲染。主机安装匹配的图形驱动库后，也可使用 NVIDIA EGL。CUDA 可用并不意味着渲染一定可用，详见 [图形后端配置及无管理员权限的替代方案](docs/server_setup.md#graphics-backends)。

克隆仓库并安装 Python 环境管理工具 `uv`：

```bash
git clone --recurse-submodules https://github.com/tsingqingyun/manipulation_lab.git
cd manipulation_lab
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"
bash scripts/setup_environment.sh
```

安装脚本会在 PATH 和 `uv` 的标准安装目录查找可执行文件，即使 Bash 重置 PATH 也可继续。非标准安装位置可用 `LAB_UV` 指定：

```bash
LAB_UV="$HOME/.local/bin/uv" bash scripts/setup_environment.sh --check-uv
LAB_UV="$HOME/.local/bin/uv" bash scripts/setup_environment.sh
```

安装脚本会创建 `.venv`，获取 Python 3.12.13，按 [完整依赖锁定文件](requirements.lock.txt) 安装并检查依赖，注册 **Manipulation Lab (Python 3.12)** Notebook 内核。两个官方源码子模块均使用固定提交，作业期间请勿自行升级。

| 组件 | 固定版本 |
|---|---|
| Python | 3.12.13 |
| PyTorch / torchvision | 2.8.0 / 0.23.0 |
| MuJoCo | 3.2.7 |
| robosuite | 1.5.1，固定 Git 提交 |
| robomimic | 0.4.0，固定 Git 提交 |
| NumPy | 1.26.4 |
| Numba / llvmlite | 0.61.2 / 0.44.0 |

源码提交和观测定义见 [configs/environment.yaml](configs/environment.yaml)。MuJoCo 通过 pip 安装，无需额外许可密钥或单独下载。

为避免部分服务器的 Numba JIT（即时编译）段错误，命令行入口和 Notebook 导入默认设置 `NUMBA_DISABLE_JIT=1`，执行原有 Python 函数。保留固定依赖版本，不更换训练算法；仿真耗时可能变化。教师需重新测量本机课堂用时。仅在本机验证通过后，才可在启动 Python/Jupyter **之前**显式设置 `NUMBA_DISABLE_JIT=0`；修改后必须重启内核。预检记录版本、实际 JIT 状态和失败阶段，详见 [部署排查](docs/server_setup.md#native-runtime-and-preflight)。

请在**启动 Jupyter 前**选择计算设备。固定版本的 PyTorch 同样支持 CPU 执行，但安装时仍会下载其 CUDA 依赖；CPU 执行不需要 GPU 或 CUDA toolkit。

```bash
# 使用 CPU 计算和软件渲染：
export LAB_DEVICE=cpu
export MUJOCO_GL=osmesa

# 在已配置好的 NVIDIA 服务器上，可改用以下设置训练：
# export LAB_DEVICE=cuda
# export CUDA_VISIBLE_DEVICES=0
# 保留 MUJOCO_GL=osmesa，或在教师验证 NVIDIA EGL 后选择 egl。
```

CPU 任务默认使用两个线程。CPU 模式能够运行，但是否满足 2–3 小时的课堂安排取决于服务器性能和排队时间，教师应提前计时。GPU 训练需要兼容 PyTorch CUDA 12.8 安装包的驱动。评测时的 Policy 推理和 MuJoCo 物理仿真在 CPU 上执行；`MUJOCO_GL` 独立选择渲染后端。

下载并校验公开数据集，然后执行包含真实训练和仿真的 **Smoke Test（最小安装验证）**：

```bash
scripts/lab_python.sh scripts/download_dataset.py
scripts/lab_python.sh scripts/smoke_test.py --output outputs/smoke_v1
```

下载流程会校验固定 SHA256 和包含 200 条轨迹的 HDF5 结构。Smoke Test 检查依赖版本、CUDA 状态、Headless Simulation（无显示器仿真）的重置与渲染、数据解析、两个 Epoch（完整训练轮次）的真实训练、Checkpoint 加载，以及标准和位置偏移条件各一次闭环 Rollout（策略执行轨迹）及视频。预期终端显示 `PASS`，且 `outputs/smoke_v1/smoke.json` 中的 `passed` 为 `true`。即使放置成功率为零，安装验证也可能通过；此处训练量不等于正式作业的训练量。排查问题需要重跑时，请使用**新的输出目录名**，保留失败记录。

服务器无法直连 Hugging Face 时，可以使用管理员提供的镜像或代理，也可以在能联网的电脑下载同一文件并传入服务器。下载脚本支持 `HF_ENDPOINT`、`LAB_DATASET_URL`、`--url` 和 `--from-file`，所有方式都必须通过同一 SHA256 校验。下面的离线导入命令在传入文件后执行：

```bash
# 将原始 low_dim_v15.hdf5 放入项目 incoming/，不要重新打包 HDF5。
scripts/lab_python.sh scripts/download_dataset.py --from-file incoming/low_dim_v15.hdf5
```

镜像、代理和文件传输的完整步骤见 [受限网络下的数据准备](docs/server_setup.md#restricted-network-dataset-transfer)。失败下载的 `.partial` 文件会保留，重试请指定新的 `--output` 路径，并让 `LAB_DATASET` 指向验证完成的文件。

教师 Reference Checkpoint（参考模型检查点）**不随 Git 仓库分发**。教师需使用相同公开数据集和固定参考配置生成：

```bash
scripts/lab_python.sh scripts/prepare_reference.py --train --output checkpoints/reference_v1
export LAB_REFERENCE_ROOT="$PWD/checkpoints/reference_v1"
```

该命令训练现有参考模型、执行评测并检查真实失败视频，应在课前完成。若没有真实失败案例，准备流程会明确报错；不得伪造案例或反复选择随机种子以获取期望结果。参考模型的用途见 [教师指南](docs/instructor_guide.md)。

### 5. 开始实验

如果课程服务器已经准备好，请跳过安装，使用教师分配的账号、小组编号和访问方式。自行部署时执行：

```bash
export LAB_GROUP=group_01
scripts/lab_python.sh scripts/start_lab.py --group "$LAB_GROUP" --port 8892
```

启动器默认将 Jupyter 临时连接文件放在 `/tmp/manipulation-lab-jupyter-<UID>`，目录初始权限为 `0700`（Jupyter 创建内核后可增加 sticky bit 成为 `1700`，仍仅当前用户可访问）、文件权限为 `0600`，避免共享盘不支持安全权限的问题。可用 `JUPYTER_RUNTIME_DIR` 指定满足这些要求的本地目录。以 root 运行时自动添加 `--allow-root`；学生仍应使用独立的普通账号。

Jupyter 监听 **127.0.0.1**，使用正常的 Jupyter token 认证。在个人电脑上建立 SSH 端口转发，并将目标账号和服务器替换为教师分配的信息：

```bash
ssh -N -L 8892:127.0.0.1:8892 user@server
```

在个人电脑打开 `http://127.0.0.1:8892/lab`，输入服务器启动日志中的 token，请勿公开该 token。如果端口 8892 已被占用，两条命令都应改为分配给你的空闲端口；启动脚本不会悄悄切换端口。多用户课堂应使用学校已有认证的 JupyterHub，或独立的 SSH/系统账号。

按顺序打开以下 Notebook，并选择本实验内核：

1. [01_demonstrations.ipynb](notebooks/01_demonstrations.ipynb)：创建实验会话，播放一条示教。
2. [02_train_policy.ipynb](notebooks/02_train_policy.ipynb)：完成两种 Learning Rate（学习率）的训练，保存真实模型与评测结果。
3. [03_policy_evaluation.ipynb](notebooks/03_policy_evaluation.ipynb)：查看上述相同测试案例的对照结果。
4. [04_failure_analysis.ipynb](notebooks/04_failure_analysis.ipynb)：选择时间步、标记错误、回答问题并导出实验材料。

Notebook 01 会创建带时间戳的小组实验会话；Notebook 02–04 自动找到该会话及上一阶段的输出。重新运行训练或分析阶段会创建新版本，保留已有结果。修改文字答案时，只需重跑答案单元格和最后的报告、导出单元格。请勿在作业中途重新启动 Notebook 01。

### 6. 实验内容

| 部分 | 实验要求 | 计划课堂时间 |
|---|---|---:|
| Part 1：理解示教数据 | 检查 Observation/Action，回放记录状态，查看初始位置分布，回答 Q1 | 20 分钟 |
| Part 2：训练 BC Policy | 固定数据、网络、初始化种子 17、50 个 Epoch 和 Batch Size（批大小），比较学习率 0.001 与 0.0003；保存两组曲线和 Checkpoint，回答 Q2–Q3 | 50–60 分钟 |
| Part 3：策略评测与泛化 | 每个模型评测 5 个标准案例和 5 个位置偏移案例；查看逐案例配对结果、位置分布和视频，回答 Q4 | 40–50 分钟 |
| Part 4：失败分析 | 检查一次真实失败，选择至少 3 个控制步，标记第一次可观察错误，回答 Q5 并导出材料 | 20–30 分钟 |

必做对照实验只改变学习率。代码会检查初始权重、数据划分、依赖版本和评测案例清单是否一致。每组 Checkpoint 均按验证损失选择，主要分析对象 `lr_a` 在测试前固定。两组结果都必须保留，包括较低的成功率；相同种子的重复运行不能视为独立样本。

### 7. 可视化

所有图表、日志和视频都会自动保存在小组实验目录中：

| 实验材料 | 查看位置 |
|---|---|
| 人类示教交互视频、Observation/Action 信息、初始位置散点图 | Notebook 01 的 `demonstration_*` 目录 |
| 训练/验证 Loss（损失）曲线、选中的 Epoch、训练配置、两种学习率对照图 | Notebook 02 的 `experiment_*/lr_a` 和 `lr_b`，以及 `learning_rate_curves.png` |
| Rollout 视频、成功率、逐案例及配对结果、实际测试初始位置 | Notebook 03 中各训练配置的 `evaluation` 目录 |
| 失败视频、机械臂/物体轨迹、使用独立坐标轴的夹爪开口与动作命令 | Notebook 04 的 `analysis_*` 目录 |
| 所选关键帧、指定控制步的准确状态、首次错误标注 | `observed_facts.json`、`keyframe_*.png`、`failure_analysis.json` |

视频每执行四次动作后采样一帧，初始状态（第 0 步）没有完全对应的视频帧。选出的关键帧会标明请求步、实际记录步及二者偏差；状态数值则来自指定控制步。位置使用世界坐标系、单位为米，动作命令使用归一化单位，时间使用 20 Hz 控制步编号。首次错误标记是学生的观察，不是自动给出的因果诊断。

### 8. 作业问题

1. **Q1：** 本任务使用哪些 Observation 和 Action？
2. **Q2：** Behavior Cloning 如何从示教数据中学习？
3. **Q3：** 更低的 Training Loss（训练损失）是否总能带来更好的机器人操作表现？
4. **Q4：** 改变物体初始位置，会如何影响学到的 Policy？
5. **Q5：** 找出一次失败，并提出一种可能的改进方法。

请结合自己的实验结果作答，区分证据、假设和限制。详细要求见 [学生作业说明](docs/assignment_student.md)。

### 9. 提交要求

每组提交一份回答 Q1–Q5 的 **1–2 页 PDF 报告**，以及 Notebook 04 生成的实验材料 ZIP。材料应包含两组训练配置和损失曲线、两个 Checkpoint、评测指标/配置/案例清单、代表性 Rollout，以及带标注的失败关键帧。自动生成的 Markdown 报告是实验材料附录，不能替代你自己的分析讨论。

存在空白答案时，生成的报告会保留 **DRAFT（草稿）** 标记。代码运行完成不代表答案完整或正确。可从 Jupyter 文件浏览器下载 ZIP，其中的 `class_results.csv` 使用教师汇总所需的统一格式。评分完成前，请保留原始实验目录。

### 10. 评分标准

| 项目 | 分值 | 评分依据 |
|---|---:|---|
| 示教数据理解 | 20 | 正确解释 Observation/Action、单位、回放和数据划分 |
| Policy 训练与对照实验 | 25 | 两组真实训练、变量控制、曲线/配置/Checkpoint，以及 Q2–Q3 |
| Policy 评测 | 30 | 匹配的标准/偏移案例、完整指标和视频、位置覆盖及合理的结论边界 |
| 失败分析与讨论 | 25 | 真实失败、首次可观察错误、状态/关键帧证据、原因假设和改进建议 |
| **总计** | **100** | 实验完成度、可复现性和分析合理性 |

**不单纯根据成功率评分。** 记录充分、分析合理的失败结果同样可以获得满分。详见 [详细评分标准](docs/assignment_student.md)。

### 11. 常见问题

- **找不到内核或无法导入依赖：** 运行安装脚本并选择本实验内核，不要使用其他项目的 Python 环境。
- **数据集缺失或哈希不匹配：** 运行下载脚本；保留报错涉及的文件并排查原因，不要跳过校验。
- **CUDA 不可用：** 启动前显式设置 `LAB_DEVICE=cpu`，两组对照实验使用相同设备设置。
- **Headless 渲染报错：** 检查 OSMesa 或 NVIDIA EGL 图形库；仅检查 `nvidia-smi` 不够。
- **Reference Checkpoint 缺失：** 教师需要在课前生成；如果学生的主要 Policy 没有失败案例，Notebook 04 需要使用真实的参考失败材料。
- **输出目录已存在：** 使用新的版本化目录。**任务排队：** 保持单元格运行；各组共享一个训练任务槽和一个评测任务槽。

更多说明见 [故障排查](docs/troubleshooting.md) 和 [实际验收记录及限制](docs/course_acceptance.md)。

### 12. 参考资料与致谢

本实验基于 [robomimic](https://robomimic.github.io/)、[robosuite](https://robosuite.ai/) 和 [MuJoCo](https://mujoco.org/)。示教数据下载遵循 [官方 robomimic 数据集文档](https://robomimic.github.io/docs/datasets/robomimic_v0.1.html)，使用其公开的 Hugging Face 分发资源。训练算法采用 [官方 robomimic BC 实现](https://github.com/ARISE-Initiative/robomimic/blob/v0.4.0/robomimic/algo/bc.py)。本实验从数据训练与当前环境兼容的模型，避免混用旧版模型库权重。依赖安装参考：[uv](https://docs.astral.sh/uv/getting-started/installation/)、[PyTorch 2.8 安装包](https://pytorch.org/get-started/previous-versions/)、[MuJoCo Python](https://mujoco.readthedocs.io/en/stable/python.html)。许可证见 [LICENSE](LICENSE)；上游代码和数据保留各自的许可证与署名要求。

### 项目结构与配置

`notebooks/`、`src/`、`scripts/`、`configs/`、`tests/` 和 `docs/` 为维护中的源码与文档；`third_party/` 包含两个固定版本的上游子模块。安装时生成 `.venv/`，下载数据时生成 `data/` 下的数据文件，教师准备阶段生成 `checkpoints/reference_v1/`，实验运行时生成 `outputs/`。大型生成文件不纳入 Git。教师需要在课前准备环境、共享数据集、真实参考案例，以及账号和资源配置。

| 环境变量 | 默认值 / 用途 |
|---|---|
| `LAB_UV` | 可选的 `uv` 可执行文件路径；安装器也会检查 PATH 和标准安装目录 |
| `NUMBA_DISABLE_JIT` | 默认为 `1`；教师验证后才可在启动前显式设为 `0` |
| `JUPYTER_RUNTIME_DIR` | 默认 `/tmp/manipulation-lab-jupyter-<UID>`；须为当前用户拥有的本地 `0700` 目录，支持 `0600` 文件 |
| `HF_ENDPOINT` / `LAB_DATASET_URL` | 可选的镜像端点 / 完整数据 URL；完整 URL 优先，SHA256 校验保持不变 |
| `LAB_VENV` | 项目内的 `.venv`；指定其他环境时使用绝对路径 |
| `LAB_DATASET` | 项目内的 `data/low_dim_v15.hdf5`；可指向共享只读 HDF5 文件 |
| `LAB_DEVICE` | 完整训练的配置默认值为 `cuda`；请显式设置为 `cpu` 或 `cuda` |
| `MUJOCO_GL` | 启动脚本默认使用 `egl`；软件渲染时设置为 `osmesa` |
| `LAB_GROUP` | `group_01`；分配的小组编号范围为 `group_01` 至 `group_06` |
| `LAB_OUTPUT_ROOT` | 项目内的 `outputs`；其下自动创建小组与实验会话目录 |
| `LAB_REFERENCE_ROOT` | 项目内的 `checkpoints`；应指向包含 `reference_evaluation/` 的目录 |
| `LAB_LOCK_DIR` | `/tmp/manipulation-learning-lab-locks`；所有小组必须共享管理员准备好的同一目录 |

[教师指南](docs/instructor_guide.md) 说明如何汇总结果并组织次日讨论；[服务器部署说明](docs/server_setup.md) 涵盖环境部署、账号、并发资源控制和故障恢复。
