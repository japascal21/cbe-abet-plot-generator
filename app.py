
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# --- Streamlit page config ---
st.set_page_config(
    page_title="CBE ABET Plot Generator",
    page_icon="📊",
    layout="wide"
)

# --- Page layout / header ---
st.markdown(
    """
    <h1 style="text-align:center; margin-bottom:0;">CBE ABET Plot Generator</h1>
    <p style="text-align:center; font-size:0.95rem; margin-top:0.2rem;">
    Upload grade data &mdash; get a clean, UConn-themed attainment bar chart and ABET-ready narrative text.
    </p>
    <hr>
    """,
    unsafe_allow_html=True,
)

# Sidebar for inputs
st.sidebar.header("Step 1: Upload Grades")
uploaded_file = st.sidebar.file_uploader(
    "Upload an Excel file (.xlsx or .xls)",
    type=["xlsx", "xls"]
)

st.sidebar.markdown("---")
st.sidebar.header("Step 2: Options")

# ABET performance settings
st.sidebar.subheader("ABET Performance Criteria")
threshold = st.sidebar.number_input(
    "Score threshold for 'meeting' the objective (e.g., 70):",
    min_value=0.0,
    max_value=1000.0,
    value=70.0,
    step=1.0,
)
target_pct = st.sidebar.slider(
    "Target % of students at or above threshold to consider objective met:",
    min_value=0,
    max_value=100,
    value=70,
    step=5,
)

st.sidebar.caption(
    "These settings are used to compute attainment on each assessment and to generate the narrative text."
)


def load_excel(file):
    """Helper to load Excel and return (xls, df, sheet_name)."""
    xls = pd.ExcelFile(file)
    if len(xls.sheet_names) > 1:
        sheet_name = st.sidebar.selectbox("Select sheet", xls.sheet_names)
    else:
        sheet_name = xls.sheet_names[0]
        st.sidebar.write(f"Using sheet: **{sheet_name}**")
    df_local = pd.read_excel(xls, sheet_name=sheet_name)
    return xls, df_local, sheet_name


