# score_workflow

基于多源品牌数据的多维度评分 Workflow 项目。项目围绕 `OLIPOP` 样本数据实现完整链路：

`数据加载 -> 指标提取 -> 评分计算 -> LLM 综合诊断 -> 报告输出`

## 项目目标

- 对目标品牌进行多维度健康度评分
- 输出结构化评分结果和中文分析报告
- 完整记录数据探索、指标设计、实现过程和任务管理
- 以规范 Git 提交流程体现阶段性开发节奏

## 目录结构

```text
score_workflow/
├─ data/
│  └─ raw/                  # 原始样本数据
├─ docs/
│  ├─ architecture.md       # 架构设计
│  ├─ data-exploration.md   # 数据探索与质量评估
│  ├─ metric-design.md      # 指标设计说明
│  └─ task-list.md          # 阶段任务清单
├─ outputs/                 # 运行产出目录
├─ src/
│  └─ score_workflow/       # 核心源码
└─ tests/                   # 单元测试
```

## 环境依赖

- Python `3.11+`
- 无强制第三方依赖，默认使用 Python 标准库即可运行
- 可选环境变量，用于启用真实 LLM 总结节点：
  - `OPENAI_API_KEY`
  - `OPENAI_BASE_URL`
  - `OPENAI_MODEL`

未配置上述变量时，Workflow 会自动退化为本地模板式中文诊断，保证流程可运行。

## 快速开始

在项目根目录执行：

```bash
python -m src.score_workflow.cli --data-dir data/raw --output-dir outputs/manual_run
```

运行完成后将生成：

- `outputs/manual_run/score_summary.json`
- `outputs/manual_run/report.md`
- `outputs/manual_run/score_chart.svg`

## Workflow 说明

核心流程如下：

1. 加载 `brand/company/products/traffic/review` 五类 JSON 数据
2. 对评论、商品、流量、品牌信息进行结构化特征提取
3. 基于有数据支撑的维度计算分数和置信度
4. 调用 LLM 节点生成中文综合总结
5. 输出 Markdown 报告、JSON 结果和 SVG 图表

## 评分维度

本项目优先实现数据直接支撑的维度：

- 品牌成熟度
- 产品质量
- 市场需求匹配度
- 创新力
- 运营韧性
- 性价比

对数据支撑不足的维度会显式标注 `skipped` 和 `low confidence`，避免伪精确。

## Git 管理策略

- 主分支：`main`
- 集成分支：`develop`
- 功能分支：`feature/brand-score-workflow`

建议提交流程：

1. 在 `feature/*` 分支开发
2. 阶段完成后合并到 `develop`
3. 验证通过后合并到 `main`
4. 为重要里程碑打标签

本次实现对应的阶段性提交会覆盖：

- 数据探索
- 指标设计
- Workflow 实现
- 报告生成

## 测试

运行单元测试：

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## 远程仓库

目标远程仓库：

`https://github.com/zfff-labb/score_workflow`

如本地已具备 GitHub 认证，可执行：

```bash
git remote add origin https://github.com/zfff-labb/score_workflow
git push -u origin feature/brand-score-workflow
git push -u origin develop
git push -u origin main
git push --tags
```
