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
| GET | `/api/users` | List all users |
| GET | `/api/users/{id}` | Get a single user |
| POST | `/api/users` | Create a new user |
| PUT | `/api/users/{id}` | Replace a user (all fields required) |
| PATCH | `/api/users/{id}` | Partially update a user |
| DELETE | `/api/users/{id}` | Delete a user |

## Project Architecture (MVC)

The project follows the **Model–View–Controller (MVC)** pattern. Right now the codebase is small, so Model and Controller responsibilities live together inside `app/main.py`, while the View layer is split out into its own `templates/` folder. As the project grows (database models, more pages), each layer is meant to move into its own file/folder under `app/`.

```
AlumniTrackingSystem/
├── app/
│   ├── __init__.py
│   ├── main.py          # Controller + Model layer (see breakdown below)
│   └── templates/       # View layer
│       ├── index.html
│       └── about.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| **Model** | `app/main.py` — `UserCreate`, `UserUpdate` classes and the in-memory `users` list | Defines the shape/validation of the data (a user record) and holds the application's data (currently in memory, no database yet). |
| **View** | `app/templates/index.html`, `app/templates/about.html` | The HTML pages returned to the browser for `/` and `/about`. For the JSON API routes (`/api/...`), the JSON response itself acts as the "view" served to API clients (e.g. Postman, Swagger UI). |
| **Controller** | `app/main.py` — the `@app.get/post/put/patch/delete` route functions (`read_root`, `read_about`, `create_user`, `list_users`, `get_user`, `replace_user`, `update_user`, `delete_user`, `read_health`, `read_swagger`) | Receives the HTTP request, talks to the Model (validates input, reads/writes `users`), and decides which View/response to return. |

## Status

Work in progress — built incrementally week by week.
