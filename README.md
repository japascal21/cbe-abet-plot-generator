
# CBE ABET Plot Generator (UConn-Styled, Combined Plot Only)

A Streamlit web app that lets faculty upload an Excel file of student
grades and automatically generates a **single, combined UConn-themed
box & whisker plot** for all selected assessments. The figure can be
downloaded as a PNG for ABET documentation.

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
