
# CBE ABET Plot Generator (UConn-Styled, With Narrative)

A Streamlit web app that lets faculty upload an Excel file of student
grades and automatically generates:

1. A **single, combined UConn-themed box & whisker plot** for all selected assessments.
2. An **auto-generated ABET narrative**, including:
   - A figure caption describing the box-and-whisker plot.
   - A paragraph summarizing whether students met the performance criterion
     on each assessment, based on a user-defined threshold and target percentage.

The figure and text can be used directly in ABET syllabi, course reports, and assessment documentation.

## Visual style

- Uses UConn-inspired colors via matplotlib:
  - Boxes: light blue fill (`#e6eef5`)
  - Edges & medians: UConn blue (`#003f7d`)
  - Whiskers & caps: gray (`#7c878e`)
- No title on the plot
- No gridlines
- Clean axes:
  - x-axis: assessment names
  - y-axis: "Grade"

## ABET interpretation logic

In the sidebar, the user can specify:
- A **score threshold** for "meeting" the objective (e.g., 70 points).
- A **target percentage** of students who should be at or above that threshold (e.g., 70%).

For each selected assessment, the app computes:
- N (number of students with a score)
- Mean and median
- Percentage of students with score ≥ threshold
- A status label:
  - `"met"` if % ≥ target
  - `"partially met"` if % is within 10 percentage points below target
  - `"not met"` otherwise

The narrative text then describes, for each assessment, whether the performance
criterion was met, partially met, or not met.

## File format

- Each **column** is an assessment (e.g., Exam 1, HW Avg, Project, Final).
- Each **row** is a student.
- Non-grade columns (Name, NetID, StudentID, etc.) can be excluded in the app UI.

## Files in this repo

- `app.py` – the main Streamlit application.
- `requirements.txt` – Python dependencies.

## How to run locally (optional)

If you want to test or modify the app locally before deploying to Streamlit Cloud:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploying to Streamlit Cloud

1. Create a new GitHub repository (e.g., `cbe-abet-plot-generator`).
2. Add `app.py` and `requirements.txt` to the repo and push to GitHub.
3. Go to https://share.streamlit.io and sign in.
4. Click **"New app"**, select your repo, branch, and `app.py` as the entry file.
5. Click **Deploy**.

## Restricting access to specific emails

In Streamlit Community Cloud:

1. Go to your app's **Settings**.
2. Under **"Access Control"** or **"Manage app viewers"**, choose **"Only invited users"**.
3. Add the specific email addresses (e.g., `firstname.lastname@uconn.edu`) you want to allow.

Only those users will be able to view and use the app.
