import pandas as pd
import streamlit as st
from databricks.sdk import WorkspaceClient


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CareerOS",
    page_icon="🚀",
    layout="wide"
)


# =========================================================
# CONFIGURATION
# =========================================================

JOBS_TABLE = "career_os.silver.jobs_clean"

# Serverless Starter Warehouse
WAREHOUSE_ID = "d7aa18d58fb686f5"


# =========================================================
# DATABRICKS CLIENT
# =========================================================

@st.cache_resource
def get_client():
    return WorkspaceClient()


# =========================================================
# EXECUTE SQL
# =========================================================

def execute_query(query):

    client = get_client()

    response = client.statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID,
        statement=query,
        wait_timeout="30s"
    )

    # -----------------------------------------------------
    # Get the SQL result
    #
    # We intentionally do NOT check response.status here.
    # The warehouse is already returning a successful result
    # with data_array containing our rows.
    # -----------------------------------------------------

    result = response.result

    if result is None:
        return pd.DataFrame()

    if result.data_array is None:
        return pd.DataFrame()

    rows = result.data_array

    # -----------------------------------------------------
    # Convert SQL rows into a Pandas DataFrame
    # -----------------------------------------------------

    columns = [
        "job_id",
        "title",
        "company",
        "location",
        "salary_min",
        "salary_max",
        "description",
        "job_url"
    ]

    df = pd.DataFrame(
        rows,
        columns=columns
    )

    # -----------------------------------------------------
    # Convert salary values to numeric
    # -----------------------------------------------------

    df["salary_min"] = pd.to_numeric(
        df["salary_min"],
        errors="coerce"
    )

    df["salary_max"] = pd.to_numeric(
        df["salary_max"],
        errors="coerce"
    )

    return df


# =========================================================
# LOAD JOBS
# =========================================================

def get_jobs():

    query = f"""
        SELECT
            job_id,
            title,
            company,
            location,
            salary_min,
            salary_max,
            description,
            job_url
        FROM {JOBS_TABLE}
        LIMIT 100
    """

    return execute_query(query)


# =========================================================
# SEARCH JOBS
# =========================================================

def search_jobs(jobs, search_query):

    if jobs.empty:
        return jobs

    search_query = search_query.strip().lower()

    # -----------------------------------------------------
    # Match job title
    # -----------------------------------------------------

    title_match = (
        jobs["title"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_query,
            regex=False
        )
    )

    # -----------------------------------------------------
    # Match job description
    # -----------------------------------------------------

    description_match = (
        jobs["description"]
        .fillna("")
        .astype(str)
        .str.lower()
        .str.contains(
            search_query,
            regex=False
        )
    )

    # -----------------------------------------------------
    # Return jobs matching either title OR description
    # -----------------------------------------------------

    return jobs[
        title_match | description_match
    ]


# =========================================================
# DISPLAY JOB
# =========================================================

def display_job(job):

    title = str(
        job["title"]
    )

    company = str(
        job["company"]
    )

    location = str(
        job["location"]
    )

    # -----------------------------------------------------
    # Job title
    # -----------------------------------------------------

    st.markdown(
        f"### {title}"
    )

    # -----------------------------------------------------
    # Company + location
    # -----------------------------------------------------

    st.write(
        f"**{company}** · {location}"
    )

    # -----------------------------------------------------
    # Salary
    # -----------------------------------------------------

    if pd.notna(
        job["salary_max"]
    ):

        try:

            salary = float(
                job["salary_max"]
            )

            st.write(
                f"💰 Up to ${salary:,.0f}"
            )

        except (
            ValueError,
            TypeError
        ):

            pass

    # -----------------------------------------------------
    # Description
    # -----------------------------------------------------

    if pd.notna(
        job["description"]
    ):

        description = str(
            job["description"]
        )

        # Keep the UI clean
        if len(description) > 500:

            description = (
                description[:500]
                + "..."
            )

        st.write(
            description
        )

    # -----------------------------------------------------
    # Job URL
    # -----------------------------------------------------

    if pd.notna(
        job["job_url"]
    ):

        st.link_button(
            "View Job ↗",
            str(job["job_url"])
        )

    st.divider()


# =========================================================
# CAREEROS HEADER
# =========================================================

st.title(
    "🚀 CareerOS"
)

st.subheader(
    "AI Career Assistant"
)

st.write(
    "AI-powered job discovery and career tracking."
)


# =========================================================
# SEARCH INPUT
# =========================================================

query = st.text_input(
    "What type of role are you looking for?",
    placeholder=(
        "e.g. Data Engineer, "
        "Analytics Engineer, "
        "Machine Learning Engineer"
    )
)


# =========================================================
# SEARCH BUTTON
# =========================================================

if st.button(
    "🔎 Search Jobs",
    use_container_width=True
):

    # -----------------------------------------------------
    # Validate input
    # -----------------------------------------------------

    if not query.strip():

        st.warning(
            "Please enter a job role first."
        )

    else:

        with st.spinner(
            "Searching CareerOS..."
        ):

            try:

                # -----------------------------------------
                # Load jobs from Databricks
                # -----------------------------------------

                jobs = get_jobs()

                # -----------------------------------------
                # Show database count
                # -----------------------------------------

                st.write(
                    f"Database rows retrieved: {len(jobs)}"
                )

                # -----------------------------------------
                # No jobs
                # -----------------------------------------

                if jobs.empty:

                    st.error(
                        "No jobs were returned from "
                        f"{JOBS_TABLE}."
                    )

                else:

                    # -------------------------------------
                    # Search
                    # -------------------------------------

                    results = search_jobs(
                        jobs,
                        query
                    )

                    # -------------------------------------
                    # No matches
                    # -------------------------------------

                    if results.empty:

                        st.warning(
                            f"No jobs matched '{query}'."
                        )

                        st.write(
                            "Here are the available "
                            "job titles:"
                        )

                        st.dataframe(
                            jobs[
                                [
                                    "title",
                                    "company",
                                    "location"
                                ]
                            ],
                            use_container_width=True
                        )

                    # -------------------------------------
                    # Matches
                    # -------------------------------------

                    else:

                        st.success(
                            f"Found {len(results)} "
                            "matching jobs."
                        )

                        st.subheader(
                            "🎯 Recommended Jobs"
                        )

                        # ---------------------------------
                        # Display each job
                        # ---------------------------------

                        for _, job in results.iterrows():

                            display_job(
                                job
                            )

            # ---------------------------------------------
            # Catch unexpected errors
            # ---------------------------------------------

            except Exception as e:

                st.error(
                    "Unable to search the "
                    "CareerOS database."
                )

                st.exception(
                    e
                )


# =========================================================
# FOOTER
# =========================================================

st.caption(
    "CareerOS · Databricks AI Capstone"
)
