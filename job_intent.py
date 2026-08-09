import re

SKILL_ALIASES = {
    "python": "Python",
    "pyspark": "PySpark",
    "spark": "Spark",
    "apache spark": "Spark",
    "databricks": "Databricks",
    "sql": "SQL",
    "snowflake": "Snowflake",
    "dbt": "dbt",
    "airflow": "Airflow",
    "kafka": "Kafka",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "java": "Java",
    "scala": "Scala",
    "hadoop": "Hadoop",
    "terraform": "Terraform",
    "kubernetes": "Kubernetes",
    "docker": "Docker",
    "tableau": "Tableau",
    "power bi": "Power BI",
    "machine learning": "Machine Learning",
    "etl": "ETL",
    "elt": "ELT",
    "data modeling": "Data Modeling",
    "data pipelines": "Data Pipelines",
    "software development": "Software Development",
    "data warehousing": "Data Warehousing",
    "data visualization": "Data Visualization",
    "data governance": "Data Governance",
    "data architecture": "Data Architecture",
    "business intelligence": "Business Intelligence",
    "data science": "Data Science",
    "data analytics": "Data Analytics",
    "software engineering": "Software Engineering"

}


# =========================================================
# LOCATIONS
# =========================================================

LOCATION_ALIASES = {
    "chicago": "Chicago",
    "dallas": "Dallas",
    "austin": "Austin",
    "houston": "Houston",
    "san antonio": "San Antonio",
    "fort worth": "Fort Worth",
    "new york": "New York",
    "new york city": "New York",
    "nyc": "New York",
    "los angeles": "Los Angeles",
    "san francisco": "San Francisco",
    "sf": "San Francisco",
    "san diego": "San Diego",
    "san jose": "San Jose",
    "bakersfield": "Bakersfield",
    "raleigh": "Raleigh",
    "charlotte": "Charlotte",
    "columbus": "Columbus",
    "cleveland": "Cleveland",
    "cincinnati": "Cincinnati",
    "detroit": "Detroit",
    "indianapolis": "Indianapolis",
    "kansas city": "Kansas City",
    "oklahoma city": "Oklahoma City",
    "memphis": "Memphis",
    "nashville": "Nashville",
    "omaha": "Omaha",
    "portland": "Portland",
    "philadelphia": "Philadelphia",
    "pittsburgh": "Pittsburgh",
    "tampa": "Tampa",
    "tucson": "Tucson",
    "tulsa": "Tulsa",
    "las vegas": "Las Vegas",
    "seattle": "Seattle",
    "boston": "Boston",
    "denver": "Denver",
    "atlanta": "Atlanta",
    "phoenix": "Phoenix",
    "miami": "Miami",
    "philadelphia": "Philadelphia",
    "washington": "Washington",
    "washington dc": "Washington",
    "dc": "Washington",
    "remote": "Remote",
}


# =========================================================
# ROLE PATTERNS
# =========================================================

ROLE_PATTERNS = [
    (
        r"\b(senior|sr\.?)\s+data\s+scientist\b",
        "Senior Data Scientist",
    ),
    (
        r"\bdata\s+scientist\b",
        "Data Scientist",
    ),
    (
        r"\b(senior|sr\.?)\s+data\s+engineer\b",
        "Senior Data Engineer",
    ),
    (
        r"\bprincipal\s+data\s+engineer\b",
        "Principal Data Engineer",
    ),
    (
        r"\blead\s+data\s+engineer\b",
        "Lead Data Engineer",
    ),
    (
        r"\b(junior|jr\.?)\s+data\s+engineer\b",
        "Junior Data Engineer",
    ),
    (
        r"\bdata\s+engineer\b",
        "Data Engineer",
    ),
    (
        r"\bmachine\s+learning\s+engineer\b",
        "Machine Learning Engineer",
    ),
    (
        r"\bml\s+engineer\b",
        "Machine Learning Engineer",
    ),
    (
        r"\bdata\s+analyst\b",
        "Data Analyst",
    ),
    (
        r"\banalytics\s+engineer\b",
        "Analytics Engineer",
    ),
    (
        r"\bsoftware\s+engineer\b",
        "Software Engineer",
    ),
]


# =========================================================
# EXTRACT ROLE
# =========================================================

def extract_role(query):

    query_lower = query.lower()

    for pattern, role in ROLE_PATTERNS:

        if re.search(
            pattern,
            query_lower
        ):
            return role

    return None


# =========================================================
# EXTRACT LOCATION
# =========================================================

def extract_location(query):

    query_lower = query.lower()

    aliases = sorted(
        LOCATION_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for alias in aliases:

        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            query_lower
        ):
            return LOCATION_ALIASES[alias]

    return None


# =========================================================
# EXTRACT SKILLS
# =========================================================

def extract_skills(query):

    query_lower = query.lower()

    found = []

    aliases = sorted(
        SKILL_ALIASES.keys(),
        key=len,
        reverse=True
    )

    for alias in aliases:

        pattern = (
            r"(?<!\w)"
            + re.escape(alias)
            + r"(?!\w)"
        )

        if re.search(
            pattern,
            query_lower
        ):

            skill = SKILL_ALIASES[alias]

            if skill not in found:
                found.append(skill)

    return found


# =========================================================
# EXTRACT SENIORITY
# =========================================================

def extract_seniority(query):

    query_lower = query.lower()

    if re.search(
        r"\b(senior|sr\.?)\b",
        query_lower
    ):
        return "Senior"

    if re.search(
        r"\bprincipal\b",
        query_lower
    ):
        return "Principal"

    if re.search(
        r"\blead\b",
        query_lower
    ):
        return "Lead"

    if re.search(
        r"\b(junior|jr\.?)\b",
        query_lower
    ):
        return "Junior"

    return None


# =========================================================
# EXTRACT WORK MODE
# =========================================================

def extract_work_mode(query):

    query_lower = query.lower()

    if "remote" in query_lower:
        return "Remote"

    if "hybrid" in query_lower:
        return "Hybrid"

    if (
        "onsite" in query_lower
        or "on-site" in query_lower
        or "on site" in query_lower
    ):
        return "Onsite"

    return None


# =========================================================
# MAIN PARSER
# =========================================================

def parse_job_intent(query):

    return {
        "original_query": query,
        "role": extract_role(query),
        "location": extract_location(query),
        "skills": extract_skills(query),
        "salary_max": None,
        "seniority": extract_seniority(query),
        "work_mode": extract_work_mode(query),
    }

