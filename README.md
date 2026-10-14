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

Factories (`app/database/factories.py`) generate realistic fake users and announcements with Faker. The seeder (`app/database/seed.py`) inserts them into the database, so you can fill the tables with test data in one command.

| Command | Meaning |
| --- | --- |
| `docker compose exec api python -m app.database.seed` | Add 20 users and 10 announcements. |
| `docker compose exec api python -m app.database.seed --users 50 --announcements 5` | Choose the counts. |
| `docker compose exec api python -m app.database.seed --fresh` | Empty both tables and reset ids first, then seed. |
| `docker compose exec api python -m app.database.seed --seed 7` | Same fake data on every run (use with `--fresh`). |

Check the result with:
```bash
docker compose exec db psql -U alumni -d alumni -c "SELECT id, name, email FROM users LIMIT 5;"
```

Tables created so far: `users` and `announcements`. The FastAPI app reads and writes them (see the note under the API endpoints). You can also inspect the tables directly with:
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
| GET | `/api/announcements` | List all announcements (`ApiAnnouncement` tag in Swagger) |
| GET | `/api/announcements/{id}` | Get a single announcement |
| POST | `/api/announcements` | Create an announcement |
| PUT | `/api/announcements/{id}` | Replace an announcement (all fields required) |
| PATCH | `/api/announcements/{id}` | Partially update an announcement |
| DELETE | `/api/announcements/{id}` | Delete an announcement |

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
│   │   └── api_announcement_controller.py       # ApiAnnouncementController -> JSON under /api/announcements
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py                        # DB connection from DATABASE_URL
│   │   ├── factories.py                         # UserFactory, AnnouncementFactory (fake data)
│   │   └── seed.py                              # Seeder: inserts fake data into the tables
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                              # User schemas + CRUD on the users table
│   │   └── announcement.py                      # Announcement schemas + CRUD on the announcements table
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
│       └── 0001_create_users_and_announcements.py
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
| **Model** | `app/models/user.py`, `app/models/announcement.py` — Pydantic schemas (`UserCreate`/`UserUpdate`, `AnnouncementCreate`/`AnnouncementUpdate`) and CRUD functions that run SQL against PostgreSQL | Defines the shape/validation of the data and reads/writes it in the database (tables described in [ddd.md](ddd.md)). |
| **View** | `app/views/user_view.py`, `app/views/announcement_view.py` (management pages), `app/templates/` (static `/` and `/about` pages) | Builds the HTML returned to the browser. For the JSON API routes, the JSON response itself is the "view" served to API clients (Postman, Swagger UI). |
| **Controller** | Two independent controllers per resource: `UserController` + `ApiUserController`, `AnnouncementController` + `ApiAnnouncementController` | Each controller has its own CRUD methods and its own `APIRouter`. The plain controller serves HTML pages; the `Api...` controller serves JSON. `main.py` registers all four routers with `app.include_router(...)`. |

## Status

Work in progress — built incrementally week by week.
