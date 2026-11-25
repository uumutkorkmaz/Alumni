# Data Design Documentation (DDD)

> Back to [README.md](README.md)

This document describes the database design of the Alumni Tracking System. The tables below are created by the migrations in [section 7](#7-migrations), and the app reads and writes them through the models in `app/models/` (see [section 8](#8-from-in-memory-models-to-tables)).

> **Status:** all four tables (`users`, `announcements`, `job_postings`, `applications`) exist in the database: migrations `0001` to `0005` have been applied (`alembic current` shows `0005 (head)`). The app uses `users` and `announcements` for its pages and API, and has JSON routes for `job_postings` and `applications` (sections [8.2](#82-routes-direct-and-nested) and [8.3](#83-applications-models-and-routes)). On a fresh database, run `alembic upgrade head` first. The validation rules for job postings are in [section 4.3.1](#431-validation-rules-for-a-job-posting). **User roles** (`student`, `alumni`, `academic`, `staff`, `admin`) and the announcement author as a user are **applied** by migration `0005` ([section 4.1.1](#411-roles-and-permissions)); the permission table there waits for the login of a later task.

## 1. Why a Database

The app first stored records in memory. The "forgetting test" showed the problem:

1. Create a user and an announcement.
2. Run `docker compose down` followed by `docker compose up`.
3. Check the records: both lists came back empty.

Restarting the container wiped the Python process's memory, so all data was lost. A database keeps data on disk, independent of the app process, so records survive restarts. After connecting the app to PostgreSQL, the same test passes: the records are still there after `down` and `up`.

## 2. Database Choice

| Decision | Choice | Reason |
| --- | --- | --- |
| DBMS | PostgreSQL 16 | Already defined as the `db` service in `docker-compose.yml`, with a persistent `pgdata` volume. |
| Connection | `DATABASE_URL=postgresql://USER:PASSWORD@db:5432/DB_NAME` | Passed to the `api` service as an environment variable. The real values live in `.env` (git ignored); `.env.example` is the committed template. See the Environment Variables section of the README. |
| Credentials | `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Read from `.env` by `docker-compose.yml`, no longer hard-coded. They apply only when the `pgdata` volume is first created. |
| Access from Python | SQLAlchemy + psycopg2 | Both are already listed in `requirements.txt`. |
| Startup order | `db` healthcheck (`pg_isready`) + `depends_on: condition: service_healthy` | The `api` container starts only after PostgreSQL accepts connections, so the app never tries to connect to a database that is still booting. |
| Table creation | Alembic migrations (`migrations/`) | Tables are created by running `alembic upgrade head` inside the `api` container. See section 7. |
| Host port | `POSTGRES_PORT` in `.env` (default `5432`) | Only for tools on the host (DBeaver, psql on the host). The app always connects inside Docker to `db:5432`, so changing this port does not touch the app. If another project already uses 5432 on the same computer, the `db` container cannot join its network; set another port (e.g. `5433`). |
| Database unreachable | `503 Service Unavailable` | When the app cannot reach PostgreSQL (container stopped, not on the network), the 5xx guardian answers 503 with an error id instead of a raw error, and writes the cause to `logs/error.logs` (README, "5xx Guardian" and "Error Log"). |

## 3. Entities

The system has four entities:

- **User**: a person in the system. Until now always an MIS graduate (alumnus/alumna); with roles (section 4.1.1, planned) a user is a `student`, a graduate (`alumni`), an `academic`, administrative `staff` or an `admin`, and the role decides what they may do.
- **Announcement**: a news item or notice published to graduates (e.g. a graduation ceremony, an event).
- **Job Posting**: a job or internship offer shared with graduates, optionally posted by a registered user (e.g. an alumnus hiring at their company).
- **Application**: a graduate's application to one job posting. It links a user and a job posting and carries its own data (status, cover letter).

## 4. Tables

### 4.1 `users`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `name` | `VARCHAR(100)` | `NOT NULL` | Full name of the graduate. |
| `email` | `VARCHAR(255)` | `NOT NULL`, `UNIQUE` | Contact email. Unique so the same person cannot be registered twice. |
| `role` | `VARCHAR(20)` | `NOT NULL`, `DEFAULT 'alumni'`, `CHECK (role IN ('student', 'alumni', 'academic', 'staff', 'admin'))` | What the person is in the system (section 4.1.1). |
| `graduation_year` | `INTEGER` | nullable, `CHECK (graduation_year BETWEEN 1950 AND 2100)`; required for `student` and `alumni` (see below) | Year of graduation; the expected year for a student. Empty for academic and administrative staff who are not counted as graduates. |
| `department` | `VARCHAR(100)` | `NOT NULL` | Department graduated from, studying in, or working in. |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the record was created. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the record was last changed. |

| Constraint / Index | Rule | Reason |
| --- | --- | --- |
| `ck_users_role` | `role IN ('student', 'alumni', 'academic', 'staff', 'admin')` | Only the five roles of section 4.1.1. |
| `ck_users_graduation_year_by_role` | `role NOT IN ('student', 'alumni') OR graduation_year IS NOT NULL` | Students and graduates must have a year; the others may leave it empty. |
| `ix_users_role` | `role` | Lists filtered by role (`/api/users?role=staff`, the album of students and graduates). |

#### 4.1.1 Roles and permissions

> **Status:** applied. The task was given in class: *"Update ddd.md for users and their roles in the system."* The roles were decided here first (design first, as with the job posting rules in section 4.3.1); migration `0005` then changed the tables, and the models, the API, the pages and the seed follow them. The data rules at the end of this section are enforced; the permissions in Table 2 (who may do what) wait for the login that a later task adds.

Until now every row of `users` was a graduate. The system has other people too: students looking for an internship, academics sharing a project position, the department office publishing announcements, and someone who runs the system. Each user gets **one role**.

**Table 1: Roles**

| Role | Who | `graduation_year` | Note |
| --- | --- | --- | --- |
| `student` | A current MIS student, looking for an internship or a first job | **Required** (expected year) | Becomes `alumni` after graduation |
| `alumni` | An MIS graduate | **Required** | The default role; the 21 existing users get it |
| `academic` | Academic staff: professors, research assistants | Optional | Manages their own postings and announcements |
| `staff` | Administrative staff: department office, career centre, dean's office, alumni association | Optional | Runs the system: users, all applications |
| `admin` | The person who runs the system | Optional | The only role that can give roles |

**Why one role per user (a column), not a `roles` table:** every permission below depends on a single role, so one value answers "may this user do this?"; a graduate who works in the department becomes `staff` and keeps their graduation year. A separate `roles` table with a join table (many roles per user) would only be needed if one person had to hold two roles with different rights at the same time, which the system does not need. The column also follows the pattern already used for `job_postings.employment_type` and `applications.status`: a short `VARCHAR` limited by a `CHECK`.

**Why `academic` is not `staff`:** both work for the department, but they do different things in the system. Administrative staff run it (add users, manage every application); academics only share their own opportunities (a TÜBİTAK project position, an assistantship, an internship, a seminar). Counting academics as `staff` would let them change applications to another academic's posting or edit user records; a separate role keeps them to *their own* postings and announcements.

**Table 2: Permissions**

✓ = allowed · **own** = only their own record · ✗ = not allowed

| Action | `student` | `alumni` | `academic` | `staff` | `admin` |
| --- | :-: | :-: | :-: | :-: | :-: |
| **Users** | | | | | |
| See the graduate album and the user list | ✓ | ✓ | ✓ | ✓ | ✓ |
| See other users' email addresses | ✗ | ✗ | ✓ | ✓ | ✓ |
| Edit their own profile | own | own | own | own | ✓ |
| Add a user | ✗ | ✗ | ✗ | ✓ (students and graduates) | ✓ |
| Edit another user | ✗ | ✗ | ✗ | ✓ (students and graduates) | ✓ |
| Delete a user | ✗ | ✗ | ✗ | ✗ | ✓ |
| Give or change a role | ✗ | ✗ | ✗ | ✗ | ✓ |
| **Announcements** | | | | | |
| Read announcements | ✓ | ✓ | ✓ | ✓ | ✓ |
| Publish an announcement | ✗ | ✗ | ✓ (course, seminar, research) | ✓ | ✓ |
| Edit or delete an announcement | ✗ | ✗ | own | own | ✓ |
| **Job postings** | | | | | |
| See job postings | ✓ | ✓ | ✓ | ✓ | ✓ |
| Open a job posting | ✗ | ✓ (for their company) | ✓ (project, assistantship, internship) | ✓ (for the department) | ✓ |
| Edit, close or delete a job posting | ✗ | own | own | ✓ | ✓ |
| **Applications** | | | | | |
| Apply to a job posting | ✓ | ✓ | ✗ | ✗ | ✗ |
| Withdraw their application (`withdrawn`) | own | own | ✗ | ✗ | ✗ |
| See applications | own | own + those to their postings | those to their postings | ✓ | ✓ |
| Change an application's status (review, interview, accepted, rejected) | ✗ | those to their postings | those to their postings | ✓ | ✓ |
| Delete an application | ✗ | ✗ | ✗ | ✗ | ✓ |

Reasons: a **student** does not open postings (they are on the job-seeking side); **academic**, **staff** and **admin** do not apply (they are not looking for a job in this system); a **graduate** who opens a posting is the employer for it, so they manage the applications it receives; **deleting users and giving roles** cannot be undone or changes rights, so only `admin` does it. **Academics** see email addresses because contacting students and graduates (projects, references, internships) is part of their work.

**Change to `users`** (migration `0005`, applied):

| Column / constraint | Before `0005` | After `0005` |
| --- | --- | --- |
| `role` | (none) | `VARCHAR(20) NOT NULL DEFAULT 'alumni'`, `CHECK (role IN ('student', 'alumni', 'academic', 'staff', 'admin'))` (`ck_users_role`) |
| `graduation_year` | `NOT NULL` | Nullable; the `BETWEEN 1950 AND 2100` check stays |
| `ck_users_graduation_year_by_role` | (none) | `CHECK (role NOT IN ('student', 'alumni') OR graduation_year IS NOT NULL)`: students and graduates must have a year, the others may leave it empty |
| `ix_users_role` | (none) | Index on `role`, for lists filtered by role (`?role=staff`, the album shows graduates) |

Every existing user becomes `alumni` through the default, and every one of them has a graduation year, so both checks pass and no row changes otherwise.

**Announcement author: `author` becomes `author_id`** (closes the open decision in section 5)

Until `0005` the author of an announcement was free text typed into a box (`announcements.author`, e.g. "Department Office"). That had three problems:

1. **Roles cannot be checked:** anyone could type "Dean's Office" and publish; the system does not know who the author is.
2. **Inconsistent values:** the same office can be written as "Department Office", "Department office" or "Bölüm Sekreterliği".
3. **No link:** "all announcements of the career centre" cannot be queried reliably.

Decision (applied by `0005`): the announcement stores **who published it**, as a user: `author_id INTEGER REFERENCES users(id) ON DELETE SET NULL`. The author must have the role `academic`, `staff` or `admin`.

- Migration `0005` creates one `staff` user for each author name already in the table ("Department Office", "Career Center", "Dean's Office", "Alumni Association"), links the existing announcements to them, then drops the `author` text column. The pages still show "By Department Office": the name now comes from the user.
- `ON DELETE SET NULL`, as for `job_postings.posted_by_user_id`: deleting an account keeps its announcements (they are still useful) and the page shows them as "Department".
- `author_id` is nullable only for that case; a new announcement always has an author.
- Index `ix_announcements_author_id`, because PostgreSQL does not index foreign keys automatically.
- `downgrade()` puts the `author` text back, filled from the users' names, and drops `author_id`.

**Schema after `0005`** (only the changed tables; the full diagram is in section 5):

```mermaid
erDiagram
    USERS {
        int id PK
        varchar name
        varchar email UK
        varchar role "student | alumni | academic | staff | admin"
        int graduation_year "required for student and alumni"
        varchar department
        timestamp created_at
        timestamp updated_at
    }
    ANNOUNCEMENTS {
        int id PK
        varchar title
        text content
        int author_id FK
        timestamp created_at
        timestamp updated_at
    }
    USERS |o--o{ ANNOUNCEMENTS : "publishes"
    USERS |o--o{ JOB_POSTINGS : "posts"
    USERS ||--o{ APPLICATIONS : "applies"
```

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    role            VARCHAR(20)  NOT NULL DEFAULT 'alumni',
    graduation_year INTEGER      CHECK (graduation_year BETWEEN 1950 AND 2100),
    department      VARCHAR(100) NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_users_role
        CHECK (role IN ('student', 'alumni', 'academic', 'staff', 'admin')),
    CONSTRAINT ck_users_graduation_year_by_role
        CHECK (role NOT IN ('student', 'alumni') OR graduation_year IS NOT NULL)
);

CREATE INDEX ix_users_role ON users (role);

CREATE TABLE announcements (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    content    TEXT         NOT NULL,
    author_id  INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_announcements_author_id ON announcements (author_id);
```

**Where each rule lives**

| Rule | Where | State |
| --- | --- | --- |
| `role` is one of the five values; students and graduates have a year | Database (`CHECK`) and the user model (`UserCreate`; a PATCH is checked on the user as it will be) | Applied; refused with **422** |
| An announcement's author is `academic`, `staff` or `admin` | `require_role()` in the user model, called by the announcement model (a `CHECK` cannot look into another table) | Applied; refused with **422**, a missing author with **404** |
| A job posting's poster is not a `student` | Job posting model | Applied; refused with **422** |
| An applicant is a `student` or `alumni` | Application model | Applied; refused with **422** |
| Table 2 ("who may do what": own records, deleting, giving roles) | The login and permission checks | A later task (login is not part of this one) |

The refusals read like *"A staff member cannot apply to a job posting (allowed: student, graduate)"*. The pages offer only the accounts that fit: the author list of the announcement form shows academic, staff and admin accounts; the applicant lists show students and graduates; the "posted by" list leaves students out.

Tested on a temporary database before the real one: upgrade from `0004` with old-style rows (the three author names became three `staff` accounts and every announcement was linked to the right one), the two `CHECK`s refusing a student without a year and an unknown role, seeding on top (no duplicate office accounts), `downgrade` back to `0004` (author text restored, the office accounts removed) and `upgrade` again; `alembic check` reports no difference. Then the real database was upgraded: the 21 users became `alumni`, four office accounts were created and the ten announcements kept their authors. Through the API: a student without a year, an academic turned into a graduate without a year, an announcement by a graduate, a posting by a student and an application by staff were all refused with 422; the allowed versions were accepted.

The first four rules depend only on the data (the role of the user named in the request), so they can be enforced as soon as the column exists. Table 2 depends on *who is signed in*, which needs the login that a later task adds.

**How people get their role (registration, next task).** Decided for the first version: students register with their student email address, academic and administrative staff with an `@istanbul.edu.tr` address, graduates with any address; every new account uploads a document and stays pending until an `admin` approves it. **Email verification (a confirmation link) is deferred to a later task.** The registration columns and tables will be designed here, in a new section, before migration `0006` adds them.

### 4.2 `announcements`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `title` | `VARCHAR(200)` | `NOT NULL` | Headline of the announcement. |
| `content` | `TEXT` | `NOT NULL` | Body text, no length limit. |
| `author_id` | `INTEGER` | `REFERENCES users(id) ON DELETE SET NULL`, indexed (`ix_announcements_author_id`) | Who published it: an `academic`, `staff` or `admin` account (section 4.1.1). Pages show the account's name ("By Department Office"); an announcement whose author account was deleted shows "Department". Replaced the free-text `author` in migration `0005`. |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the announcement was published. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When it was last edited. |

### 4.3 `job_postings`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `title` | `VARCHAR(120)` | `NOT NULL` | Position title (e.g. "Junior Data Analyst"). At most 120 characters (section 4.3.1). |
| `company` | `VARCHAR(150)` | `NOT NULL` | Hiring company. |
| `city` | `VARCHAR(150)` | `NOT NULL` | City of the job, or "Remote". Called `location` before migration `0004`. |
| `employment_type` | `VARCHAR(20)` | `NOT NULL`, `CHECK (employment_type IN ('full_time', 'part_time', 'internship', 'contract'))` | Kind of position. A fixed list so filtering by type is reliable. |
| `description` | `TEXT` | nullable, see the check below | Responsibilities and requirements, no length limit. Optional if `application_url` is given. |
| `application_url` | `VARCHAR(500)` | nullable, see the check below | Where to apply. Optional if `description` is given. |
| `deadline` | `DATE` | nullable | Last day to apply. Optional: some postings stay open until filled. |
| `is_active` | `BOOLEAN` | `NOT NULL`, `DEFAULT TRUE` | `FALSE` hides a filled or expired posting without deleting it. |
| `posted_by_user_id` | `INTEGER` | nullable, `REFERENCES users(id) ON DELETE SET NULL` | The user who shared the posting. `NULL` when the department posts it, or when the user is later deleted. |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the posting was created. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When it was last edited. |

| Index | Columns | Reason |
| --- | --- | --- |
| `ix_job_postings_posted_by_user_id` | `posted_by_user_id` | PostgreSQL does not index foreign keys automatically. This keeps "postings by this user" lookups and user deletes fast. |

| Check constraint | Rule | Reason |
| --- | --- | --- |
| `ck_job_postings_employment_type` | `employment_type IN ('full_time', 'part_time', 'internship', 'contract')` | Only the allowed kinds of position. |
| `ck_job_postings_description_or_url` | `description IS NOT NULL OR application_url IS NOT NULL` | At least one of the two (section 4.3.1). |

#### 4.3.1 Validation rules for a job posting

> **Status:** applied. These rules were given in class and decided here first (design first); migration `0004` then changed the table, and the models, the API, the pages and the seed follow them. The table in section 4.3 shows the result.

| Field | Rule | Before `0004` | Change made by `0004` |
| --- | --- | --- | --- |
| `title` | **Required**, at most **120 characters** | `VARCHAR(200) NOT NULL` | Shorten to `VARCHAR(120)` |
| `company` | **Required** | `VARCHAR(150) NOT NULL` | None |
| `city` | **Required** | Stored as `location` (`VARCHAR(150) NOT NULL`) | Rename `location` → `city` |
| `description` | **Optional**, but see the rule below | `TEXT NOT NULL` (required) | Allow `NULL` |
| `application_url` | **Optional**, but see the rule below | `VARCHAR(500)`, nullable | None |

**Rule: at least one of `description` and `application_url` is required.**

The requirement was given in class as two possible readings:

1. `description` optional, `application_url` required; or
2. `application_url` optional, `description` required.

**Decision:** neither reading alone. A posting must have **at least one** of the two; it may have both. Whoever writes a description does not have to add a URL, and whoever adds a URL does not have to write a description. Only leaving both empty is refused:

| `description` | `application_url` | Result |
| --- | --- | --- |
| filled | empty | Accepted |
| empty | filled | Accepted |
| filled | filled | Accepted |
| empty | empty | **Refused** |

**Reason:** a posting is useless only when it says neither *what the job is* nor *where to apply*. Some postings are just a link to the company's own page, others are a full text with a contact inside it. Forcing one specific field would reject one of these valid kinds of posting, while "at least one" accepts both and still rejects an empty posting.

How the rule is enforced:

- **Model (one rule, one place):** the job posting model (`app/models/job_posting.py`) checks the rule before saving, so the JSON API (direct and nested routes) and the HTML pages all go through it. A text that is empty or contains only spaces counts as missing, and spaces around values are trimmed. A refused posting answers **422** with the message *"A job posting needs a description or an application URL (at least one of the two)."* The pages show the same message above the form and keep what was typed.
- **Database:** a `CHECK` constraint keeps the rule even if a row is written outside the app:
  `CHECK (description IS NOT NULL OR application_url IS NOT NULL)` (named `ck_job_postings_description_or_url`).
- **Update (PATCH):** the rule is checked on the posting as it will be *after* the change, so clearing the only one of the two fields that is filled is refused. Required fields (`title`, `company`, `city`, ...) cannot be set to `null` by a PATCH either (422).
- **Seed:** the factory always fills at least one of the two (description only, URL only, or both), and the database check would refuse anything else.

What migration `0004` did (a new file, `0004_job_posting_validation_rules.py`; `0002` was not edited):

- `title` became `VARCHAR(120)`. Titles longer than 120 characters would have to be shortened first, or the migration fails; before applying, the database had none.
- `location` was renamed to `city` (the data stayed).
- `description` became nullable.
- The `ck_job_postings_description_or_url` check was added. Every existing row passed it, because every row had a description.
- `downgrade()` reverses all of it. Because `description` becomes required again, a posting that only has a URL first gets its URL copied into `description`. Tested: upgrade, downgrade and upgrade again on a temporary database.

### 4.4 `applications`

| Column | Type | Constraints | Description |
| --- | --- | --- | --- |
| `id` | `SERIAL` | `PRIMARY KEY` | Auto-incremented identifier. |
| `user_id` | `INTEGER` | `NOT NULL`, `REFERENCES users(id) ON DELETE CASCADE` | The graduate who applied (the applicant). |
| `job_posting_id` | `INTEGER` | `NOT NULL`, `REFERENCES job_postings(id) ON DELETE CASCADE` | The posting applied to. |
| `status` | `VARCHAR(20)` | `NOT NULL`, `DEFAULT 'submitted'`, `CHECK (status IN ('submitted', 'under_review', 'interview', 'accepted', 'rejected', 'withdrawn'))` | Where the application stands. A fixed list, so filtering by status is reliable. |
| `cover_letter` | `TEXT` | nullable | Optional motivation text written by the applicant. |
| `created_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When the application was submitted. |
| `updated_at` | `TIMESTAMP` | `NOT NULL`, `DEFAULT CURRENT_TIMESTAMP` | When it was last changed (e.g. the status moved on). |

| Constraint / Index | Columns | Reason |
| --- | --- | --- |
| `uq_applications_user_id_job_posting_id` (`UNIQUE`) | `user_id`, `job_posting_id` | A graduate can apply to a given posting only once. Its index also serves "applications of this user" lookups, because `user_id` is its first column. |
| `ix_applications_job_posting_id` | `job_posting_id` | "Applicants of this posting" lookups and posting deletes stay fast (PostgreSQL does not index foreign keys automatically). |

## 5. Relationships

```mermaid
erDiagram
    USERS {
        int id PK
        varchar name
        varchar email UK
        varchar role
        int graduation_year
        varchar department
        timestamp created_at
        timestamp updated_at
    }
    ANNOUNCEMENTS {
        int id PK
        varchar title
        text content
        int author_id FK
        timestamp created_at
        timestamp updated_at
    }
    JOB_POSTINGS {
        int id PK
        varchar title
        varchar company
        varchar city
        varchar employment_type
        text description
        varchar application_url
        date deadline
        boolean is_active
        int posted_by_user_id FK
        timestamp created_at
        timestamp updated_at
    }
    APPLICATIONS {
        int id PK
        int user_id FK
        int job_posting_id FK
        varchar status
        text cover_letter
        timestamp created_at
        timestamp updated_at
    }
    USERS |o--o{ ANNOUNCEMENTS : "publishes"
    USERS |o--o{ JOB_POSTINGS : "posts"
    USERS ||--o{ APPLICATIONS : "applies"
    JOB_POSTINGS ||--o{ APPLICATIONS : "receives"
```

**`users` → `job_postings` (one-to-many, optional):** one user can post many job postings; each posting is posted by at most one user. The link is `job_postings.posted_by_user_id → users.id`.

- It is nullable, so the department can publish a posting that belongs to no user.
- `ON DELETE SET NULL`: deleting a user keeps their postings and only clears `posted_by_user_id`. Job postings are still useful to other graduates after the poster leaves, so they should not be deleted with the user.

**`users` ↔ `job_postings` through `applications` (many-to-many):** a graduate can apply to many postings, and a posting can receive applications from many graduates. A many-to-many link cannot be stored in one column, so `applications` sits in between as a *join table*. Each row is one pair (applicant, posting) and carries its own data (`status`, `cover_letter`), which is why it is a full table and not just two ids.

- `applications.user_id → users.id` is **one-to-many**: one user, many applications.
- `applications.job_posting_id → job_postings.id` is **one-to-many**: one posting, many applications.
- Both columns are `NOT NULL`: an application without an applicant or without a posting makes no sense.
- Both use `ON DELETE CASCADE`: if a user is deleted, their applications go with them (personal data of a person who left); if a posting is deleted, applications to it go with it (they point to nothing). This differs from `job_postings.posted_by_user_id`, which uses `SET NULL`, because a posting is still useful without its poster, but an application is not useful without either side.
- `UNIQUE (user_id, job_posting_id)`: the same graduate cannot apply twice to the same posting.

**`users` → `announcements` (one-to-many, optional):** one account publishes many announcements; each announcement has at most one author. The link is `announcements.author_id → users.id`, and the author must be `academic`, `staff` or `admin` (checked by the model, section 4.1.1).

- It was a free-text `author` until migration `0005` (the "open decision" of earlier versions of this document); `0005` turned each author name into a `staff` account and linked the announcements to it.
- `ON DELETE SET NULL`, as for `job_postings.posted_by_user_id`: deleting an account keeps its announcements, which are still useful; the pages then show "Department" as the author.

## 6. SQL Equivalent

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    email           VARCHAR(255) NOT NULL UNIQUE,
    role            VARCHAR(20)  NOT NULL DEFAULT 'alumni',
    graduation_year INTEGER      CHECK (graduation_year BETWEEN 1950 AND 2100),
    department      VARCHAR(100) NOT NULL,
    created_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_users_role
        CHECK (role IN ('student', 'alumni', 'academic', 'staff', 'admin')),
    CONSTRAINT ck_users_graduation_year_by_role
        CHECK (role NOT IN ('student', 'alumni') OR graduation_year IS NOT NULL)
);

CREATE INDEX ix_users_role ON users (role);

CREATE TABLE announcements (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    content    TEXT         NOT NULL,
    author_id  INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX ix_announcements_author_id ON announcements (author_id);

CREATE TABLE job_postings (
    id                SERIAL PRIMARY KEY,
    title             VARCHAR(120) NOT NULL,
    company           VARCHAR(150) NOT NULL,
    city              VARCHAR(150) NOT NULL,
    employment_type   VARCHAR(20)  NOT NULL
                      CHECK (employment_type IN ('full_time', 'part_time', 'internship', 'contract')),
    description       TEXT,
    application_url   VARCHAR(500),
    deadline          DATE,
    is_active         BOOLEAN      NOT NULL DEFAULT TRUE,
    posted_by_user_id INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    created_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT ck_job_postings_description_or_url
        CHECK (description IS NOT NULL OR application_url IS NOT NULL)
);

CREATE INDEX ix_job_postings_posted_by_user_id ON job_postings (posted_by_user_id);

CREATE TABLE applications (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER     NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_posting_id INTEGER     NOT NULL REFERENCES job_postings(id) ON DELETE CASCADE,
    status         VARCHAR(20) NOT NULL DEFAULT 'submitted'
                   CHECK (status IN ('submitted', 'under_review', 'interview', 'accepted', 'rejected', 'withdrawn')),
    cover_letter   TEXT,
    created_at     TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP   NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_applications_user_id_job_posting_id UNIQUE (user_id, job_posting_id)
);

CREATE INDEX ix_applications_job_posting_id ON applications (job_posting_id);
```

The SQL above is shown for reading. It is not run by hand: the migrations below produce the same tables. It is the schema after `0005`.

## 7. Migrations

Migrations are managed with [Alembic](https://alembic.sqlalchemy.org/). Each migration is a Python file in `migrations/versions/` with an `upgrade()` (apply) and a `downgrade()` (undo) function. Alembic remembers the current version in the `alembic_version` table.

| Revision | File | What it does | Status |
| --- | --- | --- | --- |
| `0001` | `migrations/versions/0001_create_users_and_announcements.py` | Creates `users` and `announcements` exactly as defined in section 4. Downgrade drops both tables. | Applied |
| `0002` | `migrations/versions/0002_create_job_postings.py` | Creates `job_postings` (section 4.3) with its foreign key to `users` and its index. Downgrade drops the table. Depends on `0001`, because the foreign key needs `users` to exist. | Applied |
| `0003` | `migrations/versions/0003_create_applications.py` | Creates `applications` (section 4.4) with its two foreign keys, the unique pair and the index. Downgrade drops the table. Depends on `0002`, because it references both `users` and `job_postings`. | Applied |
| `0004` | `migrations/versions/0004_job_posting_validation_rules.py` | Applies the job posting validation rules of section 4.3.1: `title` to `VARCHAR(120)`, `location` renamed to `city`, `description` nullable, `CHECK (description IS NOT NULL OR application_url IS NOT NULL)`. Downgrade reverses it. Depends on `0003`. | Applied |
| `0005` | `migrations/versions/0005_user_roles.py` | Applies section 4.1.1: adds `users.role` (default `alumni`, `ck_users_role`, `ix_users_role`), makes `graduation_year` nullable with `ck_users_graduation_year_by_role`; creates a `staff` user for each existing announcement author, adds `announcements.author_id` (with `ix_announcements_author_id`), links the announcements and drops `author`. Downgrade restores `author` from the users' names and removes the office accounts it created. Depends on `0004`. | Applied |

`alembic upgrade head` applies the migrations that are missing, in order. It was run on the existing database (which already held 20 users and 10 announcements from the seeder): `0002` and `0003` were applied and the existing rows were untouched. Later `0004` (job posting validation rules) and `0005` (user roles, announcement authors; tested first on a temporary database, section 4.1.1) were applied the same way, and `alembic current` now shows `0005 (head)`. `alembic check` reports "No new upgrade operations detected", so the ORM models match the real tables.

| Command (run in the project folder) | Meaning |
| --- | --- |
| `docker compose exec api alembic upgrade head` | Apply all migrations (create the tables). |
| `docker compose exec api alembic current` | Show which revision the database is at. |
| `docker compose exec api alembic downgrade base` | Undo all migrations (drops the tables and their data). |
| `docker compose exec api alembic revision -m "message"` | Create a new empty migration file for the next schema change. |

**How the constraints are enforced:** the `UNIQUE` on `users.email`, the `CHECK` on `users.graduation_year` and the `NOT NULL` columns are enforced by PostgreSQL itself. They were tested by inserting invalid rows, which the database rejected.

**Note on `updated_at`:** it only has a default at insert time. PostgreSQL does not update it automatically on `UPDATE`, so the application sets it in every update query (see section 8).

### 7.1 Factories and Seeding

Test data is generated by factories and inserted by a seeder. This does not change the schema.

| File | Role |
| --- | --- |
| `app/database/factories.py` | `UserFactory`, `AnnouncementFactory` and `JobPostingFactory` build fake rows with [Faker](https://faker.readthedocs.io/). They respect the table rules: unique emails, title within 200 characters, `employment_type` from the allowed list, and the roles of section 4.1.1: about 75% graduates (`graduation_year` 2005 to 2025), 17% students (an expected year 2027 to 2030 and an `@ogr.iu.edu.tr` address) and 8% academics (a title such as "Prof. Dr.", an `@istanbul.edu.tr` address, no year). `staff_accounts()` gives the four offices that publish announcements. |
| `app/database/seed.py` | Seeder: first makes sure the four office accounts exist (the same addresses migration `0005` gives them, so nothing is duplicated), then inserts the factory rows into `users`, `announcements` (authors picked from academic, staff and admin accounts) and `job_postings` (posters picked from everyone but students). |
| `app/database/connection.py` | Creates the database connection from `DATABASE_URL`. |

| Command | Meaning |
| --- | --- |
| `docker compose exec api python -m app.database.seed` | Add 20 users, 10 announcements and 15 job postings. |
| `docker compose exec api python -m app.database.seed --users 50 --announcements 5 --job-postings 30` | Choose the counts (`0` skips a table). |
| `docker compose exec api python -m app.database.seed --fresh` | Empty all four tables (including `applications`) and reset ids to 1 first, then seed. |
| `docker compose exec api python -m app.database.seed --seed 7` | Fixed random seed: the same data every run (use with `--fresh`). |

Without `--fresh`, each run adds more rows on top of the existing ones. The seeded data is for development only.

**Seeded job postings** (what `JobPostingFactory` produces, matching section 4.3):
- `posted_by_user_id` is picked from the users that exist in the table when the seeder runs, so the foreign key is always valid. About 75% of the postings belong to a user and about 25% are department postings (`NULL`). If there are no users at all, every posting is a department posting.
- `employment_type` is one of `full_time`, `part_time`, `internship`, `contract`. About 85% of the postings are active; about 70% have a `deadline` 10 to 90 days ahead, the rest have none (`NULL`); every posting has a `description`, an `application_url` or both (about half have both, a quarter only a description, a quarter only a URL; never neither, section 4.3.1).
- `applications` is not seeded. It is emptied by `--fresh`, because `TRUNCATE` on `users` and `job_postings` must include every table that points to them (PostgreSQL refuses otherwise), and applications cannot outlive the users and postings they belong to.

## 8. From In-Memory Models to Tables

The app is now connected to the database. `app/models/user.py` and `app/models/announcement.py` run SQL (through SQLAlchemy and the connection in `app/database/connection.py`) instead of changing Python lists.

| Before (in memory) | Now (database) | Change |
| --- | --- | --- |
| `users: list[dict]` | `users` table | Rows persist across restarts. |
| `id = len(users) + 1` | `SERIAL` | The database assigns ids. The old approach could repeat an id after a delete; `SERIAL` never reuses one. Ids can have gaps, for example when an insert is rejected by a constraint. |
| `email: str` (no rule) | `UNIQUE` | A duplicate email is rejected and the API answers `409 Conflict`. |
| `graduation_year: int` (no rule) | `CHECK` between 1950 and 2100 | Checked twice: by the Pydantic models (answer `422`) and by the database. |
| `announcements: list[dict]` | `announcements` table | Rows persist across restarts. |
| `created_at` as a formatted string | `TIMESTAMP` | Stored as a real date/time. The API still returns it formatted as `YYYY-MM-DD HH:MM`. |
| No `updated_at` | `updated_at` column | The model sets it to `CURRENT_TIMESTAMP` on every update, which resolves the limitation noted in section 7. |
| Missing id in a list | `404 Not Found` | Unchanged: a missing id still answers `404`. |

The API contracts (request/response fields in `/api/users` and `/api/announcements`) stay the same, so controllers and views did not need to change. `created_at` and `updated_at` of users are stored but not returned by the API.

**How the error answers look now:** the models still raise `404 User not found`, `404 Job posting not found`, `409 ...` and so on, as described in this document. Two middlewares (README, "Middleware") then shape the answer that leaves the app: every 404 carries a `reason` with the id that was not found, e.g. `{"status": 404, "error": "Not Found", "reason": "User not found (user_id=999).", ...}`, and a database failure becomes `503` with an `error_id`. In the sections below, "`404 User not found`" means this answer.

### 8.1 ORM Models and Relationships

Each table also has a SQLAlchemy ORM model: a Python class whose attributes map to the table's columns. All models inherit from `Base` (`app/models/base.py`), so `Base.metadata` describes every table in this document.

| Model | File | Table |
| --- | --- | --- |
| `User` | `app/models/user.py` | `users` |
| `Announcement` | `app/models/announcement.py` | `announcements` |
| `JobPosting` | `app/models/job_posting.py` | `job_postings` |
| `Application` | `app/models/application.py` | `applications` |

The relationships from section 5 are defined on both sides, so each can be followed in either direction:

| Attribute | Points to | Kind | Example |
| --- | --- | --- | --- |
| `User.job_postings` | list of `JobPosting` | one-to-many | `user.job_postings` → every posting the user shared |
| `JobPosting.posted_by` | `User` or `None` | many-to-one | `posting.posted_by.name` → who shared it; `None` for department postings |
| `User.applications` | list of `Application` | one-to-many | `user.applications` → everything the user applied to |
| `JobPosting.applications` | list of `Application` | one-to-many | `posting.applications` → everyone who applied to the posting |
| `Application.applicant` | `User` | many-to-one | `application.applicant.name` → who applied |
| `Application.job_posting` | `JobPosting` | many-to-one | `application.job_posting.title` → what was applied to |

Each pair of attributes is linked with `back_populates`, so adding a posting to `user.job_postings` also sets `posting.posted_by`. `User.job_postings` uses `passive_deletes=True`: when a user is deleted, PostgreSQL's `ON DELETE SET NULL` clears `posted_by_user_id` on their postings, instead of the ORM loading and updating each posting.

`User.applications` and `JobPosting.applications` use `cascade="all, delete-orphan"` together with `passive_deletes=True`. The database does the work (`ON DELETE CASCADE` removes the applications). The ORM cascade is declared as well so that deleting a `User` or `JobPosting` object never tries to set the `NOT NULL` `user_id` / `job_posting_id` of an application to null.

**Models and migrations stay in sync:** `migrations/env.py` points Alembic at `Base.metadata`. Running `alembic check` against a database at `head` compares the models with the migrated schema and reports any difference (it answered "No new upgrade operations detected"). After changing a model, `alembic revision --autogenerate -m "..."` can draft the next migration, which must still be reviewed and documented here.

**Current use:** the CRUD functions for users and announcements still run plain SQL. The job posting functions in `app/models/job_posting.py` use the ORM (`Session`, `session.get`, `select`), and the `users` ↔ `job_postings` relationship is what the nested routes below rely on. The application functions in `app/models/application.py` use the ORM too. The `job_postings` and `applications` tables exist only after migrations `0002` and `0003` are applied.

### 8.2 Routes: Direct and Nested

Job postings are reachable in two ways. Both are JSON routes handled by `ApiJobPostingController` (`app/controllers/api_job_posting_controller.py`).

**Direct routes:** the posting is a resource of its own, found by its own id. The owner is a field in the body (`posted_by_user_id`, or `null` for a department posting).

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/job-postings` | List all postings. |
| POST | `/api/job-postings` | Create a posting. `404` if `posted_by_user_id` is not an existing user. |
| GET | `/api/job-postings/{id}` | One posting. |
| PUT | `/api/job-postings/{id}` | Replace a posting (all fields). |
| PATCH | `/api/job-postings/{id}` | Change some fields, e.g. `{"is_active": false}`. |
| DELETE | `/api/job-postings/{id}` | Delete a posting. |

**Nested routes:** the URL follows the relationship `users → job_postings`. The user in the path is the owner, so the body does not contain `posted_by_user_id`.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/users/{user_id}/job-postings` | Only the postings of this user. |
| POST | `/api/users/{user_id}/job-postings` | Create a posting owned by this user. |
| GET | `/api/users/{user_id}/job-postings/{id}` | One posting of this user. |
| DELETE | `/api/users/{user_id}/job-postings/{id}` | Delete one posting of this user. |

Rules of the nested routes:
- If the user does not exist, the answer is `404 User not found`.
- If the posting exists but belongs to another user (or to nobody), the nested route answers `404 Job posting not found`: through user 2 you cannot read or delete user 1's posting. The direct route `/api/job-postings/{id}` still shows it.
- Deleting a user does not delete their postings; they stay in `/api/job-postings` with `posted_by_user_id` set to `null` (the `ON DELETE SET NULL` rule from section 5).
- `employment_type` must be one of `full_time`, `part_time`, `internship`, `contract`; anything else answers `422`.

These routes were tested before the migrations were applied (against a temporary database) and again afterwards against the real database, where a posting, two applications (one through each nested route), the duplicate `409` and the cascade delete all behaved as described.

### 8.3 Applications: Models and Routes

`Application` is the join table between users and job postings (section 5), so its routes are nested in **two** directions. All are JSON routes handled by `ApiApplicationController` (`app/controllers/api_application_controller.py`).

**Direct routes:** the application is a resource of its own. Both sides are in the body.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/applications` | List all applications. |
| POST | `/api/applications` | Apply: body `{"user_id": 1, "job_posting_id": 2, "cover_letter": "..."}`. |
| GET | `/api/applications/{id}` | One application. |
| PATCH | `/api/applications/{id}` | Change `status` and/or `cover_letter`. |
| DELETE | `/api/applications/{id}` | Delete (withdraw) an application. |

There is no `PUT`: who applied and what they applied to must never be rewritten, so only `status` and `cover_letter` can change (`PATCH`).

**Nested under a user** (`/api/users/{user_id}/applications`): "my applications". The user in the path is the applicant.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/users/{user_id}/applications` | Applications of this user. |
| POST | `/api/users/{user_id}/applications` | This user applies: body `{"job_posting_id": 2, "cover_letter": "..."}`. |
| GET | `/api/users/{user_id}/applications/{id}` | One application of this user. |
| DELETE | `/api/users/{user_id}/applications/{id}` | The user withdraws one of their applications. |

**Nested under a job posting** (`/api/job-postings/{posting_id}/applications`): "who applied to this posting". The posting in the path is the one applied to.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/job-postings/{posting_id}/applications` | Applicants of this posting. |
| POST | `/api/job-postings/{posting_id}/applications` | Apply to this posting: body `{"user_id": 1, "cover_letter": "..."}`. |
| GET | `/api/job-postings/{posting_id}/applications/{id}` | One application to this posting. |
| PATCH | `/api/job-postings/{posting_id}/applications/{id}` | The poster moves the application on, e.g. `{"status": "interview"}`. |

Rules:
- Missing user or posting in the path or body: `404 User not found` / `404 Job posting not found`.
- An application that belongs to another user (or posting) than the one in the path: `404 Application not found`. The direct route still shows it.
- Applying twice to the same posting: `409` (the `UNIQUE (user_id, job_posting_id)` constraint).
- Applying to a posting that is not active, or whose `deadline` has passed: `409 This job posting is closed`.
- `status` must be one of `submitted` (default), `under_review`, `interview`, `accepted`, `rejected`, `withdrawn`; anything else answers `422`.
- Deleting a user deletes their applications; deleting a posting deletes the applications to it (`ON DELETE CASCADE`).

These routes were tested against a temporary database with all three migrations applied, and again against the real database after the migrations were applied: applying through both nested routes, the duplicate `409`, and the `ON DELETE CASCADE` when the posting was deleted.

## 9. Naming Conventions

- Table names are plural and lowercase: `users`, `announcements`, `job_postings`, `applications`.
- Column names use `snake_case`: `graduation_year`, `created_at`.
- Every table has an `id` primary key plus `created_at` and `updated_at` columns.
- Foreign keys are named `<role>_<table>_id` when the role matters: `posted_by_user_id` says both which table it points to and why.
- Indexes are named `ix_<table>_<column>`; unique constraints `uq_<table>_<columns>`; check constraints `ck_<table>_<rule>` (`ck_users_role`, `ck_users_graduation_year_by_role`).
- Fixed lists (role, employment type, status) are stored as lowercase `snake_case` text checked by a `CHECK`, not as numbers: `alumni`, `under_review`, `full_time`. The pages turn them into labels.
- A foreign key to the user who did something is named after the act or the role: `posted_by_user_id` (job postings), `author_id` (announcements, planned).
