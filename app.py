from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


DATA_FILE = "findex_clean.csv"
PERCENT_COLUMNS = ["Account", "Savings", "Debit", "Credit", "DigitalPay"]
SCORE_COLUMNS = ["Account", "Debit", "Credit", "DigitalPay"]
COUNTRY_COLORS = {
    "Indonesia": "#636EFA",
    "Malaysia": "#EF553B",
    "Philippines": "#00CC96",
    "Singapore": "#AB63FA",
    "Thailand": "#FFA15A",
}


st.set_page_config(
    page_title="ASEAN Digital Payments: Adoption, Infrastructure & Market Readiness",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE).dropna(how="all").copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)
    df["pop_adult"] = pd.to_numeric(df["pop_adult"], errors="coerce")

    for column in PERCENT_COLUMNS:
        df[column] = pd.to_numeric(
            df[column].astype("string").str.replace("%", "", regex=False),
            errors="coerce",
        )

    return df


def standardize(series: pd.Series) -> pd.Series:
    std = series.std(ddof=0)
    if pd.isna(std) or std == 0:
        return series * 0
    return (series - series.mean()) / std


def build_figures(df: pd.DataFrame) -> tuple[go.Figure, go.Figure, go.Figure, go.Figure]:
    fig1 = px.line(
        df,
        x="year",
        y="DigitalPay",
        color="country",
        markers=True,
        color_discrete_map=COUNTRY_COLORS,
        title="Digital Payment Adoption by Country and Year",
        labels={
            "year": "Year",
            "DigitalPay": "Digital payment usage (%)",
            "country": "Country",
        },
    )

    fig2 = px.scatter(
        df,
        x="Account",
        y="DigitalPay",
        color="country",
        size="pop_adult",
        animation_frame="year",
        color_discrete_map=COUNTRY_COLORS,
        title="Account Ownership vs Digital Payment Usage",
        labels={
            "Account": "Account ownership (%)",
            "DigitalPay": "Digital payment usage (%)",
            "pop_adult": "Adult population",
            "country": "Country",
        },
        size_max=48,
        range_x=[0, 105],
        range_y=[0, 105],
    )

    plot_df = df.melt(
        id_vars=["country", "year"],
        value_vars=["Debit", "Credit"],
        var_name="card_type",
        value_name="ownership",
    )
    plot_df = plot_df[plot_df["year"] != 2024]

    fig3 = px.bar(
        plot_df,
        x="country",
        y="ownership",
        color="card_type",
        barmode="group",
        animation_frame="year",
        title="Debit and Credit Card Ownership",
        labels={
            "country": "Country",
            "ownership": "Ownership (%)",
            "card_type": "Card type",
        },
        color_discrete_map={"Debit": "#636EFA", "Credit": "#EF553B"},
        range_y=[0, 105],
    )

    latest = df[df["year"] == 2021].copy()
    for column in SCORE_COLUMNS:
        latest[column] = standardize(latest[column])

    latest["score"] = latest[SCORE_COLUMNS].mean(axis=1)
    latest["country_score_label"] = latest["score"].round(2)

    fig4 = px.bar(
        latest.sort_values("score"),
        x="score",
        y="country",
        orientation="h",
        color="country",
        color_discrete_map=COUNTRY_COLORS,
        text="country_score_label",
        title="Payments Readiness Score in 2021",
        labels={
            "score": "Average standardized score",
            "country": "Country",
        },
    )
    fig4.update_traces(textposition="outside", cliponaxis=False)

    return fig1, fig2, fig3, fig4


def polish_figure(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        height=490,
        margin=dict(l=24, r=24, t=64, b=42),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(family="Arial, sans-serif", size=13, color="#000000"),
        title_font=dict(color="#000000"),
        legend=dict(font=dict(color="#000000"), title_font=dict(color="#000000")),
        legend_title_text="",
        template="plotly_white",
    )
    fig.update_xaxes(
        showgrid=False,
        color="#000000",
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
    )
    fig.update_yaxes(
        gridcolor="#e5e7eb",
        zerolinecolor="#cbd5e1",
        color="#000000",
        title_font=dict(color="#000000"),
        tickfont=dict(color="#000000"),
    )

    for annotation in fig.layout.annotations or []:
        annotation.font = annotation.font or {}
        annotation.font.color = "#000000"

    for slider in fig.layout.sliders or []:
        slider.font = slider.font or {}
        slider.font.color = "#000000"
        slider.currentvalue.font = slider.currentvalue.font or {}
        slider.currentvalue.font.color = "#000000"

    for menu in fig.layout.updatemenus or []:
        menu.font = menu.font or {}
        menu.font.color = "#000000"

    return fig


st.markdown(
    """
    <style>
    .stApp {
        background: #ffffff;
        color: #000000;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2.5rem;
        background: #ffffff;
    }
    h1, h2, h3 {
        letter-spacing: 0;
        color: #000000;
    }
    p, span, label, div {
        color: #000000;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #d9d9d9;
        border-radius: 8px;
        padding: 0.85rem 1rem;
        background: #ffffff;
        color: #000000;
    }
    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] [data-testid="stMetricLabel"],
    div[data-testid="stMetric"] [data-testid="stMetricValue"],
    div[data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #000000;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.65rem;
        font-weight: 700;
    }
    div[data-testid="stMetricLabel"] p {
        color: #000000;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

df = load_data()
fig1, fig2, fig3, fig4 = build_figures(df)

st.title("ASEAN Digital Payments: Adoption, Infrastructure & Market Readiness")
st.caption("Digital payment adoption in selected ASEAN markets using Findex indicators.")

latest_year = int(df["year"].max())
latest = df[df["year"] == latest_year]
previous = df[df["year"] == df["year"].min()]

avg_digital_change = latest["DigitalPay"].mean() - previous["DigitalPay"].mean()

kpi_cols = st.columns(4)
kpi_cols[0].metric("Markets", f"{df['country'].nunique():,.0f}")
kpi_cols[1].metric("Latest year", f"{latest_year}")
kpi_cols[2].metric("Avg. digital payments", f"{latest['DigitalPay'].mean():.0f}%")
kpi_cols[3].metric("Change since 2014", f"{avg_digital_change:+.0f}%")

st.divider()

top_left, top_right = st.columns(2)
bottom_left, bottom_right = st.columns(2)

with top_left:
    st.plotly_chart(polish_figure(fig1), key="fig1")

with top_right:
    st.plotly_chart(polish_figure(fig2), key="fig2")

with bottom_left:
    st.plotly_chart(polish_figure(fig3), key="fig3")

with bottom_right:
    st.plotly_chart(polish_figure(fig4), key="fig4")
