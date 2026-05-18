# AI Agent 补贴策略仿真与优化系统

> 美团实习项目 · 2026.03 - 2026.04
>
> 在线 Demo: [Streamlit Dashboard](https://meituan-subsidy-dashboard-bupmdbzvhxdmtgfut4czq3.streamlit.app/)

## 背景

美团的补贴策略优化长期依赖线上 A/B 测试，存在三个核心痛点：

- **周期长**：每次测试至少 2 周，策略迭代慢
- **覆盖窄**：暴雨、节假日等长尾场景无法实时验证
- **成本高**：真实流量做实验意味着真金白银的补贴支出

本项目提出用 **LLM Agent 替代线上 A/B 测试**——构建 200 个基于真实数据的虚拟用户，在 8 个典型场景下模拟"发券 vs 不发券"的反事实决策，实现补贴策略的**离线评估与优化**。

## 核心成果

| 指标 | 数值 |
|------|------|
| SiFi 保真度评分 | 0.340 → **0.950**（D级 → A级） |
| 下单率偏差 | 36.9pp → **3.6pp** |
| 最优策略 ROI | **14.0x**（300元预算撬动 4,197 元增量 GMV） |
| 正向策略占比 | **69.1%**（1,400 个候选动作） |
| 测试周期 | 2 周 → **1 天** |

## 技术架构

```
特征工程 → Persona注入 → Agent仿真 → Prompt校准 → SiFi评估 → 策略优化
36维画像   三模块Prompt   200人×8场景  7条约束规则   四维保真度   ECUP+拉格朗日
```

### Step 1 — 特征工程
- 解决 200 用户仅 8 条行为轨迹的极度稀疏冷启动问题
- 三级画像感知合成引擎（订单反推 → 高斯采样 → 中位数兜底）
- 马尔可夫链扩充 + KL 散度校验（阈值 < 0.5）
- 5 个并行模块提取 36 维用户特征矩阵

### Step 2 — Persona 注入
- 设计 Identity Core + Decision Rules + Persona-conditional CoT 三层 Agent Prompt 架构
- 将数值特征无损翻译为 LLM 可执行的行为规则（如 `avg_basket_size=35` → "低于 25 元划算，超过 52 元犹豫"）
- 按弹性类型生成三条异质性推理路径

### Step 3-4 — Agent 仿真与校准
- 200 用户 × 8 场景全量 LLM 仿真（豆包/智谱/ModelScope）
- 识别并修正 LLM 固有"顺从偏差"（下单率从 84.7% 校准至 51.4%）
- 7 条数据驱动的 Prompt 约束规则
- RFT 打分规则 + LoRA 微调方案（已设计，作为精调路径）

### Step 5 — SiFi 四维保真度评估
- **行为分布对齐**（权重 0.30）：卡方检验，偏差 3.6pp
- **弹性类型差异度**（权重 0.25）：排序正确，差异幅度 27.1pp
- **场景响应合理性**（权重 0.25）：5 项因果方向检验通过 4/5
- **置信度校准质量**（权重 0.20）：均值 0.664，标准差 0.159

### Step 6 — 策略优化
- Agent 反事实仿真 + ECUP 个体因果增益估计
- 拉格朗日对偶搜索实现预算约束下多目标寻优
- 识别品质导向用户的极端分化特征（47% 场景亏损 vs 53% 场景爆赚）
- 预算敏感性分析验证边际效益递减（ROI 29.2x → 7.3x）

## 关键发现

### 场景 × 弹性类型净值矩阵

| 场景 | 刚需 (n=164) | 品质导向 (n=26) | 薅羊毛党 (n=10) |
|------|-------------|----------------|----------------|
| 工作日午餐 | +18.20 | **+40.33** 🏆 | +3.03 |
| 节假日聚餐 | +21.59 | +35.58 | +13.63 |
| 下午茶 | +14.83 | +33.50 | +7.22 |
| 暴雨困办公室 | +12.57 | +29.92 | +3.15 |
| 周末暴雨晚餐 | +11.97 | +38.39 | +2.57 |

### 核心洞察

1. **品质导向用户极端分化**：全量均值 +28.81 元，但 47.3% 场景亏损（平均 -17.6 元），52.7% 场景爆赚（平均 +70.4 元）—— 必须做场景精细匹配
2. **工作日午餐最安全**：正向占比 81.5%，是发券确定性最高的场景
3. **预算边际递减**：ROI 从 29.2x（¥50 预算）递减至 7.3x（¥1,200 预算），最优性价比在 ¥50-100 区间

## 快速开始

### 方式一：在线 Demo（无需安装）

直接访问 [Streamlit Dashboard](https://meituan-subsidy-dashboard-bupmdbzvhxdmtgfut4czq3.streamlit.app/)

### 方式二：本地运行
```bash
pip install streamlit openpyxl
streamlit run dashboard_app.py
```

### 方式三：纯 HTML 看板（无需 Python）
```bash
open dashboard.html
```

## 项目结构

```
├── dashboard_app.py              # Streamlit 交互看板（主入口）
├── dashboard.html                # 纯 HTML 静态看板（无需 Python）
├── persona_injector.py           # Persona 注入（三模块 Prompt 生成）
├── run_batch.py                  # LLM 仿真批量调用
├── sifi_evaluation.py            # SiFi 四维保真度评估
├── step3_run.py                  # 策略优化主入口（v5 Agent 反事实）
├── step3_coupon_optimizer_v5.py  # 策略优化核心逻辑
├── rft_scoring.py                # RFT 10 条打分规则
├── lora_finetune.py              # LoRA 微调脚本（需 GPU）
├── step1_feature_engineering.py  # Step 1 特征工程
│
├── user_simulation_features.xlsx # 200 用户 × 36 维特征
├── agent_prompts_v2.xlsx         # 200 个 Agent Prompt
├── phase2_calibrated_final.json  # ★ 最终仿真数据（1,600 条）
├── sifi_report.json              # ★ SiFi 评估报告
├── step3_policy_output_v5.xlsx   # ★ 最终策略输出
├── step3_v5_结果速查.md           # 结果速查表
│
├── 神券订单数据样例.xlsx           # 原始数据：1,265 条真实订单
├── 用户行为序列.xlsx               # 原始数据：8 用户行为序列
├── 项目全流程说明.md               # 完整技术文档
└── sifi_evaluation_report.md     # SiFi 评估详细报告
```

## 技术栈

- **LLM API**：豆包 doubao-seed-2-0-pro、智谱 glm-4-plus、ModelScope Mistral-Small
- **评估方法**：Pearson 卡方检验、KS 检验、KL 散度
- **优化算法**：拉格朗日对偶搜索、ECUP 因果增益估计
- **可视化**：Streamlit、HTML/CSS/JS
- **数据处理**：Python、openpyxl、pandas

## 收获与反思

1. **LLM 不是直接可用的**：初始仿真下单率 84.7%，远高于真实值 51.4%。LLM 天然倾向"配合"用户需求，必须用数据驱动的校准手段修正
2. **仿真可信度需要量化**：SiFi 四维评估框架证明了"校准后的仿真可以用"，这比单纯看准确率更有说服力
3. **品质用户的极端分化**是一个关键发现：不看场景就发券，一半赚钱一半亏钱。这个洞察直接影响了策略优化的粒度设计

## License

MIT
