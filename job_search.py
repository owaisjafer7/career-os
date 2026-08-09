import json
import re
import numpy as np
from databricks.sdk import WorkspaceClient
from sentence_transformers import SentenceTransformer
from profile_embedding import get_profile_embedding
from lakebase_actions import get_current_user
from job_intent import parse_job_intent

JOBS_TABLE = "career_os.silver.jobs_clean"
EMBEDDINGS_TABLE = "career_os.ai.job_embeddings"
CDF_ANALYTICS_TABLE = "career_os.analytics.jobs_cdf"
JOB_CHANGE_SUMMARY_TABLE = "career_os.analytics.job_change_summary"
WAREHOUSE_ID = "d7aa18d58fb686f5"

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

_client = None

def get_client():
    global _client
    if _client is None:
        _client = WorkspaceClient()
    return _client

def cosine_similarity(a, b):
    if isinstance(a, str):
        a = json.loads(a)
    if isinstance(b, str):
        b = json.loads(b)

    a = np.asarray([float(x) for x in a],dtype=np.float32)
    b = np.asarray([float(x) for x in b],dtype=np.float32)

    denominator = (np.linalg.norm(a) * np.linalg.norm(b))

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)

def normalize_text(value):
    if not value:
        return ""

    value = str(value).lower()
    value = re.sub(
        r"[^a-z0-9+#. ]",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()

def location_matches(
    job_location,
    requested_location,
):
    if not requested_location:
        return True

    job_location = normalize_text(
        job_location
    )

    requested_location = normalize_text(
        requested_location
    )

    if requested_location == "remote":
        return "remote" in job_location

    return (
        requested_location
        in job_location
    )

def calculate_role_score(
    job_title,
    requested_role,
):
    if not requested_role:
        return 0.0

    title = normalize_text(
        job_title
    )

    role = normalize_text(
        requested_role
    )

    if title == role:
        return 1.0

    if role in title:
        return 0.9

    role_words = set(
        role.split()
    )

    title_words = set(
        title.split()
    )

    if not role_words:
        return 0.0

    overlap = (
        len(
            role_words
            & title_words
        )
        / len(role_words)
    )

    return overlap

def calculate_skill_score(
    job,
    requested_skills,
):
    if not requested_skills:
        return 0.0

    job_text = normalize_text(
        (
            str(
                job.get(
                    "title",
                    "",
                )
            )
            + " "
            + str(
                job.get(
                    "description",
                    "",
                )
            )
        )
    )

    matches = 0

    for skill in requested_skills:
        normalized_skill = (
            normalize_text(
                skill
            )
        )

        if normalized_skill in job_text:
            matches += 1

    return (
        matches
        / len(requested_skills)
    )

def load_jobs(client):
    sql = f"""
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
    """

    response = (
        client
        .statement_execution
        .execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=sql,
            wait_timeout="30s"
        )
    )

    if (
        response.result is None
        or response.result.data_array is None
    ):
        return {}

    jobs = {}

    for row in (
        response
        .result
        .data_array
    ):
        jobs[
            str(row[0])
        ] = {
            "job_id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "salary_min": row[4],
            "salary_max": row[5],
            "description": row[6],
            "job_url": row[7],
        }

    return jobs

def load_embeddings(client):
    sql = f"""
    SELECT
        job_id,
        embedding
    FROM {EMBEDDINGS_TABLE}
    """

    response = (
        client
        .statement_execution
        .execute_statement(
            warehouse_id=WAREHOUSE_ID,
            statement=sql,
            wait_timeout="30s"
        )
    )

    if (
        response.result is None
        or response.result.data_array is None
    ):
        return []

    return (
        response
        .result
        .data_array
    )

def get_job_market_analytics():
    client = get_client()

    sql = f"""
    SELECT
        COUNT(
            CASE
                WHEN _change_type = 'insert'
                THEN 1
            END
        ) AS new_jobs,
        COUNT(
            DISTINCT location
        ) AS active_locations,
        COUNT(
            DISTINCT company
        ) AS active_companies,
        MAX(
            _commit_timestamp
        ) AS last_refresh
    FROM {CDF_ANALYTICS_TABLE}
    """

    try:
        response = (
            client
            .statement_execution
            .execute_statement(
                warehouse_id=WAREHOUSE_ID,
                statement=sql,
                wait_timeout="30s",
            )
        )

        if (
            response.result is None
            or response.result.data_array is None
            or not response.result.data_array
        ):
            return {
                "new_jobs": 0,
                "active_locations": 0,
                "active_companies": 0,
                "last_refresh": None,
            }

        row = (
            response
            .result
            .data_array[0]
        )

        return {
            "new_jobs": int(
                row[0]
                or 0
            ),
            "active_locations": int(
                row[1]
                or 0
            ),
            "active_companies": int(
                row[2]
                or 0
            ),
            "last_refresh": (
                str(
                    row[3]
                )
                if row[3]
                else None
            ),
        }

    except Exception:
        return {
            "new_jobs": 0,
            "active_locations": 0,
            "active_companies": 0,
            "last_refresh": None,
        }

