# Troubleshooting

| 症状 | 定位与解决 |
|---|---|
| EGL device display 初始化失败 | 使用 scripts/lab_python.sh 启动。检查系统 NVIDIA EGL vendor JSON、驱动匹配和渲染设备；CUDA能用不代表EGL能用。本机已有用户级驱动580.76.05，包装器按系统驱动版本匹配启用，无需改第三方源码 |
| egl-probe 构建说 CMake 未安装 | 先装 cmake==3.31.6，并将 .venv/bin 加入 PATH；setup_environment.sh 已处理 |
| 缺少 kernel | 运行 setup_environment.sh 注册 manipulation-lab，浏览器选择该内核 |
| CUDA unavailable | 教师分配空闲GPU；或明确设置 device=cpu，并记录耗时。不要占用已有繁忙任务的GPU |
| Version / observation adapter mismatch | 只用本实验训练出的权重和固定依赖。旧官方模型库不能直接用于本环境 |
| 输出目录已存在 | 改新版本路径。Notebook 的重复阶段会分配新目录，旧失败保留 |
| 同状态 object 向量前7维不一致 | 已确认是相对传感器缓存顺序；输入适配只用物体世界位姿 object[7:14]。不要调整阈值掩盖差异 |
| 从轨迹中间恢复后专家动作不同 | HDF5物理状态没有完整控制器缓存/夹爪历史；正式评测从完整初态开始，动作连续执行 |
| 没有 successful_rollout.mp4 | 本次确实没有严格成功；看 failed_rollout.mp4，提交实际结果 |
| environment success 高于 stable success | 额外检查可能发现未释放、接触、漂移或边界余量不足；查看状态日志，保留两项指标 |
| 评测暂时没有输出 | 共享锁排队，或正在构建环境/检查固定案例。等待上限900秒；错误写入对应目录 |
| 所有回合都成功 | 用同组此前真实失败或带标签的教师失败作分析，不修改学生统计 |
| MP4不能播放 | 产物是H.264/yuv420p；Notebook用嵌入视频。确认文件完整、浏览器支持H.264，不把示教回放当策略视频 |
| report.md 有DRAFT | 四题、示教答案或 FIRST_ERROR_STEP 未填；观察后填写并重新生成分析/报告，不编造答案 |
| Controlled Experiment 拒绝通过 | 检查两组是否除 learning_rate 外还有配置、初始化、划分或评测清单差异；不能跳过检查 |
| 选关键帧显示步数差值 | 视频每4个控制步采样且在动作后记录；显示最近真实帧及其步数，不代表画面恰好来自请求步 |
| 班级CSV有 incomplete_or_invalid | 清单选中了未完成实验或模型/配置不匹配；保留该行与失败目录，不能填零分掩盖缺失 |

单次故障修复后只重跑受影响部分并换输出目录。不要反复抽种子挑选成功，也不要把失败动作加入专家训练数据。
