# Alumni Tracking System

A backend system to track Management Information Systems (MIS) graduates, built for the Web Programming (YBSB3001) course.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose

## Documentation

- [Data Design Documentation (ddd.md)](ddd.md): database tables, columns, constraints, relationships and the migration commands.

## Database Migrations

The database schema is created by [Alembic](https://alembic.sqlalchemy.org/) migrations, written from `ddd.md`. They live in `migrations/versions/`.

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

Check the result with:
```bash
docker compose exec db psql -U alumni -d alumni -c "SELECT id, name, email FROM users LIMIT 5;"
docker compose exec db psql -U alumni -d alumni -c "SELECT id, title, company, employment_type, posted_by_user_id FROM job_postings LIMIT 5;"
```

Seeded job postings belong to existing users (or to nobody, for department postings), so they also show up under `GET /api/users/{id}/job-postings`.

Tables created so far (migrations `0001`, `0002`, `0003`): `users`, `announcements`, `job_postings` and `applications`, all described in [ddd.md](ddd.md). The FastAPI app reads and writes them (see the note under the API endpoints). You can also inspect the tables directly with:
```bash
docker compose exec db psql -U alumni -d alumni -c "\dt"
```

> **Rule:** Every change to the database (new table, new/renamed/removed column, type, constraint, index or relationship) must be documented in [ddd.md](ddd.md) in the same commit. `ddd.md` is the single source of truth for the data design.

## Running the Project

1. Clone the repository:
   ```bash
   git clone https://github.com/uumutkorkmaz/alumni.git
   cd alumni
   ```

2. Create your environment file from the template:
   ```bash
   cp .env.example .env
   ```
   Then open `.env` and set your own values (see [Environment Variables](#environment-variables)).

3. Start the system:
   ```bash
   docker compose up
   ```

4. Create the database tables (run the migrations):
   ```bash
   docker compose exec api alembic upgrade head
   ```

5. API docs (Swagger UI) will be available at:
   ```
   http://localhost:8000/api/swagger
   ```
   (redirects to the auto-generated `/docs` page, kept up to date automatically with every new endpoint)

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
| `POSTGRES_PORT` | `db` | Host port mapped to PostgreSQL (default `5432`). |
| `API_PORT` | `api` | Host port mapped to the FastAPI app (default `8000`). |
| `DATABASE_URL` | `api` | Connection string: `postgresql://USER:PASSWORD@db:5432/DB_NAME`. Keep it consistent with the three `POSTGRES_*` values above. |

> If you add a new variable, add it to both `.env` and `.env.example`. Never commit `.env`.
> `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` only take effect when the `pgdata` volume is created for the first time. To apply new values to an existing volume, run `docker compose down -v` (this deletes the stored database data).

## API Endpoints

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/health` | Health check |
| GET | `/api/swagger` | Redirects to Swagger UI |

### Web interface (HTML pages, manage everything from the browser)

HTML forms can only send GET/POST, so update and delete use POST sub-routes.

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

### JSON API (Postman / Swagger)

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/users` | List all users (`ApiUser` tag in Swagger) |
| GET | `/api/users/{id}` | Get a single user |
| POST | `/api/users` | Create a new user |
| PUT | `/api/users/{id}` | Replace a user (all fields required) |
| PATCH | `/api/users/{id}` | Partially update a user |
| DELETE | `/api/users/{id}` | Delete a user |
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
| GET | `/api/announcements` | List all announcements (`ApiAnnouncement` tag in Swagger) |
| GET | `/api/announcements/{id}` | Get a single announcement |
| POST | `/api/announcements` | Create an announcement |
| PUT | `/api/announcements/{id}` | Replace an announcement (all fields required) |
| PATCH | `/api/announcements/{id}` | Partially update an announcement |
| DELETE | `/api/announcements/{id}` | Delete an announcement |

> The job posting and application routes need the `job_postings` and `applications` tables. They are created by migrations `0002` and `0003`; on a fresh database run `docker compose exec api alembic upgrade head` first, otherwise these routes answer with a server error. An application links a user to a job posting, so it is nested in two directions: under a user and under a posting. Duplicate applications and applications to closed postings answer `409`. *Direct* routes (`/api/job-postings/...`) address a posting by its own id; *nested* routes (`/api/users/{user_id}/job-postings/...`) follow the `users → job_postings` relationship. Details in [ddd.md](ddd.md#82-routes-direct-and-nested) and [ddd.md](ddd.md#83-applications-models-and-routes).

> The app is connected to PostgreSQL. The web and API routes of each resource use the same table (`users`, `announcements`), so a record created through one is visible through the other, and records survive `docker compose down` / `up`. Run the migrations first (see [Database Migrations](#database-migrations)); use the seeder to fill the tables with test data. A duplicate user email answers `409`, invalid input answers `422`, a missing id answers `404`. The database design is in [ddd.md](ddd.md).

## Project Architecture (MVC)

The project follows the **Model–View–Controller (MVC)** pattern, split into dedicated files/folders under `app/`:

```
AlumniTrackingSystem/
├── app/
│   ├── __init__.py
│   ├── main.py                          # Wires routers into the FastAPI app
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py                   # UserController -> HTML pages under /users
│   │   ├── api_user_controller.py               # ApiUserController -> JSON under /api/users
│   │   ├── announcement_controller.py           # AnnouncementController -> HTML pages under /announcements
│   │   ├── api_announcement_controller.py       # ApiAnnouncementController -> JSON under /api/announcements
│   │   ├── api_job_posting_controller.py        # ApiJobPostingController -> direct + nested JSON routes
│   │   └── api_application_controller.py        # ApiApplicationController -> direct + nested (user, posting) JSON routes
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py                        # DB connection from DATABASE_URL
│   │   ├── factories.py                         # UserFactory, AnnouncementFactory (fake data)
│   │   └── seed.py                              # Seeder: inserts fake data into the tables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                              # SQLAlchemy Base for all ORM models
│   │   ├── user.py                              # User ORM model, schemas + CRUD on the users table
│   │   ├── announcement.py                      # Announcement ORM model, schemas + CRUD on the announcements table
│   │   ├── job_posting.py                       # JobPosting ORM model + job posting functions (table from migration 0002)
│   │   └── application.py                       # Application ORM model + application functions (table from migration 0003)
│   ├── views/
│   │   ├── __init__.py
│   │   ├── layout.py                            # Shared navbar for the management pages
│   │   ├── user_view.py                         # HTML for user list/detail/edit pages
│   │   └── announcement_view.py                 # HTML for announcement list/detail/edit pages
│   └── templates/                               # Static HTML pages
│       ├── index.html
│       └── about.html
├── migrations/                                  # Alembic migrations (database schema)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_create_users_and_announcements.py
│       ├── 0002_create_job_postings.py
│       └── 0003_create_applications.py
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env                                         # Real values (git ignored)
├── .env.example                                 # Template, committed to git
├── ddd.md                                       # Data Design Documentation
└── README.md
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| **Model** | `app/models/user.py`, `app/models/announcement.py` — SQLAlchemy ORM models (`User`, `Announcement`, `JobPosting`, `Application`, with the `User.job_postings` ↔ `JobPosting.posted_by` relationship and `Application` linking `User` and `JobPosting`), Pydantic schemas (`UserCreate`/`UserUpdate`, `AnnouncementCreate`/`AnnouncementUpdate`) and CRUD functions that run SQL against PostgreSQL | Defines the tables, their relationships and the validation of the data, and reads/writes it in the database (described in [ddd.md](ddd.md)). |
| **View** | `app/views/user_view.py`, `app/views/announcement_view.py` (management pages), `app/templates/` (static `/` and `/about` pages) | Builds the HTML returned to the browser. For the JSON API routes, the JSON response itself is the "view" served to API clients (Postman, Swagger UI). |
| **Controller** | Two independent controllers per resource: `UserController` + `ApiUserController`, `AnnouncementController` + `ApiAnnouncementController` | Each controller has its own CRUD methods and its own `APIRouter`. The plain controller serves HTML pages; the `Api...` controller serves JSON. `main.py` registers all four routers with `app.include_router(...)`. |

## Status

Work in progress — built incrementally week by week.
