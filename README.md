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

## Status

Work in progress — built incrementally week by week.
