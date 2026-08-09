import re


STATE_ALIASES = {
    "tx": "texas",
    "ca": "california",
    "ny": "new york",
    "il": "illinois",
    "wa": "washington",
    "fl": "florida",
    "ga": "georgia",
    "ma": "massachusetts",
    "pa": "pennsylvania",
    "az": "arizona",
    "co": "colorado",
    "mn": "minnesota",
    "mi": "michigan",
    "md": "maryland",
    "nj": "new jersey",
    "or": "oregon",
}


SKILL_ALIASES = {
    "pyspark": "spark",
    "apache spark": "spark",
    "postgres": "postgresql",
    "amazon web services": "aws",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "microsoft azure": "azure",
    "apache airflow": "airflow",
}


def normalize_text(value):
    if not value:
        return ""
    return re.sub(r"\s+"," ",str(value).strip().lower(),)


def normalize_location(value):
    text = normalize_text(value)
    text = text.replace(",", " ")
    words = text.split()
    normalized_words = [STATE_ALIASES.get(word,word,) for word in words]
    return " ".join(normalized_words)

def canonical_skill(skill):
    normalized = normalize_text(skill)
    return SKILL_ALIASES.get(normalized,normalized,)

def skill_in_text(skill, text):
    skill = normalize_text(skill)
    text = normalize_text(text)
    if not skill or not text:
        return False
    return skill in text

def analyze_job_match(job,user_context,):
    if not user_context:
        return {
            "match_score": 0,
            "match_label": "Profile Needed",
            "semantic_score": 0,
            "skill_score": 0,
            "role_score": 0,
            "location_score": 0,
            "salary_score": 0,
            "experience_score": 0,
            "work_mode_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": (
                "Complete your CareerOS profile "
                "to receive personalized matching."
            ),
        }

    title = str(job.get("title") or "")
    description = str(job.get("description") or "")
    location = str(job.get("location") or "")
    job_text = (f"{title} {description}")
    known_skills = [
        "Python",
        "SQL",
        "Spark",
        "PySpark",
        "Databricks",
        "AWS",
        "Azure",
        "GCP",
        "Airflow",
        "Kafka",
        "Snowflake",
        "dbt",
        "Docker",
        "Kubernetes",
        "Terraform",
        "Hadoop",
        "Hive",
        "PostgreSQL",
        "MySQL",
        "MongoDB",
        "Cassandra",
        "Redshift",
        "BigQuery",
        "ETL",
        "ELT",
        "Data Modeling",
        "Data Warehousing",
        "Machine Learning",
        "Power BI",
        "Tableau",
        "Git",
        "Java",
        "Scala",
    ]

    required_skills = []

    for skill in known_skills:
        if skill_in_text(skill,job_text,):
            required_skills.append(skill)
    
    required_skills = list(dict.fromkeys(required_skills))
    user_skills = {canonical_skill(skill) for skill in user_context.get("skills",[],) if skill}

    matching_skills = []
    missing_skills = []

    for skill in required_skills:
        normalized = canonical_skill(skill)
        
        if normalized in user_skills:
            matching_skills.append(skill)
        else:
            missing_skills.append(skill)

    if required_skills:
        skill_score = (len(matching_skills) / len(required_skills)) * 100

    else:
        skill_score = 50

    semantic_score = (float(job.get("similarity",0,) or 0) * 100)

    target_role = normalize_text(user_context.get("target_role"))

    normalized_title = normalize_text(title)

    if not target_role:
        role_score = 50

    elif target_role in normalized_title:
        role_score = 100

    else:
        target_words = set(target_role.split())
        title_words = set(normalized_title.split())
        overlap = (len(target_words & title_words) / max(len(target_words),1,))
        role_score = (overlap * 100)

    preferred_location = normalize_location(user_context.get("preferred_location"))
    normalized_location = normalize_location(location)

    if not preferred_location:
        location_score = 50

    elif (
        preferred_location
        in normalized_location
        or normalized_location
        in preferred_location
    ):
        location_score = 100

    else:
        location_score = 25

    preferred_work_mode = normalize_text(user_context.get("preferred_work_mode"))

    combined_text = normalize_text(f"{title} {description} {location}")

    if (not preferred_work_mode or preferred_work_mode == "any"):
        work_mode_score = 75
    elif preferred_work_mode in combined_text:
        work_mode_score = 100
    else:
        work_mode_score = 40

    user_salary_min = (user_context.get("salary_min") or 0)
    job_salary_max = (job.get("salary_max"))

    if not user_salary_min:
        salary_score = 75
    elif job_salary_max is None:
        salary_score = 50
    else:
        try:
            job_salary_max = float(job_salary_max)
            user_salary_min = float(user_salary_min)

            if (job_salary_max >= user_salary_min):
                salary_score = 100
            elif (job_salary_max >= user_salary_min * 0.9):
                salary_score = 70
            else:
                salary_score = 30
        except (ValueError,TypeError,):
            salary_score = 50

    user_years = float(user_context.get("years_experience") or 0)
    required_years = None
    experience_patterns = [
        r"(\d+)\+?\s+years? of experience",
        r"minimum of (\d+)\s+years?",
        r"at least (\d+)\s+years?",
        r"(\d+)\+?\s+years? experience",
    ]

    description_lower = (description.lower())

    for pattern in experience_patterns:
        match = re.search(pattern,description_lower,)
        if match:
            required_years = float(match.group(1))
            break

    if required_years is None:
        experience_score = 70
    elif user_years >= required_years:
        experience_score = 100
    elif user_years >= required_years * 0.75:
        experience_score = 75
    elif user_years >= required_years * 0.5:
        experience_score = 50
    else:
        experience_score = 25

    match_score = (skill_score * 0.30 + semantic_score * 0.25 + role_score * 0.15 + experience_score * 0.10 + location_score * 0.08 + salary_score * 0.07 + work_mode_score * 0.05)
    match_score = round(max(0,min(100,match_score,),),1,)

    if match_score >= 80:
        match_label = ("Strong Apply")
    elif match_score >= 65:
        match_label = ("Apply")
    elif match_score >= 50:
        match_label = ("Stretch")
    else:
        match_label = ("Weak Match")

    if match_label == "Strong Apply":
        recommendation = ("Strong fit for your profile. This should be a high-priority application.")
    elif match_label == "Apply":
        if missing_skills:
            recommendation = ("Good overall fit. " f"Your biggest visible gap is " f"{missing_skills[0]}.")
        else:
            recommendation = ("Good overall fit based on your current CareerOS profile.")
    elif match_label == "Stretch":
        if missing_skills:
            recommendation = ("Possible stretch opportunity. " f"Strengthening {missing_skills[0]} could improve your fit.")
        else:
            recommendation = ("Possible stretch opportunity. Review the experience requirements carefully.")
    else:
        recommendation = ("Lower-priority match based on your current profile and preferences.")


    return {
        "match_score": match_score,
        "match_label": match_label,
        "semantic_score": round(semantic_score,1,),
        "skill_score": round(skill_score,1,),
        "role_score": round(role_score,1,),
        "location_score": round(location_score,1,),
        "salary_score": round(salary_score,1,),
        "experience_score": round(experience_score,1,),
        "work_mode_score": round(work_mode_score,1,),
        "required_years": required_years,
        "required_skills": required_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
    }