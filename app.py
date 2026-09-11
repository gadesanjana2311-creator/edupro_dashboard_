
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="EduPro Instructor Performance",
    page_icon="🎓",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

@st.cache_data
def load_data():

    teachers = pd.read_excel(
        "EduPro Online Platform(5).xlsx",
        sheet_name="Teachers"
    )

    courses = pd.read_excel(
        "EduPro Online Platform(5).xlsx",
        sheet_name="Courses"
    )

    transactions = pd.read_excel(
        "EduPro Online Platform(5).xlsx",
        sheet_name="Transactions"
    )

    df = transactions.merge(
        teachers,
        on="TeacherID",
        how="left"
    )

    df = df.merge(
        courses,
        on="CourseID",
        how="left"
    )

    return teachers, courses, transactions, df


teachers, courses, transactions, df = load_data()


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🎓 EduPro Instructor Performance & Course Quality Dashboard")

st.markdown(
    """
    ### Instructor Performance and Course Quality Evaluation

    This dashboard provides data-driven analysis of:
    - Instructor performance
    - Teaching experience
    - Course quality
    - Instructor expertise
    - Course ratings
    - Enrollment performance
    """
)


# --------------------------------------------------
# SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

expertise_options = sorted(
    teachers["Expertise"].dropna().unique()
)

selected_expertise = st.sidebar.multiselect(
    "Select Expertise",
    expertise_options,
    default=expertise_options
)

category_options = sorted(
    courses["CourseCategory"].dropna().unique()
)

selected_category = st.sidebar.multiselect(
    "Select Course Category",
    category_options,
    default=category_options
)

level_options = sorted(
    courses["CourseLevel"].dropna().unique()
)

selected_level = st.sidebar.multiselect(
    "Select Course Level",
    level_options,
    default=level_options
)


# --------------------------------------------------
# FILTER DATA
# --------------------------------------------------

filtered_df = df[
    (df["Expertise"].isin(selected_expertise)) &
    (df["CourseCategory"].isin(selected_category)) &
    (df["CourseLevel"].isin(selected_level))
].copy()


# --------------------------------------------------
# KPIs
# --------------------------------------------------

avg_teacher_rating = filtered_df[
    "TeacherRating"
].mean()

avg_course_rating = filtered_df[
    "CourseRating"
].mean()

total_enrollments = filtered_df[
    "TransactionID"
].nunique()

total_instructors = filtered_df[
    "TeacherID"
].nunique()

total_courses = filtered_df[
    "CourseID"
].nunique()


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Average Teacher Rating",
    f"{avg_teacher_rating:.2f}"
)

col2.metric(
    "Average Course Rating",
    f"{avg_course_rating:.2f}"
)

col3.metric(
    "Total Enrollments",
    f"{total_enrollments:,}"
)

col4.metric(
    "Instructors",
    f"{total_instructors:,}"
)

col5.metric(
    "Courses",
    f"{total_courses:,}"
)


st.divider()


# --------------------------------------------------
# INSTRUCTOR LEADERBOARD
# --------------------------------------------------

st.header("🏆 Instructor Performance Leaderboard")

leaderboard = (
    filtered_df
    .groupby(
        [
            "TeacherID",
            "TeacherName",
            "Expertise"
        ]
    )
    .agg(
        TeacherRating=("TeacherRating", "first"),
        AverageCourseRating=("CourseRating", "mean"),
        Experience=("YearsOfExperience", "first"),
        Enrollments=("TransactionID", "count"),
        CoursesTaught=("CourseID", "nunique")
    )
    .reset_index()
)

leaderboard["OverallScore"] = (
    leaderboard["TeacherRating"] * 0.5 +
    leaderboard["AverageCourseRating"] * 0.5
)

leaderboard = leaderboard.sort_values(
    "OverallScore",
    ascending=False
)

st.dataframe(
    leaderboard,
    use_container_width=True
)


# --------------------------------------------------
# EXPERIENCE VS TEACHER RATING
# --------------------------------------------------

st.header("📈 Experience vs Teacher Rating")

fig1 = px.scatter(
    leaderboard,
    x="Experience",
    y="TeacherRating",
    size="Enrollments",
    color="Expertise",
    hover_name="TeacherName",
    title="Teaching Experience vs Teacher Rating"
)

