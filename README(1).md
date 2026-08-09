# 🚀 CareerOS

### AI Job Hunting Copilot

**An end-to-end Databricks AI capstone combining data engineering,
semantic retrieval, Lakebase, and agentic AI.**

`Databricks` · `Apache Spark` · `Delta Lake` · `Lakebase` · `Streamlit` · `AI Agents` · `Embeddings`

*Link: *[*https://career-os-7474659615296236.aws.databricksapps.com/*](https://career-os-7474659615296236.aws.databricksapps.com/)

------------------------------------------------------------------------

## 🌟 Overview

**CareerOS** is an AI-powered job hunting copilot built to make job
discovery and application management more personalized and actionable.

Instead of relying only on keyword search, CareerOS
combines **job-description embeddings** with a user's career profile,
skills, target role, location, work-mode preference, salary
expectations, and experience. The application can search and rank jobs,
explain match quality, save jobs, track application status, generate
tailored application materials, prepare users for interviews, and
surface stale applications.

### ✅ Capstone Requirements Covered

CareerOS implements every core capstone requirement, including **Change
Data Feed (CDF) → Delta Analytics**.

  ------------------------------------------------------------------------------------
  Requirement         CareerOS Implementation                      Status
  ------------------- ------------------------------- --------------------------------
  ⚡ Spark data       Adzuna → Bronze Delta → Silver                 ✅
  pipeline            Delta → embeddings → CDF        
                      analytics                       

  🌐 Third-party API  Adzuna Jobs API with secrets,                  ✅
                      retries, backoff, timeouts, and 
                      deduplication                   

  📄 Unstructured     Job descriptions plus                          ✅
  data                resume/profile text             

  🧠 Semantic         Sentence Transformer                           ✅
  retrieval           embeddings + cosine             
                      similarity + hybrid ranking     

  🖥️ Databricks App   Streamlit frontend deployed as                 ✅
                      a Databricks App                

  🗄️ Lakebase         Profiles, skills, jobs,                        ✅
                      applications, interview notes,  
                      and contacts                    

  🤖 AI agent         Databricks-served tool-calling                 ✅
                      model with grounded read/write  
                      tools                           

  ✍️ Real agent       Save jobs and update                           ✅
  actions             application status in Lakebase  

  🔄 Delta Change     CDF enabled on                                 ✅
  Data Feed           `career_os.silver.jobs_clean`   

  📊 CDF analytics    Changes written to analytics                   ✅
                      Delta tables and surfaced in    
                      the app                         
  ------------------------------------------------------------------------------------

------------------------------------------------------------------------

## 💡 Why CareerOS?

Traditional job boards mostly answer:

> **"Which postings contain these keywords?"**

CareerOS aims to answer:

> **"Which jobs actually fit this candidate, why do they fit, where are
> the gaps, and what should the candidate do next?"**

CareerOS combines **retrieval, deterministic scoring, persistent user
context, and an agentic action layer** rather than treating an LLM as a
standalone chatbot.

------------------------------------------------------------------------

# ✨ Core Features

## 🔎 Semantic Job Search

Users can search with natural-language requests instead of exact
keywords.

    Data engineer jobs in Dallas with Python and Databricks

    Machine learning engineer jobs in Austin

The search layer parses job intent, embeds the semantic query, compares
it against stored job embeddings, and incorporates role and skill
relevance.

------------------------------------------------------------------------

## 🧠 Profile-Aware Retrieval

CareerOS stores an embedding representing the user's career profile.

Job retrieval can combine:

-   **Query → Job** semantic similarity
-   **Profile → Job** similarity
-   **Target-role** relevance
-   **Requested-skill** relevance

### Search Ranking Formula

Signal Weight

------------------------------------------------------------------------

Semantic similarity **50%** Profile similarity **25%** Role
relevance **15%** Requested-skill relevance **10%**

This makes results personalized even when two users enter similar
searches.

------------------------------------------------------------------------

## 🎯 CareerOS Match Analysis

Individual jobs can be evaluated against the user's stored career
profile.

CareerOS considers:

Dimension Weight

------------------------------------------------------------------------

🧠 Skills **30%** 🔎 Semantic fit **25%** 🎯 Target role **15%** 📈
Experience **10%** 📍 Location **8%** 💰 Salary **7%** 🏢 Work
mode **5%**

Jobs receive an overall recommendation:

       Score Recommendation

------------------------------------------------------------------------

     80--100 🟢 **Strong Apply**
    68--79.9 🔵 **Apply**
    55--67.9 🟡 **Stretch**
    Below 55 🔴 **Weak Match**

CareerOS also exposes component scores and visible skill gaps, making
the recommendation **explainable instead of a black-box percentage**.

------------------------------------------------------------------------

## ⭐ Saved Jobs

Users can save jobs discovered through CareerOS.

Saving a job persists the relevant posting data to **Lakebase** and
creates or updates the user's saved-job record.

------------------------------------------------------------------------

## 📈 Application Tracking

CareerOS supports the application pipeline:

    ⭐ saved → ✅ applied → 🎤 interviewing → 🎉 offer / ❌ rejected

The application layer creates or updates status records while preserving
relevant timestamps.

------------------------------------------------------------------------

## ⏰ Stale Application Detection

CareerOS can identify applications that have not been updated for a
configurable number of days, helping users identify opportunities that
may need a follow-up.

------------------------------------------------------------------------

## ✍️ Tailored Cover Letters

For a saved job, the agent retrieves:

-   Actual stored job posting
-   Job description
-   User profile
-   User skills
-   Resume / professional background

It then creates a concise, tailored cover-letter snippet.

> **Grounding rule:** CareerOS must never invent employers, degrees,
> certifications, metrics, achievements, projects, or technologies that
> are not supported by the user's stored profile or resume.

------------------------------------------------------------------------

## 📄 Tailored Resume Bullets

CareerOS generates job-specific resume bullets using the actual posting
and the candidate's stored background.

The objective is **not** to fabricate a perfect resume. It is to
emphasize genuine experience that is most relevant to the target role.

------------------------------------------------------------------------

## 🎤 Interview Preparation

For a stored job, CareerOS can generate interview preparation grounded
in the actual job description and profile:

-   Likely technical questions
-   Likely behavioral questions
-   Skills the interviewer may probe
-   Resume experiences to emphasize
-   STAR-story angles grounded in actual experience
-   Thoughtful questions to ask the interviewer

------------------------------------------------------------------------

# 🏗️ Architecture

                             ┌─────────────────────┐
                             │     Adzuna API      │
                             │   Live Job Data     │
                             └──────────┬──────────┘
                                        │
                                        ▼
                             ┌─────────────────────┐
                             │  Spark Ingestion    │
                             │  Python + requests  │
                             └──────────┬──────────┘
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │ career_os.bronze.jobs_raw   │
                         │       Delta / Bronze        │
                         └──────────────┬──────────────┘
                                        │
                              Spark Transformations
                                        │
                                        ▼
                         ┌─────────────────────────────┐
                         │ career_os.silver.jobs_clean │
                         │        Delta / Silver       │
                         └──────────────┬──────────────┘
                                        │
                                   Embeddings
                                        │
                                        ▼
                       ┌─────────────────────────────────┐
                       │ career_os.ai.job_embeddings     │
                       └───────────────┬─────────────────┘
                                       │
                          Cosine Similarity / Ranking
                                       │
                                       ▼
    ┌────────────────────┐   ┌──────────────────────────┐
    │ Profile Embedding  │──▶│   Semantic Job Search   │
    └────────────────────┘   └─────────────┬────────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │    CareerOS App      │
                                │ Streamlit / DB App   │
                                └──────────┬───────────┘
                                           │
                                   AI Agent + Tools
                                           │
                      ┌────────────────────┴───────────────────┐
                      │                                        │
                      ▼                                        ▼
            ┌───────────────────┐                   ┌───────────────────┐
            │ Databricks Model  │                   │     Lakebase      │
            │ Tool-calling LLM  │                   │   PostgreSQL      │
            └───────────────────┘                   └───────────────────┘

------------------------------------------------------------------------

# ⚙️ Data Engineering Pipeline

## 🥉 1. Bronze --- Adzuna API Ingestion

CareerOS retrieves live job postings from the **Adzuna Jobs API**.

The ingestion process searches combinations of roles and locations
across data, analytics, machine learning, AI, software engineering, BI,
and related roles.

### Pipeline Features

-   HTTP requests to Adzuna
-   Pagination support
-   Retry handling
-   Exponential backoff
-   Request timeouts
-   API-response parsing
-   Job-ID deduplication
-   Explicit Spark schemas
-   Pipeline timestamps
-   Delta writes

### Bronze Table

    career_os.bronze.jobs_raw

Representative fields:

    job_id
    title
    description
    company
    location
    category
    salary_min
    salary_max
    salary_is_predicted
    latitude
    longitude
    job_url
    created
    pipeline_run_time

------------------------------------------------------------------------

## 🥈 2. Silver --- Clean Job Data

Bronze data is transformed into the cleaned dataset used by CareerOS:

    career_os.silver.jobs_clean

This is the primary structured job source used by the semantic-search
layer.

------------------------------------------------------------------------

## 🧠 3. AI --- Job Embeddings

Unstructured job-description text is embedded and stored for semantic
retrieval:

    career_os.ai.job_embeddings

CareerOS currently uses:

    all-MiniLM-L6-v2

At query time, the user's search is embedded and compared with job
embeddings using **cosine similarity**.

------------------------------------------------------------------------

# 🔄 Change Data Feed & Job-Market Analytics

CareerOS uses **Delta Lake Change Data Feed (CDF)** to turn changes in
the Silver jobs table into an analytics layer consumed by the
application.

CDF is enabled on:

``` sql
career_os.silver.jobs_clean
```

The pipeline reads change records containing:

``` text
_change_type
_commit_version
_commit_timestamp
```

Changes are persisted to:

``` text
career_os.analytics.jobs_cdf
```

A summarized analytics table is also created:

``` text
career_os.analytics.job_change_summary
```

## 📊 Analytics Surfaced in the App

The CareerOS dashboard exposes CDF-backed metrics including:

-   **Jobs Captured**
-   **Active Locations**
-   **Active Companies**
-   **Last Job-Market Refresh**
-   **Top Job Markets**
-   **Recent Job Feed Activity**

The recent activity feed displays individual job changes with job title,
company, location, change type, and commit timestamp.

At the latest validated run, the dashboard displayed **11,185 captured
jobs**, **366 active locations**, and **3,082 active companies**, with
recent CDF events visible directly in the Streamlit interface.

## CDF Data Flow

``` text
career_os.silver.jobs_clean
          │
          │ Delta Change Data Feed
          ▼
career_os.analytics.jobs_cdf
          │
          ├──────────────▶ Recent Job Feed Activity
          │
          ▼
career_os.analytics.job_change_summary
          │
          ├──────────────▶ Top Job Markets
          │
          └──────────────▶ Job Market Metrics
                              │
                              ▼
                         CareerOS App
```

This closes the loop from **operational Delta changes → analytics Delta
tables → visible application analytics**.

------------------------------------------------------------------------

# 🔍 Search & Ranking

## Intent Parsing

Natural-language queries are parsed into:

    role
    location
    skills

Role and requested skills are used to construct a focused semantic
query.

## Location Filtering

When a location is explicitly requested, CareerOS filters results
accordingly. Remote intent can also be detected through location text.

## Semantic Similarity

For query embedding `q` and job embedding `j`:

    cosine(q, j) = (q · j) / (||q|| ||j||)

## Profile Similarity

When a stored profile embedding exists, CareerOS compares it with each
job embedding.

This provides persistent candidate context without requiring users to
repeat their background in every search.

## Hybrid Ranking

Semantic, profile, role, and skill signals are combined into one final
search score.

> **Retrieval answers:** "What should I see?" **Match analysis
> answers:** "How well does this job fit me?"

------------------------------------------------------------------------

# 🗄️ Lakebase Transactional Layer

CareerOS uses **Lakebase / PostgreSQL** for user-specific,
agent-actionable state.

## Tables

Table Purpose

------------------------------------------------------------------------

`users` CareerOS users `profiles` Career preferences and resume
context `skills` Skills, proficiency, and experience `job_postings` Jobs
required by transactional/agent workflows `saved_jobs` Saved
opportunities `applications` Application pipeline
state `interview_notes` Notes tied to
applications `contacts` Career/network contacts

### Profile Context

    target_role
    preferred_location
    preferred_work_mode
    salary_min
    years_experience
    resume_text

------------------------------------------------------------------------

# 🔌 Lakebase Access Layer

Database connectivity is isolated in `lakebase.py`.

    App / Agent
         │
         ▼
    lakebase_actions.py
         │
         ▼
    lakebase.py
         │
         ▼
    Lakebase PostgreSQL

### `lakebase.py`

Responsible for:

-   Retrieving the Lakebase URL from Databricks Secrets
-   Opening PostgreSQL connections with `psycopg2`
-   Providing a SQLAlchemy engine
-   Running parameterized reads
-   Running committed writes

### `lakebase_actions.py`

Provides higher-level operations:

    get_current_user
    get_profile
    save_profile
    get_skills
    save_skill
    delete_skill
    save_job
    get_saved_jobs
    remove_saved_job
    update_application_status
    get_applications
    update_follow_up_date
    add_interview_note
    get_interview_notes
    get_stale_applications
    get_job_posting

------------------------------------------------------------------------

# 🤖 AI Agent

CareerOS includes a **tool-calling AI agent** backed by a
Databricks-served model.

Default model:

    databricks-meta-llama-3-3-70b-instruct

The model can be overridden with:

    CAREEROS_AGENT_MODEL

## 🛠️ Agent Tools

------------------------------------------------------------------------

Tool Purpose Type

------------------------------------------------------------------------

`search_jobs` Semantic job discovery 📖 Read

`save_job` Persist a selected job ✍️ Write

`list_saved_jobs` Retrieve saved jobs 📖 Read

`update_application_status` Change pipeline status ✍️ Write

`get_stale_applications` Find neglected 📖 Read applications

`draft_cover_letter` Retrieve grounded 📖 Read job/profile context

`draft_resume_bullets` Retrieve grounded 📖 Read job/profile context

## `prepare_interview` Retrieve grounded 📖 Read interview context

This is an **agentic workflow**: the model chooses when a tool is
needed, receives structured results, and continues reasoning from those
results.

## Tool Execution Loop

    User
      │
      ▼
     LLM
      │
      ▼
    Tool required?
      │
      ├──── No ────▶ Final Response
      │
      └──── Yes
              │
              ▼
       Execute CareerOS Tool
              │
              ▼
       Structured Result
              │
              ▼
             LLM
              │
              ▼
       Continue / Call Tool

A maximum tool-action loop prevents uncontrolled execution.

## 🛡️ Agent Grounding Rules

The system prompt instructs CareerOS to:

-   Search when job openings are requested
-   Never invent jobs
-   Use stored career context for fit evaluation
-   Retrieve saved jobs through the correct tool
-   Retrieve the actual job before drafting job-specific materials
-   Never claim a database write succeeded unless the tool succeeded
-   Avoid inventing candidate experience
-   Ground cover letters, resume bullets, and interview preparation in
    stored evidence

------------------------------------------------------------------------

# 🖥️ Frontend

CareerOS is delivered through a **Streamlit-based Databricks App**.

The frontend supports:

-   🔎 Job search
-   🎯 Match analysis
-   🧠 Profile similarity
-   ⭐ Saving jobs
-   📋 Saved-job management
-   ✅ Marking applications as applied
-   ✍️ Cover-letter generation
-   📄 Resume-bullet generation
-   🎤 Interview preparation
-   👤 Career-profile management
-   🧰 Skill management

Generated AI outputs are stored in Streamlit session state so
job-specific results remain available during normal interaction.

------------------------------------------------------------------------

# 👤 Profile Management

CareerOS maintains persistent career context:

    Target role
    Preferred location
    Preferred work mode
    Minimum salary
    Years of experience
    Resume / professional background
    Skills

That profile is reused across the system:

                         ┌──────────────────┐
                         │     Profile      │
                         └────────┬─────────┘
                                  │
             ┌────────────────────┼────────────────────┐
             │                    │                    │
             ▼                    ▼                    ▼
       Match Scoring       Profile Embedding      Search Ranking
             │                    │                    │
             └──────────────┬─────┴──────────┬─────────┘
                            ▼                ▼
                     Resume Tailoring   Interview Prep
                            │
                            ▼
                    Cover-Letter Generation

This creates a persistent personalized copilot rather than a stateless
chatbot.

------------------------------------------------------------------------

# 🔐 Security & Secrets

> \[!IMPORTANT\] **Never commit API keys, database URLs, passwords,
> tokens, or exported secret values to Git.**

Sensitive configuration is stored with **Databricks Secrets**.

Recommended organization:

    database
    └── lakebase-url

    adzuna
    ├── app-id
    └── app-key

Example:

    APP_ID = dbutils.secrets.get(
        scope="adzuna",
        key="app-id",
    )

    APP_KEY = dbutils.secrets.get(
        scope="adzuna",
        key="app-key",
    )

The Lakebase connection layer similarly retrieves its database URL from
the configured secret scope and key.

------------------------------------------------------------------------

# 📁 Project Structure

    CareerOS/
    ├── app.py
    ├── ai_agent.py
    ├── job_search.py
    ├── job_intent.py
    ├── profile_embedding.py
    ├── lakebase.py
    ├── lakebase_actions.py
    ├── requirements.txt
    ├── README.md
    └── notebooks/
        ├── adzuna_ingestion
        ├── bronze_to_silver
        ├── job_embeddings
        └── jobs_cdf_analytics

> Notebook names may differ depending on workspace organization.

## Key Modules

Module Responsibility

------------------------------------------------------------------------

`app.py` Streamlit frontend and user workflows `ai_agent.py` Agent
prompt, tools, execution, context
injection `job_search.py` Semantic/profile search and hybrid
ranking `job_intent.py` Natural-language job-intent
parsing `profile_embedding.py` Candidate-profile
embeddings `lakebase.py` Low-level PostgreSQL/Lakebase
access `lakebase_actions.py` CareerOS-specific reads and writes

------------------------------------------------------------------------

# 🏆 Capstone Requirement Coverage

  -----------------------------------------------------------------------------------------------
  Requirement         Implementation                                          Status
  ------------------- ------------------------------------------ --------------------------------
  Spark data pipeline Adzuna ingestion → Bronze → Silver →                      ✅
                      embeddings                                 

  Third-party API     Adzuna Jobs API                                           ✅

  Unstructured-data   Job descriptions and resume/profile text                  ✅
  processing                                                     

  Semantic retrieval  `all-MiniLM-L6-v2` embeddings + cosine                    ✅
                      similarity                                 

  Databricks App      Streamlit CareerOS frontend                               ✅

  Lakebase            Transactional career and application state                ✅

  AI agent            Databricks model + CareerOS tools                         ✅

  Agent read tools    Search, saved jobs, stale applications,                   ✅
                      job/profile retrieval                      

  Agent write tools   Save jobs + update application status                     ✅

  Grounded cover      Actual job posting + stored candidate                     ✅
  letters             context                                    

  Grounded resume     Actual job posting + stored candidate                     ✅
  bullets             context                                    

  Grounded interview  Actual job posting + stored candidate                     ✅
  preparation         context                                    

  Personalized AI     Profile + skills + preferences + profile                  ✅
                      embedding                                  

  Delta Change Data   Enabled on `career_os.silver.jobs_clean`                  ✅
  Feed                                                           

  CDF analytics Delta `career_os.analytics.jobs_cdf`                            ✅
  table                                                          

  CDF summary Delta   `career_os.analytics.job_change_summary`                  ✅
  table                                                          

  Analytics surfaced  Job-market metrics, top markets, recent                   ✅
  in app              change feed                                
  -----------------------------------------------------------------------------------------------

> **CareerOS covers the full capstone architecture: Spark, a third-party
> API, unstructured-data retrieval, a Databricks App, Lakebase, an AI
> agent with real reads/writes, and CDF-backed Delta analytics.**

------------------------------------------------------------------------

# 🔄 End-to-End Workflow

    1️⃣ Build Profile
            ↓
    2️⃣ Search Naturally
            ↓
    3️⃣ Semantic + Profile Ranking
            ↓
    4️⃣ Analyze CareerOS Match
            ↓
    5️⃣ Save Opportunity
            ↓
    6️⃣ Tailor Application
            ↓
    7️⃣ Track Application Status
            ↓
    8️⃣ Prepare for Interview
            ↓
    9️⃣ Identify Follow-Ups

### Example

**1. Build a profile** Store target role, location, salary expectations,
experience, resume context, and skills.

**2. Search naturally**

    Find data engineer jobs in Dallas using Python and Databricks.

**3. Rank personally** Jobs receive query-similarity and
profile-similarity signals.

**4. Analyze a job** CareerOS calculates a multi-factor match score and
explains strengths and gaps.

**5. Save the opportunity** The user or agent persists the job to
Lakebase.

**6. Tailor the application** CareerOS retrieves the actual posting and
profile before generating materials.

**7. Track progress**

    saved → applied → interviewing → offer / rejected

**8. Prepare for interviews** Generate job-specific preparation grounded
in the posting and candidate background.

**9. Follow up** Stale-application logic identifies opportunities that
may need attention.

------------------------------------------------------------------------

# 💬 Example Agent Prompts

    Find data engineer jobs in Dallas.

    Find Python and Databricks jobs in Texas.

    Show me all my saved jobs.

    Save the best 3 jobs for my profile.

    Mark job 5807055900 as applied.

    Draft a tailored 2-paragraph cover letter for job 5807055900.

    Write 3 tailored resume bullets for job 5807055900.

    Prepare me for an interview for job 5807055900.

    Show me applications that have been stale for 7 days.

------------------------------------------------------------------------

# 🧩 Design Decisions

## Delta Lake + Lakebase

CareerOS intentionally uses both technologies for different workloads.

### ⚡ Delta Lake --- Analytical Layer

-   Raw API ingestion
-   Cleaning and transformation
-   Job corpus
-   Embeddings
-   Search-oriented processing
-   Delta Change Data Feed
-   Job-change analytics
-   Job-market summary tables

### 🗄️ Lakebase --- Transactional Layer

-   User profiles
-   Skills
-   Saved jobs
-   Applications
-   Notes
-   Agent writes

This separates analytical workloads from application-state workloads.

## Why Hybrid Ranking?

Embedding similarity alone does not guarantee career fit.

A semantically similar posting can still have the wrong:

-   Seniority
-   Skills
-   Location
-   Salary
-   Work arrangement

CareerOS therefore combines semantic retrieval with structured career
signals.

## Why Separate Retrieval From Match Scoring?

**Retrieval** identifies promising candidates from the job corpus.

**Match analysis** performs a richer, explainable evaluation of a
specific posting.

## Why Ground Generative Features?

Application materials are useful only when they are credible.

CareerOS retrieves the actual job and candidate background before
generation and explicitly prevents unsupported career claims.

------------------------------------------------------------------------

# 🛡️ Reliability Features

-   ✅ API request timeout handling
-   ✅ Retry logic
-   ✅ Exponential backoff
-   ✅ Job deduplication
-   ✅ Explicit Spark schemas
-   ✅ Parameterized SQL
-   ✅ Transaction commits
-   ✅ Database uniqueness constraints
-   ✅ Controlled application statuses
-   ✅ Structured tool success/error responses
-   ✅ Maximum agent tool iterations
-   ✅ Graceful missing-profile/job handling
-   ✅ LLM anti-fabrication instructions

------------------------------------------------------------------------

# 🚀 Running CareerOS

High-level setup:

1.  Configure Databricks access and required compute/SQL resources.
2.  Create the required catalogs, schemas, and Lakebase tables.
3.  Store Adzuna credentials and the Lakebase URL in Databricks Secrets.
4.  Run the Adzuna ingestion pipeline.
5.  Transform Bronze jobs into the Silver dataset.
6.  Generate or refresh job embeddings.
7.  Generate/update the user's profile embedding after profile changes.
8.  Configure the Databricks App environment.
9.  Install application dependencies.
10. Enable/verify CDF on `career_os.silver.jobs_clean`.
11. Run the CDF analytics pipeline to refresh
    `career_os.analytics.jobs_cdf` and
    `career_os.analytics.job_change_summary`.
12. Launch/deploy the Streamlit Databricks App.
13. Create a career profile and skills.
14. Search, analyze, save, track, and interact with jobs through
    CareerOS.
15. Verify the Job Market Activity dashboard displays CDF-backed metrics
    and recent changes.

------------------------------------------------------------------------

# 🧪 Testing Checklist

## ⚡ Data Pipeline

-    Adzuna API requests succeed
-    Bronze table contains jobs
-    Job IDs are deduplicated
-    Silver table contains cleaned jobs
-    Job descriptions are populated
-    Embeddings exist for searchable jobs

## 👤 Profile

-    Profile loads
-    Profile edits persist
-    Skills can be added
-    Skills can be removed
-    Profile embedding is generated/refreshed

## 🔎 Search

-    Natural-language search works
-    Role parsing works
-    Location filtering works
-    Semantic similarity appears
-    Profile similarity appears
-    Results are ranked sensibly

## 🎯 Match Analysis

-    Match score appears
-    Component scores appear
-    Matching skills appear
-    Skill gaps appear
-    Recommendation label is sensible

## 🤖 Agent

-    Agent searches through `search_jobs`
-    Agent lists saved jobs through `list_saved_jobs`
-    Agent can save a valid search result
-    Agent can update application status
-    Cover-letter generation retrieves the actual posting
-    Resume bullets retrieve the actual posting
-    Interview preparation retrieves the actual posting
-    Stale-application lookup works
-    Agent does not fabricate database-write success

## 🔄 Change Data Feed & Analytics

-   CDF is enabled on `career_os.silver.jobs_clean`
-   CDF records include `_change_type`, `_commit_version`, and
    `_commit_timestamp`
-   `career_os.analytics.jobs_cdf` contains job changes
-   `career_os.analytics.job_change_summary` contains aggregated market
    changes
-   Dashboard job-market metrics return non-zero values after ingestion
-   Top Job Markets renders from the analytics layer
-   Recent Job Feed Activity renders CDF-backed job changes

## 🔐 Security

-    Adzuna credentials are not hard-coded
-    Lakebase URL is stored in Databricks Secrets
-    Credentials are not committed to Git
-    Secrets are not printed in notebook output

------------------------------------------------------------------------

# 🗺️ Future Improvements

## Near-Term

-   Add USAJobs or RemoteOK as additional job sources
-   Schedule automatic ingestion and embedding refreshes
-   Add application follow-up reminders
-   Add richer interview-note workflows
-   Improve skill extraction beyond a fixed vocabulary
-   Add job-age/freshness signals
-   Add explicit seniority detection

## Advanced

-   Introduce a production vector-search index
-   Use managed embedding endpoints where appropriate
-   Learn ranking weights from user behavior
-   Add recruiter/contact relationship tracking
-   Generate job-specific application checklists
-   Add agent observability and latency tracking
-   Build a labeled retrieval-quality benchmark
-   Add offline match-score calibration
-   Add multi-user authentication and isolation
-   Add automated data-quality checks and pipeline monitoring

------------------------------------------------------------------------

# 💥 What Makes CareerOS Different?

CareerOS is **not** simply:

    Job API + Chatbot

It connects:

    Live External Data
            +
    Spark Engineering Pipeline
            +
    Unstructured Text Embeddings
            +
    Semantic Retrieval
            +
    Persistent Candidate Profile
            +
    Profile Embedding
            +
    Explainable Match Scoring
            +
    Lakebase Transactional State
            +
    Tool-Calling AI Agent
            +
    Real Database Actions
            +
    Interactive Databricks Frontend

The result is an application where AI is connected to both
an **analytical job corpus** and **persistent transactional state**.

CareerOS moves beyond answering questions and participates in the actual
job-search workflow.

------------------------------------------------------------------------

# 🧰 Tech Stack

Layer Technologies

------------------------------------------------------------------------

Data Platform Databricks Data Engineering Apache Spark / PySpark Storage
Delta Lake Transactional Database Lakebase / PostgreSQL AI
DatabricksOpenAI Model Integration Databricks SDK Frontend Streamlit /
Databricks Apps Embeddings Sentence Transformers Embedding
Model `all-MiniLM-L6-v2` Similarity NumPy / cosine similarity Database
Access `psycopg2`, SQLAlchemy External Data Adzuna Jobs API Language
Python

------------------------------------------------------------------------

# 🔀 Data + AI Flow

    Adzuna
       │
       ▼
    API Ingestion
       │
       ▼
    🥉 Bronze Delta
       │
       ▼
    Spark Cleaning
       │
       ▼
    🥈 Silver Delta
       │
       ├──────────────▶ Structured Job Attributes
       │
       ▼
    Job Descriptions
       │
       ▼
    Embeddings
       │
       ▼
    Semantic Retrieval ◀──── Profile Embedding
       │
       ▼
    Hybrid Ranking
       │
       ▼
    CareerOS UI
       │
       ├────▶ 🎯 Match Explanation
       ├────▶ ⭐ Save Job ──────────┐
       ├────▶ ✍️ Cover Letter      │
       ├────▶ 📄 Resume Bullets    │
       ├────▶ 🎤 Interview Prep    │
       └────▶ 📈 Application Status│
                                    ▼
                                 Lakebase

------------------------------------------------------------------------

# 🎬 Demo Story

A strong CareerOS demo can be completed in a few minutes:

1.  **Show the architecture** --- explain why Delta and Lakebase have
    different responsibilities.
2.  **Show the Spark pipeline** --- demonstrate real Adzuna ingestion.
3.  **Show Bronze and Silver** --- establish the data-engineering
    foundation.
4.  **Show the embeddings layer** --- demonstrate unstructured-data
    processing.
5.  **Open CareerOS** --- show the persistent career profile.
6.  **Run a natural-language job search.**
7.  **Show semantic + profile similarity.**
8.  **Analyze a result** --- explain the CareerOS Match breakdown.
9.  **Save a job** --- demonstrate a real application/database write.
10. **Generate grounded application material** --- resume bullets or a
    cover letter.
11. **Run interview preparation** for the same posting.
12. **Update application status** --- show persistence in Lakebase.
13. **Finish with the full story** --- the same profile, job corpus, and
    transactional history work together across the experience.

------------------------------------------------------------------------

# 🏁 Capstone Summary

CareerOS demonstrates an **end-to-end AI data product**, not an isolated
model demo.

### ⚡ Data Engineering

Live API ingestion, Spark processing, Delta tables, explicit schemas,
deduplication, refreshable data, Delta Change Data Feed, and downstream
analytics tables.

### 🧠 Context Engineering

Job descriptions, resume context, skills, profile data, embeddings, and
hybrid retrieval.

### 🖥️ Application Engineering

Streamlit frontend, persistent Lakebase state, database access layers,
and secrets management.

### 🤖 Agentic AI

Tool selection, structured reads, real writes, multi-step execution, and
grounded generation.

### 💡 Product Thinking

Personalized ranking, explainable match scores, application tracking,
interview preparation, and workflow-oriented AI assistance.

------------------------------------------------------------------------

# 🙏 Acknowledgments

CareerOS was created as an **AI Job Hunting Copilot** capstone using the
Databricks AI/Data Engineering ecosystem and an architecture centered
on **Spark, Lakebase, unstructured retrieval, Databricks Apps, and AI
agents**.

Job-listing data is sourced through the **Adzuna API** according to the
applicable API terms.

------------------------------------------------------------------------

## 👨‍💻 Author

**Owais Jafer**

*Built as an end-to-end Databricks AI capstone demonstrating data
engineering, retrieval, transactional state, and agentic AI in one
application.*

### ⭐ CareerOS --- Find better opportunities. Understand the fit. Take action.

:::
