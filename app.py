
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="CBE ABET Plot Generator", layout="wide")

st.title("CBE ABET Plot Generator")

st.markdown(
    """
Upload an **Excel file** where:

- Each **column** is an assessment (Exam 1, HW Avg, Project, Final, etc.)
- Each **row** is a student  
- Non-grade columns (e.g., `Name`, `NetID`, `StudentID`) can be excluded.

The app will generate **box & whisker plots** that you can download as PNGs
for use in ABET course files, annual reports, and assessment documentation.
"""
)

uploaded_file = st.file_uploader("Upload an Excel file (.xlsx or .xls)", type=["xlsx", "xls"])

if uploaded_file is not None:
    # Try to read Excel and let user pick sheet if multiple
    try:
        xls = pd.ExcelFile(uploaded_file)
        if len(xls.sheet_names) > 1:
            sheet_name = st.selectbox("Select sheet", xls.sheet_names)
        else:
            sheet_name = xls.sheet_names[0]
        df = pd.read_excel(xls, sheet_name=sheet_name)
    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.stop()

    st.subheader("Data Preview")
    st.write("First few rows of your data:")
    st.dataframe(df.head())

    st.subheader("Column Settings")

    all_columns = list(df.columns)

    # Suggest default exclusions based on common ID/name patterns
    default_exclude = [col for col in all_columns if any(
        key.lower() in col.lower() for key in ["name", "id", "netid", "student"]
    )]

    exclude_cols = st.multiselect(
        "Columns to exclude (non-grade columns):",
        options=all_columns,
        default=default_exclude
    )

    # Drop excluded columns, keep numeric-only
    df_for_grades = df.drop(columns=exclude_cols, errors="ignore")
    numeric_df = df_for_grades.select_dtypes(include="number")

    if numeric_df.empty:
        st.error("No numeric columns found after exclusions. Please adjust your selection or check your file format.")
        st.stop()

    st.success("Numeric assessment columns detected:")
    st.write(list(numeric_df.columns))

    selected_assessments = st.multiselect(
        "Select assessment columns to include in plots:",
        options=list(numeric_df.columns),
        default=list(numeric_df.columns)
    )

    if not selected_assessments:
        st.error("Please select at least one assessment column.")
        st.stop()

    numeric_df = numeric_df[selected_assessments]

    st.markdown("---")
    st.subheader("Combined Box & Whisker Plot (All Selected Assessments)")

    fig_all, ax_all = plt.subplots(figsize=(10, 6))
    numeric_df.boxplot(ax=ax_all)
    ax_all.set_title("Box & Whisker Plot for All Assessments")
    ax_all.set_ylabel("Grade")
    ax_all.set_xlabel("Assessment")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig_all)

    buf_all = BytesIO()
    fig_all.savefig(buf_all, format="png", dpi=300, bbox_inches="tight")
    buf_all.seek(0)
    st.download_button(
        label="Download combined boxplot (PNG)",
        data=buf_all,
        file_name="boxplots_all_assessments.png",
        mime="image/png"
    )

    st.markdown("---")
    st.subheader("Individual Assessment Boxplots")

    for col in numeric_df.columns:
        st.markdown(f"**{col}**")
        fig, ax = plt.subplots(figsize=(4, 6))
        ax.boxplot(numeric_df[col].dropna(), vert=True)
        ax.set_ylabel("Grade")
        ax.set_title(f"Box & Whisker: {col}")
        plt.tight_layout()
        st.pyplot(fig)

        buf = BytesIO()
        fig.savefig(buf, format="png", dpi=300, bbox_inches="tight")
        buf.seek(0)
        st.download_button(
            label=f"Download {col} boxplot (PNG)",
            data=buf,
            file_name=f"boxplot_{col.replace(' ', '_')}.png",
            mime="image/png",
            key=f"download_{col}"
        )
        plt.close(fig)
else:
    st.info("Upload an Excel file to begin.")