st.plotly_chart(
    fig1,
    use_container_width=True
)


# --------------------------------------------------
# TEACHER RATING VS COURSE RATING
# --------------------------------------------------

st.header("⭐ Teacher Rating vs Course Rating")

teacher_course = (
    filtered_df
    .groupby(
        ["TeacherID", "TeacherName"]
    )
    .agg(
        TeacherRating=("TeacherRating", "first"),
        CourseRating=("CourseRating", "mean")
    )
    .reset_index()
)

fig2 = px.scatter(
    teacher_course,
    x="TeacherRating",
    y="CourseRating",
    hover_name="TeacherName",
    title="Teacher Rating vs Average Course Rating",
    trendline="ols"
)

st.plotly_chart(
    fig2,
    use_container_width=True
)


# --------------------------------------------------
# COURSE QUALITY BY CATEGORY
# --------------------------------------------------

st.header("📚 Course Quality by Category")

category_analysis = (
    filtered_df
    .groupby("CourseCategory")
    .agg(
        AverageRating=("CourseRating", "mean"),
        NumberOfCourses=("CourseID", "nunique")
    )
    .reset_index()
)

fig3 = px.bar(
    category_analysis,
    x="CourseCategory",
    y="AverageRating",
    text_auto=".2f",
    title="Average Course Rating by Category"
)

st.plotly_chart(
    fig3,
    use_container_width=True
)


# --------------------------------------------------
# COURSE QUALITY HEATMAP
# --------------------------------------------------

st.header("🔥 Course Quality Heatmap")

heatmap_data = pd.pivot_table(
    filtered_df,
    values="CourseRating",
    index="CourseCategory",
    columns="CourseLevel",
    aggfunc="mean"
)

fig4 = px.imshow(
    heatmap_data,
    text_auto=".2f",
    aspect="auto",
    title="Average Course Rating by Category and Level"
)

st.plotly_chart(
    fig4,
    use_container_width=True
)


# --------------------------------------------------
# EXPERTISE ANALYSIS
# --------------------------------------------------

st.header("👨‍🏫 Expertise-wise Performance")

expertise_analysis = (
    filtered_df
    .groupby("Expertise")
    .agg(
        AverageTeacherRating=("TeacherRating", "mean"),
        AverageCourseRating=("CourseRating", "mean"),
        AverageExperience=("YearsOfExperience", "mean"),
        TotalEnrollments=("TransactionID", "count")
    )
    .reset_index()
)

fig5 = px.bar(
    expertise_analysis,
    x="Expertise",
    y="AverageCourseRating",
    color="Expertise",
    text_auto=".2f",
    title="Course Quality by Instructor Expertise"
)

st.plotly_chart(
    fig5,
    use_container_width=True
)


# --------------------------------------------------
# ENROLLMENT ANALYSIS
# --------------------------------------------------

st.header("👥 Instructor Rating vs Enrollment")

fig6 = px.scatter(
    leaderboard,
    x="TeacherRating",
    y="Enrollments",
    size="AverageCourseRating",
    color="Expertise",
    hover_name="TeacherName",
    title="Instructor Rating vs Enrollment"
)

st.plotly_chart(
    fig6,
    use_container_width=True
)


# --------------------------------------------------
# COURSE LEVEL ANALYSIS
# --------------------------------------------------

st.header("🎯 Course Level Performance")

level_analysis = (
    filtered_df
    .groupby("CourseLevel")
    .agg(
        AverageRating=("CourseRating", "mean"),
        Enrollments=("TransactionID", "count")
    )
    .reset_index()
)

fig7 = px.bar(
    level_analysis,
    x="CourseLevel",
    y="AverageRating",
    text_auto=".2f",
    title="Average Rating by Course Level"
)

st.plotly_chart(
    fig7,
    use_container_width=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.markdown(
    """
    ### Conclusion

    The EduPro dashboard provides a data-driven framework for
    evaluating instructor effectiveness and course quality.

    The analysis helps identify:
    - High-performing instructors
    - Low-performing instructors
    - Strong expertise areas
    - High-quality course categories
    - Relationship between experience and performance
    - Relationship between instructor ratings and enrollments
    """
)
