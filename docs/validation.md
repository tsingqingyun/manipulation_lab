# 实测验收 — 2026-10-11

基础闭环和四个 Notebook 已实际执行通过。学生模型真实完成训练与10次策略评测；教师参考另行训练、另行标记。以下是开发验收样本，不是学生课堂最终成绩，也不是论文基准结果。

## 固定环境与来源

Linux x86_64，Python 3.12.13，robomimic 0.4.0（7c66e7a），robosuite 1.5.1（51cc0178），MuJoCo 3.2.7，PyTorch 2.8.0、torchvision 0.23.0、CUDA wheel 12.8，NumPy 1.26.4，h5py 3.14.0，JupyterLab 4.4.9。全部163项包兼容检查通过；requirements.lock.txt 固定依赖，两个源码子模块固定提交。

官方 Can PH v1.5 数据实测200条、23207步，单轨迹82–151步，无采集时间戳，20Hz控制步。下载约44.7 MiB，约9秒；SHA256 `3f2eb92e0a5025d0095e866ac16cc8092d6a762abe27dec90dbaff9027282962`。160/20/20完整轨迹划分，种子20261011。训练初始Can世界位置范围 x=[-0.01972,0.21884] m、y=[-0.41857,-0.08220] m、z=0.86 m。

可审查指标和每个回合记录见 [validation_metrics.json](validation_metrics.json)。原始不可覆盖运行在本机 outputs/，大型权重/视频不入Git。

## 通过的行为

| 验收项 | 实际证据 |
|---|---|
| 1 Environment | PickPlaceCan创建、reset/step、EGL真实256×256图像；preflight 10.37秒 |
| 2 Dataset | 官方HDF5读取、全部200条动作与观测有限值检查、轨迹划分无重叠 |
| 3 Training | 官方确定性BC，50完整训练轮，真实CSV损失曲线和可重载checkpoint |
| 4 Inference | 相同学生checkpoint连续执行动作；没有切换教师权重 |
| 5 Evaluation | 种子101–105，标准5次、位移5次，全部逐条记录，零执行错误 |
| 6 Visualization | 真实训练PNG、真实H.264 MP4；成功/失败视频均存在 |
| 7 Teaching workflow | 四Notebook从头按序运行，含人类回放、真实训练、10次评测、失败信号/关键帧/草稿报告 |

5个针对性测试通过：完整轨迹拆分无泄漏、序列不跨episode、未释放/接触/未在容器内/持续时间不足不能算成功、速度超限不能算成功、旧模型契约拒绝。一次完整Notebook验收之后，只对发现的报告相对图片链接进行修复并单独复测；保留原验收输出。

浏览器验收：Google Chrome 155 打开本机JupyterLab（HTTP200）和Notebook 01；实际生成的成功视频可解码和播放，256×256、7.6秒，播放进度实测前进到0.800秒，readyState=4。记录在 outputs/notebook_acceptance_v1/browser_acceptance.json。早先自动化Chromium不支持H.264（canPlayType为空），不能作为视频损坏证据；Google Chrome核验通过。该浏览器仅用于开发验证，不是学生Python依赖。学生浏览器需支持H.264。

## 结果与耗时

| 模型 | 训练 | 验证MSE选中轮 | 标准环境/稳定 | 位移环境/稳定 |
|---|---|---:|---:|---:|
| Student 256×3 MLP | 50轮，8.04秒 | 第7轮，0.0347311 | 2/5，2/5 | 3/5，3/5 |
| Instructor 512×3 MLP | 400轮，52.08秒 | 第15轮，0.0345757 | 4/5，4/5 | 3/5，2/5 |

学生最后训练MSE为0.0177401；教师为0.0079668。两者按验证误差选中checkpoint，不按测试成功率挑选。位移结果不一定更差，5回合的小样本不能支持总体优劣判断。

学生10回合仿真49.05秒，教师46.22秒。四Notebook总运行约77.3秒，各为9.18、13.41、53.01、1.66秒；01中的人类状态回放6.13秒。课程2–3小时包含阅读、调参、讨论、人工回答和失败分析，计算快速不代表作业无需这些工作。

