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
| GET | `/users` | List all users (`User` tag in Swagger) |
| GET | `/users/{id}` | Get a single user |
| POST | `/users` | Create a new user |
| PUT | `/users/{id}` | Replace a user (all fields required) |
| PATCH | `/users/{id}` | Partially update a user |
| DELETE | `/users/{id}` | Delete a user |
| GET | `/api/users` | List all users (`ApiUser` tag in Swagger) |
| GET | `/api/users/{id}` | Get a single user |
| POST | `/api/users` | Create a new user |
| PUT | `/api/users/{id}` | Replace a user (all fields required) |
| PATCH | `/api/users/{id}` | Partially update a user |
| DELETE | `/api/users/{id}` | Delete a user |

> `/users` and `/api/users` both read/write the same in-memory `users` list in `app/models/user.py`, so a record created through one is visible through the other.

## Project Architecture (MVC)

The project follows the **Model–View–Controller (MVC)** pattern, split into dedicated files/folders under `app/`:

```
AlumniTrackingSystem/
├── app/
│   ├── __init__.py
│   ├── main.py                          # Wires routers into the FastAPI app
│   ├── controllers/
│   │   ├── __init__.py
│   │   ├── user_controller.py           # UserController -> routes under /users
│   │   └── api_user_controller.py       # ApiUserController -> routes under /api/users
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py                      # UserCreate/UserUpdate schemas + in-memory CRUD
│   └── templates/                       # View layer
│       ├── index.html
│       └── about.html
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

| Layer | Location | Responsibility |
| --- | --- | --- |
| **Model** | `app/models/user.py` — `UserCreate`, `UserUpdate` schemas, the in-memory `users` list, and the `create_user`/`get_users`/`get_user`/`update_user`/`partial_update_user`/`delete_user` functions | Defines the shape/validation of the data and holds + manipulates the application's data (currently in memory, no database yet). |
| **View** | `app/templates/index.html`, `app/templates/about.html` | The HTML pages returned to the browser for `/` and `/about`. For the JSON API routes, the JSON response itself acts as the "view" served to API clients (e.g. Postman, Swagger UI). |
| **Controller** | `app/controllers/user_controller.py` (`UserController`, mounted at `/users`) and `app/controllers/api_user_controller.py` (`ApiUserController`, mounted at `/api/users`) — two independent controller classes, each defining its own CRUD methods (`create`, `list`, `get`, `replace`, `update`, `delete`) and its own `APIRouter` | Receives the HTTP request, calls into the Model to read/write `users`, and returns the result. `main.py` instantiates both controllers and registers their routers with `app.include_router(...)`. |

## Status

Work in progress — built incrementally week by week.
