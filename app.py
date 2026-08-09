import streamlit as st
from job_search import (
    semantic_job_search,
    get_job_market_analytics,
    get_top_job_markets,
    get_recent_job_changes,
)
from lakebase_actions import (
    get_current_user,
    get_profile,
    get_skills,
    save_skill,
    delete_skill,
    save_job,
    save_profile,
    get_saved_jobs,
    update_application_status,
    get_applications,
    add_interview_note,
    get_interview_notes,
    get_stale_applications,
    update_follow_up_date,
)
from ai_agent import run_career_agent
from job_match import analyze_job_match
from profile_embedding import save_profile_embedding

st.set_page_config(
    page_title="CareerOS",
    page_icon="🚀",
    layout="wide",
)

# Custom CSS for enhanced aesthetics and better text visibility
st.markdown("""
<style>
    /* Global styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        background: rgba(255, 255, 255, 0.98);
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        margin-top: 2rem;
    }
    
    /* Headers - High contrast for visibility */
    h1 {
        color: #1a202c !important;
        font-weight: 800 !important;
        font-size: 3.5rem !important;
        margin-bottom: 0.5rem !important;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    h2 {
        color: #1a202c !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    
    h3 {
        color: #1a202c !important;
        font-weight: 600 !important;
        margin-top: 1.5rem;
    }
    
    /* Body text - High contrast */
    p, div, span, label {
        color: #2d3748 !important;
    }
    
    /* Bold text */
    strong, b {
        color: #1a202c !important;
        font-weight: 700 !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f7fafc;
        border-radius: 10px;
        padding: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: white;
        border-radius: 8px;
        color: #1a202c !important;
        font-weight: 600;
        padding: 0 24px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #edf2f7;
        border-color: #667eea;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Metrics styling */
    [data-testid="stMetricValue"] {
        font-size: 2.5rem !important;
        font-weight: 800 !important;
        color: #667eea !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-weight: 700 !important;
        color: #1a202c !important;
        font-size: 1rem !important;
    }
    
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #667eea;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    [data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.25);
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 700 !important;
        border: none;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        color: #1a202c !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 700 !important;
    }
    
    .stButton > button[kind="secondary"] {
        background-color: #ffffff !important;
        color: #1a202c !important;
        border: 2px solid #e2e8f0 !important;
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select,
    .stNumberInput > div > div > input,
    .stDateInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #cbd5e0;
        padding: 0.75rem;
        font-size: 1rem;
        color: #1a202c !important;
        background-color: white;
        transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus,
    .stNumberInput > div > div > input:focus,
    .stDateInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.15);
    }
    
    /* Input labels */
    .stTextInput label, .stTextArea label, .stSelectbox label, 
    .stNumberInput label, .stDateInput label {
        color: #1a202c !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f7fafc;
        border-radius: 8px;
        font-weight: 700 !important;
        color: #1a202c !important;
        padding: 1rem;
        border-left: 4px solid #667eea;
        font-size: 1.1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background-color: #edf2f7;
    }
    
    /* Success/Warning/Info/Error messages */
    .stSuccess {
        background-color: #f0fdf4 !important;
        border-left: 5px solid #10b981 !important;
        border-radius: 8px;
        padding: 1rem;
        color: #065f46 !important;
        font-weight: 600 !important;
    }
    
    .stWarning {
        background-color: #fffbeb !important;
        border-left: 5px solid #f59e0b !important;
        border-radius: 8px;
        padding: 1rem;
        color: #92400e !important;
        font-weight: 600 !important;
    }
    
    .stInfo {
        background-color: #eff6ff !important;
        border-left: 5px solid #3b82f6 !important;
        border-radius: 8px;
        padding: 1rem;
        color: #1e40af !important;
        font-weight: 600 !important;
    }
    
    .stError {
        background-color: #fef2f2 !important;
        border-left: 5px solid #ef4444 !important;
        border-radius: 8px;
        padding: 1rem;
        color: #991b1b !important;
        font-weight: 600 !important;
    }
    
    /* Link buttons */
    .stLinkButton > a {
        border-radius: 8px;
        font-weight: 700 !important;
        text-decoration: none;
        color: #1a202c !important;
        background-color: white;
        border: 2px solid #e2e8f0;
        transition: all 0.3s ease;
        padding: 0.75rem 1.5rem;
        display: inline-block;
    }
    
    .stLinkButton > a:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.3);
        border-color: #667eea;
    }
    
    /* Chat messages */
    .stChatMessage {
        background-color: #f7fafc;
        border-radius: 12px;
        padding: 1.25rem;
        margin: 0.75rem 0;
        border-left: 4px solid #667eea;
        color: #1a202c !important;
    }
    
    .stChatMessage p {
        color: #2d3748 !important;
    }
    
    /* Caption text */
    .caption {
        color: #4a5568 !important;
        font-size: 0.875rem;
        font-weight: 500 !important;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        h1 {
            font-size: 2.5rem !important;
        }
        
        .main .block-container {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

if "results" not in st.session_state:
    st.session_state["results"] = []

if "search_query" not in st.session_state:
    st.session_state["search_query"] = ""

if "intent" not in st.session_state:
    st.session_state["intent"] = {}

if "agent_messages" not in st.session_state:
    st.session_state["agent_messages"] = []

if "agent_conversation" not in st.session_state:
    st.session_state["agent_conversation"] = []

try:
    current_user = get_current_user()
    if current_user:
        current_profile = get_profile(
            current_user["user_id"]
        ) or {}
        current_skills = get_skills(
            current_user["user_id"]
        )
        user_context = {
            "target_role": current_profile.get(
                "target_role"
            ),
            "preferred_location": current_profile.get(
                "preferred_location"
            ),
            "preferred_work_mode": current_profile.get(
                "preferred_work_mode"
            ),
            "salary_min": current_profile.get(
                "salary_min"
            ),
            "years_experience": current_profile.get(
                "years_experience"
            ),
            "resume_text": current_profile.get(
                "resume_text"
            ),
            "skills": [
                skill["skill_name"]
                for skill in current_skills
                if skill.get("skill_name")
            ],
        }
    else:
        user_context = None
except Exception:
    current_user = None
    user_context = None

st.title("🚀 CareerOS")

st.write("AI-powered job discovery, application tracking, and career assistance built on Databricks.")

dashboard_tab, search_tab, profile_tab, saved_tab, applications_tab, agent_tab = st.tabs(
    [
        "📊 Dashboard",
        "🔎 Search Jobs",
        "👤 Profile",
        "⭐ Saved Jobs",
        "📋 Applications",
        "🤖 Career Agent",
    ]
)

with dashboard_tab:
    st.subheader("📊 Career Dashboard")

    if not current_user:
        st.warning("Unable to load your CareerOS dashboard.")

    else:
        try:
            dashboard_saved_jobs = get_saved_jobs(current_user["user_id"])
        except Exception:
            dashboard_saved_jobs = []

        try:
            dashboard_applications = get_applications(current_user["user_id"])
        except Exception:
            dashboard_applications = []


        try:
            dashboard_stale = get_stale_applications(current_user["user_id"],stale_days=7,)
        except Exception:
            dashboard_stale = []


        applied_count = 0
        interviewing_count = 0
        offer_count = 0
        rejected_count = 0

        for application in dashboard_applications:
            status = (application.get("status") or "").lower()

            if status == "applied":
                applied_count += 1
            elif status == "interviewing":
                interviewing_count += 1
            elif status == "offer":
                offer_count += 1
            elif status == "rejected":
                rejected_count += 1


        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = (st.columns(5))

        with metric_col1:
            st.metric("⭐ Saved",len(dashboard_saved_jobs),)

        with metric_col2:
            st.metric("📨 Applied",applied_count,)

        with metric_col3:
            st.metric("🎤 Interviewing",interviewing_count,)

        with metric_col4:st.metric("🏆 Offers",offer_count,)

        with metric_col5:
            st.metric("⏰ Need Follow-up",len(dashboard_stale),)

        st.divider()

        st.subheader("👤 Career Target")

        if user_context:
            profile_col1, profile_col2, profile_col3 = (st.columns(3))

            with profile_col1:
                st.write("**Target Role**")
                st.write(user_context.get("target_role") or "Not set")

            with profile_col2:
                st.write("**Preferred Location**")
                st.write(user_context.get("preferred_location") or "Not set")

            with profile_col3:
                st.write("**Experience**")
                years = user_context.get("years_experience")

                if years is not None:
                    st.write(f"{years} years")
                else:
                    st.write("Not set")

            profile_skills = (user_context.get("skills") or [])

            if profile_skills:
                st.write("**Skills:** " + ", ".join(profile_skills))

        else:
            st.info("Complete your CareerOS profile to unlock personalized insights.")

        st.divider()

        st.subheader("📋 Application Pipeline")

        pipeline_col1, pipeline_col2, pipeline_col3, pipeline_col4 = (st.columns(4))

        with pipeline_col1:
            st.write("**Applied**")
            st.write(f"### {applied_count}")

        with pipeline_col2:
            st.write("**Interviewing**")
            st.write(f"### {interviewing_count}")

        with pipeline_col3:
            st.write("**Offers**")
            st.write(f"### {offer_count}")

        with pipeline_col4:
            st.write("**Rejected**")
            st.write(f"### {rejected_count}")

        st.divider()

        st.subheader("⏰ Follow-up Alerts")

        if dashboard_stale:
            st.warning(f"{len(dashboard_stale)} application(s) " f"have not been updated in 7+ days.")

            for application in dashboard_stale[:5]:
                title = (application.get("title") or "Unknown Job")
                company = (application.get("company") or "Unknown Company")
                status = (application.get("status") or "unknown")
                st.write(f"**{title}** · {company} "f"— {status.title()}")

        else:
            st.success("No stale applications right now.")

        st.divider()
        
        st.subheader("📊 Job Market Activity")

        try:
            market_analytics = get_job_market_analytics()
            top_markets = get_top_job_markets(limit=5)
            recent_changes = get_recent_job_changes(limit=8)
        except Exception as e:
            st.warning("Job market analytics are temporarily unavailable.")

            market_analytics = {}
            top_markets = []
            recent_changes = []

        analytics_col1, analytics_col2, analytics_col3 = (st.columns(3))

        with analytics_col1:
            st.metric("🆕 Jobs Captured",market_analytics.get("new_jobs",0),)

        with analytics_col2:
            st.metric("📍 Active Locations",market_analytics.get("active_locations",0),)

        with analytics_col3:
            st.metric("🏢 Active Companies",market_analytics.get("active_companies",0),)

        last_refresh = market_analytics.get("last_refresh")

        if last_refresh:
            st.caption(f"Last job-market refresh: {last_refresh}")

        st.markdown("#### 🌎 Top Job Markets")

        if top_markets:
            for market in top_markets:
                location = (market.get("location") or "Unknown Location")
                new_jobs = market.get("new_jobs",0,)

                st.write(f"**{location}** — {new_jobs:,} new jobs")
        else:
            st.info("No job-market analytics available yet.")

        st.markdown("#### ⚡ Recent Job Feed Activity")

        if recent_changes:
            for change in recent_changes:
                title = (change.get("title") or "Unknown Job")
                company = (change.get("company") or "Unknown Company")
                location = (change.get("location") or "Unknown Location")
                change_type = (change.get("change_type") or "unknown")
                timestamp = change.get("commit_timestamp")

                if change_type == "insert":
                    change_icon = "🟢"
                    change_label = "New"
                elif change_type == "update_postimage":
                    change_icon = "🟡"
                    change_label = "Updated"
                elif change_type == "delete":
                    change_icon = "🔴"
                    change_label = "Removed"
                else:
                    change_icon = "⚪"
                    change_label = change_type.replace("_"," ").title()

                st.write(f"{change_icon} **{change_label}:** {title} · {company}")

                st.caption(
                    f"{location}"
                    + (
                        f" · {timestamp}"
                        if timestamp
                        else ""
                    )
                )
        else:
            st.info("No recent CDF job activity found.")

        st.divider()

        st.subheader("🕒 Recent Applications")

        if dashboard_applications:
            for application in dashboard_applications[:5]:
                title = (application.get("title") or "Unknown Job")
                company = (application.get("company") or "Unknown Company")
                status = (application.get("status") or "saved")
                st.write(f"**{title}** · {company}")
                st.caption(f"Status: {status.title()}")
        else:
            st.info("No applications yet.")

with search_tab:

    st.subheader("Find your next opportunity")

    query = st.text_input(
        "What kind of job are you looking for?",
        value=st.session_state["search_query"],
        placeholder=("Senior Data Engineer using Python, Spark and Databricks in Dallas"
        ),
        key="job_search_input",
    )

    if st.button(
        "🔎 Search Jobs",
        type="primary",
        key="search_jobs_button",
    ):

        if not query.strip():
            st.warning("Please enter a job search.")

        else:
            with st.spinner("Finding the best matches..."):

                try:
                    results = semantic_job_search(query, top_k=10,)

                    st.session_state["results"] = results
                    st.session_state["search_query"] = query

                    if results:
                        st.session_state["intent"] = (results[0].get("intent",{},))
                    else:
                        st.session_state["intent"] = {}

                except Exception as e:
                    st.error(
                        "Something went wrong while searching."
                    )
                    st.exception(e)

                    st.session_state["results"] = []
                    st.session_state["intent"] = {}

    results = st.session_state["results"]
    intent = st.session_state["intent"]

    if results:

        st.success(f"Found {len(results)} matching jobs.")

        if intent:
            with st.expander("🔎 Search understood", expanded=True,):

                role_col, location_col, skills_col = (st.columns(3))
                with role_col:
                    st.write("**Role**")
                    st.write(intent.get("role") or "Any")

                with location_col:
                    st.write("**Location**")
                    st.write(intent.get("location") or "Any")

                with skills_col:
                    st.write("**Skills**")

                    skills = intent.get("skills",[],)

                    st.write(
                        ", ".join(skills)
                        if skills
                        else "Any"
                    )

        for job in results:
            match = analyze_job_match(job,user_context,)
            st.markdown(f"### {job.get('title') or 'Unknown Job'}")

            company = (job.get("company") or "Unknown company")
            location = (job.get("location") or "Location unavailable")

            st.write(f"**{company}** · {location}")
            st.write(f"🎯 CareerOS Match: " f"**{match['match_score']:.1f}%**")
            st.write(f"🧠 Profile similarity: " f"**{job.get('profile_score', 0) * 100:.1f}%**")
            st.write(f"**Recommendation: " f"{match['match_label']}**")
            with st.expander("Why this score"):
                metric_col1, metric_col2 = (st.columns(2))
                
                with metric_col1:
                    st.write(f"🧠 Skills: " f"{match['skill_score']:.0f}%")
                    st.write(f"🎯 Role: " f"{match['role_score']:.0f}%")
                    st.write(f"📍 Location: " f"{match['location_score']:.0f}%")
                    st.write(f"🏢 Work mode: " f"{match['work_mode_score']:.0f}%")

                with metric_col2:
                    st.write(f"🔎 Semantic fit: " f"{match['semantic_score']:.0f}%")
                    st.write(f"📈 Experience: " f"{match['experience_score']:.0f}%")
                    st.write(f"💰 Salary: " f"{match['salary_score']:.0f}%")
                    
                if match["matching_skills"]:
                    st.write("✅ **Matching skills:** " + ", ".join(match["matching_skills"]))
                    
                if match["missing_skills"]:
                    st.write("⚠️ **Skill gaps:** " + ", ".join(match["missing_skills"][:5]))
                
                if match.get("required_years") is not None:
                    st.write(f"📅 Job appears to request " f"{match['required_years']:.0f}+ " f"years of experience.")
                    
                st.write(f"💡 {match['recommendation']}")

            salary_max = job.get("salary_max")
            if salary_max is not None:
                try:
                    st.write(f"💰 Up to " f"${float(salary_max):,.0f}")
                except (ValueError,TypeError,):
                    pass

            description = str(job.get("description") or "")

            if len(description) > 500:
                description = (description[:500] + "...")

            st.write(description)

            action_col1, action_col2, action_col3 = (st.columns(3))

            job_url = job.get("job_url")

            with action_col1:
                if job_url:
                    st.link_button("View Job ↗",job_url,use_container_width=True,)
                else:
                    st.button("View Job ↗",disabled=True,key=(f"view_disabled_" f"{job['job_id']}"),use_container_width=True,)

            with action_col2:
                if st.button("⭐ Save Job",key=f"save_{job['job_id']}",use_container_width=True,):
                    if not current_user:
                        st.error("Unable to load the current user.")
                    else:
                        try:
                            save_job(user_id=current_user["user_id"],
                                job_id=job["job_id"],
                                title=job.get("title"),
                                company=job.get("company"),
                                location=job.get("location"),
                                job_url=job.get("job_url"),
                                description=job.get("description"),
                            )

                            st.success("⭐ Job saved.")

                        except Exception as e:
                            st.error("Unable to save this job.")
                            st.exception(e)

            with action_col3:
                if st.button("✅ Mark Applied",key=f"apply_{job['job_id']}",use_container_width=True,):
                    if not current_user:
                        st.error("Unable to load the current user.")
                    else:
                        try:
                            save_job(user_id=current_user["user_id"],
                                job_id=job["job_id"],
                                title=job.get("title"),
                                company=job.get("company"),
                                location=job.get("location"),
                                job_url=job.get("job_url"),
                                description=job.get("description"),
                            )

                            update_application_status(
                                user_id=current_user["user_id"],
                                job_id=job["job_id"],
                                status="applied",
                            )

                            st.success("✅ Job marked as applied.")

                        except Exception as e:
                            st.error("Unable to mark this job as applied."
                            )
                            st.exception(e)

            st.divider()

with profile_tab:
    st.subheader("👤 Career Profile")
    if not current_user:
        st.warning("Unable to load your profile.")
    else:
        try:
            profile = get_profile(current_user["user_id"])
            skills = get_skills(current_user["user_id"])
        except Exception as e:
            st.error("Unable to load profile.")
            st.exception(e)

            profile = None
            skills = []
        profile = profile or {}
        target_role = st.text_input("Target role",
                                    value=(profile.get("target_role") or ""),
                                    placeholder="Senior Data Engineer",)
        preferred_location = st.text_input("Preferred location",
                                           value=(profile.get("preferred_location") or ""),
                                           placeholder="Dallas, TX",)
        work_modes = ["Any",
                      "Remote",
                      "Hybrid",
                      "Onsite",]
        saved_work_mode = (profile.get("preferred_work_mode") or "Any")
        work_mode_index = ( work_modes.index(saved_work_mode)
            if saved_work_mode in work_modes
            else 0
        )
        preferred_work_mode = st.selectbox("Preferred work mode",
                                           work_modes,
                                           index=work_mode_index,)
        salary_min = st.number_input("Minimum salary",
                                     min_value=0,
                                     step=5000,
                                     value=int(profile.get("salary_min") or 0),)
        years_experience = st.number_input("Years of experience",
                                           min_value=0,
                                           max_value=50,
                                           step=1,
                                           value=int(profile.get("years_experience") or 0),
        )

        resume_text = st.text_area("Resume / professional summary",
                                   value=(profile.get("resume_text") or ""),
                                   height=250,
                                   placeholder=("Paste your resume text or professional summary here..."),
        )

        if st.button("💾 Save Profile",type="primary",):
            try:
                save_profile(
                    user_id=current_user["user_id"],
                    target_role=target_role,
                    preferred_location=preferred_location,
                    preferred_work_mode=preferred_work_mode,
                    salary_min=salary_min,
                    years_experience=years_experience,
                    resume_text=resume_text,
                )
                save_profile_embedding(current_user["user_id"])
                st.success("Profile and AI embedding saved.")
                
            except Exception as e:
                st.error("Unable to save profile.")
                st.exception(e)

        st.divider()

        st.subheader("🧠 Skills")

        skill_name = st.text_input("Skill", placeholder="Databricks", key="new_skill_name",)

        proficiency = st.selectbox(
            "Proficiency",
            [
                "Beginner",
                "Intermediate",
                "Advanced",
                "Expert",
            ],
            key="new_skill_proficiency",
        )

        skill_years = st.number_input(
            "Years using this skill",
            min_value=0.0,
            max_value=50.0,
            step=0.5,
            key="new_skill_years",
        )

        if st.button("➕ Add Skill"):
            try:
                save_skill(user_id=current_user["user_id"],
                           skill_name=skill_name,
                           proficiency=proficiency,
                           years_experience=skill_years,
                )
                save_profile_embedding(current_user["user_id"])
                st.success("Skill saved.")
                st.rerun()

            except Exception as e:
                st.error("Unable to save skill.")
                st.exception(e)

        if skills:
            st.write(f"**{len(skills)} skills saved**")

            for skill in skills:
                skill_col1, skill_col2 = (st.columns([4, 1]))

                with skill_col1:
                    st.write(f"**{skill['skill_name']}** — " f"{skill.get('proficiency') or 'Not set'}")

                    if skill.get("years_experience") is not None:
                        st.caption(f"{skill['years_experience']} " f"years experience")

                with skill_col2:
                    if st.button("Remove",key=(f"remove_skill_" f"{skill['skill_id']}"),):
                        delete_skill(current_user["user_id"],skill["skill_name"],)
                        save_profile_embedding(current_user["user_id"]
)

                        st.rerun()
        else:
            st.info("No skills added yet.")

with saved_tab:
    st.subheader("⭐ Saved Jobs")
    if not current_user:
        st.warning("Unable to load your saved jobs.")
    else:
        try:
            saved_jobs = get_saved_jobs(current_user["user_id"])
        except Exception as e:
            st.error("Unable to load saved jobs.")
            st.exception(e)
            saved_jobs = []
        if not saved_jobs:
            st.info("You have not saved any jobs yet.")
        else:
            st.write(f"**{len(saved_jobs)} saved jobs**")
            for job in saved_jobs:
                title = (job.get("title") or "Unknown Job")
                company = (job.get("company") or "Unknown Company")
                location = (job.get("location") or "Location unavailable")
                status = (job.get("status") or "saved")
                
                st.markdown(f"### {title}")
                st.write(f"**{company}** · {location}")
                st.write(f"Status: **{status.title()}**")
                saved_col1, saved_col2, saved_col3, saved_col4, saved_col5 = st.columns(5)

                with saved_col1:
                    if job.get("job_url"):
                        st.link_button("View Job ↗", job["job_url"],use_container_width=True,)

                with saved_col2:
                    if st.button("✅ Mark Applied",key=f"saved_apply_{job['job_id']}",use_container_width=True,):
                        try:
                            update_application_status(
                                user_id=current_user["user_id"],
                                job_id=job["job_id"],
                                status="applied",
                            )

                            st.success("Application marked as applied.")
                            st.rerun()

                        except Exception as e:
                            st.error("Unable to update the application.")
                            st.exception(e)

                with saved_col3:
                    if st.button("✍️ Cover Letter",key=f"cover_letter_{job['job_id']}",use_container_width=True,):
                        try:
                            result = run_career_agent(
                                user_message=(
                                    f"Draft a tailored 2-paragraph "
                                    f"cover letter for job "
                                    f"{job['job_id']}. "
                                    f"Use my CareerOS profile and "
                                    f"the actual job description. "
                                    f"Do not invent experience."
                                ),
                                conversation=[],
                            )

                            st.session_state[f"cover_letter_result_"f"{job['job_id']}"] = result.get("message","",)

                        except Exception as e:
                            st.error("Unable to generate cover letter.")
                            st.exception(e)

                with saved_col4:
                    if st.button("📄 Resume Bullets",key=f"resume_bullets_{job['job_id']}",use_container_width=True,):
                        try:
                            result = run_career_agent(
                                user_message=(
                                    f"Write 3 tailored resume bullets "
                                    f"for job {job['job_id']} "
                                    f"using only experience from "
                                    f"my CareerOS profile."
                                ),
                                conversation=[],
                            )

                            st.session_state[f"resume_bullets_result_" f"{job['job_id']}"] = result.get("message","",)

                        except Exception as e:
                            st.error("Unable to generate resume bullets.")
                            st.exception(e)
                
                with saved_col5:
                    if st.button("🎤 Interview Prep",key=f"interview_prep_{job['job_id']}",use_container_width=True,):
                        try:
                            result = run_career_agent(
                                user_message=(
                                    f"Prepare me for an interview for job "
                                    f"{job['job_id']}. "
                                    f"Use the actual job description and "
                                    f"my CareerOS profile. "
                                    f"Give me likely technical questions, "
                                    f"behavioral questions, key skills to prepare, "
                                    f"STAR story ideas, and questions I should ask."
                                ),
                            conversation=[],
                            )

                            st.session_state[f"interview_prep_result_{job['job_id']}"] = result.get("message","",)

                        except Exception as e:
                            st.error("Unable to generate interview prep.")
                            st.exception(e)

                cover_letter_key = (f"cover_letter_result_"f"{job['job_id']}")
                resume_bullets_key = (f"resume_bullets_result_" f"{job['job_id']}")
                interview_prep_key = (f"interview_prep_result_{job['job_id']}")
                
                if st.session_state.get(cover_letter_key):
                    with st.expander("✍️ Tailored Cover Letter",expanded=True,):
                        st.markdown(st.session_state[cover_letter_key])

                if st.session_state.get(resume_bullets_key):
                    with st.expander("📄 Tailored Resume Bullets",expanded=True,):
                        st.markdown(st.session_state[resume_bullets_key])

                if st.session_state.get(interview_prep_key):
                    with st.expander("🎤 Interview Preparation",expanded=True,):
                        st.markdown(st.session_state[interview_prep_key])

                st.divider()

with applications_tab:
    st.subheader("📋 Applications")

    if not current_user:
        st.warning("Unable to load your applications.")
    else:
        try:
            stale_apps = get_stale_applications(current_user["user_id"],stale_days=7,)
        except Exception:
            stale_apps = []

        if stale_apps:
            st.warning(f"⚠️ {len(stale_apps)} application(s) " f"have not been updated in 7+ days.")

        try:
            applications = get_applications(current_user["user_id"])

        except Exception as e:
            st.error("Unable to load applications.")
            st.exception(e)
            applications = []

        if not applications:
            st.info("No applications yet.")

        else:
            st.write(f"Tracking " f"**{len(applications)} applications**")

            statuses = ["saved",
                "applied",
                "interviewing",
                "rejected",
                "offer",
            ]

            for application in applications:
                application_id = application["application_id"]
                job_id = application["job_id"]
                title = (application.get("title") or "Unknown Job")
                company = (application.get("company") or "Unknown Company")
                location = (application.get("location") or "Location unavailable")
                current_status = (application.get("status") or "saved")
                
                st.markdown(f"### {title}")
                st.write(f"**{company}** · {location}")
                st.write(f"Current status: " f"**{current_status.title()}**")

                applied_at = application.get("applied_at")

                if applied_at:
                    st.write(f"📅 Applied: {applied_at}")

                current_follow_up = (application.get("follow_up_date"))

                if current_follow_up:
                    st.write(f"⏰ Follow-up: " f"{current_follow_up}")

                status_index = (statuses.index(current_status)
                    if current_status in statuses
                    else 0
                )

                new_status = st.selectbox("Application status",options=statuses,index=status_index,key=f"status_{job_id}",)

                status_col, job_col = (st.columns(2))

                with status_col:
                    if st.button("Update Status",key=(f"update_status_" f"{job_id}"),use_container_width=True,):
                        try:
                            update_application_status(
                                user_id=current_user["user_id"],
                                job_id=job_id,
                                status=new_status,
                            )

                            st.success("Application status updated.")
                            st.rerun()

                        except Exception as e:
                            st.error("Unable to update application status.")
                            st.exception(e)

                with job_col:
                    if application.get("job_url"):
                        st.link_button("View Job ↗",application["job_url"],use_container_width=True,)

                follow_up_date = st.date_input("Follow-up date",value=current_follow_up,
                    key=(f"follow_up_" f"{application_id}"),)

                if st.button("📅 Save Follow-up Date",key=(f"save_follow_up_" f"{application_id}"),use_container_width=True,):
                    try:
                        update_follow_up_date(
                            user_id=current_user[
                                "user_id"
                            ],
                            job_id=job_id,
                            follow_up_date=follow_up_date,
                        )

                        st.success("Follow-up date saved.")
                        st.rerun()

                    except Exception as e:
                        st.error("Unable to save follow-up date.")
                        st.exception(e)

                note_text = st.text_area("Interview / follow-up note", key=(f"note_" f"{application_id}"), placeholder=("Technical interview focused on Python, SQL and system design."),)

                if st.button("📝 Save Note",key=(f"save_note_" f"{application_id}"),use_container_width=True,):
                    try:
                        add_interview_note(application_id=application_id,note_text=note_text,follow_up_date=follow_up_date,)

                        st.success("Note saved.")
                        st.rerun()

                    except Exception as e:
                        st.error("Unable to save note.")
                        st.exception(e)

                try:
                    notes = get_interview_notes(application_id)
                except Exception:
                    notes = []

                if notes:
                    with st.expander(f"📝 Notes ({len(notes)})"):
                        for note in notes:
                            st.write(note["note_text"])
                            
                            if note.get("interview_date"):
                                st.caption(f"Interview: " f"{note['interview_date']}")

                            if note.get("follow_up_date"):
                                st.caption(f"Follow-up: " f"{note['follow_up_date']}")

                            st.caption(f"Created: " f"{note['created_at']}")
                            st.divider()

                st.divider()

with agent_tab:

    st.subheader("🤖 Career Agent")
    st.write("Ask CareerOS to search for jobs, save opportunities, and manage your application pipeline.")

    with st.expander("💡 Example requests"):
        st.write("• Find me Data Engineer jobs in Dallas.")
        st.write("• Find Data Analyst jobs in Austin and save the best one.")
        st.write("• Show me my saved jobs.")
        st.write("• Which applications have not been updated in 7 days?")
        st.write("• Mark job 12345 as interviewing.")

    for message in st.session_state["agent_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    agent_prompt = st.chat_input("Ask CareerOS...",key="career_agent_input",)

    if agent_prompt:
        st.session_state["agent_messages"].append({"role": "user","content": agent_prompt,})

        with st.chat_message("user"):
            st.markdown(agent_prompt)

        with st.chat_message("assistant"):
            with st.spinner("CareerOS is working..."):
                try:
                    agent_result = run_career_agent(
                        user_message=agent_prompt,
                        conversation=(st.session_state["agent_conversation"]),
                    )
                    response_text = (agent_result.get("message") or ("CareerOS completed the request but returned no message."))
                    st.markdown(response_text)
                    conversation = (agent_result.get("conversation"))
                    if conversation is not None:
                        st.session_state["agent_conversation"] = conversation
                    st.session_state["agent_messages"].append({"role": "assistant", "content": response_text,})
                except Exception as e:
                    st.error("Career Agent was unable to complete the request.")
                    st.exception(e)

    if st.session_state["agent_messages"]:
        if st.button("Clear Conversation", key="clear_agent_conversation",):
            st.session_state["agent_messages"] = []
            st.session_state["agent_conversation"] = []
            
            st.rerun()