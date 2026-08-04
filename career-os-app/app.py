import streamlit as st
import pandas as pd


st.set_page_config(
    page_title="CareerOS",
    page_icon="🚀",
    layout="wide"
)


st.title("🚀 CareerOS AI Career Assistant")

st.write(
    "AI-powered job discovery and career tracking."
)


query = st.text_input(
    "What type of role are you looking for?"
)


if st.button("Search Jobs"):

    st.subheader("Recommended Jobs")

from pyspark.sql import SparkSession

spark = SparkSession.builder.getOrCreate()


jobs_df = spark.table(
    "career_os.silver.jobs_clean"
)


results = (
    jobs_df
    .select(
        "job_id",
        "title",
        "company",
        "location",
        "salary_max"
    )
    .limit(10)
    .toPandas()
)


st.dataframe(
    results,
    use_container_width=True
)