# Instructor Guide

先以真实训练与连续策略控制证明实验链成立，再让学生解释损失、闭环成功与数据覆盖的关系。无需为了漂亮的成功率隐藏失败，也无需给新生增加模型实现负担。

## 前一天准备

按 README 安装一次独立环境，运行 preflight。预留约 10 GiB 磁盘；本机单次低维训练约 1.6 GiB 进程峰值内存，GPU 张量峰值不足 30 MiB，另有 CUDA 上下文和驱动开销。默认 2 个 CPU 线程、1 个训练任务和1个评测任务；并发队列等待上限 900 秒、学生训练最长 3600 秒、评测最长 2400 秒、单回合最长 180 秒。逐步日志和错误保留。

数据 200 条按 160/20/20 分割。默认学生确定性 MLP 为 256×3 隐藏层、50 轮、学习率 1e-3；教师 512×3、400 轮、3e-4。两者只使用训练集拟合，验证 MSE 选择模型，固定测试集合从未进入训练。教师更多训练不保证更低验证损失；展示过拟合本身有教学价值。

教师参考需要提前运行以下命令，并检查实际结果后发布。请用新目录；不要覆盖已有参考。

```bash
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/train.py \
  --config configs/bc_reference.json --output outputs/reference_new/training
scripts/lab_python.sh scripts/evaluate.py \
  --checkpoint outputs/reference_new/training/student_policy.pth \
  --config configs/evaluation.yaml --output outputs/reference_new/evaluation
```

本机已生成只读 checkpoints/instructor_reference.pth 及明确标记的参考评测。参考不是学生训练的替代品。参考的完整成功判据与学生相同，不调整阈值去追求更高数字。

## 与课程知识的联系

| Task | 已学知识 | 必须讲清 |
|---|---|---|
| 1 | 传感器、执行器、遥操作 | 观测和动作是有单位/坐标约定的数据；专家是一位熟练人类 |
| 2 | 模仿学习、神经网络 | BC 是监督学习，标签是专家动作；训练轮数不是仿真回合 |
| 3 | FK/IK、反馈控制、动作接口 | 高层策略输出增量，OSC 位姿控制器转换为底层控制，仿真产生下一观测 |
| 4 | 分布偏移、接触、环境建模、失败恢复 | 动作误差改变未来输入；定位第一个可见偏差，再提出可验证原因 |

数据流：HDF5 人类记录 → 固定完整轨迹划分 → 选择16维可靠观测 → 仅训练集归一化 → 官方 robomimic BC 与 MSE → 保存模型/环境/观测契约 → 原样加载 → 仿真20Hz逐步反馈 → 独立判据与日志 → 学生分析。训练验证误差与 rollout 任务成功是不同指标。

## 预期现象和诊断

MLP 可能停在抓取前、关闭夹爪但未抓住、成功搬运后靠近边界、释放后仍不稳定。先看物体是否随末端上升、夹爪是否接触、何时开始偏离。自动程序只记录可观测事实，不输出未经验证的“数据不足”“摩擦不对”等原因。判据较严格导致 environment success 高于 stable success 是允许且需讲解的结果。

对象位置分布从训练 episode 的第一帧统计；位移筛选在看任何策略成功率前进行，只保留仍在源容器内的初始化。对照条件使用相同模型与相同测试案例。此实验尚未独立做全范围 IK 可达性证明；标准任务区域是操作范围依据。不把位置外包围盒内/外当作高维分布的证明。

恢复任意中间物理状态不等于恢复控制器缓存和夹爪命令历史，因此原始中段单步比较可能有误差。正式策略评测从完整初态开始连续执行。选用世界位姿避开 v1.5.1 相对传感器缓存，不修改官方库。动作单步复现不宣称逐位一致。

## 45 分钟课堂讲解 + 15 分钟机动

| 分钟 | 内容 | 互动 |
|---|---|---|
| 0–5 | 展示一个完整成功和一个失败 | 先让学生说出成功定义 |
| 5–15 | Demonstrations & Behavior Cloning | 画出一条轨迹的 obs/action；说明完整轨迹划分 |
| 15–25 | Training Loss vs Task Success | 比较不同组曲线与成功率，讨论闭环累积误差 |
| 25–40 | Position Shift & Failure Analysis | 用相同测试集对比；区分事实、假设和受控检验 |
| 40–45 | ACT / Diffusion Policy / VLA 与 BC | 更丰富的动作序列/分布/感知，仍需数据、接口和闭环验收 |

15 分钟机动用于演示重放、解释异常和答疑。不要把进阶方法介绍变成必须实现的新作业。

## 班级汇总

docs/class_results.csv 可用 Excel/LibreOffice 编辑。记录每组明确选择的 run，而不是事后只保留最高成功率。脚本可合并指定的真实 summary：

```bash
scripts/lab_python.sh scripts/aggregate_results.py \
  --summaries outputs/group_01/<run>/<evaluation>/summary.json \
              outputs/group_02/<run>/<evaluation>/summary.json \
  --output outputs/class_summary_v1.csv
```

讨论样本量：5 回合成功率的粒度就是20个百分点，不能推断细微优劣。更多回合可用 --episodes 和 --seeds，最大数量受满足固定位移范围的20条保留初态限制。不要重复完全相同初态并当作更多独立样本。

## 多组部署

优先使用现有 JupyterHub，为 group_01…group_06 分配独立系统用户。共享代码/环境、data/ 和 checkpoints/ 由教师持有，仅允许学生读取；各组输出目录归该组所有，权限 0700。管理员配置每组 LAB_GROUP 和 LAB_OUTPUT_ROOT，使根目录仅该组可写。独立系统权限才提供隔离；Notebook 的组名不是访问控制。

为所有进程配置同一个 LAB_LOCK_DIR。管理员预建目录和 training.lock、evaluation.lock，允许课堂用户打开锁文件（共享用户组权限0660），不允许学生替换/删除锁文件。通过系统服务/cgroups 给每组内核与脚本限制 CPU/RAM；脚本的线程数、超时和锁只是作业级约束。不要开放匿名 JupyterLab 到公网。当前交付实测了单用户 SSH 隧道服务，未用6个真实账号做并发验收。

## 备用流程

学生模型失败：保留其10次结果，另用教师参考探索推理。GPU不可用：明确设置CPU后仍需真实训练。网络失败：使用已核验哈希的共享数据。仿真不可用：检查EGL和固定版本，先修复；教师可展示标注来源的参考视频并讨论，但 Task 3 未执行必须记为未完成，不能算通过。空答案报告仍是草稿。

可选进阶：在基础交付后比较各50条、位置集中的示教与位置分散的示教；保持架构、预算和测试集一致。当前版本未实现自动覆盖实验，避免影响基础作业。
