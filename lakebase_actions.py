from lakebase import (
    run_query,
    run_write,
)

CURRENT_USER_EMAIL = "demo@careeros.local"


def get_current_user():
    rows = run_query(
        """SELECT user_id, email, full_name FROM users WHERE email = %s LIMIT 1""",(CURRENT_USER_EMAIL,))
    return rows[0] if rows else None

def save_job(user_id,job_id,title,company,location,job_url,description=None,):
    run_write(
        """
        INSERT INTO job_postings (job_id,title,company,location,job_url,description,source)
        VALUES (%s,%s,%s,%s,%s,%s,'Adzuna')
        ON CONFLICT (job_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            company = EXCLUDED.company,
            location = EXCLUDED.location,
            job_url = EXCLUDED.job_url,
            description = EXCLUDED.description,
            updated_at = CURRENT_TIMESTAMP
        """,
        (str(job_id),title,company,location,job_url,description,)
    )

    run_write(
        """INSERT INTO saved_jobs (user_id,job_id,status)
        VALUES (%s,%s,'saved')
        ON CONFLICT (user_id,job_id)
        DO UPDATE SET status = 'saved', updated_at = CURRENT_TIMESTAMP
        """,
        (user_id,str(job_id),)
    )

def get_saved_jobs(user_id):
    return run_query(
        """
        SELECT s.saved_job_id,s.job_id,s.status,s.notes,s.created_at,s.updated_at,j.title,j.company,j.location,j.job_url
        FROM saved_jobs s
        LEFT JOIN job_postings j
            ON s.job_id = j.job_id
        WHERE s.user_id = %s
        ORDER BY s.updated_at DESC
        """,
        (user_id,)
    )

def remove_saved_job(user_id,job_id,):
    return run_write(
        """
        DELETE FROM saved_jobs WHERE user_id = %s AND job_id = %s
        """,
        (
            user_id,str(job_id),
        )
    )

def update_application_status(user_id,job_id,status,):
    allowed_statuses = {"saved","applied","interviewing","rejected","offer",}
    status = str(status).lower()
    if status not in allowed_statuses:
        raise ValueError(f"Invalid application status: " f"{status}")

    run_write(
        """
        INSERT INTO applications (user_id,job_id,status,applied_at)
        VALUES (
            %s,
            %s,
            %s,
            CASE
                WHEN %s = 'applied'
                THEN CURRENT_TIMESTAMP
                ELSE NULL
            END
        )

        ON CONFLICT (
            user_id,
            job_id
        )
        DO UPDATE SET
            status = EXCLUDED.status,
            applied_at = CASE
                WHEN EXCLUDED.status = 'applied'
                     AND applications.applied_at IS NULL
                THEN CURRENT_TIMESTAMP
                ELSE applications.applied_at
            END,
            updated_at = CURRENT_TIMESTAMP
        """,
        (
            user_id,
            str(job_id),
            status,
            status,
        )
    )

def get_applications(user_id):
    return run_query(
        """
        SELECT
            a.application_id,
            a.job_id,
            a.status,
            a.applied_at,
            a.follow_up_date,
            a.notes,
            a.created_at,
            a.updated_at,

            j.title,
            j.company,
            j.location,
            j.job_url

        FROM applications a

        LEFT JOIN job_postings j
            ON a.job_id = j.job_id

        WHERE a.user_id = %s

        ORDER BY
            a.updated_at DESC
        """,
        (
            user_id,
        )
    )


# =========================================================
# UPDATE FOLLOW-UP DATE
# =========================================================

def update_follow_up_date(
    user_id,
    job_id,
    follow_up_date,
):

    return run_write(
        """
        UPDATE applications

        SET
            follow_up_date = %s,
            updated_at = CURRENT_TIMESTAMP

        WHERE user_id = %s
          AND job_id = %s
        """,
        (
            follow_up_date,
            user_id,
            str(job_id),
        )
    )


# =========================================================
# ADD INTERVIEW NOTE
# =========================================================

def add_interview_note(
    application_id,
    note_text,
    interview_date=None,
    follow_up_date=None,
):

    note_text = (
        str(note_text).strip()
        if note_text is not None
        else ""
    )


    if not note_text:

        raise ValueError(
            "Interview note cannot be empty."
        )


    return run_write(
        """
        INSERT INTO interview_notes (
            application_id,
            note_text,
            interview_date,
            follow_up_date
        )

        VALUES (
            %s,
            %s,
            %s,
            %s
        )
        """,
        (
            application_id,
            note_text,
            interview_date,
            follow_up_date,
        )
    )


