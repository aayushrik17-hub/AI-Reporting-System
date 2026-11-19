

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import streamlit as st


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"

REPORTS_DIR = OUTPUT_DIR / "reports"
CHARTS_DIR = OUTPUT_DIR / "charts"
PRESENTATIONS_DIR = OUTPUT_DIR / "presentations"

UPLOAD_FILE = DATA_DIR / "sales_data.csv"

CLEANED_FILE = OUTPUT_DIR / "cleaned_data.csv"
EDA_FILE = REPORTS_DIR / "eda_report.json"
INSIGHTS_FILE = REPORTS_DIR / "ai_insights.json"
WORD_FILE = REPORTS_DIR / "executive_summary.docx"
PPT_FILE = PRESENTATIONS_DIR / "business_performance_report.pptx"


# ==================================================
# 2. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Reporting System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================================================
# 3. CUSTOM THEME
# ==================================================

st.markdown("""
<style>

.stApp {
    background-color: #F5F6F8;
}

.block-container {
    max-width: 1450px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}

[data-testid="stSidebar"] {
    background-color: #202D3B;
}

[data-testid="stSidebar"] * {
    color: #F4F5F7;
}

.app-title {
    font-size: 31px;
    font-weight: 750;
    color: #263D55;
    margin-bottom: 2px;
}

.app-subtitle {
    font-size: 14px;
    color: #778391;
    margin-bottom: 20px;
}

.section-title {
    color: #263D55;
    font-size: 21px;
    font-weight: 700;
    margin-top: 12px;
    margin-bottom: 12px;
}

.insight-card {
    background-color: #FFFFFF;
    border: 1px solid #E3E8ED;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 12px;
    color: #344354;
    line-height: 1.6;
}

.small-label {
    color: #7A8794;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-value {
    color: #315D82;
    font-size: 27px;
    font-weight: 750;
    margin-top: 7px;
}

div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E3E8ED;
    padding: 18px;
    border-radius: 12px;
}

div[data-testid="stMetricLabel"] {
    color: #687786;
}

div[data-testid="stMetricValue"] {
    color: #315D82;
    font-weight: 700;
}

div.stButton > button {
    background-color: #315D82;
    color: white;
    border-radius: 8px;
    border: none;
    min-height: 42px;
}

div.stButton > button:hover {
    background-color: #47799F;
    color: white;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 15px;
}

.stTabs [data-baseweb="tab"] {
    height: 45px;
    font-weight: 600;
}

hr {
    border-color: #E2E7EC;
}

</style>
""", unsafe_allow_html=True)


# ==================================================
# 4. HELPER FUNCTIONS
# ==================================================

def load_json(file_path):

    if not file_path.exists():
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return None


