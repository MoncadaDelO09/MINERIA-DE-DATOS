import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# CONFIGURACION


st.set_page_config(
    page_title="Dashboard de Ventas",
    layout="wide",
    initial_sidebar_state="expanded"
)


# CSS


def load_css():
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

COLORS = {
    "cyan":    "#0ea5e9",
    "amber":   "#f59e0b",
    "emerald": "#10b981",
    "violet":  "#8b5cf6",
    "rose":    "#f43f5e",
    "slate":   "#64748b",
}

PLOT_BG   = "#131f35"
PAPER_BG  = "#131f35"
GRID_CLR  = "#1e293b"
TEXT_CLR  = "#94a3b8"
TITLE_CLR = "#e2e8f0"

def plotly_base_layout(title=""):
    return dict(
        title=dict(
            text=title,
            font=dict(family="Inter", size=13, color=TITLE_CLR),
            x=0.0, xanchor="left", pad=dict(l=4, t=4)
        ),
        template="plotly_dark",
        paper_bgcolor=PAPER_BG,
        plot_bgcolor=PLOT_BG,
        font=dict(family="Inter", color=TEXT_CLR, size=11),
        margin=dict(l=16, r=16, t=44, b=16),
        legend=dict(
            bgcolor="#1e293b",
            bordercolor="#334155",
            borderwidth=1,
            font=dict(size=11)
        ),
        xaxis=dict(
            gridcolor=GRID_CLR,
            linecolor=GRID_CLR,
            tickfont=dict(size=10, family="JetBrains Mono"),
        ),
        yaxis=dict(
            gridcolor=GRID_CLR,
            linecolor=GRID_CLR,
            tickfont=dict(size=10, family="JetBrains Mono"),
        ),
    )


# CARGAR DATOS

@st.cache_data
def load_data():
    return pd.read_csv("dataset_limpio.csv")

df = load_data()


# SIDEBAR


with st.sidebar:
    st.markdown("###  Filtros")
    st.markdown("---")

    region = st.multiselect(
        "Región",
        options=sorted(df["Region"].unique()),
        default=list(df["Region"].unique()),
    )

    categoria = st.multiselect(
        "Categoría",
        options=sorted(df["Category"].unique()),
        default=list(df["Category"].unique()),
    )

    st.markdown("---")

    st.markdown(
        f"""
        <div style="font-size:10px;color:#475569;font-family:'JetBrains Mono',monospace;line-height:1.8;">
        REGISTROS ACTIVOS<br>
        <span style="color:#0ea5e9;font-size:16px;font-weight:700;">
        {len(df[df["Region"].isin(region) & df["Category"].isin(categoria)]):,}
        </span><br>de {len(df):,} totales
        </div>
        """,
        unsafe_allow_html=True
    )

df_filtrado = df[
    (df["Region"].isin(region)) &
    (df["Category"].isin(categoria))
]


# KPIs


total_ventas    = df_filtrado["Sales"].sum()
total_clientes  = df_filtrado["Customer ID"].nunique()
promedio_ventas = df_filtrado["Sales"].mean()
total_ordenes   = df_filtrado.shape[0]

producto_top = (
    df_filtrado.groupby("Product Name")["Quantity"]
    .sum()
    .idxmax()
    if not df_filtrado.empty else "—"
)

ganancia_total = df_filtrado["Profit"].sum() if "Profit" in df_filtrado.columns else None


# ENCABEZADO


st.markdown(
    """
    <div class="dash-header">
        <div class="dash-header-text">
            <p class="dash-header-title">Dashboard de Análisis de Ventas</p>
            <p class="dash-header-sub">sales_analytics · v1.0 · dataset_limpio.csv</p>
        </div>
        <span class="dash-badge">● LIVE</span>
    </div>
    """,
    unsafe_allow_html=True
)


# SECCION: KPIs


