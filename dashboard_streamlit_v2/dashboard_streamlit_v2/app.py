import os
from typing import Tuple

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from google.auth.exceptions import DefaultCredentialsError
from google.cloud import bigquery
from google.oauth2 import service_account

st.set_page_config(
    page_title="Air Quality Torino",
    page_icon="AQ",
    layout="wide",
    initial_sidebar_state="expanded",
)

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "dm-torino-airquality")
DATASET = os.getenv("BQ_MARTS_DATASET", "staging_marts")

EU_NO2 = 40.0
EU_PM10 = 40.0
WHO_NO2 = 10.0
WHO_PM10 = 15.0
EU_PM10_DAYS = 35

COLORS = {
    "ink": "#0F172A",
    "muted": "#64748B",
    "light": "#94A3B8",
    "bg": "#F5F7FB",
    "panel": "#FFFFFF",
    "border": "#E2E8F0",
    "navy": "#0B1F3A",
    "blue": "#1D4ED8",
    "blue_soft": "#DBEAFE",
    "cyan": "#0F766E",
    "cyan_soft": "#CCFBF1",
    "orange": "#EA580C",
    "orange_soft": "#FFEDD5",
    "red": "#DC2626",
    "red_soft": "#FEE2E2",
    "green": "#059669",
    "green_soft": "#D1FAE5",
    "amber": "#B45309",
    "amber_soft": "#FEF3C7",
    "slate": "#334155",
}
TYPE_COLORS = {"Traffic": COLORS["blue"], "Background": COLORS["orange"]}
PLOTLY_CONFIG = {"displayModeBar": False, "displaylogo": False, "responsive": True}

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    .stApp {{
        background: {COLORS['bg']};
        color: {COLORS['ink']};
        font-family: 'Manrope', system-ui, sans-serif;
    }}

    section[data-testid="stSidebar"] {{
        background: #FFFFFF;
        border-right: 1px solid {COLORS['border']};
    }}

    .main .block-container {{
        max-width: 1440px;
        padding-top: 1rem;
        padding-bottom: 2.2rem;
    }}

    .hero {{
        background:
            radial-gradient(circle at 88% 18%, rgba(96,165,250,.28), transparent 24%),
            linear-gradient(135deg, #07111F 0%, #0F172A 55%, #1E3A8A 100%);
        border-radius: 22px;
        padding: 34px 38px;
        color: #FFFFFF;
        box-shadow: 0 18px 50px rgba(15, 23, 42, 0.22);
        margin-bottom: 22px;
    }}

    .hero-kicker {{
        color: #93C5FD;
        text-transform: uppercase;
        letter-spacing: .16em;
        font-size: .72rem;
        font-weight: 800;
        margin-bottom: 10px;
    }}

    .hero-title {{
        font-size: 2.35rem;
        font-weight: 800;
        line-height: 1.02;
        letter-spacing: -.045em;
        margin-bottom: 10px;
    }}

    .page-context {{
        color: {COLORS['blue']};
        text-transform: uppercase;
        letter-spacing: .14em;
        font-size: .7rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .page-main-title {{
        color: {COLORS['ink']};
        font-size: 1.7rem;
        line-height: 1.08;
        letter-spacing: -.04em;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .page-subtitle-meta {{
        color: {COLORS['muted']};
        font-size: .86rem;
        font-weight: 600;
        margin-bottom: 18px;
    }}

    .hero-subtitle {{
        font-size: .96rem;
        line-height: 1.7;
        color: #DBEAFE;
        max-width: 820px;
    }}

    .tag-row {{
        margin-top: 18px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }}

    .tag {{
        display: inline-block;
        background: rgba(255,255,255,.09);
        border: 1px solid rgba(255,255,255,.18);
        color: #E0F2FE;
        border-radius: 999px;
        padding: 5px 11px;
        font-size: .72rem;
        font-weight: 700;
    }}

    .section-title {{
        margin: 0 0 14px 0;
        padding-bottom: 10px;
        border-bottom: 2px solid {COLORS['border']};
        font-size: 1.02rem;
        font-weight: 800;
        color: {COLORS['ink']};
        letter-spacing: -.02em;
    }}

    .chart-title {{
        color: {COLORS['ink']};
        font-size: 0.95rem;
        font-weight: 800;
        line-height: 1.3;
        margin: 0 0 8px 0;
    }}

    .rq-banner {{
        background: {COLORS['blue_soft']};
        border: 1px solid #BFDBFE;
        border-left: 5px solid {COLORS['blue']};
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 18px;
    }}

    .rq-id {{
        color: {COLORS['blue']};
        text-transform: uppercase;
        letter-spacing: .14em;
        font-size: .68rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .rq-text {{
        color: {COLORS['ink']};
        font-size: .95rem;
        line-height: 1.6;
        font-weight: 600;
    }}

    .metric-card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 18px 18px 16px;
        box-shadow: 0 8px 20px rgba(15,23,42,.05);
        min-height: 122px;
    }}

    .metric-label {{
        color: {COLORS['muted']};
        text-transform: uppercase;
        letter-spacing: .1em;
        font-size: .69rem;
        font-weight: 800;
        margin-bottom: 7px;
    }}

    .metric-value {{
        color: var(--accent);
        font-size: 2rem;
        line-height: 1;
        letter-spacing: -.04em;
        font-weight: 800;
        margin-bottom: 6px;
    }}

    .metric-sub {{
        color: {COLORS['muted']};
        font-size: .8rem;
        line-height: 1.45;
        font-weight: 500;
    }}

    .panel {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 8px 20px rgba(15,23,42,.05);
    }}

    .rq-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 22px;
        margin: 0 0 18px 0;
    }}

    .rq-card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 22px 22px 20px;
        box-shadow: 0 8px 20px rgba(15,23,42,.05);
        min-height: 230px;
        display: flex;
        flex-direction: column;
    }}

    .rq-card-title {{
        font-size: 1rem;
        line-height: 1.55;
        font-weight: 800;
        color: {COLORS['ink']};
        margin-bottom: 16px;
    }}

    .rq-card-answer {{
        margin-top: auto;
    }}

    @media (max-width: 980px) {{
        .rq-grid {{
            grid-template-columns: 1fr;
        }}
    }}

    .note {{
        background: #FFFFFF;
        border: 1px dashed {COLORS['border']};
        border-radius: 12px;
        padding: 12px 14px;
        color: {COLORS['slate']};
        font-size: .83rem;
        line-height: 1.55;
    }}

    .answer-box {{
        background: {COLORS['green_soft']};
        border: 1px solid #A7F3D0;
        border-left: 5px solid {COLORS['green']};
        border-radius: 14px;
        padding: 16px 18px;
        margin-top: 10px;
    }}

    .answer-label {{
        color: {COLORS['green']};
        text-transform: uppercase;
        letter-spacing: .14em;
        font-size: .68rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .answer-text {{
        color: {COLORS['ink']};
        font-size: .92rem;
        line-height: 1.62;
    }}

    .mini-card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 16px;
        box-shadow: 0 8px 20px rgba(15,23,42,.04);
        min-height: 146px;
    }}

    .mini-label {{
        font-size: .68rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .12em;
        margin-bottom: 8px;
        color: var(--mini-accent);
    }}

    .mini-text {{
        color: {COLORS['ink']};
        font-size: .85rem;
        line-height: 1.55;
    }}

    .architecture-card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 16px 14px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(15,23,42,.04);
        height: 100%;
    }}

    .architecture-icon {{
        font-size: 1.55rem;
        margin-bottom: 8px;
        color: {COLORS['blue']};
    }}

    .architecture-title {{
        color: {COLORS['ink']};
        font-size: .82rem;
        font-weight: 800;
        margin-bottom: 6px;
    }}

    .architecture-text {{
        color: {COLORS['muted']};
        font-size: .74rem;
        line-height: 1.55;
        white-space: pre-line;
    }}

    .architecture-arrow {{
        color: {COLORS['light']};
        font-size: 1.4rem;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }}

    .limit-chip-row {{
        margin-bottom: 8px;
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }}

    .limit-chip {{
        display: inline-block;
        border-radius: 999px;
        padding: 4px 10px;
        font-size: .72rem;
        font-weight: 700;
    }}

    .chip-eu {{
        background: {COLORS['red_soft']};
        color: {COLORS['red']};
        border: 1px solid #FCA5A5;
    }}

    .chip-who {{
        background: {COLORS['amber_soft']};
        color: {COLORS['amber']};
        border: 1px solid #FCD34D;
    }}

    .chip-ok {{
        background: {COLORS['green_soft']};
        color: {COLORS['green']};
        border: 1px solid #86EFAC;
    }}

    .chip-info {{
        background: {COLORS['blue_soft']};
        color: {COLORS['blue']};
        border: 1px solid #93C5FD;
    }}

    .fact-grid-card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: 16px;
        padding: 14px 10px;
        text-align: center;
        box-shadow: 0 8px 20px rgba(15,23,42,.04);
    }}

    .fact-grid-year {{
        color: {COLORS['muted']};
        text-transform: uppercase;
        letter-spacing: .1em;
        font-size: .64rem;
        font-weight: 800;
        margin-bottom: 4px;
    }}

    .fact-grid-type {{
        font-size: .7rem;
        font-weight: 700;
        margin-bottom: 6px;
        color: var(--accent);
    }}

    .fact-grid-value {{
        color: var(--accent);
        font-size: 2.1rem;
        line-height: 1;
        font-weight: 800;
        letter-spacing: -.04em;
    }}

    .fact-grid-caption {{
        color: {COLORS['muted']};
        font-size: .68rem;
        margin-top: 4px;
    }}

    .status-badge {{
        display: inline-block;
        border-radius: 999px;
        padding: 3px 9px;
        font-size: .68rem;
        font-weight: 800;
        margin-top: 6px;
    }}

    .status-badge.bad {{
        color: {COLORS['red']};
        background: {COLORS['red_soft']};
    }}

    .status-badge.good {{
        color: {COLORS['green']};
        background: {COLORS['green_soft']};
    }}

    .status-badge.warn {{
        color: {COLORS['amber']};
        background: {COLORS['amber_soft']};
    }}

    div[data-testid="stDataFrame"] {{
        border-radius: 14px;
        overflow: hidden;
        border: 1px solid {COLORS['border']};
    }}

    .footer-note {{
        color: {COLORS['light']};
        font-size: .78rem;
        text-align: center;
        border-top: 1px solid {COLORS['border']};
        padding-top: 14px;
        margin-top: 22px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_client() -> bigquery.Client:
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    fallback_path = os.path.join(os.path.expanduser("~"), "gcp-keys", "dlt-loader-key.json")

    for candidate in [credentials_path, fallback_path]:
        if candidate and os.path.exists(candidate):
            credentials = service_account.Credentials.from_service_account_file(candidate)
            return bigquery.Client(project=PROJECT_ID, credentials=credentials)

    return bigquery.Client(project=PROJECT_ID)


@st.cache_data(show_spinner=False, ttl=3600)
def run_query(sql: str) -> pd.DataFrame:
    job = get_client().query(sql)
    return job.result().to_dataframe(create_bqstorage_client=False)


@st.cache_data(show_spinner="Loading data from BigQuery...", ttl=3600)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    station_type_summary = run_query(
        f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.mart_station_type_year_summary`
        ORDER BY reporting_year, station_type
        """
    )

    station_fact = run_query(
        f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.fact_air_quality_annual`
        ORDER BY station_code, reporting_year
        """
    )

    aq_weather = run_query(
        f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.mart_air_quality_weather_yearly`
        ORDER BY station_code, reporting_year
        """
    )

    station_enriched = run_query(
        f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.dim_station_enriched`
        ORDER BY station_code
        """
    )

    dq_geocoding = run_query(
        f"""
        SELECT *
        FROM `{PROJECT_ID}.{DATASET}.dq_reverse_geocoding_quality`
        """
    )

    return station_type_summary, station_fact, aq_weather, station_enriched, dq_geocoding


def section(title: str) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def page_header(title: str) -> None:
    st.markdown(
        f"""
        <div class="page-context">Università degli Studi di Milano-Bicocca</div>
        <div class="page-main-title">{title}</div>
        <div class="page-subtitle-meta">Data Management Project</div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, subtitle: str, accent: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value" style="--accent:{accent};">{value}</div>
            <div class="metric-sub">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def research_banner(rq_id: str, question: str) -> None:
    st.markdown(
        f"""
        <div class="rq-banner">
            <div class="rq-id">{rq_id}</div>
            <div class="rq-text">{question}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def answer_box(text: str) -> None:
    st.markdown(
        f"""
        <div class="answer-box">
            <div class="answer-label">Direct answer</div>
            <div class="answer-text">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def simple_note(text: str) -> None:
    st.markdown(f'<div class="note">{text}</div>', unsafe_allow_html=True)


def chart_title(title: str) -> None:
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)


def limit_chips(show_eu: str | None = None, show_who: str | None = None, show_info: str | None = None) -> None:
    parts = []
    if show_eu:
        parts.append(f'<span class="limit-chip chip-eu">{show_eu}</span>')
    if show_who:
        parts.append(f'<span class="limit-chip chip-who">{show_who}</span>')
    if show_info:
        parts.append(f'<span class="limit-chip chip-info">{show_info}</span>')
    if parts:
        st.markdown(f'<div class="limit-chip-row">{"".join(parts)}</div>', unsafe_allow_html=True)


def apply_filters(df: pd.DataFrame, years: list[int], station_types: list[str]) -> pd.DataFrame:
    out = df.copy()
    if "reporting_year" in out.columns and years:
        out = out[out["reporting_year"].isin(years)]
    if "station_type" in out.columns and station_types:
        out = out[out["station_type"].isin(station_types)]
    return out


def base_layout(fig: go.Figure, height: int = 420, hovermode: str = "x unified") -> go.Figure:
    fig.update_layout(
        height=height,
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=12, r=12, t=72, b=24),
        font=dict(family="Manrope, Arial", color=COLORS["ink"], size=12),
        title=dict(text=" ", font=dict(size=15, color=COLORS["ink"]), x=0.01, xanchor="left"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="left",
            x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
            title=dict(text=" "),
        ),
        legend_title_text=" ",
        hovermode=hovermode,
    )
    fig.update_xaxes(showgrid=False, zeroline=False, title_text=" ")
    fig.update_yaxes(showgrid=True, gridcolor="#EEF2F7", zeroline=False, title_text=" ")
    return fig


def add_limit_line(fig: go.Figure, y: float, color: str, dash: str = "dash") -> go.Figure:
    fig.add_hline(y=y, line_width=1.7, line_color=color, line_dash=dash, opacity=0.85)
    return fig


def render_chart(fig: go.Figure) -> None:
    fig.update_layout(title_text=" ", legend_title_text=" ")
    fig.for_each_trace(lambda trace: trace.update(legendgrouptitle_text=" "))
    st.plotly_chart(fig, use_container_width=True, config=PLOTLY_CONFIG)


def safe_mean(series: pd.Series) -> float:
    return float(series.mean()) if len(series.dropna()) else 0.0


def get_value(df: pd.DataFrame, station_type: str, year: int, metric: str) -> float | None:
    row = df[(df["station_type"] == station_type) & (df["reporting_year"] == year)]
    if row.empty:
        return None
    return float(row.iloc[0][metric])


try:
    summary, fact, aq_weather, station_enriched, dq_geocoding = load_data()
except DefaultCredentialsError as exc:
    fallback_path = os.path.join(os.path.expanduser("~"), "gcp-keys", "dlt-loader-key.json")
    st.error("Unable to load data from BigQuery because Google credentials are not configured.")
    st.code(
        "\n".join(
            [
                f'$env:GOOGLE_APPLICATION_CREDENTIALS = "{fallback_path}"',
                f'$env:GCP_PROJECT_ID = "{PROJECT_ID}"',
                '& "../.venv/Scripts/streamlit.exe" run "dashboard_streamlit_v2/app.py"',
            ]
        ),
        language="powershell",
    )
    st.caption(f"Expected fallback key path: {fallback_path}")
    st.exception(exc)
    st.stop()
except Exception as exc:
    st.error("Unable to load data from BigQuery. Check credentials and environment variables.")
    st.exception(exc)
    st.stop()

all_years = sorted(summary["reporting_year"].dropna().unique().tolist())
all_station_types = sorted(summary["station_type"].dropna().unique().tolist())

with st.sidebar:
    st.markdown("### Air Quality Torino")
    st.caption("Data Management Project")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        [
            "Executive Summary",
            "RQ1 - Traffic vs Background",
            "RQ2 - Temporal Evolution",
            "RQ3 - PM10 Exceedances",
            "RQ4 - Integration & Quality",
            "Conclusions",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**Filters**")
    years = st.multiselect("Reporting year", options=all_years, default=all_years)
    station_types = st.multiselect("Station type", options=all_station_types, default=all_station_types)

    st.markdown("---")
    st.caption(f"Project: {PROJECT_ID}")
    st.caption(f"Dataset: {DATASET}")

summary_f = apply_filters(summary, years, station_types)
fact_f = apply_filters(fact, years, station_types)
aq_weather_f = apply_filters(aq_weather, years, station_types)
station_enriched_f = (
    station_enriched[station_enriched["station_type"].isin(station_types)]
    if station_types
    else station_enriched
)

latest_year = int(summary_f["reporting_year"].max()) if len(summary_f) else int(summary["reporting_year"].max())
latest_snapshot = summary[summary["reporting_year"] == latest_year].copy()
dq_row = dq_geocoding.iloc[0]
latest_traffic_no2 = get_value(summary, "Traffic", latest_year, "avg_no2_annual_mean_ugm3") or 0
latest_background_no2 = get_value(summary, "Background", latest_year, "avg_no2_annual_mean_ugm3") or 0

st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">Università degli Studi di Milano-Bicocca · Data Management Project</div>
        <div class="hero-title">Air Quality Assessment in Torino</div>
        <div class="hero-subtitle">
            Annual PM10 and NO2 analysis across Traffic and Background monitoring stations in Torino,
            enriched with yearly weather indicators and reverse-geocoded station metadata.
            This dashboard is aligned with the updated project scope and answers the final research questions.
        </div>
        <div class="tag-row">
            <span class="tag">EEA DiscoData</span>
            <span class="tag">Open-Meteo API</span>
            <span class="tag">OSM / Nominatim</span>
            <span class="tag">BigQuery</span>
            <span class="tag">dlt</span>
            <span class="tag">dbt</span>
            <span class="tag">30 dbt tests passed</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if page == "Executive Summary":
    page_header("Executive Summary")
    section("Executive summary")
    simple_note(
        "The final project no longer evaluates anti-smog policies causally. Instead, it focuses on annual PM10 and NO2 indicators, "
        "Traffic vs Background station comparison, yearly weather enrichment, reverse geocoding and formal data-quality validation."
    )

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        metric_card("Air quality records", "669", "EEA annual statistics loaded", COLORS["blue"])
    with c2:
        metric_card("Weather records", "26328", "hourly observations from Open-Meteo", COLORS["cyan"])
    with c3:
        metric_card("Stations", "4", "Torino monitoring sites", COLORS["green"])
    with c4:
        metric_card("Research questions", "4", "final implemented RQs", COLORS["orange"])
    with c5:
        metric_card("dbt tests", "30 / 30", "all completed successfully", COLORS["red"])
    with c6:
        metric_card("Geocoding coverage", f"{dq_row['enrichment_coverage_pct']:.0f}%", "station enrichment coverage", COLORS["amber"])

    st.write("")
    section("Final project title and goal")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-label">Project title</div>
                <div style="font-size:1.2rem;font-weight:800;color:#0F172A;line-height:1.4;">
                    Air Quality Assessment in Torino through Integration of Environmental,
                    Meteorological and Spatial Enrichment Data
                </div>
                <div style="margin-top:12px;color:#334155;font-size:.9rem;line-height:1.7;">
                    The goal is to build a reproducible data-management pipeline for analyzing annual air-quality indicators in Torino.
                    The system integrates EEA air-quality statistics, Open-Meteo weather observations and reverse-geocoded station metadata,
                    covering acquisition, storage, transformation, enrichment, quality measurement and analytical reporting.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-label">Final analytical focus</div>
                <div style="display:grid;gap:10px;">
                    <div class="note"><b>RQ1</b>: Traffic vs Background annual concentration comparison</div>
                    <div class="note"><b>RQ2</b>: Temporal evolution from 2022 to 2024</div>
                    <div class="note"><b>RQ3</b>: PM10 exceedance days above 50 ug/m3</div>
                    <div class="note"><b>RQ4</b>: Weather and geocoding integration quality</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    section("Research questions")
    rq_cols = st.columns(4)
    rq_cards = [
        (COLORS["blue"], "RQ1 - Descriptive", "How do PM10 and NO2 annual concentrations differ between Traffic and Background stations during 2022-2024?"),
        (COLORS["cyan"], "RQ2 - Temporal", "How do annual PM10 and NO2 indicators evolve between 2022 and 2024 for different station types?"),
        (COLORS["red"], "RQ3 - Exceedance", "How do PM10 exceedance days above 50 ug/m3 vary across years and station types?"),
        (COLORS["green"], "RQ4 - Integration", "Can yearly weather indicators and reverse-geocoded station information be integrated with measurable quality?"),
    ]
    for col, (accent, title, body) in zip(rq_cols, rq_cards):
        with col:
            st.markdown(
                f"""
                <div class="mini-card" style="--mini-accent:{accent};">
                    <div class="mini-label">{title}</div>
                    <div class="mini-text">{body}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    section("End-to-end architecture")
    architecture = [
        ("1", "External sources", "EEA DiscoData\nOpen-Meteo API\nOSM / Nominatim"),
        ("2", "dlt ingestion", "3 Python pipelines\nraw BigQuery tables"),
        ("3", "dbt transformation", "staging models\nmart models\n30 schema tests"),
        ("4", "Analytical warehouse", "fact_air_quality_annual\nmart_station_type_year_summary\ndim_station_enriched"),
        ("5", "Dashboard", "RQ-driven analysis\npresentation-ready views"),
    ]
    arch_cols = st.columns([1, 0.18, 1, 0.18, 1, 0.18, 1, 0.18, 1])
    for idx, (icon, title, text) in enumerate(architecture):
        with arch_cols[idx * 2]:
            st.markdown(
                f"""
                <div class="architecture-card">
                    <div class="architecture-icon">{icon}</div>
                    <div class="architecture-title">{title}</div>
                    <div class="architecture-text">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if idx < len(architecture) - 1:
            with arch_cols[idx * 2 + 1]:
                st.markdown('<div class="architecture-arrow">&rarr;</div>', unsafe_allow_html=True)

    st.write("")
    section("Appendix from DM_Project.pdf")
    with st.expander("Show implemented data sources and acquisition strategy"):
        acquisition_df = pd.DataFrame(
            [
                ["Hourly weather observations", "Open-Meteo Historical API", "API via Python / dlt", "raw.weather_torino_hourly", "Meteorological context and yearly indicators"],
                ["Air-quality statistics", "EEA DiscoData AirQualityStatistics", "SQL / HTTP API via Python / dlt", "raw.air_quality_statistics_torino", "Main PM10 / NO2 and exceedance indicators"],
                ["Station address enrichment", "Nominatim / OpenStreetMap", "Reverse geocoding API via Python / dlt", "raw.station_reverse_geocoding", "Address enrichment and error measurement"],
            ],
            columns=["Dataset", "Provider", "Method", "Implemented asset", "Role"],
        )
        st.dataframe(acquisition_df, use_container_width=True, hide_index=True)

    with st.expander("Show final implemented roadmap"):
        roadmap_df = pd.DataFrame(
            [
                ["Phase 0", "Local environment setup", "Done", "Python, VS Code, Git, virtual environment, .gitignore"],
                ["Phase 1", "GCP + BigQuery setup and updated research design", "Done", "Project dm-torino-airquality, raw dataset, service account, auth"],
                ["Phase 2", "Open-Meteo ingestion", "Done", "26,328 records in raw.weather_torino_hourly"],
                ["Phase 3", "EEA DiscoData ingestion and exploratory analysis", "Done", "669 records in raw.air_quality_statistics_torino"],
                ["Phase 4", "dbt transformation layer", "Done", "Staging and mart models created successfully"],
                ["Phase 5", "Integration, enrichment and data quality", "Done", "Reverse geocoding quality metrics and 30 dbt tests passed"],
                ["Phase 6", "Final report, operational guide, PPT and optional dashboard", "In progress", "Final deliverables to be packaged"],
            ],
            columns=["Phase", "Objective", "Status", "Main evidence"],
        )
        st.dataframe(roadmap_df, use_container_width=True, hide_index=True)

    with st.expander("Show infrastructure, setup and troubleshooting"):
        infra_df = pd.DataFrame(
            [
                ["GCP project ID", "dm-torino-airquality"],
                ["Region / location", "europe-west8"],
                ["Initial dataset", "raw"],
                ["Service account", "dlt-loader"],
                ["Credential file", "C:/Users/Pc/gcp-keys/dlt-loader-key.json"],
                ["Authentication variable", "GOOGLE_APPLICATION_CREDENTIALS"],
            ],
            columns=["Component", "Final value / status"],
        )
        st.dataframe(infra_df, use_container_width=True, hide_index=True)
        st.code(
            """
gcloud auth login
gcloud config set project dm-torino-airquality
bq mk --location=europe-west8 --dataset raw
New-Item -ItemType Directory -Force -Path "$HOME\\gcp-keys"
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\\Users\\Pc\\gcp-keys\\dlt-loader-key.json"
            """.strip(),
            language="powershell",
        )
        troubleshooting_df = pd.DataFrame(
            [
                ["gcloud not recognized", "Installed the official Google Cloud SDK instead of the wrong pip package."],
                ["PowerShell execution policy blocked scripts", "Set CurrentUser execution policy to RemoteSigned."],
                ["Billing disabled", "Linked the GCP project to a billing account."],
                ["Bash syntax in PowerShell", "Used PowerShell-native single-line commands."],
            ],
            columns=["Issue", "Resolution"],
        )
        st.dataframe(troubleshooting_df, use_container_width=True, hide_index=True)

elif page == "RQ1 - Traffic vs Background":
    page_header("RQ1 - Traffic vs Background")
    research_banner(
        "Research Question 1 - Descriptive",
        "How do PM10 and NO2 annual concentrations differ between Traffic and Background monitoring stations in Torino during 2022-2024?",
    )

    no2_traffic = get_value(summary, "Traffic", latest_year, "avg_no2_annual_mean_ugm3") or 0
    no2_background = get_value(summary, "Background", latest_year, "avg_no2_annual_mean_ugm3") or 0
    pm10_traffic = get_value(summary, "Traffic", latest_year, "avg_pm10_annual_mean_ugm3") or 0
    pm10_background = get_value(summary, "Background", latest_year, "avg_pm10_annual_mean_ugm3") or 0

    section(f"Headline numbers for {latest_year}")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Traffic NO2", f"{no2_traffic:.2f}", "ug/m3 annual mean", COLORS["blue"])
    with c2:
        metric_card("Background NO2", f"{no2_background:.2f}", "ug/m3 annual mean", COLORS["orange"])
    with c3:
        metric_card("Traffic PM10", f"{pm10_traffic:.2f}", "ug/m3 annual mean", COLORS["blue"])
    with c4:
        metric_card("Background PM10", f"{pm10_background:.2f}", "ug/m3 annual mean", COLORS["orange"])

    st.write("")
    section("Station-type comparison")
    left, right = st.columns(2)
    with left:
        limit_chips("EU annual limit: NO2 = 40 ug/m3", "WHO AQG: NO2 = 10 ug/m3")
        chart_title("NO2 annual mean by station type")
        fig = px.bar(
            summary_f,
            x="reporting_year",
            y="avg_no2_annual_mean_ugm3",
            color="station_type",
            barmode="group",
            text="avg_no2_annual_mean_ugm3",
            color_discrete_map=TYPE_COLORS,
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_line_width=0)
        add_limit_line(fig, EU_NO2, COLORS["red"], "dash")
        add_limit_line(fig, WHO_NO2, COLORS["amber"], "dot")
        fig = base_layout(fig, 430)
        fig.update_xaxes(title_text=" ", type="category")
        fig.update_yaxes(title="ug/m3", range=[0, max(60, summary_f["avg_no2_annual_mean_ugm3"].max() * 1.25 if len(summary_f) else 60)])
        render_chart(fig)
    with right:
        limit_chips("EU annual limit: PM10 = 40 ug/m3", "WHO AQG: PM10 = 15 ug/m3")
        chart_title("PM10 annual mean by station type")
        fig = px.bar(
            summary_f,
            x="reporting_year",
            y="avg_pm10_annual_mean_ugm3",
            color="station_type",
            barmode="group",
            text="avg_pm10_annual_mean_ugm3",
            color_discrete_map=TYPE_COLORS,
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_line_width=0)
        add_limit_line(fig, EU_PM10, COLORS["red"], "dash")
        add_limit_line(fig, WHO_PM10, COLORS["amber"], "dot")
        fig = base_layout(fig, 430)
        fig.update_xaxes(title_text=" ", type="category")
        fig.update_yaxes(title="ug/m3", range=[0, max(46, summary_f["avg_pm10_annual_mean_ugm3"].max() * 1.25 if len(summary_f) else 46)])
        render_chart(fig)

    section("Evidence table")
    rq1_table = summary_f.rename(
        columns={
            "station_type": "Station type",
            "reporting_year": "Year",
            "avg_pm10_annual_mean_ugm3": "Avg PM10",
            "avg_no2_annual_mean_ugm3": "Avg NO2",
            "avg_pm10_days_above_50": "Avg PM10 days above 50",
            "n_stations": "Stations",
        }
    )
    st.dataframe(
        rq1_table.style.format({
            "Avg PM10": "{:.2f}",
            "Avg NO2": "{:.2f}",
            "Avg PM10 days above 50": "{:.1f}",
        }),
        use_container_width=True,
        hide_index=True,
    )

    no2_gap_latest = no2_traffic - no2_background
    answer_box(
        f"Traffic stations show higher annual PM10 and NO2 concentrations than Background stations in every observed year. "
        f"For example, in {latest_year} the NO2 annual mean is {no2_traffic:.2f} ug/m3 for Traffic versus {no2_background:.2f} ug/m3 for Background, "
        f"a gap of {no2_gap_latest:.2f} ug/m3."
    )

elif page == "RQ2 - Temporal Evolution":
    page_header("RQ2 - Temporal Evolution")
    research_banner(
        "Research Question 2 - Temporal",
        "How do annual PM10 and NO2 indicators evolve between 2022 and 2024 for different station types?",
    )

    section("Temporal trends")
    left, right = st.columns(2)
    with left:
        limit_chips("EU annual limit: NO2 = 40 ug/m3", "WHO AQG: NO2 = 10 ug/m3")
        chart_title("NO2 annual mean over time")
        fig = px.line(
            summary_f,
            x="reporting_year",
            y="avg_no2_annual_mean_ugm3",
            color="station_type",
            markers=True,
            color_discrete_map=TYPE_COLORS,
        )
        fig.update_traces(line=dict(width=3.4), marker=dict(size=10, line=dict(width=2, color="#FFFFFF")))
        add_limit_line(fig, EU_NO2, COLORS["red"], "dash")
        add_limit_line(fig, WHO_NO2, COLORS["amber"], "dot")
        fig = base_layout(fig, 420)
        fig.update_xaxes(title_text=" ", dtick=1)
        fig.update_yaxes(title="ug/m3", range=[0, max(60, summary_f["avg_no2_annual_mean_ugm3"].max() * 1.25 if len(summary_f) else 60)])
        render_chart(fig)
    with right:
        limit_chips("EU annual limit: PM10 = 40 ug/m3", "WHO AQG: PM10 = 15 ug/m3")
        chart_title("PM10 annual mean over time")
        fig = px.line(
            summary_f,
            x="reporting_year",
            y="avg_pm10_annual_mean_ugm3",
            color="station_type",
            markers=True,
            color_discrete_map=TYPE_COLORS,
        )
        fig.update_traces(line=dict(width=3.4), marker=dict(size=10, line=dict(width=2, color="#FFFFFF")))
        add_limit_line(fig, EU_PM10, COLORS["red"], "dash")
        add_limit_line(fig, WHO_PM10, COLORS["amber"], "dot")
        fig = base_layout(fig, 420)
        fig.update_xaxes(title_text=" ", dtick=1)
        fig.update_yaxes(title="ug/m3", range=[0, max(46, summary_f["avg_pm10_annual_mean_ugm3"].max() * 1.22 if len(summary_f) else 46)])
        render_chart(fig)

    section("Year-over-year changes")
    yoy = summary_f.sort_values(["station_type", "reporting_year"]).copy()
    yoy["Delta PM10"] = yoy.groupby("station_type")["avg_pm10_annual_mean_ugm3"].diff()
    yoy["Delta NO2"] = yoy.groupby("station_type")["avg_no2_annual_mean_ugm3"].diff()
    yoy["Delta PM10 %"] = yoy.groupby("station_type")["avg_pm10_annual_mean_ugm3"].pct_change() * 100
    yoy["Delta NO2 %"] = yoy.groupby("station_type")["avg_no2_annual_mean_ugm3"].pct_change() * 100
    yoy = yoy.dropna(subset=["Delta PM10", "Delta NO2"])
    if len(yoy):
        yoy_display = yoy.rename(
            columns={
                "station_type": "Station type",
                "reporting_year": "Year",
                "avg_pm10_annual_mean_ugm3": "PM10 mean",
                "avg_no2_annual_mean_ugm3": "NO2 mean",
            }
        )
        st.dataframe(
            yoy_display[["Station type", "Year", "PM10 mean", "NO2 mean", "Delta PM10", "Delta NO2", "Delta PM10 %", "Delta NO2 %"]].style.format(
                {
                    "PM10 mean": "{:.2f}",
                    "NO2 mean": "{:.2f}",
                    "Delta PM10": "{:+.2f}",
                    "Delta NO2": "{:+.2f}",
                    "Delta PM10 %": "{:+.1f}%",
                    "Delta NO2 %": "{:+.1f}%",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Select at least two years to display year-over-year changes.")

    answer_box(
        "Annual indicators change visibly between 2022 and 2024. PM10 decreases for both Traffic and Background station types across the period analyzed, "
        "while NO2 also declines but remains comparatively high at Traffic stations, close to the EU annual limit."
    )

elif page == "RQ3 - PM10 Exceedances":
    page_header("RQ3 - PM10 Exceedances")
    research_banner(
        "Research Question 3 - Exceedance analysis",
        "How do PM10 exceedance days above 50 ug/m3 vary across years and station types?",
    )

    section("Observed exceedance evidence")
    grid_cols = st.columns(6)
    evidence_rows = summary[(summary["reporting_year"].isin([2022, 2023, 2024]))].sort_values(["reporting_year", "station_type"]).copy()
    for col, (_, row) in zip(grid_cols, evidence_rows.iterrows()):
        station_type = row["station_type"]
        accent = TYPE_COLORS.get(station_type, COLORS["blue"])
        exceeds = float(row["avg_pm10_days_above_50"]) > EU_PM10_DAYS
        badge_class = "bad" if exceeds else "good"
        badge_text = "exceeds EU" if exceeds else "below EU"
        with col:
            st.markdown(
                f"""
                <div class="fact-grid-card" style="--accent:{accent};">
                    <div class="fact-grid-year">{int(row['reporting_year'])}</div>
                    <div class="fact-grid-type">{station_type}</div>
                    <div class="fact-grid-value">{float(row['avg_pm10_days_above_50']):.1f}</div>
                    <div class="fact-grid-caption">days above 50 ug/m3</div>
                    <div class="status-badge {badge_class}">{badge_text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    section("PM10 exceedance days by year and station type")
    limit_chips(show_eu="EU daily exceedance maximum: 35 days / year")
    chart_title("Days above 50 ug/m3 by year and station type")
    fig = px.bar(
        summary_f,
        x="avg_pm10_days_above_50",
        y="reporting_year",
        color="station_type",
        barmode="group",
        orientation="h",
        text="avg_pm10_days_above_50",
        color_discrete_map=TYPE_COLORS,
    )
    fig.update_traces(texttemplate="%{text:.1f}", textposition="outside", marker_line_width=0)
    fig.add_vline(x=EU_PM10_DAYS, line_width=1.7, line_color=COLORS["red"], line_dash="dash")
    fig = base_layout(fig, 430, "closest")
    fig.update_xaxes(title="Days above 50 ug/m3", range=[0, max(90, summary_f["avg_pm10_days_above_50"].max() * 1.2 if len(summary_f) else 90)])
    fig.update_yaxes(title="Year", type="category")
    render_chart(fig)

    section("Per-station detail")
    station_order = sorted(fact_f["station_code"].dropna().unique().tolist())
    exceedance_detail = fact_f.copy()
    exceedance_detail["Year label"] = exceedance_detail["reporting_year"].astype(str)
    limit_chips(show_eu="Red dashed line: EU maximum = 35 days / year")
    chart_title("PM10 exceedance days by Torino station")
    fig = px.bar(
        exceedance_detail,
        x="pm10_days_above_50",
        y="station_code",
        color="Year label",
        barmode="group",
        orientation="h",
        text="pm10_days_above_50",
        color_discrete_map={"2022": "#3B82F6", "2023": "#F97316", "2024": "#8B5CF6"},
        category_orders={"station_code": station_order, "Year label": ["2022", "2023", "2024"]},
    )
    fig.update_traces(texttemplate="%{text:.0f}", textposition="outside", marker_line_width=0)
    fig.add_vline(x=EU_PM10_DAYS, line_width=1.7, line_color=COLORS["red"], line_dash="dash")
    fig = base_layout(fig, 450, "closest")
    fig.add_annotation(
        x=EU_PM10_DAYS,
        y=1.06,
        xref="x",
        yref="paper",
        text="EU limit: 35 days",
        showarrow=False,
        font=dict(size=11, color=COLORS["red"]),
        bgcolor="#FFFFFF",
    )
    fig.update_xaxes(title_text=" ")
    fig.update_yaxes(title_text=" ", categoryorder="array", categoryarray=station_order)
    render_chart(fig)

    answer_box(
        "PM10 days above 50 ug/m3 are higher for Traffic stations in all observed years: 71.5 vs 47.5 in 2022, 58.0 vs 28.0 in 2023, and 44.5 vs 39.0 in 2024. "
        "Traffic stations exceed the EU maximum of 35 days every year, while Background stations exceed it in 2022 and 2024 but stay below it in 2023."
    )

elif page == "RQ4 - Integration & Quality":
    page_header("RQ4 - Integration & Quality")
    research_banner(
        "Research Question 4 - Integration and enrichment",
        "Can yearly weather indicators and reverse-geocoded station information be integrated into the analytical warehouse with measurable quality?",
    )

    section("Integration quality metrics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Weather enrichment success", f"{safe_mean(aq_weather_f['weather_enrichment_success']) * 100:.0f}%", "successful station-years", COLORS["green"])
    with c2:
        metric_card("Geocoding coverage", f"{dq_row['enrichment_coverage_pct']:.1f}%", "reverse-geocoded stations", COLORS["green"])
    with c3:
        metric_card("Average distance", f"{dq_row['avg_distance_m']:.2f} m", "mean geocoding error", COLORS["cyan"])
    with c4:
        metric_card("Max distance", f"{dq_row['max_distance_m']:.2f} m", "largest geocoding error", COLORS["orange"])

    st.write("")
    section("Geographic integration by station")
    geo_cols = [
        "station_code",
        "station_type",
        "station_area",
        "city",
        "latitude",
        "longitude",
        "postcode",
        "display_name",
    ]
    geo_available = [column for column in geo_cols if column in station_enriched_f.columns]
    geo_table = station_enriched_f[geo_available].rename(
        columns={
            "station_code": "Station ID",
            "station_type": "Station type",
            "station_area": "Station area",
            "city": "City",
            "latitude": "Latitude",
            "longitude": "Longitude",
            "postcode": "Postcode",
            "display_name": "Integrated address",
        }
    )
    st.dataframe(
        geo_table.style.format({"Latitude": "{:.5f}", "Longitude": "{:.5f}"}),
        use_container_width=True,
        hide_index=True,
        height=420,
    )

    st.write("")
    section("Geocoding quality measurements")
    left, right = st.columns([0.95, 1.05])
    with left:
        limit_chips(show_info="Target quality reference: within 100 m")
        chart_title("Geocoded distance by station")
        fig = px.bar(
            station_enriched_f.sort_values("distance_original_geocoded_m"),
            x="station_code",
            y="distance_original_geocoded_m",
            color="station_type",
            text="distance_original_geocoded_m",
            color_discrete_map=TYPE_COLORS,
        )
        fig.update_traces(texttemplate="%{text:.2f}", textposition="outside", marker_line_width=0)
        fig.add_hline(y=100, line_width=1.7, line_color=COLORS["amber"], line_dash="dash")
        fig = base_layout(fig, 390)
        fig.update_xaxes(title_text=" ", type="category")
        fig.update_yaxes(title="Distance (m)", range=[0, max(110, station_enriched_f["distance_original_geocoded_m"].max() * 1.25 if len(station_enriched_f) else 110)])
        render_chart(fig)
    with right:
        station_cols = [
            "station_code",
            "station_type",
            "latitude",
            "longitude",
            "city",
            "postcode",
            "display_name",
            "distance_original_geocoded_m",
        ]
        available_cols = [c for c in station_cols if c in station_enriched_f.columns]
        display = station_enriched_f[available_cols].rename(
            columns={
                "station_code": "Station ID",
                "station_type": "Station type",
                "latitude": "Latitude",
                "longitude": "Longitude",
                "city": "City",
                "postcode": "Postcode",
                "display_name": "Address",
                "distance_original_geocoded_m": "Geocoded distance",
            }
        )
        st.dataframe(
            display.style.format({"Latitude": "{:.5f}", "Longitude": "{:.5f}", "Geocoded distance": "{:.2f}"}),
            use_container_width=True,
            hide_index=True,
            height=390,
        )

    with st.expander("Show data-quality and implemented assets evidence"):
        st.markdown(
            """
            - 30 dbt tests completed successfully.
            - Weather enrichment succeeded for all station-year records.
            - Reverse-geocoding enrichment achieved 100% station coverage.
            - Final implemented assets include three dlt pipelines, raw BigQuery tables, dbt staging models and dbt mart models.
            """
        )

    answer_box(
        f"Yes. Weather enrichment succeeded for all station-year records and reverse-geocoded station enrichment achieved 100% station coverage. "
        f"The maximum geocoding distance is {dq_row['max_distance_m']:.2f} m, and the dbt quality layer completed successfully with 30 tests passed."
    )

else:
    page_header("Conclusions")
    section("Final answers to the research questions")
    st.markdown(
        f"""
        <div class="rq-grid">
            <div class="rq-card">
                <div class="metric-label">RQ1</div>
                <div class="rq-card-title">Traffic stations show higher PM10 and NO2 annual means than Background stations.</div>
                <div class="rq-card-answer note">Evidence: in {latest_year}, NO2 is {latest_traffic_no2:.2f} ug/m3 for Traffic versus {latest_background_no2:.2f} ug/m3 for Background.</div>
            </div>
            <div class="rq-card">
                <div class="metric-label">RQ2</div>
                <div class="rq-card-title">PM10 decreases between 2022 and 2024 for both station types.</div>
                <div class="rq-card-answer note">Evidence: the temporal trend is downward for both Traffic and Background stations across the full analysis period.</div>
            </div>
            <div class="rq-card">
                <div class="metric-label">RQ3</div>
                <div class="rq-card-title">Traffic stations record more PM10 exceedance days in every observed year.</div>
                <div class="rq-card-answer note">Evidence: 71.5 vs 47.5 in 2022, 58.0 vs 28.0 in 2023, 44.5 vs 39.0 in 2024.</div>
            </div>
            <div class="rq-card">
                <div class="metric-label">RQ4</div>
                <div class="rq-card-title">Weather and geocoding enrichment were integrated successfully with measurable quality.</div>
                <div class="rq-card-answer note">Evidence: weather join success = 100%, geocoding coverage = {dq_row['enrichment_coverage_pct']:.0f}%, max distance = {dq_row['max_distance_m']:.2f} m.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    section("Compliance snapshot")
    comp1, comp2, comp3 = st.columns(3)
    with comp1:
        st.markdown(
            f"""
            <div class="panel">
                <div class="metric-label">NO2 annual mean</div>
                <div class="note"><b>Traffic</b>: near or slightly above the EU 40 ug/m3 limit in 2022-2024.</div>
                <div class="note" style="margin-top:10px;"><b>Background</b>: compliant with the EU limit in all years.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with comp2:
        st.markdown(
            f"""
            <div class="panel">
                <div class="metric-label">PM10 annual mean</div>
                <div class="note"><b>Traffic</b>: compliant with the EU annual limit in all years.</div>
                <div class="note" style="margin-top:10px;"><b>Background</b>: compliant with the EU annual limit in all years.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with comp3:
        st.markdown(
            f"""
            <div class="panel">
                <div class="metric-label">PM10 exceedance days</div>
                <div class="note"><b>Traffic</b>: exceeds the EU maximum of 35 days in all three years.</div>
                <div class="note" style="margin-top:10px;"><b>Background</b>: exceeds in 2022 and 2024, below threshold in 2023.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    section("WHO air-quality guideline gap")
    st.markdown(
        f"""
        <div class="panel">
            <div class="note"><b>NO2</b>: all stations exceed the WHO AQG 2021 threshold of 10 ug/m3 in every observed year.</div>
            <div class="note" style="margin-top:10px;"><b>PM10</b>: all stations exceed the WHO AQG 2021 threshold of 15 ug/m3 in every observed year.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")
    section("Final implemented assets")
    assets_left, assets_right = st.columns(2)
    with assets_left:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-label">Pipelines and warehouse</div>
                <div class="note"><b>dlt pipelines</b>: open_meteo.py, eea_discodata.py, station_reverse_geocoding.py</div>
                <div class="note" style="margin-top:10px;"><b>Raw BigQuery tables</b>: raw.weather_torino_hourly, raw.air_quality_statistics_torino, raw.station_reverse_geocoding</div>
                <div class="note" style="margin-top:10px;"><b>dbt staging</b>: stg_weather_torino_hourly, stg_air_quality_statistics_torino, stg_station_reverse_geocoding</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with assets_right:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-label">Analytical layer and quality</div>
                <div class="note"><b>dbt marts</b>: dim_station, fact_air_quality_annual, mart_station_type_year_summary, fact_weather_yearly, mart_air_quality_weather_yearly, dim_station_enriched, dq_reverse_geocoding_quality</div>
                <div class="note" style="margin-top:10px;"><b>Query files</b>: annual means, station type summary, PM10 exceedances, station-year KPI summaries</div>
                <div class="note" style="margin-top:10px;"><b>Quality evidence</b>: 30 dbt tests completed successfully</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    section("Current project status and next steps")
    status_left, status_right = st.columns(2)
    with status_left:
        simple_note(
            "The technical core is complete: acquisition, storage, dbt transformations, integration / enrichment, "
            "error measurement and data quality are implemented."
        )
    with status_right:
        simple_note(
            "The remaining work is documentation packaging: final report, PowerPoint presentation, operational guide and optional dashboard refinement."
        )

st.markdown(
    """
    <p class="footer-note">
        Data Management Project · Università degli Studi di Milano-Bicocca · Sources: EEA DiscoData, Open-Meteo, OSM/Nominatim · Stack: dlt, dbt, BigQuery, Streamlit, Plotly
    </p>
    """,
    unsafe_allow_html=True,
)