def get_top_job_markets(
    limit=10,
):
    client = get_client()

    limit = max(
        1,
        min(
            int(limit),
            25,
        ),
    )

    sql = f"""
    SELECT
        location,
        SUM(
            job_changes
        ) AS new_jobs
    FROM {JOB_CHANGE_SUMMARY_TABLE}
    WHERE _change_type = 'insert'
    GROUP BY location
    ORDER BY new_jobs DESC
    LIMIT {limit}
    """

    try:
        response = (
            client
            .statement_execution
            .execute_statement(
                warehouse_id=WAREHOUSE_ID,
                statement=sql,
                wait_timeout="30s",
            )
        )

        if (
            response.result is None
            or response.result.data_array is None
        ):
            return []

        results = []

        for row in (
            response
            .result
            .data_array
        ):
            results.append(
                {
                    "location": (
                        row[0]
                        or "Unknown"
                    ),
                    "new_jobs": int(
                        row[1]
                        or 0
                    ),
                }
            )

        return results

    except Exception:
        return []

def get_recent_job_changes(
    limit=10,
):
    client = get_client()

    limit = max(
        1,
        min(
            int(limit),
            25,
        ),
    )

    sql = f"""
    SELECT
        job_id,
        title,
        company,
        location,
        _change_type,
        _commit_timestamp
    FROM {CDF_ANALYTICS_TABLE}
    ORDER BY
        _commit_timestamp DESC
    LIMIT {limit}
    """

    try:
        response = (
            client
            .statement_execution
            .execute_statement(
                warehouse_id=WAREHOUSE_ID,
                statement=sql,
                wait_timeout="30s",
            )
        )

        if (
            response.result is None
            or response.result.data_array is None
        ):
            return []

        results = []

        for row in (
            response
            .result
            .data_array
        ):
            results.append(
                {
                    "job_id": str(
                        row[0]
                    ),
                    "title": (
                        row[1]
                        or "Unknown Job"
                    ),
                    "company": (
                        row[2]
                        or "Unknown Company"
                    ),
                    "location": (
                        row[3]
                        or "Unknown Location"
                    ),
                    "change_type": (
                        row[4]
                        or "unknown"
                    ),
                    "commit_timestamp": (
                        str(
                            row[5]
                        )
                        if row[5]
                        else None
                    ),
                }
            )

        return results

    except Exception:
        return []

def semantic_job_search(
    query,
    top_k=10,
):
    intent = parse_job_intent(
        query
    )

    role = intent["role"]
    location = intent["location"]
    skills = intent["skills"]

    semantic_parts = []

    if role:
        semantic_parts.append(
            role
        )

    if skills:
        semantic_parts.extend(
            skills
        )

    if semantic_parts:
        semantic_query = " ".join(
            semantic_parts
        )
    else:
        semantic_query = query

    model = get_model()

    query_embedding = (
        model
        .encode(
            semantic_query
        )
        .tolist()
    )

    profile_embedding = None

    try:
        current_user = (
            get_current_user()
        )

        if current_user:
            stored_profile = (
                get_profile_embedding(
                    current_user[
                        "user_id"
                    ]
                )
            )

            if stored_profile:
                profile_embedding = (
                    stored_profile
                    .get(
                        "embedding"
                    )
                )

    except Exception:
        profile_embedding = None

    client = get_client()

    jobs = load_jobs(
        client
    )

    embeddings = (
        load_embeddings(
            client
        )
    )

    if (
        not jobs
        or not embeddings
    ):
        return []

    matches = []

    for row in embeddings:
        job_id = str(
            row[0]
        )

        embedding = row[1]

        job = jobs.get(
            job_id
        )

        if job is None:
            continue

        if not location_matches(
            job.get(
                "location"
            ),
            location,
        ):
            continue

        semantic_score = (
            cosine_similarity(
                query_embedding,
                embedding,
            )
        )

        if (
            profile_embedding
            is not None
        ):
            profile_score = (
                cosine_similarity(
                    profile_embedding,
                    embedding,
                )
            )
        else:
            profile_score = 0.0

        role_score = (
            calculate_role_score(
                job.get(
                    "title"
                ),
                role,
            )
        )

        skill_score = (
            calculate_skill_score(
                job,
                skills,
            )
        )

        final_score = (
            semantic_score * 0.50
            + profile_score * 0.25
            + role_score * 0.15
            + skill_score * 0.10
        )

        matches.append(
            {
                "job_id": job_id,
                "semantic_score": semantic_score,
                "profile_score": profile_score,
                "role_score": role_score,
                "skill_score": skill_score,
                "final_score": final_score,
            }
        )

    matches.sort(
        key=lambda x: x[
            "final_score"
        ],
        reverse=True,
    )

    matches = matches[
        :top_k
    ]

    results = []

    for match in matches:
        job = jobs.get(
            match[
                "job_id"
            ]
        )

        if job is None:
            continue

        result = dict(
            job
        )

        result[
            "similarity"
        ] = match[
            "semantic_score"
        ]

        result[
            "profile_score"
        ] = match[
            "profile_score"
        ]

        result[
            "final_score"
        ] = match[
            "final_score"
        ]

        result[
            "role_score"
        ] = match[
            "role_score"
        ]

        result[
            "skill_score"
        ] = match[
            "skill_score"
        ]

        result[
            "intent"
        ] = intent

        results.append(
            result
        )

    return results