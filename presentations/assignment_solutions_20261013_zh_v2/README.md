# 机器人操作学习实验：中文题解修订版

15 页题解沿用上一版的浅色底、蓝灰与暖棕配色、衬线标题。
正文、图表说明和逐页讲稿使用中文；公式、变量名与数学符号保持英文写法。
讲稿共 **880 秒（14 分 40 秒）**。本次只改展示，沿用四份 Notebook 的完整执行结果。

## 打开材料

- [题解 PPT：含两段高清重放视频](Manipulation_Lab_Solutions_ZH.pptx)
- [静态 PDF：字体已嵌入](Manipulation_Lab_Solutions_ZH.pdf)
- [15 页总览](preview/contact_sheet.png)
- [逐页中文讲稿](speaker_notes_zh.txt)
- [四份已执行并填写参考答案的 Notebook](../../notebooks/solutions_20261013/README.md)
- [原始实验与完整证据](../assignment_solutions_20261013/README.md)
- [验证记录](verification.json)

本地 `Chinese_Slides_Package.zip` 包含本目录的 PPT、PDF、讲稿、字体、素材、
构建脚本和证据；不重复打包 Notebook 或模型检查点，也不提交 Git。
请先安装 `fonts/` 内三个 OTF 字体，以保持 PowerPoint 字体与布局。

## 可视化改进

1. 用可编辑图解讲清 16 维观察、7 维动作、两个夹爪关节与一个开合命令。
2. 放大训练与验证曲线、五个配对案例和位置偏移图，明确轴、单位与样本数。
3. 用近景展示第 45、53、57、65 步，对齐开口毫米值与罐子高度。
4. 分开说明真实记录、原因假设和待执行检验。
5. 使用标准英文数学记号表达损失函数，LaTeX 源码保存在 `slides.json`。

## 数据来源与限制

没有重新训练或调用策略进行评测。原实验为两个学习率、一个训练种子、每条件
五个配对案例，共 20 次评测：A 标准/偏移均为 3/5，B 均为 5/5。
原结果和四份已执行 Notebook 均做了文件哈希比对，内容未变。

高清画面从原初态重放已保存动作、只改变相机获得。成功重放 141 步，失败片段
只展示原 500 步中的前 101 步。核对的物体位置、末端位置、夹爪关节与开口最大
绝对差均为 0；接触、进入目标区域与环境成功布尔记录全部一致。
`replay_provenance.json` 保存相机、帧映射和素材哈希。两段视频为半速，编码尺寸
960×544；静帧近景为 960×640。

首次相机重放额外调用 `sim.forward()`，产生约 0.075 mm 的物体位置差异，
已排除并保留在 `outputs/solutions_20261013_v2/chinese_replay_failed_v1`。
修正后只更新相机变换，未放宽比对标准。

验证记录覆盖页数、文字完整性、中文字体、英文公式、素材哈希、视频完整解码
和嵌入文件一致性；另做逐页视觉检查。授课电脑上的原生 PowerPoint 视频播放
尚未实测。原因假设与干预方案仍未验证；有限仿真案例不能证明真实机器人效果
或严格分布外泛化。

## 重建

安装字体及 `authoring-requirements.txt` 中的制稿依赖，在仓库根目录运行：

```bash
python presentations/assignment_solutions_20261013_zh_v2/build_deck.py
python presentations/assignment_solutions_20261013_zh_v2/build_deck.py --static --skip-charts
libreoffice --headless --convert-to pdf --outdir /tmp/manipulation-zh-pdf \
  presentations/assignment_solutions_20261013_zh_v2/Manipulation_Lab_Solutions_ZH_static.pptx
```

将导出的 PDF 复制为本目录 `Manipulation_Lab_Solutions_ZH.pdf`，再执行
`python presentations/assignment_solutions_20261013_zh_v2/verify_deck.py`。
验证需要原版题解目录和已执行 Notebook；只重建页面可直接使用本包保存的数据与素材。
主 PPT 保留视频，静态版本用相同视频的海报帧导出 PDF。
`prepare_assets.py` 仅用于重新渲染相机，依赖原实验轨迹、数据集和实验环境；
普通制稿无需执行。`prepare_fonts.py` 从系统 Noto 集合提取 SC 字体，仅改名称，
并逐字形核对内容未变；已附字体时无需重跑。