if uploaded_file is not None:
    try:
        xls, df, sheet_name = load_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

    st.subheader("Preview of Uploaded Data")
    st.caption(f"Sheet: **{sheet_name}**")
    st.dataframe(df.head())

    st.markdown("---")
    st.subheader("Column Settings")

    all_columns = list(df.columns)

    # Suggest default exclusions based on common ID/name patterns
    default_exclude = [
        col for col in all_columns
        if any(key.lower() in col.lower() for key in ["name", "id", "netid", "student"])
    ]

    exclude_cols = st.multiselect(
        "Columns to exclude (non-grade columns):",
        options=all_columns,
        default=default_exclude,
        help="These columns will be removed before generating attainment metrics."
    )

    # Drop excluded columns, keep numeric-only
    df_for_grades = df.drop(columns=exclude_cols, errors="ignore")
    numeric_df = df_for_grades.select_dtypes(include="number")

    if numeric_df.empty:
        st.error("No numeric columns found after exclusions. Adjust your selection or check your file format.")
        st.stop()

    st.success("Numeric assessment columns detected:")
    st.write(list(numeric_df.columns))

    selected_assessments = st.multiselect(
        "Select assessment columns to include in the attainment bar chart and ABET narrative:",
        options=list(numeric_df.columns),
        default=list(numeric_df.columns)
    )

    if not selected_assessments:
        st.error("Please select at least one assessment column.")
        st.stop()

    numeric_df = numeric_df[selected_assessments]

    # --- Compute summary statistics and attainment for each assessment ---
    summary_rows = []
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if series.empty:
            continue
        n = series.count()
        mean_val = series.mean()
        median_val = series.median()
        pct_at_or_above = (series >= threshold).mean() * 100.0

        # Determine attainment status based on target_pct
        if pct_at_or_above >= target_pct:
            status = "met"
        elif pct_at_or_above >= max(target_pct - 10, 0):
            status = "partially met"
        else:
            status = "not met"

        summary_rows.append({
            "Assessment": col,
            "N": n,
            "Mean": mean_val,
            "Median": median_val,
            "% ≥ threshold": pct_at_or_above,
            "Status": status,
        })

    if not summary_rows:
        st.error("No valid numeric data found for the selected assessments.")
        st.stop()

    summary_df = pd.DataFrame(summary_rows)

    st.markdown("---")
    st.subheader("Attainment Bar Chart")

    # --- UConn brand-inspired colors ---
    uconn_blue = "#003f7d"   # primary
    uconn_gray = "#7c878e"   # accent for target line

    # Data for bar chart
    labels = summary_df["Assessment"].tolist()
    values = summary_df["% ≥ threshold"].tolist()

    fig_all, ax_all = plt.subplots(figsize=(10, 6))

    x_positions = range(len(labels))
    bars = ax_all.bar(x_positions, values, color=uconn_blue)

    # Horizontal line for target percentage
    ax_all.axhline(target_pct, color=uconn_gray, linestyle="--", linewidth=1.5)
    ax_all.text(
        len(labels) - 0.5,
        target_pct + 1,
        f"Target: {target_pct}%",
        color=uconn_gray,
        fontsize=9,
        ha="right",
        va="bottom"
    )

    # Label each bar with its percentage
    for i, v in enumerate(values):
        ax_all.text(
            i,
            v + 1,
            f"{v:.1f}%",
            ha="center",
            va="bottom",
            fontsize=9
        )

    # Style axes
    ax_all.set_ylim(0, max(100, max(values) * 1.1))
    ax_all.set_ylabel("% of students ≥ threshold", fontsize=11)
    ax_all.set_xlabel("Assessment", fontsize=11)
    ax_all.set_xticks(list(x_positions))
    ax_all.set_xticklabels(labels, rotation=45, ha="right")

    # Remove gridlines & title
    ax_all.grid(False)
    ax_all.set_title("")

    plt.tight_layout()
    st.pyplot(fig_all)

    # Download button for bar chart
    buf_all = BytesIO()
    fig_all.savefig(buf_all, format="png", dpi=300, bbox_inches="tight")
    buf_all.seek(0)
    st.download_button(
        label="Download attainment chart (PNG)",
        data=buf_all,
        file_name="cbe_abet_attainment_bar_chart.png",
        mime="image/png"
    )

    # --- Show summary table ---
    st.markdown("---")
    st.subheader("Summary Statistics by Assessment")
    st.dataframe(summary_df.style.format({
        "Mean": "{:.1f}",
        "Median": "{:.1f}",
        "% ≥ threshold": "{:.1f}"
    }))

    # --- ABET narrative generation ---
    st.markdown("---")
    st.subheader("Auto-Generated ABET Narrative")

    fig_caption = (
        "Figure 1. Bar chart showing the percentage of students meeting the performance "
        f"threshold of {threshold:.0f} points on each selected assessment. The dashed horizontal "
        f"line indicates the target of {target_pct}% of students at or above the threshold. "
        "This visualization provides a direct view of attainment levels used to evaluate ABET "
        "learning objective(s) associated with the course."
    )

    narrative_lines = []
    narrative_lines.append(
        f"Using a performance threshold of {threshold:.0f} points and a target of {target_pct}% "
        "of students at or above this threshold, assessment-level attainment of the ABET objective was evaluated as follows:"
    )

    for row in summary_rows:
        narrative_lines.append(
            f"- **{row['Assessment']}**: {row['% ≥ threshold']:.1f}% of students scored at or above the threshold "
            f"({row['Status']} the performance criterion)."
        )

    # Overall statement
    num_met = sum(1 for r in summary_rows if r["Status"] == "met")
    num_partial = sum(1 for r in summary_rows if r["Status"] == "partially met")
    num_not = sum(1 for r in summary_rows if r["Status"] == "not met")

    overall_sentence_parts = []
    if num_met:
        overall_sentence_parts.append(f"{num_met} assessment(s) met the criterion")
    if num_partial:
            overall_sentence_parts.append(f"{num_partial} were partially met")
    if num_not:
        overall_sentence_parts.append(f"{num_not} did not meet the criterion")

    if overall_sentence_parts:
        overall_sentence = (
            "Overall, " + ", ".join(overall_sentence_parts) +
            ", providing a basis for documenting ABET outcome attainment and identifying areas for improvement."
        )
        narrative_lines.append("")
        narrative_lines.append(overall_sentence)

    full_text = "**Figure Caption**\n\n" + fig_caption + "\n\n**ABET Outcome Interpretation**\n\n" + "\n".join(narrative_lines)

    st.markdown(full_text)

    st.text_area(
        "Copy-pasteable narrative for your syllabus or course report:",
        value=fig_caption + "\n\n" + "\n".join(narrative_lines),
        height=250
    )

else:
    st.info("Use the file uploader in the left sidebar to begin.")
    st.markdown(
        """
        **Instructions**  
        1. Export your gradebook to Excel (one column per assessment, one row per student).  
        2. Click “Browse files” in the sidebar and select your Excel file.  
        3. Exclude any non-grade columns (e.g., names, IDs).  
        4. Select which assessments to include.  
        5. Set the ABET threshold and target percentage for attainment.  
        6. Download the attainment bar chart as a PNG and copy the narrative text for your ABET documentation.
        """
    )
