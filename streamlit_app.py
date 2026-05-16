#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 单用户仿真能力建设及在补贴策略中的应用 — 全流程可视化 Dashboard
"""

import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import openpyxl
from collections import Counter
import os

st.set_page_config(
    page_title="AI 用户仿真 × 补贴策略平台",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══ 全局样式 ═══
st.markdown("""
<style>
    .main > div { padding-top: 0.5rem; }
    [data-testid="stSidebar"] { display: none; }
    .block-container { padding-top: 0 !important; }
    .pipeline-step {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white; padding: 12px 18px; border-radius: 10px;
        text-align: center; font-weight: 600; font-size: 14px;
        margin: 4px; display: inline-block; min-width: 120px;
    }
    .pipeline-arrow { font-size: 24px; display: inline-block; vertical-align: middle; margin: 0 4px; color: #999; }
    .metric-card {
        background: white; border-radius: 12px; padding: 20px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08); text-align: center;
    }
    .metric-card .label { font-size: 13px; color: #888; }
    .metric-card .value { font-size: 32px; font-weight: 700; color: #1a1a2e; }
    .metric-card .delta { font-size: 13px; margin-top: 4px; }
</style>
""", unsafe_allow_html=True)

# ═══ 数据目录 ═══
DATA_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══ 数据加载 ═══
@st.cache_data
def load_phase1():
    with open(os.path.join(DATA_DIR, "phase1_llm_final.json"), "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

@st.cache_data
def load_phase2():
    with open(os.path.join(DATA_DIR, "phase2_calibrated_final.json"), "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

@st.cache_data
def load_user_features():
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "user_simulation_features.xlsx"), read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    return pd.DataFrame(rows[1:], columns=rows[0])

@st.cache_data
def load_sifi():
    with open(os.path.join(DATA_DIR, "sifi_report.json"), "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_policy():
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "step3_policy_output_v5.xlsx"), read_only=True)
    all_uplift = pd.read_excel(os.path.join(DATA_DIR, "step3_policy_output_v5.xlsx"), sheet_name="all_uplift")
    selected = pd.read_excel(os.path.join(DATA_DIR, "step3_policy_output_v5.xlsx"), sheet_name="selected_policy")
    segments = pd.read_excel(os.path.join(DATA_DIR, "step3_policy_output_v5.xlsx"), sheet_name="user_segments")
    return all_uplift, selected, segments

# 加载数据
try:
    df_p1 = load_phase1()
    df_p2 = load_phase2()
    df_features = load_user_features()
    sifi = load_sifi()
    df_all_uplift, df_selected, df_segments = load_policy()
    data_loaded = True
except Exception as e:
    st.error(f"数据加载失败: {e}")
    data_loaded = False

if not data_loaded:
    st.stop()

# ═══ 颜色方案 ═══
COLORS = {
    "primary": "#667eea",
    "success": "#2e7d32",
    "warning": "#f57c00",
    "danger": "#e53935",
    "info": "#0288d1",
    "purple": "#764ba2",
}
PHASE_COLORS = {"Phase 1": "#e53935", "Phase 2": "#2e7d32", "真实": "#1565c0"}
ELASTICITY_COLORS = {"缺乏弹性(刚需)": "#1565c0", "低弹性(撇脂定价目标)": "#f57c00", "高弹性(薅羊毛党)": "#e53935"}

# ═══ 页面标题 ═══
st.markdown("# 🤖 AI 单用户仿真 × 补贴策略优化平台")
st.caption("基于 LLM Agent 的用户行为仿真系统 | 从特征工程到策略落地的全流程可视化")

# ═══ Tab 切换 ═══
tabs = st.tabs([
    "📊 项目总览",
    "🔬 Step 1: 特征工程",
    "🧠 Step 2: Persona 注入",
    "⚡ Step 3: 冷启动仿真",
    "🎯 Step 4: Prompt 校准",
    "📏 Step 5: SiFi 评估",
    "💰 Step 6: 策略优化",
])

# ═══════════════════════════════════════════════════════════════
# Tab 1: 项目总览
# ═══════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown("## 项目全景")

    # Pipeline 流程图
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <span class="pipeline-step">Step 1<br>特征工程</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Step 2<br>Persona 注入</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Step 3<br>冷启动仿真</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Step 4<br>Prompt 校准</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step">Step 5<br>SiFi 评估</span>
        <span class="pipeline-arrow">→</span>
        <span class="pipeline-step" style="background: linear-gradient(135deg, #f57c00, #e53935);">Step 6<br>策略优化</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # 核心指标
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">用户画像</div>
            <div class="value">200</div>
            <div class="delta" style="color:{COLORS['info']}">36 维特征</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">仿真场景</div>
            <div class="value">8</div>
            <div class="delta" style="color:{COLORS['info']}">控制变量设计</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">仿真轨迹</div>
            <div class="value">{len(df_p1)+len(df_p2):,}</div>
            <div class="delta" style="color:{COLORS['info']}">Phase1: {len(df_p1)} + Phase2: {len(df_p2)}</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        grade = sifi["phase2"]["grade"]
        sifi_score = sifi["phase2"]["sifi"]
        st.markdown(f"""<div class="metric-card">
            <div class="label">SiFi 保真度</div>
            <div class="value" style="color:{COLORS['success']}">{sifi_score:.3f}</div>
            <div class="delta" style="color:{COLORS['success']}">{grade} 级 ✅</div>
        </div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class="metric-card">
            <div class="label">最优 ROI</div>
            <div class="value" style="color:{COLORS['success']}">14.0x</div>
            <div class="delta" style="color:{COLORS['info']}">¥300 预算</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # 问题 → 方案 → 结果
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### ❓ 问题")
        st.info(
            "美团补贴策略依赖线上 A/B 测试，\n"
            "- 每次测试需 2 周\n"
            "- 长尾场景（暴雨/节假日）覆盖为零\n"
            '- 产品经理在“盲投”'
        )
    with c2:
        st.markdown("### 💡 方案")
        st.success(
            "用 AI Agent 模拟 200 个真实用户，\n"
            '在 8 个场景下做"发券 vs 不发券"的\n'
            "反事实对比，替代线上 A/B 测试。\n\n"
            "**核心创新**: Prompt 校准将下单率\n"
            "从 85% 校准到 51%"
        )
    with c3:
        st.markdown("### 📈 结果")
        st.warning(
            "- SiFi 从 **D 级** → **A 级**\n"
            "- 下单率偏差从 36.9% → 3.6%\n"
            "- 测试周期从 2 周 → 1 天\n"
            "- 最优策略 ROI **14.0 倍**\n"
            "- 长尾场景覆盖 **100%**"
        )

# ═══════════════════════════════════════════════════════════════
# Tab 2: 特征工程
# ═══════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown("## Step 1: 特征工程 — 200 用户 × 36 维特征")

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("### 用户画像分布")
        fig = px.pie(df_features, names="elasticity_type", title="弹性类型分布",
                     color="elasticity_type", color_discrete_map=ELASTICITY_COLORS)
        fig.update_traces(textinfo="label+percent+value")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.markdown("### 城市分布")
        city_counts = df_features["city"].value_counts().head(10)
        fig = px.bar(x=city_counts.values, y=city_counts.index, orientation="h",
                     title="Top 10 城市", labels={"x": "用户数", "y": "城市"})
        fig.update_layout(yaxis=dict(autorange="reversed"))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 关键特征分布")

    feature_cols = ["avg_basket_size", "impulse_buy_rate", "deep_compare_rate",
                    "decayed_frequency", "lifecycle_health_score", "brand_hhi",
                    "avg_discount_enjoyed", "bad_weather_order_ratio"]

    c1, c2 = st.columns(2)
    for i, col in enumerate(feature_cols):
        target = c1 if i % 2 == 0 else c2
        with target:
            fig = px.histogram(df_features, x=col, color="elasticity_type",
                              color_discrete_map=ELASTICITY_COLORS,
                              nbins=20, title=col, barmode="overlay", opacity=0.7)
            fig.update_layout(height=250, showlegend=(i==0))
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 36 维特征分组")

    feature_groups = {
        "基础画像 (6)": ["city", "age", "lifecycle_stage", "member_status", "historical_spending_tier"],
        "行为统计 (9)": ["total_sessions", "add_cart_count", "weekend_poi_explore", "late_night_actions",
                       "avg_add_cart_per_session", "category_entropy", "impulse_buy_rate", "deep_compare_rate", "avg_dwell_time"],
        "价格财务 (6)": ["avg_basket_size", "premium_order_ratio", "high_discount_hunter_ratio",
                       "avg_discount_enjoyed", "delivery_fee_tolerance", "elasticity_type"],
        "活跃度 (4)": ["raw_frequency", "decayed_frequency", "decayed_monetary", "lifecycle_health_score"],
        "品牌偏好 (3)": ["brand_hhi", "avg_chosen_rating", "avg_items_per_order"],
        "场景标签 (5)": ["bad_weather_order_ratio", "loyalty_tag", "social_proof_tag", "household_tag", "weather_tag"],
    }
    for group, cols in feature_groups.items():
        with st.expander(f"📂 {group}（{len(cols)} 个字段）"):
            st.write(", ".join(cols))

# ═══════════════════════════════════════════════════════════════
# Tab 3: Persona 注入
# ═══════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown("## Step 2: Persona 注入 — 数值特征 → Agent Prompt")

    st.markdown("""
    每个用户的 36 维特征被翻译成三模块 Prompt：
    - **Module A — 身份内核**（你是谁）
    - **Module B — 决策规则**（你怎么花钱）
    - **Module C — CoT 思维链**（你内心怎么想）
    """)

    st.markdown("---")
    st.markdown("### 三种 CoT 路径对比")

    cot_paths = {
        "薅羊毛党": "券值评估 → 凑单计算 → 替代方案比较 → 最终决策",
        "品质用户": "需求与品质评估 → 品牌熟悉度 → 价格确认 → 最终决策",
        "刚需用户": "需求判断 → 习惯性选择 → 价格快速确认 → 最终决策",
    }

    cols = st.columns(3)
    colors_cot = [COLORS["danger"], COLORS["warning"], COLORS["primary"]]
    for i, (name, path) in enumerate(cot_paths.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background: white; border-radius: 12px; padding: 20px;
                        box-shadow: 0 2px 12px rgba(0,0,0,0.08); border-left: 4px solid {colors_cot[i]};">
                <h4 style="color: {colors_cot[i]};">{name}</h4>
                <p style="font-size: 14px; color: #555;">{path}</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 示例 Agent Prompt")

    selected_user = st.selectbox("选择用户", df_features["user_id"].unique(), key="persona_user")
    user_row = df_features[df_features["user_id"] == selected_user].iloc[0]

    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown("**用户特征摘要**")
        st.write(f"城市: {user_row['city']}")
        st.write(f"年龄: {user_row['age']}")
        st.write(f"弹性类型: {user_row['elasticity_type']}")
        st.write(f"客单价: {user_row['avg_basket_size']}")
        st.write(f"冲动购买率: {user_row['impulse_buy_rate']}")
        st.write(f"深度比价率: {user_row['deep_compare_rate']}")
        st.write(f"品牌集中度: {user_row['brand_hhi']}")
    with c2:
        prompt = user_row.get("llm_agent_prompt", "（无 Prompt 数据）")
        st.markdown("**生成的 Agent Prompt**")
        st.text_area("", value=str(prompt)[:2000], height=300, disabled=True, key="prompt_display")

# ═══════════════════════════════════════════════════════════════
# Tab 4: 冷启动仿真
# ═══════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown("## Step 3: 冷启动仿真 — 8 场景 × 200 用户")

    st.markdown("### 场景设计（控制变量）")

    scenarios = {
        "weekday_lunch": {"name": "工作日午餐", "time": "工作日 12:00", "weather": "晴", "coupon": "满30减8", "discount": "27%", "intent": "基准场景"},
        "afternoon_tea": {"name": "下午茶", "time": "工作日 15:00", "weather": "小雨", "coupon": "满25减8", "discount": "32%", "intent": "非刚需+冲动"},
        "weekend_rain_dinner": {"name": "周末暴雨晚餐", "time": "周末 18:00", "weather": "暴雨", "coupon": "满50减15", "discount": "30%", "intent": "赛题暴雨"},
        "weekday_breakfast": {"name": "工作日早餐", "time": "工作日 08:00", "weather": "晴", "coupon": "满15减5", "discount": "33%", "intent": "低客单价便捷"},
        "weekend_no_coupon": {"name": "周末无券", "time": "周末 11:00", "weather": "晴", "coupon": "无", "discount": "0%", "intent": "对照组"},
        "late_night": {"name": "夜宵", "time": "工作日 22:00", "weather": "晴", "coupon": "满20减6", "discount": "30%", "intent": "深夜行为"},
        "holiday_gathering": {"name": "节假日聚餐", "time": "节假日 12:00", "weather": "晴", "coupon": "满80减25", "discount": "31%", "intent": "高客单价"},
        "rain_stuck": {"name": "暴雨困办公室", "time": "工作日 16:00", "weather": "暴雨", "coupon": "满30减12", "discount": "40%", "intent": "极端组合"},
    }

    scenario_df = pd.DataFrame([
        {"场景": v["name"], "时间": v["time"], "天气": v["weather"],
         "优惠券": v["coupon"], "折扣率": v["discount"], "设计意图": v["intent"]}
        for v in scenarios.values()
    ])
    st.dataframe(scenario_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### Phase 1 vs Phase 2 行为分布对比")

    # 按场景统计行为分布
    def get_action_dist(df, label):
        records = []
        for scenario_key, info in scenarios.items():
            subset = df[df["scenario_key"] == scenario_key]
            if len(subset) == 0:
                continue
            action_counts = subset["action"].value_counts(normalize=True)
            for action in ["order", "cart", "browse", "ignore"]:
                records.append({
                    "场景": info["name"],
                    "行为": action,
                    "占比": action_counts.get(action, 0),
                    "版本": label
                })
        return pd.DataFrame(records)

    dist_p1 = get_action_dist(df_p1, "Phase 1")
    dist_p2 = get_action_dist(df_p2, "Phase 2")
    dist_combined = pd.concat([dist_p1, dist_p2])

    action_colors = {"order": "#2e7d32", "cart": "#f57c00", "browse": "#0288d1", "ignore": "#e53935"}

    fig = px.bar(dist_combined, x="场景", y="占比", color="行为", barmode="stack",
                 facet_col="版本", color_discrete_map=action_colors,
                 title="行为分布对比（Phase 1 vs Phase 2）")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 置信度分布对比")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df_p1, x="confidence", nbins=20, title="Phase 1 置信度分布",
                          color_discrete_sequence=[COLORS["danger"]])
        fig.add_vline(x=df_p1["confidence"].mean(), line_dash="dash", annotation_text=f"均值={df_p1['confidence'].mean():.3f}")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(df_p2, x="confidence", nbins=20, title="Phase 2 置信度分布",
                          color_discrete_sequence=[COLORS["success"]])
        fig.add_vline(x=df_p2["confidence"].mean(), line_dash="dash", annotation_text=f"均值={df_p2['confidence'].mean():.3f}")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# Tab 5: Prompt 校准
# ═══════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("## Step 4: Prompt 校准 — 从 85% 到 51%")

    st.markdown("### 核心指标对比")

    p1_order_rate = (df_p1["action"] == "order").mean()
    p2_order_rate = (df_p2["action"] == "order").mean()
    real_order_rate = 0.478

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Phase 1 下单率", f"{p1_order_rate:.1%}", "偏高 +36.9%", delta_color="inverse")
    with col2:
        st.metric("Phase 2 下单率", f"{p2_order_rate:.1%}", "偏差仅 +3.6%", delta_color="normal")
    with col3:
        st.metric("真实下单率", f"{real_order_rate:.1%}", "基准线")

    st.markdown("---")
    st.markdown("### 按弹性类型的下单率对比")

    elasticity_data = []
    for etype in df_p1["elasticity_type"].unique():
        p1_rate = df_p1[df_p1["elasticity_type"] == etype]["action"].eq("order").mean()
        p2_rate = df_p2[df_p2["elasticity_type"] == etype]["action"].eq("order").mean()
        elasticity_data.append({"弹性类型": etype, "下单率": p1_rate, "版本": "Phase 1"})
        elasticity_data.append({"弹性类型": etype, "下单率": p2_rate, "版本": "Phase 2"})
    df_elast = pd.DataFrame(elasticity_data)

    fig = px.bar(df_elast, x="弹性类型", y="下单率", color="版本", barmode="group",
                 color_discrete_map=PHASE_COLORS, title="弹性类型下单率对比")
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 按场景的下单率对比")

    scenario_data = []
    for skey, info in scenarios.items():
        p1_rate = df_p1[df_p1["scenario_key"] == skey]["action"].eq("order").mean()
        p2_rate = df_p2[df_p2["scenario_key"] == skey]["action"].eq("order").mean()
        scenario_data.append({"场景": info["name"], "下单率": p1_rate, "版本": "Phase 1"})
        scenario_data.append({"场景": info["name"], "下单率": p2_rate, "版本": "Phase 2"})
    df_scen = pd.DataFrame(scenario_data)

    fig = px.bar(df_scen, x="场景", y="下单率", color="版本", barmode="group",
                 color_discrete_map=PHASE_COLORS, title="场景下单率对比")
    fig.update_layout(yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 7 条校准约束")

    constraints = [
        "不是发券就下单 → 真实券使用率仅 47.8%",
        "无券更多浏览/忽略 → 52.4% 订单未使用券",
        "无夜宵习惯则忽略 → late_night_actions=0 的用户占多数",
        "券门槛太高则放弃 → 平均客单价 41.9 元",
        "置信度不总是高 → Phase 1 均值 0.87 偏高",
        "薅羊毛党无券不买 → high_discount_hunter_ratio 高的用户依赖券",
        '刚需非饭点意愿低 → 核心驱动力是"饿了"',
    ]
    for i, c in enumerate(constraints):
        st.markdown(f"**{i+1}.** {c}")

# ═══════════════════════════════════════════════════════════════
# Tab 6: SiFi 评估
# ═══════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown("## Step 5: SiFi 保真度评估 — D 级 → A 级")

    # 雷达图对比
    dimensions = ["行为分布对齐", "弹性类型差异度", "场景响应合理性", "置信度校准"]
    p1_scores = [
        sifi["phase1"]["distribution"]["score"],
        sifi["phase1"]["elasticity"]["score"],
        sifi["phase1"]["scenario"]["score"],
        sifi["phase1"]["confidence"]["score"],
    ]
    p2_scores = [
        sifi["phase2"]["distribution"]["score"],
        sifi["phase2"]["elasticity"]["score"],
        sifi["phase2"]["scenario"]["score"],
        sifi["phase2"]["confidence"]["score"],
    ]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=p1_scores + [p1_scores[0]], theta=dimensions + [dimensions[0]],
        fill="toself", name="Phase 1", line_color=COLORS["danger"], opacity=0.3
    ))
    fig.add_trace(go.Scatterpolar(
        r=p2_scores + [p2_scores[0]], theta=dimensions + [dimensions[0]],
        fill="toself", name="Phase 2", line_color=COLORS["success"], opacity=0.3
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="SiFi 四维评估雷达图",
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 分维度详细展示
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Phase 1（无校准）")
        st.error(f"**SiFi = {sifi['phase1']['sifi']:.3f}  |  {sifi['phase1']['grade']} 级**")
        d1 = sifi["phase1"]["distribution"]
        st.write(f"- 下单率: 仿真 {d1['order_rate_sim']:.1%} vs 真实 {d1['order_rate_real']:.1%} (偏差 {d1['order_rate_diff']:.1%})")
        e1 = sifi["phase1"]["elasticity"]
        for k, v in e1["type_rates"].items():
            st.write(f"- {k}: {v:.1%}")
        st.write(f"- 置信度均值: {sifi['phase1']['confidence']['mean']:.3f}")

    with col2:
        st.markdown("### Phase 2（有校准）")
        st.success(f"**SiFi = {sifi['phase2']['sifi']:.3f}  |  {sifi['phase2']['grade']} 级 ✅**")
        d2 = sifi["phase2"]["distribution"]
        st.write(f"- 下单率: 仿真 {d2['order_rate_sim']:.1%} vs 真实 {d2['order_rate_real']:.1%} (偏差 {d2['order_rate_diff']:.1%})")
        e2 = sifi["phase2"]["elasticity"]
        for k, v in e2["type_rates"].items():
            st.write(f"- {k}: {v:.1%}")
        st.write(f"- 置信度均值: {sifi['phase2']['confidence']['mean']:.3f}")

    # 各维度得分柱状图
    st.markdown("---")
    st.markdown("### 各维度得分改善")

    score_df = pd.DataFrame({
        "维度": dimensions * 2,
        "得分": p1_scores + p2_scores,
        "版本": ["Phase 1"] * 4 + ["Phase 2"] * 4
    })
    fig = px.bar(score_df, x="维度", y="得分", color="版本", barmode="group",
                 color_discrete_map=PHASE_COLORS, title="SiFi 各维度得分对比")
    fig.update_layout(yaxis_range=[0, 1.1])
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════
# Tab 7: 策略优化
# ═══════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown("## Step 6: 补贴策略优化 — Agent 反事实 Uplift")

    # 总览指标
    st.markdown("### 1,400 个候选动作总览")
    pos = (df_all_uplift["uplift_gmv"] > 0).sum()
    neg = (df_all_uplift["uplift_gmv"] < 0).sum()
    zero = (df_all_uplift["uplift_gmv"] == 0).sum()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("正向 uplift", f"{pos} ({pos/len(df_all_uplift):.1%})")
    with c2:
        st.metric("负向 uplift", f"{neg} ({neg/len(df_all_uplift):.1%})")
    with c3:
        st.metric("平均 uplift GMV", f"¥{df_all_uplift['uplift_gmv'].mean():.2f}")
    with c4:
        st.metric("平均净值", f"¥{df_all_uplift['net_value'].mean():.2f}")

    st.markdown("---")

    # 预算敏感性
    st.markdown("### 预算敏感性分析")
    budget_data = pd.DataFrame({
        "预算(元)": [50, 100, 200, 300, 500, 800, 1200],
        "发券数": [11, 23, 45, 63, 93, 149, 182],
        "增量GMV": [1458.4, 2265.2, 3359.3, 4197.0, 5553.5, 7234.3, 8718.6],
        "ROI": [29.2, 22.7, 16.8, 14.0, 11.1, 9.1, 7.3],
    })

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(budget_data, x="预算(元)", y="增量GMV", color="ROI",
                     color_continuous_scale="Greens", title="不同预算下的增量 GMV")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.line(budget_data, x="预算(元)", y="ROI", markers=True,
                     title="ROI 随预算递减（边际效益）")
        fig.update_traces(line_color=COLORS["primary"], line_width=3)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 净值矩阵
    st.markdown("### 场景 × 弹性类型 净值矩阵")

    matrix_data = []
    for _, row in df_all_uplift.iterrows():
        matrix_data.append({
            "场景": scenarios.get(row["scenario_key"], {}).get("name", row["scenario_key"]),
            "弹性类型": row["elasticity_type"],
            "净值": row["net_value"],
        })
    df_matrix = pd.DataFrame(matrix_data)
    pivot = df_matrix.pivot_table(index="场景", columns="弹性类型", values="净值", aggfunc="mean")

    fig = px.imshow(pivot, text_auto=".1f", aspect="auto",
                    color_continuous_scale="RdYlGn", title="平均净值矩阵（元）")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # 用户分群
    st.markdown("### 用户四象限分群")
    seg_counts = df_segments["segment"].value_counts()
    fig = px.pie(values=seg_counts.values, names=seg_counts.index,
                 title="用户分群分布", color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_traces(textinfo="label+percent+value")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Top uplift 用户
    st.markdown("### 净值最高的 10 个发券决策")
    top10 = df_selected.nlargest(10, "net_value")[
        ["user_id", "elasticity_type", "avg_basket_size", "scenario_label",
         "coupon_desc", "uplift_conv", "uplift_gmv", "expected_cost", "net_value", "roi"]
    ].copy()
    top10.columns = ["用户", "弹性类型", "客单价", "场景", "优惠券",
                     "增量转化率", "增量GMV", "预期成本", "净值", "ROI"]
    st.dataframe(top10.style.format({
        "客单价": "¥{:.1f}", "增量转化率": "+{:.2f}", "增量GMV": "¥{:.1f}",
        "预期成本": "¥{:.2f}", "净值": "¥{:.1f}", "ROI": "{:.1f}x"
    }), use_container_width=True, hide_index=True)

    st.markdown("---")

    # Uplift 分布
    st.markdown("### Uplift GMV 分布")
    fig = px.histogram(df_all_uplift, x="uplift_gmv", nbins=50, color="elasticity_type",
                      color_discrete_map=ELASTICITY_COLORS, title="Uplift GMV 分布（按弹性类型）",
                      barmode="overlay", opacity=0.7)
    fig.add_vline(x=0, line_dash="dash", line_color="black")
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

# ═══ 页脚 ═══
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #999; font-size: 12px;'>"
    "AI 单用户仿真能力建设及在补贴策略中的应用 | 2026"
    "</div>",
    unsafe_allow_html=True
)
