# 独立仓库迁移说明

教学实验已从 ICLR 主仓库的 `pipelines/manipulation_learning_lab` 提取到 `/home/jingchen/projects/manipulation_lab`，远程为 `https://github.com/tsingqingyun/manipulation_lab`。来源提交为 `dcb8e4afb4a6cb686d6e2dc143b1a28c3c724ad9`；保留目标仓库原有 LICENSE 与 main 历史。

迁移代码提交 `68226388a04e17186282e2399bafc9610c50a5c0` 已推送到 `origin/main`，并通过 `git ls-remote` 核对远端提交一致。目标保持原有公开可见性。原仓库 HEAD、工作区状态和暂存差异均与迁移前一致。

## 迁移范围

导入教学代码、四个 Notebook、配置、固定依赖、测试及教学文档。两个第三方源码库位于本仓库 `third_party/`，固定提交与 `configs/environment.yaml` 一致。安装脚本使用当前仓库根目录，不再访问原主仓库。

服务器的数据和参考模型已独立复制到 `data/`、`checkpoints/`；历史输出完整保存在 `outputs/source_snapshot_20261012/`。上述目录以及 `.venv/` 不进入 Git。全新克隆需要按 README 下载官方数据，参考模型需要按教师指南训练。

原目录仍有正在使用的 Jupyter 会话，因此本次保留原目录和服务。旧会话继续访问原目录；后续开发和新会话使用新目录。原有 8892 端口被占用时，可启动新实例：

    cd /home/jingchen/projects/manipulation_lab
    CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/start_lab.py --group group_01 --port 8893

配套 SSH 隧道使用 `ssh -N -L 8893:127.0.0.1:8893 jingchen@<服务器地址>`。按顺序从 Notebook 01 开始，创建新的会话。历史输出中的绝对路径是原始来源记录，不改写为新实验结果，也不直接作为新目录的活动会话指针。

## 验证范围

本次迁移验收于 2026-10-12 完成：

| 项目 | 实测结果 |
|---|---|
| 独立环境 | Python 3.12.13，163 个包兼容检查通过；应用、两个源码库、Jupyter 内核全部指向新目录 |
| 原有测试 | `scripts/lab_python.sh -m pytest -q tests`：5 passed，4.60 秒；14 条第三方弃用警告 |
| 仿真与渲染 | preflight 11.49 秒；reset/step、256×256 EGL 图像检查通过；3 个相同输入案例恢复的所选观测最大误差为 2.22e-16 |
| 数据与模型保留 | 194 个数据、模型与历史输出文件逐一 SHA256 相同；原有 47 个教学文件在源目录保持不变 |
| Git 隔离 | 两个子模块固定提交未变，无依赖原仓库的 Git 对象引用；原仓库 HEAD 和暂存差异不变；目标原有 LICENSE 未修改 |

验收输出保存在本机 `outputs/migration_20261012_v1/preflight/`。这里只证明目录迁移后仍可运行；单步动力学误差继续按原预检逐项记录，不以状态恢复误差代替动力学误差。原库关于可选机器人、全身 IK 和私有宏文件的警告不影响当前 Panda/OSC_POSE 路线，不为消除警告而更改依赖。

首次安装因非交互 Bash 的 PATH 缺少 uv 而在创建环境前停止；显式补入 `~/.local/bin` 后安装成功。README 已说明此前提。未进行重复训练或成功率筛选。

迁移不修改算法、数据划分、观测动作契约、成功判据或物理参数；历史成功率沿用 `validation.md`，不声称此次重新完成了训练或实机验证。