P0首个可用闭环 outputs/p0_v3：训练7.74秒，标准/位移各2回合共30.89秒，稳定成功各1/2。之后Notebook验收得到相同学生权重SHA256 `59de6f66056b9de6d8288fe3ba77afd0e9ce1bea827378c1e4ae3ef7192dd72d`。参考权重SHA256 `dd66603600e5df85567aed6d92c83601c488e135b6dcbfad0840e929554958a7`。

标准测试来源按固定顺序为 demo_39、demo_185、demo_29、demo_48、demo_157；位移条件从同状态给Can世界X加0.04m。初态筛选只检查源容器范围，在策略执行之前完成。所有逐步状态和动作保存在NPZ，失败没有删除。

## 资源

本机8张RTX PRO 5000 Blackwell，每张约48GiB；本任务训练使用空闲GPU0，未占用原本繁忙的GPU2/3。预检可用RAM约326GiB、磁盘147GiB。环境占7.4GiB，数据45MiB，验收输出约10MiB（之后浏览器截图略有增加）。

学生训练进程峰值RSS 1608MiB，PyTorch峰值GPU张量分配22.31MiB；教师分别1580MiB、29.16MiB。这些GPU数字**不包括**驱动/上下文/其他进程，也不是整张卡峰值占用。训练和推理设置2个CPU线程；评测物理仿真与策略在CPU，EGL渲染用GPU，学生评测进程峰值RSS约1608.53MiB。未采样整机CPU/GPU利用率时间序列，不把线程上限当作占用率。

## 成功运行的命令

以下为迁移前记录的命令；在独立仓库中，工作目录为 manipulation_lab 根目录：

```bash
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/train.py \
  --config configs/bc_student.json --output outputs/p0_v3/training
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/evaluate.py \
  --checkpoint outputs/p0_v3/training/student_policy.pth \
  --config configs/evaluation.yaml --episodes 2 --output outputs/p0_v3/evaluation
CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/train.py \
  --config configs/bc_reference.json --output outputs/reference_v1/training
scripts/lab_python.sh scripts/evaluate.py \
  --checkpoint outputs/reference_v1/training/student_policy.pth \
  --config configs/evaluation.yaml --output outputs/reference_v1/evaluation
```

这些路径现已存在，复现请换新目录。实际四Notebook验收产物：outputs/notebook_acceptance_v1/；学生会话：outputs/group_06/20261011T153726Z_a6beed5e/。思考题仍为空，报告明确标记DRAFT，未伪造学生分析答案。

## 已发现并保留的问题

首次环境安装缺CMake导致egl-probe构建失败，补固定CMake后通过。系统默认EGL未发现NVIDIA vendor，包装器使用本机已有的匹配用户级驱动；没有更换系统驱动或改第三方库。

最早的数据接口差异在 object 前7个相对状态：恢复同一状态时缓存依赖导致最大差1.972；选择后的16维观测与HDF5相同状态最大差2.22e-16。原始v1训练结果和v1/v2失败日志保留。最终训练和推理统一采用世界位姿适配器。

直接恢复中段物理状态再执行专家动作，没有完整控制器缓存/夹爪命令历史，单步位置差可达约2.45cm；强制刷新控制器并恢复专家历史夹爪累积量的专项诊断中，末端最大差3.84mm、物体1.53mm。该诊断不是完整动作回放逐位重现证明。正式评测始终从完整初态连续运行；人类示教视频明确是记录状态回放。

## 真实限制

单用户JupyterLab已启动，教学Notebook执行通过；6个真实独立账号并发、跨机器重装和课堂网络未实测。正式课堂仍需管理员在已有JupyterHub中配置账号、只读共享目录、每组独立输出权限及服务资源上限。

只使用20条保留示教初态中的安全位移子集，未扩展任意随机可达位置；没有独立全空间IK可达性证明，不称为OOD。稳定放置额外判据使用物体中心、水平半径余量和短窗口运动，不是全网格包含或真实世界可靠性证明。

未实现可选的50条集中/分散覆盖实验，也没有ACT、Diffusion或VLA训练。教师参考有效但并非所有回合成功。原始数据、物理引擎、机器人资产、第三方库源码及仓库原有研究/演示文件均未修改。