# =========================================================
# GET INTERVIEW NOTES
# =========================================================

def get_interview_notes(
    application_id
):

    return run_query(
        """
        SELECT
            interview_note_id,
            application_id,
            note_text,
            interview_date,
            follow_up_date,
            created_at

        FROM interview_notes

        WHERE application_id = %s

        ORDER BY
            created_at DESC
        """,
        (
            application_id,
        )
    )


# =========================================================
# GET STALE APPLICATIONS
# =========================================================

def get_stale_applications(
    user_id,
    stale_days=7,
):

    stale_days = int(
        stale_days
    )


    if stale_days < 1:

        raise ValueError(
            "stale_days must be at least 1."
        )


    return run_query(
        """
        SELECT
            a.application_id,
            a.job_id,
            a.status,
            a.applied_at,
            a.follow_up_date,
            a.updated_at,

            j.title,
            j.company,
            j.location,
            j.job_url

        FROM applications a

        LEFT JOIN job_postings j
            ON a.job_id = j.job_id

        WHERE a.user_id = %s

          AND a.status NOT IN (
              'rejected',
              'offer'
          )

          AND a.updated_at
              < CURRENT_TIMESTAMP
                - (%s * INTERVAL '1 day')

        ORDER BY
            a.updated_at ASC
        """,
        (
            user_id,
            stale_days,
        )
    )

# =========================================================
# GET PROFILE
# =========================================================

def get_profile(user_id):
    rows = run_query(
        """
        SELECT
            profile_id,
            user_id,
            target_role,
            preferred_location,
            preferred_work_mode,
            salary_min,
            years_experience,
            resume_text,
            created_at,
            updated_at
        FROM profiles
        WHERE user_id = %s
        LIMIT 1
        """,
        (user_id,),
    )

    return rows[0] if rows else None

def save_profile(
    user_id,
    target_role=None,
    preferred_location=None,
    preferred_work_mode=None,
    salary_min=None,
    years_experience=None,
    resume_text=None,
):
    existing = get_profile(user_id)

    if existing:
        return run_write(
            """
            UPDATE profiles
            SET
                target_role = %s,
                preferred_location = %s,
                preferred_work_mode = %s,
                salary_min = %s,
                years_experience = %s,
                resume_text = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            """,
            (
                target_role,
                preferred_location,
                preferred_work_mode,
                salary_min,
                years_experience,
                resume_text,
                user_id,
            ),
        )

    return run_write(
        """
        INSERT INTO profiles (
            user_id,
            target_role,
            preferred_location,
            preferred_work_mode,
            salary_min,
            years_experience,
            resume_text
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s
        )
        """,
        (
            user_id,
            target_role,
            preferred_location,
            preferred_work_mode,
            salary_min,
            years_experience,
            resume_text,
        ),
    )

def get_skills(user_id):
    return run_query(
        """
        SELECT
            skill_id,
            skill_name,
            proficiency,
            years_experience
        FROM skills
        WHERE user_id = %s
        ORDER BY skill_name
        """,
        (user_id,),
    )

def save_skill(
    user_id,
    skill_name,
    proficiency=None,
    years_experience=None,
):
    skill_name = str(skill_name).strip()

    if not skill_name:
        raise ValueError("Skill name cannot be empty.")

    return run_write(
        """
        INSERT INTO skills (
            user_id,
            skill_name,
            proficiency,
            years_experience
        )
        VALUES (
            %s, %s, %s, %s
        )
        ON CONFLICT (user_id, skill_name)
        DO UPDATE SET
            proficiency = EXCLUDED.proficiency,
            years_experience = EXCLUDED.years_experience
        """,
        (
            user_id,
            skill_name,
            proficiency,
            years_experience,
        ),
    )

def delete_skill(user_id,skill_name,):
    return run_write(
        """DELETE FROM skills WHERE user_id = %s AND skill_name = %s""",
        (user_id, skill_name,),
    )

def get_job_posting(job_id):
    rows = run_query(
        """
        SELECT
            job_id,
            title,
            company,
            location,
            job_url,
            source,
            description
        FROM job_postings
        WHERE job_id = %s
        LIMIT 1
        """,
        (
            str(job_id),
        )
    )

    return rows[0] if rows else None