st.markdown('<div class="section-label">Métricas clave</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

kpi_data = [
    {
        "col": col1,
        "label": "Total Ventas",
        "value": f"${total_ventas:,.0f}",
        "delta": "↑ acumulado",
        "delta_type": "up",
        "accent": COLORS["cyan"],
    },
    {
        "col": col2,
        "label": "Clientes Únicos",
        "value": f"{total_clientes:,}",
        "delta": f"{total_ordenes:,} órdenes",
        "delta_type": "neutral",
        "accent": COLORS["emerald"],
    },
    {
        "col": col3,
        "label": "PRomedio Por Compra",
        "value": f"${promedio_ventas:,.2f}",
        "delta": "por orden",
        "delta_type": "neutral",
        "accent": COLORS["amber"],
    },
    {
        "col": col4,
        "label": "Producto Top",
        "value": producto_top,
        "delta": "por cantidad",
        "delta_type": "up",
        "accent": COLORS["violet"],
        "small": True,
    },
]

for kpi in kpi_data:
    value_class = "kpi-value small" if kpi.get("small") else "kpi-value"
    with kpi["col"]:
        st.markdown(
            f"""
            <div class="kpi-card" style="--accent:{kpi['accent']}">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="{value_class}">{kpi['value']}</div>
                <span class="kpi-delta {kpi['delta_type']}">{kpi['delta']}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

if ganancia_total is not None:
    st.markdown(
        f"""
        <div class="kpi-card" style="--accent:{COLORS['emerald']};margin-top:14px;">
            <span class="kpi-icon"></span>
            <div class="kpi-label">Ganancia Total</div>
            <div class="kpi-value">${ganancia_total:,.0f}</div>
            <span class="kpi-delta {'up' if ganancia_total > 0 else 'neutral'}">
                {'↑' if ganancia_total > 0 else '↓'} margen neto
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )


# SECCION: GRAFICOS FILA 1


st.markdown('<div class="section-label">Distribución</div>', unsafe_allow_html=True)

col5, col6 = st.columns(2)

ventas_categoria = (
    df_filtrado.groupby("Category")["Sales"]
    .sum()
    .reset_index()
    .sort_values("Sales", ascending=False)
)

fig_bar = px.bar(
    ventas_categoria,
    x="Category",
    y="Sales",
    color="Category",
    color_discrete_sequence=list(COLORS.values()),
    text_auto=".3s",
)

fig_bar.update_traces(
    marker_line_width=0,
    textfont=dict(size=10, family="JetBrains Mono"),
    textposition="outside",
)

fig_bar.update_layout(
    **plotly_base_layout("Ventas por Categoría"),
    showlegend=False,
)

ventas_region = (
    df_filtrado.groupby("Region")["Sales"]
    .sum()
    .reset_index()
)

fig_pie = px.pie(
    ventas_region,
    names="Region",
    values="Sales",
    hole=0.55,
    color_discrete_sequence=list(COLORS.values()),
)

fig_pie.update_traces(
    textposition="outside",
    textfont=dict(size=10, family="JetBrains Mono"),
    hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<extra></extra>",
)

fig_pie.update_layout(**plotly_base_layout("Ventas por Región"))

fig_pie.update_layout(legend=dict(
    bgcolor="#1e293b",
    bordercolor="#334155",
    borderwidth=1,
    font=dict(size=11),
    orientation="v",
    x=1.02, y=0.5, xanchor="left",
))

fig_pie.add_annotation(
    text=f"${ventas_region['Sales'].sum():,.0f}",
    x=0.5, y=0.55,
    font=dict(size=15, color=TITLE_CLR, family="Inter"),
    showarrow=False,
)
fig_pie.add_annotation(
    text="total",
    x=0.5, y=0.44,
    font=dict(size=10, color=TEXT_CLR, family="JetBrains Mono"),
    showarrow=False,
)

with col5:
    st.plotly_chart(fig_bar, use_container_width=True)

with col6:
    st.plotly_chart(fig_pie, use_container_width=True)


# SECCIoN: TENDENCIA


if "Year" in df_filtrado.columns:
    st.markdown('<div class="section-label">Tendencia temporal</div>', unsafe_allow_html=True)

    ventas_tiempo = (
        df_filtrado.groupby("Year")["Sales"]
        .sum()
        .reset_index()
    )

    fig_line = go.Figure()

    fig_line.add_trace(go.Scatter(
        x=ventas_tiempo["Year"],
        y=ventas_tiempo["Sales"],
        mode="lines+markers",
        name="Ventas",
        line=dict(color=COLORS["cyan"], width=2.5),
        marker=dict(size=7, color=COLORS["cyan"], line=dict(width=2, color=PAPER_BG)),
        fill="tozeroy",
        fillcolor="rgba(14, 165, 233, 0.09)",
        hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
    ))

    if "Profit" in df_filtrado.columns:
        profit_tiempo = (
            df_filtrado.groupby("Year")["Profit"]
            .sum()
            .reset_index()
        )
        fig_line.add_trace(go.Scatter(
            x=profit_tiempo["Year"],
            y=profit_tiempo["Profit"],
            mode="lines+markers",
            name="Ganancia",
            line=dict(color=COLORS["emerald"], width=2, dash="dot"),
            marker=dict(size=6, color=COLORS["emerald"], line=dict(width=2, color=PAPER_BG)),
            hovertemplate="<b>%{x}</b><br>$%{y:,.0f}<extra></extra>",
        ))

    fig_line.update_layout(**plotly_base_layout("Tendencia de Ventas"))
    st.plotly_chart(fig_line, use_container_width=True)


# SECCION: TOP PAÍSES


st.markdown('<div class="section-label">Ranking de países</div>', unsafe_allow_html=True)

top_paises = (
    df_filtrado.groupby("Country")
    .agg(
        Ganancia=("Profit", "sum"),
        Ventas=("Sales", "sum"),
    )
    .sort_values("Ganancia", ascending=False)
    .head(10)
    .reset_index()
)

top_paises.index = top_paises.index + 1

col7, col8 = st.columns([3, 2])

with col7:
    _, centro, _ = st.columns([0.05, 1, 0.05])
    with centro:
        st.markdown(
            """
            <div class="table-header">
                <span class="table-title"> Top 10 Países</span>
                <span class="table-badge">por ganancia</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.dataframe(
            top_paises.style.format({"Ganancia": "${:,.2f}", "Ventas": "${:,.2f}"}),
            use_container_width=True,
            height=400,
        )


# GRAFICO: TOP 10 PRODUCTOS MAS VENDIDOS


st.markdown('<div class="section-label">Top productos</div>', unsafe_allow_html=True)

top_productos = (
    df_filtrado.groupby("Product Name")
    .agg(
        Cantidad=("Quantity", "sum"),
        Ventas=("Sales", "sum"),
    )
    .sort_values("Cantidad", ascending=False)
    .head(10)
    .reset_index()
)

fig_top = px.bar(
    top_productos.sort_values("Cantidad"),
    x="Cantidad",
    y="Product Name",
    orientation="h",
    color="Cantidad",
    color_continuous_scale=[[0, "#1e3a5f"], [1, COLORS["cyan"]]],
    text_auto=".3s",
)

fig_top.update_traces(
    textfont=dict(size=9, family="JetBrains Mono"),
    textposition="outside",
)

fig_top.update_layout(
    **plotly_base_layout("Top 10 Productos más Vendidos por Cantidad"),
    showlegend=False,
    coloraxis_showscale=False,
)

fig_top.update_yaxes(tickfont=dict(size=9))

st.plotly_chart(fig_top, use_container_width=True)