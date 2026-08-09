import json
import os
from databricks_openai import DatabricksOpenAI
from job_search import semantic_job_search
from lakebase_actions import (
    get_current_user,
    get_profile,
    get_skills,
    get_job_posting,
    save_job,
    get_saved_jobs,
    update_application_status,
    get_stale_applications,
)

MODEL_NAME = os.environ.get("CAREEROS_AGENT_MODEL", "databricks-meta-llama-3-3-70b-instruct",)

_client = None

def get_client():
    
    global _client
    if _client is None:
        _client = DatabricksOpenAI()
    return _client

def get_user_context():
    
    user = get_current_user()
    if not user:
        return None
    user_id = user["user_id"]
    profile = get_profile(user_id) or {}
    skills = get_skills(user_id)
    skill_names = [skill["skill_name"] for skill in skills if skill.get("skill_name")]
    
    return {
        "user_id": user_id,
        "full_name": user.get("full_name"),
        "target_role": profile.get("target_role"),
        "preferred_location": profile.get("preferred_location"),
        "preferred_work_mode": profile.get("preferred_work_mode"),
        "salary_min": profile.get("salary_min"),
        "years_experience": profile.get("years_experience"),
        "resume_text": profile.get("resume_text"),
        "skills": skill_names,
    }


SYSTEM_PROMPT = """
You are CareerOS, an AI Job Hunting Copilot.

You help users:
- find relevant jobs
- compare jobs against their career profile
- explain why a job is or is not a good match
- save jobs
- view saved jobs
- track application status
- identify stale applications
- tailor application materials

You have access to the user's stored career profile,
skills, preferences, resume context, saved jobs,
and CareerOS job data through tools.

Important rules:

1. Use search_jobs whenever the user asks for job openings.
2. Do not invent jobs.
3. Use the user's profile and skills when evaluating job fit.
4. Only save jobs that were returned by CareerOS search.
5. If the user asks to save the best N jobs:
   - search first
   - compare the results against the user's profile
   - choose the strongest matches
   - save those jobs
6. Explain relevant strengths and gaps when discussing job fit.
7. Respect the user's target role, preferred location,
   work mode, salary expectations, experience, and skills.
8. Never claim a database write succeeded unless the tool succeeded.
9. Application statuses are:
   saved, applied, interviewing, rejected, offer.

When the user asks to see saved jobs,
always call list_saved_jobs.

When the user asks for a cover letter for a specific job ID,
always call draft_cover_letter before writing the cover letter.

When the user asks for resume bullets for a specific job ID,
always call draft_resume_bullets before writing them.

Never say that CareerOS cannot access saved jobs or job data
when an appropriate CareerOS tool is available.

When drafting application materials:

- Use only facts supported by the user's profile and resume.
- Never invent employers, degrees, certifications, metrics,
  achievements, or technologies the user has not provided.
- Tailor the writing to the actual job description.
- For cover letters, write a concise 1-2 paragraph snippet
  unless the user asks for more.
- For resume bullets, write achievement-oriented bullets
  grounded in the user's background.
- If there is not enough evidence to support a claim,
  do not fabricate it.

When the user asks for interview preparation for a specific job ID,
always call prepare_interview first.

Use the actual job description and the user's stored profile.

Interview preparation should include:
- likely technical questions
- likely behavioral questions
- skills the interviewer is likely to probe
- resume experiences the user should emphasize
- suggested STAR-story angles grounded in the user's actual background
- thoughtful questions the user can ask the interviewer

Do not invent experience, projects, employers, metrics, or technologies
that are not supported by the user's profile or resume.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": ("Search CareerOS for jobs using natural-language semantic search."),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                    },
                    "top_k": {
                        "type": "integer",
                        "default": 5,
                    },
                },
                "required": [
                    "query",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_job",
            "description": ("Save a job returned by CareerOS."),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string",},
                    "title": {"type": "string",},
                    "company": {"type": "string",},
                    "location": {"type": "string",},
                    "job_url": {"type": "string",},
                    "description": {"type": "string",},
                },
                "required": ["job_id","title","company","location",],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_saved_jobs",
            "description": ("Return all jobs saved by the current user."),
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_application_status",
            "description": ("Update an application's pipeline status."),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string",},
                    "status": {
                        "type": "string",
                        "enum": ["saved","applied","interviewing","rejected","offer",],
                    },
                },
                "required": ["job_id","status",],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_stale_applications",
            "description": ("Return applications that have not been updated recently."),
            "parameters": {
                "type": "object",
                "properties": {
                    "stale_days": {
                        "type": "integer",
                        "default": 7,
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_cover_letter",
            "description": ("Retrieve the saved job posting and user profile needed to draft a tailored cover-letter snippet."),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {"type": "string",},
                },
                "required": ["job_id",],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_resume_bullets",
            "description": ("Retrieve the saved job posting and user profile needed to create tailored resume bullets."),
            "parameters": {
                "type": "object",
                "properties": {
                    "job_id": {
                        "type": "string",
                    },
                    "bullet_count": {
                        "type": "integer",
                        "default": 3,
                    },
                },
                "required": ["job_id",],
            },
        },
    },
    {
    "type": "function",
    "function": {
        "name": "prepare_interview",
        "description": ("Retrieve the saved job posting and user profile needed to generate tailored interview preparation."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "job_id": {
                    "type": "string",
                    "description": "CareerOS job ID.",
                },
            },
            "required": ["job_id",],
        },
    },
},
]

def execute_tool(tool_name,arguments,):
    user = get_current_user()
    if not user:
        return {
            "success": False,
            "error": "CareerOS current user was not found.",
        }

    user_id = user["user_id"]
    if tool_name == "search_jobs":
        query = arguments["query"]

        top_k = int(
            arguments.get(
                "top_k",
                5,
            )
        )

        results = semantic_job_search(query,top_k=top_k,)

        clean_results = []

        for job in results:
            clean_results.append(
                {
                    "job_id": str(job.get("job_id")),
                    "title": job.get("title"),
                    "company": job.get("company"),
                    "location": job.get("location"),
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "job_url": job.get("job_url"),
                    "description": job.get("description"),
                    "similarity": round(float(job.get("similarity",0,)),4,),
                }
            )

        return {
            "success": True,
            "count": len(clean_results),
            "jobs": clean_results,
        }

    if tool_name == "save_job":
        save_job(
            user_id=user_id,
            job_id=arguments["job_id"],
            title=arguments.get("title"),
            company=arguments.get("company"),
            location=arguments.get("location"),
            job_url=arguments.get("job_url"),
            description=arguments.get("description"),
        )

        return {
            "success": True,
            "job_id": arguments["job_id"],
            "message": "Job saved successfully.",
        }

    if tool_name == "list_saved_jobs":
        rows = get_saved_jobs(user_id)

        jobs = []

        for row in rows:
            jobs.append(
                {
                    "job_id": str(row.get("job_id")),
                    "title": row.get("title"),
                    "company": row.get("company"),
                    "location": row.get("location"),
                    "status": row.get("status"),
                }
            )

        return {
            "success": True,
            "count": len(jobs),
            "jobs": jobs,
        }

    if tool_name == "update_application_status":
        update_application_status(user_id=user_id,job_id=arguments["job_id"],status=arguments["status"],)

        return {
            "success": True,
            "job_id": arguments["job_id"],
            "status": arguments["status"],
        }

    if tool_name == "get_stale_applications":
        stale_days = int(
            arguments.get(
                "stale_days",
                7,
            )
        )

        rows = get_stale_applications(user_id=user_id,stale_days=stale_days,)

        applications = []

        for row in rows:
            applications.append(
                {
                    "application_id": row.get("application_id"),
                    "job_id": str(row.get("job_id")),
                    "title": row.get("title"),
                    "company": row.get("company"),
                    "status": row.get("status"),
                    "updated_at": str(row.get("updated_at")),
                }
            )

        return {
            "success": True,
            "count": len(applications),
            "applications": applications,
        }

    if tool_name == "draft_cover_letter":
        job = get_job_posting(arguments["job_id"])

        if not job:
            return {
                "success": False,
                "error": "Job posting was not found.",
            }

        profile = get_profile(user_id) or {}
        skills = get_skills(user_id)

        return {
            "success": True,
            "task": "cover_letter",
            "job": {
                "job_id": str(job.get("job_id")),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "description": job.get("description"),
            },
            "profile": {
                "target_role": profile.get("target_role"),
                "years_experience": profile.get("years_experience"),
                "resume_text": profile.get("resume_text"),
                "skills": [skill["skill_name"] for skill in skills if skill.get("skill_name")],
            },
        }

    if tool_name == "draft_resume_bullets":
        job = get_job_posting(arguments["job_id"])

        if not job:
            return {
                "success": False,
                "error": "Job posting was not found.",
            }

        profile = get_profile(user_id) or {}
        skills = get_skills(user_id)

        return {
            "success": True,
            "task": "resume_bullets",
            "bullet_count": int(
                arguments.get("bullet_count",3,)),
            "job": {
                "job_id": str(job.get("job_id")),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "description": job.get("description"),
            },
            "profile": {
                "target_role": profile.get("target_role"),
                "years_experience": profile.get("years_experience"),
                "resume_text": profile.get("resume_text"),
                "skills": [skill["skill_name"] for skill in skills if skill.get("skill_name")],
            },
        }

    if tool_name == "prepare_interview":
        job = get_job_posting(arguments["job_id"])
        if not job:
            return {
                "success": False,
                "error": "Job posting was not found.",
                }

        profile = get_profile(user_id) or {}
        skills = get_skills(user_id)

        return {
            "success": True,
            "task": "interview_prep",
            "job": {
                "job_id": str(job.get("job_id")),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "description": job.get("description"),
                },
                "profile": {"target_role": profile.get("target_role"),
                "years_experience": profile.get("years_experience"),
                "resume_text": profile.get("resume_text"),
                "skills": [skill["skill_name"] for skill in skills if skill.get("skill_name")],
            },
        }

    return {
        "success": False,
        "error": f"Unknown tool: {tool_name}",
    }


def run_career_agent(user_message,conversation=None,):
    client = get_client()
    user_context = get_user_context()
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    if user_context:
        skills_text = (", ".join(user_context.get("skills",[],)) or "Not specified")
        profile_context = f"""
            Current CareerOS user profile:

            Target role:
            {user_context.get("target_role") or "Not specified"}

            Preferred location:
            {user_context.get("preferred_location") or "Not specified"}

            Preferred work mode:
            {user_context.get("preferred_work_mode") or "Not specified"}

            Minimum salary:
            {user_context.get("salary_min") or "Not specified"}

            Years of experience:
            {user_context.get("years_experience") or "Not specified"}

            Skills:
            {skills_text}

            Resume / professional background:
            {user_context.get("resume_text") or "Not provided"}

            Use this profile when:
            - evaluating job relevance
            - ranking or recommending search results
            - explaining strengths and gaps
            - deciding which jobs are best to save
            - tailoring career recommendations
            """

        messages.append(
            {
                "role": "system",
                "content": profile_context,
            }
        )

    if conversation:
        messages.extend(
            conversation
        )

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    for _ in range(6):
        response = (
            client
            .chat
            .completions
            .create(
                model=MODEL_NAME,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.1,
                max_tokens=800,
            )
        )

        assistant_message = (
            response
            .choices[0]
            .message
        )

        messages.append(assistant_message.model_dump(exclude_none=True))

        tool_calls = (assistant_message.tool_calls or [])

        if not tool_calls:
            return {
                "message": (assistant_message.content or ""),
                "conversation": messages,
            }

        for tool_call in tool_calls:
            tool_name = (
                tool_call
                .function
                .name
            )

            try:
                arguments = json.loads(
                    tool_call
                    .function
                    .arguments
                    or "{}"
                )

                tool_result = execute_tool(
                    tool_name,
                    arguments,
                )

            except Exception as e:
                tool_result = {
                    "success": False,
                    "error": str(e),
                }

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": (tool_call.id),
                    "content": json.dumps(tool_result,default=str,),
                }
            )

    return {
        "message": ("CareerOS reached the maximum number of tool actions for this request."),
        "conversation": messages,
    }