def normalize_key(key):

    return (
        str(key).lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


def find_section(data, names):

    names = {normalize_key(name) for name in names}

    if isinstance(data, dict):

        for key, value in data.items():

            if normalize_key(key) in names:
                return value

        for value in data.values():

            result = find_section(value, names)

            if result is not None:
                return result

    elif isinstance(data, list):

        for item in data:

            result = find_section(item, names)

            if result is not None:
                return result

    return None


def find_metric(data, names):

    if not isinstance(data, dict):
        return None

    names = {normalize_key(name) for name in names}

    for key, value in data.items():

        if normalize_key(key) in names:
            return value

    return None


def format_number(value):

    if value is None:
        return "N/A"

    try:
        return f"{float(value):,.2f}"

    except (ValueError, TypeError):
        return str(value)


def get_kpis(eda):

    result = find_section(
        eda,
        ["kpis", "key_performance_indicators"]
    )

    return result if isinstance(result, dict) else {}


def get_chart_files():

    if not CHARTS_DIR.exists():
        return []

    return sorted([
        file for file in CHARTS_DIR.iterdir()
        if file.suffix.lower() in [
            ".png", ".jpg", ".jpeg"
        ]
    ])


def readable_title(filename):

    return filename.stem.replace("_", " ").title()


def show_insight_section(title, items):

    st.markdown(f"### {title}")

    if not items:
        st.caption("No information available.")

    elif isinstance(items, list):

        for item in items:

            st.markdown(
                f'<div class="insight-card">{item}</div>',
                unsafe_allow_html=True
            )

    else:

        st.markdown(
            f'<div class="insight-card">{items}</div>',
            unsafe_allow_html=True
        )


# ==================================================
# 5. SIDEBAR NAVIGATION
# ==================================================

with st.sidebar:

    st.markdown("## 📊 AI Reporting")
    st.caption("Business Intelligence Platform")

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Dashboard",
            "Data & Pipeline",
            "Business Insights",
            "Reports & Downloads"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("### Project Overview")

    st.caption("Python | Pandas | Streamlit")
    st.caption("Data Analytics | Business Intelligence")
    st.caption("Automated Reporting")

    st.divider()

    st.caption("AI Reporting System · Portfolio Project")


# ==================================================
# 6. LOAD EXISTING REPORTS
# ==================================================

eda_report = load_json(EDA_FILE)
insights = load_json(INSIGHTS_FILE)

kpis = get_kpis(eda_report) if eda_report else {}

chart_files = get_chart_files()


# ==================================================
# 7. APPLICATION HEADER
# ==================================================

st.markdown(
    '<div class="app-title">AI Reporting System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">'
    'Automated business analytics, performance monitoring '
    'and report generation'
    '</div>',
    unsafe_allow_html=True
)


# ==================================================
# 8. DASHBOARD PAGE
# ==================================================

if page == "Dashboard":

    st.markdown(
        '<div class="section-title">Business Performance Overview</div>',
        unsafe_allow_html=True
    )

    if not eda_report or not kpis:

        st.info(
            "No completed analysis is available. "
            "Go to Data & Pipeline to upload a dataset "
            "and generate your reports."
        )

    else:

        # KPI extraction

        revenue = find_metric(
            kpis,
            ["total_sales", "total_revenue", "revenue"]
        )

        orders = find_metric(
            kpis,
            ["total_orders", "orders", "unique_orders"]
        )

        aov = find_metric(
            kpis,
            ["average_order_value", "avg_order_value", "aov"]
        )

        quantity = find_metric(
            kpis,
            ["total_quantity", "quantity_sold", "total_units"]
        )

        st.caption("Key Performance Indicators")

        # KPI cards

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Total Revenue", format_number(revenue))
        c2.metric("Total Orders", format_number(orders))
        c3.metric("Average Order Value", format_number(aov))
        c4.metric("Quantity Sold", format_number(quantity))

        st.divider()

        # Charts

        st.markdown("### Sales Analytics")

        if chart_files:

            for i in range(0, len(chart_files), 2):

                col1, col2 = st.columns(2)

                with col1:

                    st.markdown(
                        f"**{readable_title(chart_files[i])}**"
                    )

                    st.image(
                        str(chart_files[i]),
                        use_container_width=True
                    )

                if i + 1 < len(chart_files):

                    with col2:

                        st.markdown(
                            f"**{readable_title(chart_files[i + 1])}**"
                        )

                        st.image(
                            str(chart_files[i + 1]),
                            use_container_width=True
                        )

        else:

            st.info("No charts available. Run the analysis pipeline.")

        st.divider()

        # Business highlights

        st.markdown("### Business Highlights")

        if insights:

            summary = insights.get(
                "executive_summary",
                "No executive summary available."
            )

            st.markdown(
                f'<div class="insight-card">{summary}</div>',
                unsafe_allow_html=True
            )

            col1, col2 = st.columns(2)

            with col1:

                findings = insights.get("key_findings", [])

                show_insight_section(
                    "Key Findings",
                    findings[:3]
                )

            with col2:

                recommendations = insights.get(
                    "recommendations",
                    []
                )

                st.markdown("### Priority Recommendations")

                for item in recommendations[:3]:

                    if isinstance(item, dict):

                        st.markdown(
                            f'<div class="insight-card">'
                            f'<b>{item.get("action", "")}</b><br>'
                            f'{item.get("reason", "")}<br>'
                            f'<small>Priority: '
                            f'{item.get("priority", "N/A")}</small>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                    else:

                        st.write(item)

        else:

            st.info("Generate business insights to view highlights.")


# ==================================================
# 9. DATA & PIPELINE PAGE
# ==================================================

elif page == "Data & Pipeline":

    st.markdown("### Upload and Analyze Your Dataset")

    st.write(
        "Upload a CSV or Excel file to start the automated "
        "data preparation and reporting workflow."
    )

    uploaded_file = st.file_uploader(
        "Choose your dataset",
        type=["csv", "xlsx", "xls"]
    )

    preview_df = None

    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(".csv"):
                preview_df = pd.read_csv(uploaded_file)

            else:
                preview_df = pd.read_excel(uploaded_file)

            st.success(
                f"Successfully uploaded: {uploaded_file.name}"
            )

            st.markdown("#### Dataset Preview")

            st.dataframe(
                preview_df.head(10),
                use_container_width=True,
                hide_index=True
            )

            c1, c2, c3 = st.columns(3)

            c1.metric("Rows", f"{len(preview_df):,}")
            c2.metric("Columns", f"{len(preview_df.columns):,}")
            c3.metric(
                "Missing Values",
                f"{preview_df.isnull().sum().sum():,}"
            )

        except Exception as error:

            st.error(f"Unable to read dataset: {error}")

            preview_df = None

    st.divider()

    st.markdown("### Generate Reports")

    st.caption(
        "The pipeline runs data cleaning, EDA, local business "
        "insights, executive summary and PowerPoint generation."
    )

    if uploaded_file is not None and preview_df is not None:

        if st.button(
            "Generate Business Reports",
            type="primary",
            use_container_width=True
        ):

            try:

                DATA_DIR.mkdir(parents=True, exist_ok=True)
                REPORTS_DIR.mkdir(parents=True, exist_ok=True)
                CHARTS_DIR.mkdir(parents=True, exist_ok=True)
                PRESENTATIONS_DIR.mkdir(parents=True, exist_ok=True)

                # Save uploaded file in the expected input format.

                preview_df.to_csv(
                    UPLOAD_FILE,
                    index=False
                )

                pipeline = [
                    ("Data Cleaning", "data_loader.py"),
                    ("Exploratory Data Analysis", "data_analysis.py"),
                    ("Business Insights", "ai_insights.py"),
                    ("Executive Summary", "executive_summary.py"),
                    ("PowerPoint Generation", "presentation_generator.py")
                ]

                success = True

                with st.status(
                    "Generating your reports...",
                    expanded=True
                ) as status:

                    for stage, script in pipeline:

                        st.write(f"Running: {stage}")

                        script_path = BASE_DIR / "src" / script

                        if not script_path.exists():

                            st.error(f"Missing script: {script}")
                            success = False
                            break

                        result = subprocess.run(
                            [
                                sys.executable,
                                str(script_path)
                            ],
                            cwd=str(BASE_DIR),
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=300
                        )

                        if result.returncode != 0:

                            st.error(f"{stage} failed.")

                            st.code(
                                result.stderr or result.stdout
                            )

                            success = False
                            break

                        st.write(f"Completed: {stage}")

                    if success:

                        status.update(
                            label="All reports generated successfully!",
                            state="complete",
                            expanded=False
                        )

                    else:

                        status.update(
                            label="Pipeline execution failed.",
                            state="error"
                        )

                st.session_state["pipeline_complete"] = success

                if success:

                    st.success(
                        "Your business reports are ready."
                    )

                    st.cache_data.clear()

                    st.rerun()

            except subprocess.TimeoutExpired:

                st.error(
                    "A pipeline stage exceeded five minutes. "
                    "Check the Python scripts."
                )

            except Exception as error:

                st.error(f"Pipeline error: {error}")

    else:

        st.info("Upload a dataset to activate report generation.")


# ==================================================
# 10. BUSINESS INSIGHTS PAGE
# ==================================================

elif page == "Business Insights":

    st.markdown("### Business Insights and Recommendations")

    if not insights:

        st.info(
            "No business insights available. "
            "Generate reports from the Data & Pipeline page."
        )

    else:

        # Executive summary

        st.markdown("#### Executive Summary")

        st.markdown(
            f'<div class="insight-card">'
            f'{insights.get("executive_summary", "Not available")}'
            f'</div>',
            unsafe_allow_html=True
        )

        # Insight categories

        tab1, tab2, tab3, tab4 = st.tabs([
            "Key Findings",
            "Positive Trends",
            "Areas of Concern",
            "Opportunities"
        ])

        with tab1:

            show_insight_section(
                "Key Findings",
                insights.get("key_findings", [])
            )

        with tab2:

            show_insight_section(
                "Positive Trends",
                insights.get("positive_trends", [])
            )

        with tab3:

            show_insight_section(
                "Areas of Concern",
                insights.get("areas_of_concern", [])
            )

        with tab4:

            show_insight_section(
                "Business Opportunities",
                insights.get("business_opportunities", [])
            )

        st.divider()

        # Recommendations

        st.markdown("### Business Recommendations")

        recommendations = insights.get("recommendations", [])

        if recommendations:

            for index, item in enumerate(recommendations, start=1):

                if isinstance(item, dict):

                    with st.container(border=True):

                        st.markdown(
                            f"**{index}. {item.get('action', 'Recommendation')}**"
                        )

                        st.write(
                            item.get("reason", "No reason provided.")
                        )

                        priority = item.get("priority", "Not specified")

                        st.caption(f"Priority: {priority}")

                else:

                    st.write(f"{index}. {item}")

        # Data limitations

        with st.expander("Review Data Limitations"):

            show_insight_section(
                "Data Limitations",
                insights.get("data_limitations", [])
            )


# ==================================================
# 11. REPORTS AND DOWNLOADS PAGE
# ==================================================

elif page == "Reports & Downloads":

    st.markdown("### Download Your Reports")

    st.write(
        "Download the generated datasets, analytical reports "
        "and business presentations."
    )

    download_files = [
        (
            "Cleaned Dataset",
            CLEANED_FILE,
            "text/csv"
        ),
        (
            "EDA Report",
            EDA_FILE,
            "application/json"
        ),
        (
            "Business Insights",
            INSIGHTS_FILE,
            "application/json"
        ),
        (
            "Executive Summary (Word)",
            WORD_FILE,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ),
        (
            "Business Presentation (PowerPoint)",
            PPT_FILE,
            "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
    ]

    available_count = sum(
        file_path.exists()
        for _, file_path, _ in download_files
    )

    st.metric("Available Reports", available_count)

    st.divider()

    for label, file_path, mime_type in download_files:

        col1, col2 = st.columns([3, 1])

        with col1:

            st.markdown(f"**{label}**")

            if file_path.exists():
                st.caption(file_path.name)
            else:
                st.caption("Not generated yet")

        with col2:

            if file_path.exists():

                with open(file_path, "rb") as file:

                    st.download_button(
                        "Download",
                        data=file.read(),
                        file_name=file_path.name,
                        mime=mime_type,
                        key=f"download_{file_path.name}",
                        use_container_width=True
                    )

            else:

                st.button(
                    "Unavailable",
                    disabled=True,
                    key=f"unavailable_{file_path.name}",
                    use_container_width=True
                )

        st.divider()


# ==================================================
# 12. FOOTER
# ==================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#87919D;
        font-size:12px;
        padding:20px;
    ">
        AI Reporting System · Python · Pandas · Streamlit
        <br>
        Automated Business Analytics and Reporting
    </div>
    """,
    unsafe_allow_html=True
)
