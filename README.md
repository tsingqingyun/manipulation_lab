# Manipulation Learning Lab: From Demonstrations to Robot Policies

真实 Can 人类示教 → 确定性 Behavior Cloning（模仿专家动作）→ 学生自己的模型 → PickPlaceCan 闭环仿真 → 标准/位置位移评测 → 失败报告。适合 5–6 组跨学科学生，2–3 小时；训练和评测必须亲自执行。

| Task | 学生操作 | 提交 |
|---|---|---|
| 1 | 查看机器人观测、动作和完整示教 | 示教分析 |
| 2 | 实际训练 BC 网络 | 训练曲线与 checkpoint |
| 3 | 自己的模型运行标准 5 次、位移 5 次 | 成功率与 rollout |
| 4 | 分析一次真实失败并提出改进 | 1–2 页报告与关键帧 |

学生先读 [作业说明](docs/assignment_student.md)，教师读 [教师指南](docs/instructor_guide.md)。[实测验收](docs/validation.md) 区分运行通过、成功率和仍未验证的限制；[常见问题](docs/troubleshooting.md) 包含本机 EGL 修复。

## 安装与浏览器入口

本项目已独立为 `manipulation_lab`，从仓库根目录运行所有命令。首次安装会下载约数 GB 的 PyTorch/CUDA 依赖；无需每个学生安装。Python、两项源码子模块、全部 Python 依赖及数据 SHA256 均已固定。

先安装 [uv](https://docs.astral.sh/uv/getting-started/installation/) 并确保它在 PATH 中；使用默认安装位置时可运行 `export PATH="$HOME/.local/bin:$PATH"`。

```bash
git clone --recurse-submodules https://github.com/tsingqingyun/manipulation_lab.git
cd manipulation_lab
bash scripts/setup_environment.sh
scripts/lab_python.sh scripts/download_dataset.py
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/preflight.py --output outputs/setup_v1/preflight
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/start_lab.py --group group_01 --port 8892
```

在自己电脑建立 SSH 隧道，然后用启动日志中的 token 登录 `http://127.0.0.1:8892/lab`，依次打开 notebooks/01–04。token 是 Jupyter 自动生成的登录凭据，不提交到 Git。实验启动器默认只监听服务器本机。

服务器上的独立工作目录为 `/home/jingchen/projects/manipulation_lab`。已有运行的保留方式与迁移验证范围见 [迁移说明](docs/migration.md)。`docs/validation.md` 与 `docs/validation_metrics.json` 保留迁移前的历史实测记录。

```bash
ssh -N -L 8892:127.0.0.1:8892 jingchen@<服务器地址>
```

本机若已启动，可在服务器运行 `scripts/lab_python.sh -m jupyter server list` 获取自己的登录 URL。课堂多人使用已有 JupyterHub 的独立系统用户；本仓库没有自行实现账号系统。单用户演示服务的组名隔离防止误覆盖，不是安全权限隔离。

## 独立脚本复现

以下目录必须不存在；重跑换新的版本目录，已有失败保留。

```bash
scripts/lab_python.sh scripts/inspect_dataset.py --output outputs/my_run_v1/inspection
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/train.py \
  --config configs/bc_student.json --output outputs/my_run_v1/training
scripts/lab_python.sh scripts/evaluate.py \
  --checkpoint outputs/my_run_v1/training/student_policy.pth \
  --config configs/evaluation.yaml --output outputs/my_run_v1/evaluation
scripts/lab_python.sh -m pytest -q tests
```

`evaluate.py` 可接收 `--episodes N --seeds ...`，但不得超过符合源容器安全范围的保留初态数量。每个条件使用相同案例顺序。输出 results.csv、summary.json、逐步 NPZ、真实 MP4 和成功率图；没有成功回合时不生成虚假的 successful_rollout.mp4。Notebook 报告调用独立 generate_report.py。

## 兼容性与数据约定

使用 robomimic 0.4.0、robosuite 1.5.1、MuJoCo 3.2.7、PyTorch 2.8.0/CUDA 12.8、Python 3.12.13。源码提交见 configs/environment.yaml，完整依赖见 requirements.lock.txt。

数据是官方 v1.5 Can PH low_dim_v15，200 条人类轨迹，23207 个控制步，20 Hz。按完整 episode（一次示教）固定分为 160/20/20；只用训练集计算归一化均值和标准差。测试 rollout 永不回灌到人类数据。时间使用步数和控制间隔，没有伪造采集时间戳。

输入 16 维：末端世界位置、xyzw 四元数、夹爪关节、物体世界位置和 xyzw 四元数。object[0:7] 的官方相对传感器在恢复状态时存在缓存顺序差异，因此训练/推理一致使用 object[7:14]；原数据不改。位置单位米，世界 Z 向上。动作是世界系 OSC_POSE（操作空间位姿控制器）增量：3 位移、3 轴角、1 夹爪，范围 [-1,1]；映射到 ±0.05m/±0.5rad，夹爪正闭负开。

稳定成功要求环境成功、物体中心处于目标格且留物体水平半径余量、夹爪张开且无接触，并在策略继续执行的 20 个控制间隔中保持位移≤1cm、速度≤5cm/s。这个额外判据比环境标志严格，但不是任意姿态物体网格完整包含的几何证明。阈值公开于 configs/evaluation.yaml。

固定 +4cm 世界 X 位移称 **Position Shift Test**。仅挑选位移后仍位于源容器内部的测试初态，该筛选在看策略结果前完成；不宣称分布外基准。视频区分人类状态回放和真实学习策略运行。

官方资料：[数据与版本说明](https://robomimic.github.io/docs/datasets/robomimic_v0.1.html)、[旧权重限制](https://robomimic.github.io/docs/model_zoo/robomimic_v0.1.html)、[官方 BC 实现](https://github.com/ARISE-Initiative/robomimic/blob/v0.4.0/robomimic/algo/bc.py)。本实验重新训练，不下载混用旧模型库权重。
