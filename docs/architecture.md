# Workflow 架构设计

## 目标

构建一个可运行、可解释、可扩展的品牌多维度评分 Workflow，覆盖以下最小流程：

`数据加载 -> 多维度指标提取 -> 评分计算 -> LLM 综合诊断 -> 报告输出`

## 模块划分

### 1. Data Loader

负责读取 `data/raw` 中的 JSON 文件，并进行基础结构校验。

输入：

- `brand-info.json`
- `company-info.json`
- `products-info.json`
- `review-info.json`
- `traffic-info.json`

输出：

- 统一的 `DatasetBundle`

### 2. Feature Extractor

负责将原始 JSON 转换为稳定、可评分的特征，包括：

- 评论均分与星级分布
- 评论关键词与投诉主题
- 商品数量、变体数量、价格统计
- 饮料商品和周边商品粗分类
- 网站流量与来源结构
- 国家覆盖、渠道覆盖和联系方式规模

输出：

- `FeatureBundle`

### 3. Score Engine

对有数据支撑的维度进行评分，并输出：

- 维度得分
- 维度置信度
- 评分理由
- 跳过原因

总分采用“已启用维度权重归一化”计算，避免因缺失维度拉低结果。

### 4. LLM Summary Node

优先使用环境变量配置的 OpenAI 兼容接口生成中文综合诊断。

若未配置接口，则启用本地模板总结，保证 Workflow 在离线场景仍可运行。

### 5. Report Generator

输出三类交付物：

- `score_summary.json`
- `report.md`
- `score_chart.svg`

## 设计原则

- 可解释：所有分数均有公式、输入特征和原因说明
- 低伪精确：对数据不足维度显式跳过，不硬算
- 可扩展：新增品牌时只需替换数据目录
- 可运行：默认仅依赖标准库，不绑定外部服务
- 可验证：评分函数可被单元测试覆盖
