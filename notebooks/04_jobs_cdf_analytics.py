from pyspark.sql.functions import (
    col,
    current_timestamp,
)

SOURCE_TABLE = "career_os.silver.jobs_clean"
ANALYTICS_TABLE = "career_os.analytics.jobs_cdf"

STARTING_VERSION = 9


cdf_df = (
    spark.read
    .option("readChangeFeed","true",)
    .option("startingVersion",STARTING_VERSION,)
    .table(SOURCE_TABLE)
)


analytics_df = (
    cdf_df
    .select(
        col("job_id"),
        col("title"),
        col("company"),
        col("location"),
        col("salary_min"),
        col("salary_max"),
        col("job_url"),
        col("_change_type"),
        col("_commit_version"),
        col("_commit_timestamp"),
    )
    .withColumn("analytics_loaded_at",current_timestamp(),)
)


(
    analytics_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema","true",)
    .saveAsTable(ANALYTICS_TABLE)
)

print(f"CDF analytics table created: " f"{ANALYTICS_TABLE}")

display(spark.table("career_os.analytics.jobs_cdf").limit(20))

display(
    spark.sql("""
    SELECT
        _change_type,
        COUNT(*) AS change_count
    FROM career_os.analytics.jobs_cdf
    GROUP BY _change_type
    ORDER BY change_count DESC
    """)
)

job_change_summary_df = spark.sql("""
SELECT
    DATE(_commit_timestamp) AS change_date,
    _change_type,
    location,
    COUNT(*) AS job_changes
FROM career_os.analytics.jobs_cdf
GROUP BY
    DATE(_commit_timestamp),
    _change_type,
    location
""")

(
    job_change_summary_df
    .write
    .format("delta")
    .mode("overwrite")
    .saveAsTable("career_os.analytics.job_change_summary")
)

job_change_summary_df = spark.sql("""
SELECT
    DATE(_commit_timestamp) AS change_date,
    _change_type,
    location,
    COUNT(*) AS job_changes
FROM career_os.analytics.jobs_cdf
GROUP BY
    DATE(_commit_timestamp),
    _change_type,
    location
""")

(
    job_change_summary_df
    .write
    .format("delta")
    .mode("overwrite")
    .option("overwriteSchema", "true")
    .saveAsTable("career_os.analytics.job_change_summary")
)

print(
    "Created analytics summary table: career_os.analytics.job_change_summary"
)

display(
    spark.sql("""
    SELECT
        _change_type,
        COUNT(*) AS change_count
    FROM career_os.analytics.jobs_cdf
    GROUP BY _change_type
    ORDER BY change_count DESC
    """)
)

display(
    spark.sql("""
    SELECT
        change_date,
        location,
        job_changes
    FROM career_os.analytics.job_change_summary
    WHERE _change_type = 'insert'
    ORDER BY job_changes DESC
    LIMIT 20
    """)
)