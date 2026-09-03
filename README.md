# AI-Assisted Task Review

A small React and FastAPI application for creating tasks, tracking their status, deleting tasks, and requesting an AI review through OpenRouter.

## Docker setup

Install and start Docker Desktop. Then copy `backend/.env.example` to `backend/.env` and set the real OpenRouter key:

```env
OPENROUTER_API_KEY=your-real-openrouter-key
```

From the project root, build and start both services:

```bash
docker compose up --build
```

Open the application at [http://localhost:8080](http://localhost:8080). The frontend and backend are served together, and the SQLite database persists in the `task-review-data` Docker volume.

Stop the services with `Ctrl+C` or:

```bash
docker compose down
```

Remove the services and database volume:

```bash
docker compose down -v
```

## Local setup

Backend:

```bash
cd backend
python -m venv venv
source venv/Scripts/activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Frontend, in a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). The frontend uses `http://127.0.0.1:8000` by default. Set `VITE_API_URL` if the backend uses another address.

## How it works

The backend creates the SQLite tables when it starts and inserts three sample tasks if the table is empty. The React app loads tasks from the API, then updates its screen after creating, updating, analysing, or deleting a task.

The Docker setup has two services:

- `backend`: runs FastAPI on internal port `8000` and stores SQLite data in `/app/data`.
- `frontend`: builds React into Nginx, serves the website on port `8080`, and proxies `/tasks/` and `/health` to the backend.

The backend uses the OpenAI-compatible SDK to call OpenRouter. The key is read only from `backend/.env`; it is never sent to the browser.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check that the server is running |
| `GET` | `/tasks/` | List all tasks |
| `GET` | `/tasks/?status=NEW` | Filter tasks by status |
| `POST` | `/tasks/` | Create a task |
| `GET` | `/tasks/{task_id}` | Fetch one task |
| `PATCH` | `/tasks/{task_id}/status` | Change task status |
| `DELETE` | `/tasks/{task_id}` | Permanently delete a task |
| `POST` | `/tasks/{task_id}/analyse` | Request an OpenRouter analysis |

Valid priorities are `LOW`, `MEDIUM`, and `HIGH`. Valid statuses are `NEW`, `IN_PROGRESS`, and `COMPLETED`.

## API examples

Run these while the backend is available on port `8000`:

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/tasks/
curl "http://127.0.0.1:8000/tasks/?status=NEW"

curl -X POST http://127.0.0.1:8000/tasks/ \
	-H "Content-Type: application/json" \
	-d '{"title":"Learn the API","description":"Practice the task workflow","priority":"MEDIUM"}'
```

Copy the `id` from the create response and replace `TASK_ID` below:

```bash
curl http://127.0.0.1:8000/tasks/TASK_ID

curl -X PATCH http://127.0.0.1:8000/tasks/TASK_ID/status \
	-H "Content-Type: application/json" \
	-d '{"status":"COMPLETED"}'

curl -X POST http://127.0.0.1:8000/tasks/TASK_ID/analyse

curl -X DELETE http://127.0.0.1:8000/tasks/TASK_ID
```

When using Docker, replace port `8000` with `8080` for requests that go through the frontend proxy.

## Database

The local database is `backend/data/tasks.db`. Docker stores the same database in the named volume `task-review-data`.

To inspect local records from `backend/`:

```bash
python -c "import sqlite3; db=sqlite3.connect('data/tasks.db'); [print(row) for row in db.execute('SELECT * FROM tasks')]; db.close()"
```

To reset local sample data, stop the backend, delete `backend/data/tasks.db`, and start it again.

## Tests

Run the backend tests from `backend/`:

```bash
python -m pytest -q
```

The tests use a separate SQLite database and mock AI responses, so they do not change development data or use OpenRouter credits.
