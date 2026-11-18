# Alumni Tracking System

A backend system to track Management Information Systems (MIS) graduates, built for the Web Programming (YBSB3001) course. Graduates (users), announcements, job postings and applications are managed through HTML pages and a JSON API, stored in PostgreSQL, and the whole system starts with one command: `docker compose up`.

## Tech Stack

- **Backend:** FastAPI (Python), SQLAlchemy ORM, Alembic migrations
- **Database:** PostgreSQL 16
- **Containerization:** Docker & Docker Compose

## Contents

- [Running the Project](#running-the-project)
- [Environment Variables](#environment-variables)
- [Database, Migrations and Seeding](#database-migrations-and-seeding)
- [Pages and API Endpoints](#pages-and-api-endpoints)
- [Middleware: the request pipeline](#middleware-the-request-pipeline) (logger, 404 guardian, generic 404 page, 5xx guardian, error log)
- [Project Architecture (MVC)](#project-architecture-mvc)
- [Troubleshooting](#troubleshooting)
- [Progress](#progress)
- **[Data Design Documentation (ddd.md)](ddd.md):** tables, columns, constraints, relationships, validation rules and migrations.
- **[Brand Guide (brand.md)](brand.md):** the site's identity under Istanbul University: palette taken from the university's own colours (İÜ green, gold, navy), logo, typography, components, contrast rules and tone of voice.
- **[Design System (DESIGN.md)](DESIGN.md):** the brand turned into a design system for people and AI agents, in the [awesome-design-md](https://github.com/VoltAgent/awesome-design-md) / Google Stitch format: design tokens, component recipes, the motion and animation system, responsive rules and ready-to-use prompts.

> **Rule:** Every change to the database (new table, new/renamed/removed column, type, constraint, index or relationship) must be documented in [ddd.md](ddd.md) in the same commit. `ddd.md` is the single source of truth for the data design, and tables change only through migrations.

## Running the Project

1. Clone the repository:
   ```bash
   git clone https://github.com/uumutkorkmaz/alumni.git
   cd alumni
   ```
2. Create your environment file from the template, then open `.env` and set your own values (see [Environment Variables](#environment-variables)):
   ```bash
   cp .env.example .env
   ```
3. Start the system (add `--build` the first time, and whenever `Dockerfile` or `requirements.txt` changes):
   ```bash
   docker compose up --build
   ```
4. Create the database tables (run the migrations):
   ```bash
   docker compose exec api alembic upgrade head
   ```
5. Optionally fill the tables with test data:
   ```bash
   docker compose exec api python -m app.database.seed --fresh
   ```
6. Open:
   - the site: `http://localhost:8000`
   - the API documentation (Swagger UI): `http://localhost:8000/api/swagger` (redirects to the auto-generated `/docs` page, which follows every new endpoint by itself)

If a step fails, see [Troubleshooting](#troubleshooting).

## Environment Variables

Configuration and secrets (database user, password, ports) are not hard-coded in `docker-compose.yml`. They are read from a `.env` file, which Docker Compose loads automatically.

| File | In git? | Purpose |
| --- | --- | --- |
| `.env` | No (listed in `.gitignore`) | Your real values, including the password. Stays on your machine. |
| `.env.example` | Yes | Template with placeholder values. Copy it to `.env` and fill it in. |

| Variable | Used by | Description |
| --- | --- | --- |
| `POSTGRES_USER` | `db` | Database user created on first start. |
| `POSTGRES_PASSWORD` | `db` | Password of that user. |
| `POSTGRES_DB` | `db` | Name of the database. |
| `POSTGRES_PORT` | `db` | Host port mapped to PostgreSQL (default `5432`). Only tools on your computer (DBeaver, psql) use it; change it if another program already uses 5432. |
| `API_PORT` | `api` | Host port mapped to the FastAPI app (default `8000`). |
| `DATABASE_URL` | `api` | Connection string: `postgresql://USER:PASSWORD@db:5432/DB_NAME`. Keep it consistent with the three `POSTGRES_*` values above. It always uses `db:5432` (inside Docker), whatever `POSTGRES_PORT` is. |
| `TZ` | `api` | Time zone of the app container, used by the request log (default `Europe/Istanbul`). |
| `DEBUG_ROUTES` | `api` | `1` adds the test-only route `GET /api/debug/error`, which fails on purpose to show the 5xx guardian. Default `0`; keep it `0` wherever real users can reach the app. |

> If you add a new variable, add it to both `.env` and `.env.example`. Never commit `.env`.
> `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` only take effect when the `pgdata` volume is created for the first time. To apply new values to an existing volume, run `docker compose down -v` (this deletes the stored database data).

## Database, Migrations and Seeding

The database schema is created by [Alembic](https://alembic.sqlalchemy.org/) migrations, written from `ddd.md`. They live in `migrations/versions/`. Tables so far (migrations `0001` to `0004`): `users`, `announcements`, `job_postings` and `applications`, all described in [ddd.md](ddd.md).

| Migration | What it does |
| --- | --- |
| `0001` | Creates `users` and `announcements`. |
| `0002` | Creates `job_postings` (one user → many postings). |
| `0003` | Creates `applications` (join table: users ↔ job postings). |
| `0004` | Job posting validation rules: `title` at most 120 characters, `location` renamed to `city`, `description` optional, at least one of `description` / `application_url` ([ddd.md 4.3.1](ddd.md#431-validation-rules-for-a-job-posting)). |

| Command | Meaning |
| --- | --- |
| `docker compose exec api alembic upgrade head` | Create/update the tables to the latest version. |
| `docker compose exec api alembic current` | Show the current database version. |
| `docker compose exec api alembic downgrade base` | Undo all migrations (drops the tables and their data). |

### Factories and Seeding

Factories (`app/database/factories.py`) generate realistic fake users, announcements and job postings with Faker. The seeder (`app/database/seed.py`) inserts them into the database, so you can fill the tables with test data in one command.

| Command | Meaning |
| --- | --- |
| `docker compose exec api python -m app.database.seed` | Add 20 users, 10 announcements and 15 job postings. |
| `docker compose exec api python -m app.database.seed --users 50 --announcements 5 --job-postings 30` | Choose the counts (`0` skips a table). |
| `docker compose exec api python -m app.database.seed --fresh` | Empty all tables (including `applications`) and reset ids first, then seed. |
| `docker compose exec api python -m app.database.seed --seed 7` | Same fake data on every run (use with `--fresh`). |

Seeded job postings belong to existing users (or to nobody, for department postings), so they also show up under `GET /api/users/{id}/job-postings`. Each one has a description, an application URL or both, never neither.

Look inside the database:
```bash
docker compose exec db psql -U alumni -d alumni -c "\dt"
docker compose exec db psql -U alumni -d alumni -c "SELECT id, name, email FROM users LIMIT 5;"
docker compose exec db psql -U alumni -d alumni -c "SELECT id, title, company, city, posted_by_user_id FROM job_postings LIMIT 5;"
```

## Pages and API Endpoints

The app is connected to PostgreSQL. The pages and the JSON API of each resource use the same table, so a record created through one is visible through the other, and records survive `docker compose down` / `up`.

### General

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Home page: what the system does, live counters (graduates, job postings and how many are open, applications, announcements), the newest open job postings, the latest announcements and "how it works" in three steps; still opens when the database is down (counters show a dash, the lists show a note) |
| GET | `/about` | About page |
| GET | `/404` | Generic 404 page; invalid browser requests are redirected here (answers 404) |
| GET | `/api/health` | Health check |
| GET | `/api/swagger` | Redirects to Swagger UI (`/docs`) |
| GET | `/api/debug/error` | Test-only: fails on purpose (500). Exists only when `DEBUG_ROUTES=1` |

### Web interface (HTML pages, manage everything from the browser)

HTML forms can only send GET and POST, so update and delete use POST sub-routes; after a successful form the page redirects (`303`).

| Method | Path | Description |
| --- | --- | --- |
| GET | `/users` | User list + create form (`User` tag in Swagger) |
| POST | `/users` | Create a user (form submit) |
| GET | `/users/{id}` | User detail page |
| GET | `/users/{id}/edit` | Edit form |
| POST | `/users/{id}/edit` | Update a user |
| POST | `/users/{id}/delete` | Delete a user |
| GET | `/announcements` | Announcement list + create form (`Announcement` tag in Swagger) |
| POST | `/announcements` | Create an announcement (form submit) |
| GET | `/announcements/{id}` | Announcement detail page |
| GET | `/announcements/{id}/edit` | Edit form |
| POST | `/announcements/{id}/edit` | Update an announcement |
| POST | `/announcements/{id}/delete` | Delete an announcement |
| GET | `/job-postings` | Job posting list + create form (`JobPosting` tag in Swagger) |
| POST | `/job-postings` | Create a job posting (a refused form comes back with the message and what was typed) |
| GET | `/job-postings/{id}` | Posting detail page: its applicants and an apply form |
| GET | `/job-postings/{id}/edit` | Edit form |
| POST | `/job-postings/{id}/edit` | Update a job posting |
| POST | `/job-postings/{id}/delete` | Delete a job posting (its applications go with it) |
| POST | `/job-postings/{id}/apply` | Apply to this posting from its page (shows a message if refused) |
| GET | `/applications` | Application list, status change, delete and a new-application form (`Application` tag in Swagger) |
| POST | `/applications` | Apply (form submit; a duplicate or a closed posting shows a message above the table) |
| POST | `/applications/{id}/status` | Change the status of an application |
| POST | `/applications/{id}/delete` | Delete (withdraw) an application |

Every page shares one navbar (Home, About, Users, Announcements, Job Postings, Applications, API Docs) and one stylesheet (`app/static/app.css`), and works on phone screens too. List pages have a filter box that narrows the table as you type, a `+ New ...` button that jumps to the create form, and a confirmation question before anything is deleted. Status values use coloured badges; a refused action shows a red message at the top of the page. User-supplied text is escaped on every page.

### JSON API (Postman / Swagger)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/users` | List all users (`ApiUser` tag in Swagger) |
| GET | `/api/users/{id}` | Get a single user |
| POST | `/api/users` | Create a new user |
| PUT | `/api/users/{id}` | Replace a user (all fields required) |
| PATCH | `/api/users/{id}` | Partially update a user |
| DELETE | `/api/users/{id}` | Delete a user |
| GET | `/api/announcements` | List all announcements (`ApiAnnouncement` tag in Swagger) |
| GET | `/api/announcements/{id}` | Get a single announcement |
| POST | `/api/announcements` | Create an announcement |
| PUT | `/api/announcements/{id}` | Replace an announcement (all fields required) |
| PATCH | `/api/announcements/{id}` | Partially update an announcement |
| DELETE | `/api/announcements/{id}` | Delete an announcement |
| GET | `/api/job-postings` | List all job postings (`ApiJobPosting` tag, direct route) |
| POST | `/api/job-postings` | Create a job posting (`posted_by_user_id` in the body, or `null`) |
| GET | `/api/job-postings/{id}` | Get a single job posting |
| PUT | `/api/job-postings/{id}` | Replace a job posting |
| PATCH | `/api/job-postings/{id}` | Partially update a job posting |
| DELETE | `/api/job-postings/{id}` | Delete a job posting |
| GET | `/api/users/{user_id}/job-postings` | Job postings of one user (nested route) |
| POST | `/api/users/{user_id}/job-postings` | Create a job posting owned by that user |
| GET | `/api/users/{user_id}/job-postings/{id}` | One job posting of that user (`404` if it belongs to someone else) |
| DELETE | `/api/users/{user_id}/job-postings/{id}` | Delete one job posting of that user |
| GET | `/api/applications` | List all applications (`ApiApplication` tag, direct route) |
| POST | `/api/applications` | Apply: `user_id`, `job_posting_id`, optional `cover_letter` in the body |
| GET | `/api/applications/{id}` | Get a single application |
| PATCH | `/api/applications/{id}` | Change `status` / `cover_letter` |
| DELETE | `/api/applications/{id}` | Delete (withdraw) an application |
| GET | `/api/users/{user_id}/applications` | Applications of one user (nested route) |
| POST | `/api/users/{user_id}/applications` | That user applies to a posting (`job_posting_id` in the body) |
| GET | `/api/users/{user_id}/applications/{id}` | One application of that user |
| DELETE | `/api/users/{user_id}/applications/{id}` | That user withdraws the application |
| GET | `/api/job-postings/{posting_id}/applications` | Applicants of one job posting (nested route) |
| POST | `/api/job-postings/{posting_id}/applications` | A user applies to that posting (`user_id` in the body) |
| GET | `/api/job-postings/{posting_id}/applications/{id}` | One application to that posting |
| PATCH | `/api/job-postings/{posting_id}/applications/{id}` | Move the application on (e.g. `status: interview`) |

- *Direct* routes (`/api/job-postings/...`) address a posting by its own id; *nested* routes (`/api/users/{user_id}/job-postings/...`) follow the `users → job_postings` relationship. An application links a user to a job posting, so it is nested in two directions. Details in [ddd.md 8.2](ddd.md#82-routes-direct-and-nested) and [ddd.md 8.3](ddd.md#83-applications-models-and-routes).
- **Job posting rules** ([ddd.md 4.3.1](ddd.md#431-validation-rules-for-a-job-posting)): `title` is required (at most 120 characters), `company` and `city` are required, and a posting needs **at least one** of `description` and `application_url` (either one, or both). The JSON field for the place is `city` (it was `location` before migration `0004`).
- **Status codes:** a duplicate user email, a duplicate application and an application to a closed posting answer `409`; invalid input answers `422`; a missing id answers `404` with a reason; a database failure answers `503` with an error id (see [Middleware](#middleware-the-request-pipeline)).

## Middleware: the request pipeline

A **middleware** runs around every request: before the route's controller runs and after its answer is ready. Four of them shape what leaves the app (`app/middleware/`, registered in `app/main.py`):

```
request ─► logger ─► 5xx guardian ─► 404 guardian ─► route ─► controller ─► model ─► database
answer  ◄─ logger ◄─ 5xx guardian ◄─ 404 guardian ◄─ ...
```

| Middleware | File | Job |
| --- | --- | --- |
| Logger | `logger.py` | Writes one line per request on the terminal: time, method, route, status, duration. |
| 404 guardian | `not_found_guardian.py` | Every 404 answers with a **reason**; invalid browser requests are redirected to the generic `/404` page. |
| 5xx guardian | `server_error_guardian.py` | A server failure answers 500/503 with a reason and an **error id**, never with a traceback; the details go to `logs/error.logs`. |

The middleware added last runs outermost, so `main.py` adds them from the inside out: the 404 guardian, then the 5xx guardian (it also catches a failure inside the 404 guardian), then the logger (it sees and logs the final answer).

### Request logging (logger middleware)

```
time      method route status duration
09:58:29  GET /users 200 57 ms
09:58:31  POST /api/users 409 2 ms
10:53:02  GET /olmayan-sayfa 302 28 ms
10:39:47  GET /api/users 503 4067 ms
```

- Watch it live: run `docker compose up` in the foreground, or `docker compose logs -f api` if the containers run in the background (`-d`). Docker Desktop shows the same lines under the container's **Logs** tab.
- Every request is logged (pages, the JSON API, Swagger, static files) with its real final status code (200, 302, 303, 307, 404, 405, 409, 422, 500, 503, ...).
- Uvicorn's own access log is turned off (`--no-access-log` in the `Dockerfile`), so each request appears once, in this format. The time zone comes from `TZ`.

### 404 guardian

Every `404 Not Found` leaves the app with a **reason**. The guardian tells the cases apart:

| Case | Example | Reason |
| --- | --- | --- |
| No route matches the address | `GET /api/olmayan` | `No route matches GET /api/olmayan. Check the address; every API route is listed at /api/swagger.` |
| The address is right, but the record does not exist | `GET /api/users/999` | `User not found (user_id=999).` |
| A static file does not exist | `GET /static/yok.css` | `The file /static/yok.css does not exist.` |

- The JSON API and other clients get JSON: `{"status": 404, "error": "Not Found", "reason": "...", "method": "GET", "path": "/api/users/999"}`.
- In the browser, a valid address with a missing record (e.g. `/users/999`) gets an HTML page with the same reason and a link back to its list.

### Generic 404 page and redirect of invalid requests

An **invalid browser request** is not answered with a raw error: it is **redirected** to the generic 404 page at **`/404`**, which shows the address that was asked for and links to the pages that exist.

| Invalid browser request | Example | Answer |
| --- | --- | --- |
| No route matches the address | `GET /olmayan-sayfa` | `302` → `/404?path=%2Folmayan-sayfa` |
| The address itself is malformed (a path parameter of the wrong type) | `GET /users/abc` | `302` → `/404?path=%2Fusers%2Fabc` (instead of a raw 422) |
| A form posted to an address that does not exist | `POST /olmayan` | `303` → `/404?path=...` (303 makes the browser load the page with GET) |

- The `/404` page itself answers **404**, so the end of the redirect still says "not found" (search engines and programs do not take it for a real page).
- Not redirected: the JSON API (`/api/...` keeps its JSON 404 or 422; programs expect a status code, not a redirect), a valid address with a missing record (`/users/999` keeps its page with the reason), form errors (`422` with the message on the form) and missing static files.
- The requested address is only shown on the page (escaped), never used as a redirect target, so `/404?path=` cannot send anyone to another site.

### 5xx guardian

A server-side failure ("my mistake", 5xx) never sends a traceback or internal details to the client. The client gets a status, a reason and an **error id**; the details are written to `logs/error.logs` under the same error id.

| Case | Status | Reason sent to the client |
| --- | --- | --- |
| The database cannot be reached (e.g. the `db` container is stopped) | **503** Service Unavailable | `The database is not reachable right now, so this request could not be completed. Please try again in a moment.` |
| Any other unexpected error in the code | **500** Internal Server Error | `Something went wrong on the server. This is our mistake, not yours; it has been logged with the error id below.` |
| A route answers 5xx on purpose | its own status | its own reason |

```json
{"status": 503, "error": "Service Unavailable", "reason": "The database is not reachable right now, ...", "error_id": "498df6ee", "method": "GET", "path": "/api/users"}
```

- JSON for the API and other clients; an HTML error page for browser pages, with the reason, the error id and a "Try again" button.
- The terminal only shows the usual request line (`GET /api/users 503 4067 ms`); the error itself goes to the error log.
- To see a 500 on purpose, set `DEBUG_ROUTES=1` in `.env` and call `GET /api/debug/error`. To see a 503, run `docker compose stop db`, open a page, then `docker compose start db`.

### Error log (`logs/error.logs`)

Server errors (5xx) are kept in **`logs/error.logs`**, so they can be read later, after the terminal is closed or the container is recreated. The `logs/` folder of the project is mounted into the `api` container (`./logs:/code/logs` in `docker-compose.yml`), so the file is right there in the project folder.

Each error is one short record: when, the error id, the request, the cause, **where in our code** it happened (file, line, function, code), where it finally broke inside a library, and the error message. Framework internals are left out so the cause is easy to find.

```
2026-11-11 10:39:50  ERROR abc7df08  GET /job-postings/3  503
cause: database unreachable: OperationalError
where (our code):
  app/controllers/job_posting_controller.py:119 in get: return HTMLResponse(self._detail(posting_id))
  app/controllers/job_posting_controller.py:168 in _detail: posting = job_posting_model.get_job_posting(posting_id)
  app/models/job_posting.py:187 in get_job_posting: return _to_dict(_find(session, posting_id, user_id))
  app/models/job_posting.py:155 in _find: posting = session.get(JobPosting, posting_id)
failed inside: psycopg2/__init__.py:122 in connect
error: sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) could not translate host name "db" to address: Name or service not known
--------------------------------------------------------------------------------
```

- Find one error by the id a user reports: `findstr abc7df08 logs\error.logs` (Windows) or `grep -A8 abc7df08 logs/error.logs`.
- Watch new errors live: `Get-Content logs\error.logs -Wait -Tail 20` (PowerShell) or `tail -f logs/error.logs`.
- At 1 MB the file is renamed to `error.logs.1` and a new one starts (5 old files are kept), so it never grows without limit.
- Deleting the file to clear it is fine: the next error creates it again.
- Log files are not committed (`logs/*` is in `.gitignore`); only the empty folder (`logs/.gitkeep`) is.
- Client mistakes (4xx) are not written here: they are not server errors. They appear in the terminal request log with their status code.

## Project Architecture (MVC)

The project follows the **Model–View–Controller (MVC)** pattern, split into dedicated files/folders under `app/`, with middleware around every request:

```
AlumniTrackingSystem/
├── app/
│   ├── __init__.py
│   ├── main.py                                  # Creates the app, adds the middleware, wires the routers, /, /about, /404
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py                   # UserController -> HTML pages under /users
│   │   ├── api_user_controller.py               # ApiUserController -> JSON under /api/users
│   │   ├── announcement_controller.py           # AnnouncementController -> HTML pages under /announcements
│   │   ├── api_announcement_controller.py       # ApiAnnouncementController -> JSON under /api/announcements
│   │   ├── job_posting_controller.py            # JobPostingController -> HTML pages under /job-postings
│   │   ├── api_job_posting_controller.py        # ApiJobPostingController -> direct + nested JSON routes
│   │   ├── application_controller.py            # ApplicationController -> HTML pages under /applications
│   │   └── api_application_controller.py        # ApiApplicationController -> direct + nested (user, posting) JSON routes
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── logger.py                            # Logger: one terminal line per request
│   │   ├── not_found_guardian.py                # 404 guardian: reasons, redirect of invalid browser requests to /404
│   │   └── server_error_guardian.py             # 5xx guardian: 500/503 with a reason and an error id; writes logs/error.logs
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py                        # DB connection from DATABASE_URL
│   │   ├── stats.py                             # Read-only queries for the home page (counters, newest open postings, latest announcements)
│   │   ├── factories.py                         # UserFactory, AnnouncementFactory, JobPostingFactory (fake data)
│   │   └── seed.py                              # Seeder: inserts fake data into the tables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                              # SQLAlchemy Base for all ORM models
│   │   ├── user.py                              # User ORM model, schemas + CRUD on the users table
│   │   ├── announcement.py                      # Announcement ORM model, schemas + CRUD on the announcements table
│   │   ├── job_posting.py                       # JobPosting ORM model, schemas, validation rules + functions
│   │   └── application.py                       # Application ORM model, schemas + functions
│   ├── views/
│   │   ├── __init__.py
│   │   ├── layout.py                            # Shared page skeleton: fonts, navbar, footer, motion script, helpers (render_page, page_header, ...)
│   │   ├── home_view.py                         # HTML for the home page
│   │   ├── user_view.py                         # HTML for user list/detail/edit pages
│   │   ├── announcement_view.py                 # HTML for announcement list/detail/edit pages
│   │   ├── job_posting_view.py                  # HTML for job posting list/detail/edit pages
│   │   ├── application_view.py                  # HTML for the application list page
│   │   └── error_view.py                        # HTML error pages: generic 404, 404 with a reason, 5xx
│   ├── static/
│   │   └── app.css                              # The one stylesheet used by every page (tokens and components from DESIGN.md)
│   └── templates/                               # Page body of /about (the layout adds navbar and footer)
│       └── about.html
├── logs/                                        # error.logs (git ignored), written by the 5xx guardian
├── migrations/                                  # Alembic migrations (database schema)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_create_users_and_announcements.py
│       ├── 0002_create_job_postings.py
│       ├── 0003_create_applications.py
│       └── 0004_job_posting_validation_rules.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                                         # Real values (git ignored)
├── .env.example                                 # Template, committed to git
├── ddd.md                                       # Data Design Documentation
├── brand.md                                     # Brand Guide (logo, colours, type, components, tone)
├── DESIGN.md                                    # Design System (tokens, components, motion, prompts)
└── README.md
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| **Model** | `app/models/` — SQLAlchemy ORM models (`User`, `Announcement`, `JobPosting`, `Application`, with the `User.job_postings` ↔ `JobPosting.posted_by` relationship and `Application` linking `User` and `JobPosting`), Pydantic schemas and the functions that read and write PostgreSQL | Defines the tables, their relationships and the rules of the data (each rule written once, here), e.g. a job posting needs a description or an application URL. Described in [ddd.md](ddd.md). |
| **View** | `app/views/` (`layout.py` holds the shared navbar and page skeleton; one file per resource; `error_view.py` for error pages), `app/templates/` (body of `/about`), `app/static/app.css` | Builds the HTML returned to the browser. For the JSON API routes, the JSON response itself is the "view" served to API clients (Postman, Swagger UI). |
| **Controller** | `app/controllers/` — two independent controllers per resource: `UserController` + `ApiUserController`, `AnnouncementController` + `ApiAnnouncementController`, `JobPostingController` + `ApiJobPostingController`, `ApplicationController` + `ApiApplicationController` | Each controller has its own methods and its own `APIRouter`. The plain controller serves HTML pages; the `Api...` controller serves JSON. `main.py` registers all the routers with `app.include_router(...)`. |
| **Middleware** | `app/middleware/` — logger, 404 guardian, 5xx guardian | Runs around every request, before and after the controller: logs it, and turns errors into answers with a reason (404) or an error id (5xx). See [Middleware](#middleware-the-request-pipeline). |

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `docker compose up` says `Bind for 0.0.0.0:5432 failed: port is already allocated` (or pages are slow and answer 503) | Another program or project on the computer already uses port 5432, so the `db` container cannot start on its network. | Set another host port in `.env`, e.g. `POSTGRES_PORT=5433`, then `docker compose up -d`. The app is not affected (it uses `db:5432` inside Docker); DBeaver/psql on the host use the new port. The same works for `API_PORT` if 8000 is taken. |
| Pages answer **503** "The database is not reachable" | The `db` container is stopped or not running correctly. | `docker compose ps` should show `db` as `healthy`; start it with `docker compose up -d`. The cause is also in `logs/error.logs`. |
| `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified` | Docker Desktop is not running. | Start Docker Desktop and wait until it says it is running. |
| A page or route answers **500**, or the tables seem missing | On a fresh database the migrations have not run yet. | `docker compose exec api alembic upgrade head`, then optionally the seeder. |
| A change in `requirements.txt` or `Dockerfile` does not show | The image was built before the change. | `docker compose up -d --build`. (Changes under `app/` show at once: the folder is mounted and the server reloads.) |
| `docker compose up` starts the wrong app | Two projects in folders with the same name shared one Compose project name. | This project sets `name: alumni-fastapi` in `docker-compose.yml`, so its containers and images have their own names. |

## Progress

The system is built incrementally, one task (and one commit) at a time, following the course.

| Step | What was built |
| --- | --- |
| Setup | Public repository, README, FastAPI scaffold, Docker and Docker Compose. |
| Routing | First routes: `/`, `/hello`, `/hello/{name}`, `/sum/{a}/{b}`, `/about`; a home page and an about page. |
| HTTP methods and CRUD | `/api/health`; users CRUD in memory (`POST`, `GET`, `PUT`, `PATCH`, `DELETE`); Postman; Swagger at `/api/swagger`. |
| MVC | Architecture in the README; user model; two controllers per resource (pages and JSON API); views; announcements (model, two controllers, routes, management pages). |
| Database and ORM | Forgetting test; `ddd.md`; PostgreSQL service with a named volume; `.env` / `.env.example`; Alembic migrations; factories and seeding; the app moved from memory to the database (only the models changed). |
| Relational data and advanced routing | `job_postings` (one-to-many) and `applications` (many-to-many, join table, unique pair); ORM relationships; direct and nested routes; seeding job postings; pages for job postings and applications; one stylesheet and layout for the whole site. |
| **Latest session (2026-11-11): rules, middleware and errors** | Job posting validation rules decided in `ddd.md` and applied by migration `0004` (title ≤ 120 characters, required company and city, at least one of description and application URL); **logger** middleware; **404 guardian** (reasons); **5xx guardian** (500/503 with an error id, no traceback); **error log** in `logs/error.logs`; **generic 404 page** at `/404` with redirect of invalid browser requests; port conflict on 5432 solved with `POSTGRES_PORT` and documented in [Troubleshooting](#troubleshooting). |

## Status

Work in progress: built incrementally week by week.
