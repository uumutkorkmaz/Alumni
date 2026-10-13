# Alumni Tracking System

A backend system to track Management Information Systems (MIS) graduates, built for the Web Programming (YBSB3001) course.

## Tech Stack

- **Backend:** FastAPI (Python)
- **Database:** PostgreSQL
- **Containerization:** Docker & Docker Compose

## Running the Project

1. Clone the repository:
   ```bash
   git clone https://github.com/uumutkorkmaz/alumni.git
   cd alumni
   ```

2. Start the system:
   ```bash
   docker compose up
   ```

3. API docs (Swagger UI) will be available at:
   ```
   http://localhost:8000/api/swagger
   ```
   (redirects to the auto-generated `/docs` page, kept up to date automatically with every new endpoint)

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

> There is no database yet. The web and API routes for each resource share the same in-memory list in `app/models/`, so a record created through one is visible through the other. All data is lost when the server restarts.

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
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                              # User schemas + in-memory CRUD
│   │   └── announcement.py                      # Announcement schemas + in-memory CRUD
│   ├── views/
│   │   ├── __init__.py
│   │   ├── user_view.py                         # HTML for user list/detail/edit pages
│   │   └── announcement_view.py                 # HTML for announcement list/detail/edit pages
│   └── templates/                               # Static HTML pages
│       ├── index.html
│       └── about.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| **Model** | `app/models/user.py`, `app/models/announcement.py` — Pydantic schemas (`UserCreate`/`UserUpdate`, `AnnouncementCreate`/`AnnouncementUpdate`), an in-memory list, and CRUD functions | Defines the shape/validation of the data and holds + manipulates it (in memory, no database yet). An announcement has `id`, `title`, `content`, `author`, `created_at`. |
| **View** | `app/views/user_view.py`, `app/views/announcement_view.py` (management pages), `app/templates/` (static `/` and `/about` pages) | Builds the HTML returned to the browser. For the JSON API routes, the JSON response itself is the "view" served to API clients (Postman, Swagger UI). |
| **Controller** | Two independent controllers per resource: `UserController` + `ApiUserController`, `AnnouncementController` + `ApiAnnouncementController` | Each controller has its own CRUD methods and its own `APIRouter`. The plain controller serves HTML pages; the `Api...` controller serves JSON. `main.py` registers all four routers with `app.include_router(...)`. |

## Status

Work in progress — built incrementally week by week.
