# 将教学实验独立到 manipulation_lab

本计划遵循 [ExecPlan 规范](../PLANS.md)，随迁移进度更新。

## 目标与最终效果

用户从 `https://github.com/tsingqingyun/manipulation_lab` 克隆后，可以在仓库根目录安装、启动和运行原有四步教学实验，不再依赖 ICLR 主仓库。服务器独立目录为 `/home/jingchen/projects/manipulation_lab`。Git 子模块是固定到具体提交的外部源码依赖；本项目只需要 robomimic 和 robosuite 两个子模块。

## 当前进度

- [x]（2026-10-11 15:59Z）核对来源、目标仓库和两边 Git 状态；目标 main 起点为 5338cdd，原仓库为 dcb8e4a。
- [x]（2026-10-11 15:59Z）复制 47 个受版本控制的教学项目文件；本地数据和模型独立复制，原输出另存到 outputs/source_snapshot_20261012。
- [x]（2026-10-11 16:04Z）修正根目录安装路径，独立配置两个源码子模块，补充迁移说明。
- [x]（2026-10-12）建立新虚拟环境，163 包兼容检查通过；5 个测试通过，完成一次仿真/渲染迁移验收。
- [x]（2026-10-11 16:04Z）迁移提交 68226388a04e17186282e2399bafc9610c50a5c0 已推送 origin/main；远端 SHA 与本地一致，原仓库 HEAD、工作区状态和暂存差异均未改变。

## 意外发现

目标仓库已存在，且为公开仓库；初始提交只有 LICENSE，必须保留。原目录存在运行中的 JupyterLab 及内核，并有与教学实验无关的暂存修改，因此不能移动、清空或提交原工作区。

安装脚本以 `../..` 定位 ICLR 主仓库，直接复制无法安装两个外部库。原 Python 虚拟环境包含绝对路径，不能直接搬运。

首次安装在创建环境前停止：当前非交互 Bash 的 PATH 没有包含已安装 uv 的 `~/.local/bin`。保留该次日志，给安装命令显式补入该 PATH 后继续；不修改全局 shell 配置。

## 决策记录

2026-10-12 / Codex：以目标现有 main 和 LICENSE 为基础导入教学项目，不带入原仓库历史、论文附件或其他项目。保留目标当前可见性。

2026-10-12 / Codex：原代码和运行服务保持原状，新目录作为独立工作目录。数据和模型复制但不提交；历史输出以快照保留，不把旧 Notebook 会话指针当作新目录的活动会话。历史指标保留原始来源路径，不伪造重新运行的记录。

2026-10-12 / Codex：从本机已有子模块复制独立 Git 对象，再使用官方远程 URL 和原提交。新建 Python 虚拟环境，利用本机下载缓存，避免旧目录依赖。

## 当前结果与回顾

独立安装及验收完成：5 个测试通过，preflight 11.49 秒，状态恢复与渲染通过，194 个本地文件哈希一致。应用、第三方库和 Jupyter 内核均从新目录加载。迁移提交 6822638 已推送并核对 GitHub main；本次文档更新记录交付证据。未修改核心算法或原仓库暂存内容，未重跑训练挑选成功率。原目录与正在运行的服务保留，切换现有会话不在本次迁移范围内。

## 项目背景

源代码为 `/home/jingchen/projects/ICLR2027_DeformablePhysTwin_private/pipelines/manipulation_learning_lab`，来源提交 `dcb8e4afb4a6cb686d6e2dc143b1a28c3c724ad9`。核心 Python 包在 `src/manipulation_lab`，其 ROOT 根据本文件路径定位实验根目录，已能适配新位置。`scripts/setup_environment.sh` 是已知需要修改的安装入口。

## 实施方案

保留 LICENSE，导入项目文件。将安装脚本的 LAB_REPO 改为 LAB_ROOT，在根目录维护 `.gitmodules` 与 `third_party/robomimic`、`third_party/robosuite`。README 改为独立仓库的克隆与安装命令，补充迁移说明并强化运行产物忽略规则。数据坐标、单位、控制频率、划分、算法和验收阈值不变。

## 具体执行

工作目录 `/home/jingchen/projects/manipulation_lab`：

    bash scripts/setup_environment.sh
    scripts/lab_python.sh -m pytest -q tests
    CUDA_VISIBLE_DEVICES=0 scripts/lab_python.sh scripts/preflight.py --output outputs/migration_20261012_v1/preflight
    git push origin HEAD:refs/heads/main

## 验证与验收

验证两个子模块固定提交与 configs/environment.yaml 一致，依赖检查通过，Python 导入路径和 Jupyter 内核解释器全部属于新目录，已有 5 个测试通过。运行一次 preflight，确认数据读取、相同输入的观测恢复、仿真 reset/step 及 EGL 图像渲染通过。核对源/副本的数据模型哈希、原仓库 HEAD 和暂存差异不变。推送前检查只有本任务新增提交；推送后 GitHub main SHA 与本地 HEAD 相同。

## 可重复执行与恢复

不得覆盖目标已有文件、原数据或历史输出。验收输出路径已存在时使用新版本；失败保留且报告，不连续重跑。提交或推送失败时保留本地状态，报告原因。原目录仍可服务现有会话，无需回滚文件。

## 产物与备注

代码、Notebook、配置及教学文档进入 Git；data、checkpoints、outputs、.venv 和缓存不进入 Git。迁移快照是原始运行的复制，不作为新的训练证据。

## 接口与依赖

robomimic `7c66e7a41b5d9dcc905b1a68346bfee1b49b79c9`；robosuite `51cc01785bab80ffeed20da15e67d7dd4140e76a`；Python 3.12.13。命令入口和 Notebook 行为保留。
