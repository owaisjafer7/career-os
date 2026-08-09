from sentence_transformers import SentenceTransformer

from lakebase import (
    run_query,
    run_write,
)

from lakebase_actions import (
    get_profile,
    get_skills,
)


MODEL_NAME = "all-MiniLM-L6-v2"

_model = None


def get_model():
    global _model

    if _model is None:
        _model = SentenceTransformer(
            MODEL_NAME
        )

    return _model


def build_profile_text(
    user_id,
):
    profile = get_profile(
        user_id
    ) or {}

    skills = get_skills(
        user_id
    )

    skill_names = [
        skill["skill_name"]
        for skill in skills
        if skill.get("skill_name")
    ]

    target_role = (
        profile.get("target_role")
        or ""
    )

    preferred_location = (
        profile.get("preferred_location")
        or ""
    )

    preferred_work_mode = (
        profile.get("preferred_work_mode")
        or ""
    )

    years_experience = (
        profile.get("years_experience")
        or ""
    )

    resume_text = (
        profile.get("resume_text")
        or ""
    )

    profile_text = f"""
Target role: {target_role}

Preferred location: {preferred_location}

Preferred work mode: {preferred_work_mode}

Years of experience: {years_experience}

Skills: {", ".join(skill_names)}

Resume:
{resume_text}
"""

    return " ".join(
        profile_text.split()
    )


def generate_profile_embedding(
    user_id,
):
    profile_text = build_profile_text(
        user_id
    )

    if not profile_text.strip():
        raise ValueError(
            "Profile does not contain enough "
            "information to generate an embedding."
        )

    model = get_model()

    embedding = model.encode(
        profile_text
    ).tolist()

    return {
        "profile_text": profile_text,
        "embedding": embedding,
    }


def save_profile_embedding(
    user_id,
):
    result = generate_profile_embedding(
        user_id
    )

    run_write(
        """
        INSERT INTO profile_embeddings (
            user_id,
            profile_text,
            embedding,
            updated_at
        )
        VALUES (
            %s,
            %s,
            %s,
            CURRENT_TIMESTAMP
        )

        ON CONFLICT (user_id)

        DO UPDATE SET
            profile_text = EXCLUDED.profile_text,
            embedding = EXCLUDED.embedding,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            user_id,
            result["profile_text"],
            result["embedding"],
        ),
    )

    return result


def get_profile_embedding(
    user_id,
):
    rows = run_query(
        """
        SELECT
            user_id,
            profile_text,
            embedding,
            updated_at
        FROM profile_embeddings
        WHERE user_id = %s
        LIMIT 1
        """,
        (
            user_id,
        ),
    )

    return rows[0] if rows else None