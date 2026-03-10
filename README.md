# BudgetHive API

FastAPI backend for BudgetHive, a budget management React application. Replaces Supabase with SQLite + JWT auth.

## Project Structure

```
budgetHive-api/
├── main.py                 # FastAPI app entry point
├── requirements.txt
├── render.yaml             # Render deployment config
├── .env.example
├── README.md
└── app/
    ├── __init__.py
    ├── config.py           # Settings (env vars)
    ├── database.py         # SQLAlchemy engine, session
    ├── auth.py             # JWT, password hashing
    ├── dependencies.py     # Budget ownership checks
    ├── models/
    │   ├── __init__.py
    │   ├── user.py         # User, Profile
    │   └── budget.py       # Budget, Activity, BudgetRevision, DepartmentShare
    ├── schemas/
    │   ├── __init__.py
    │   ├── auth.py
    │   └── budget.py
    └── routers/
        ├── __init__.py
        ├── auth.py
        ├── budgets.py
        ├── activities.py
        ├── revisions.py
        └── shares.py
```

## SQLite Schema

```sql
-- users
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- profiles
CREATE TABLE profiles (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    avatar_url TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- budgets
CREATE TABLE budgets (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255),
    answers JSON,
    budget_data JSON,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- activities
CREATE TABLE activities (
    id VARCHAR(36) PRIMARY KEY,
    budget_id VARCHAR(36) NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    details JSON,
    created_at TIMESTAMP
);

-- budget_revisions
CREATE TABLE budget_revisions (
    id VARCHAR(36) PRIMARY KEY,
    budget_id VARCHAR(36) NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    revision_number INTEGER NOT NULL,
    answers JSON,
    budget_data JSON,
    created_at TIMESTAMP
);

-- department_shares
CREATE TABLE department_shares (
    id VARCHAR(36) PRIMARY KEY,
    budget_id VARCHAR(36) NOT NULL REFERENCES budgets(id) ON DELETE CASCADE,
    share_type VARCHAR(50),
    permissions JSON,
    expires_at TIMESTAMP,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

## Run Locally

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment (optional)**
   ```bash
   cp .env.example .env
   # Edit .env: set SECRET_KEY, CORS_ORIGINS for your frontend
   ```

4. **Start the server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **API docs**
   - Swagger: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Deploy on Render

1. **Create a new Web Service**
   - Connect your GitHub repo (or use `render.yaml` blueprint)
   - Select `budgetHive-api` as root (or adjust paths)

2. **Build & Start**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Environment variables**
   - `SECRET_KEY`: Generate a strong secret (Render can auto-generate)
   - `CORS_ORIGINS`: Your frontend URL, e.g. `https://budgethive.onrender.com`
   - `DATABASE_URL`: `sqlite:///./budgethive.db` (default; Render disk is ephemeral – use a persistent disk for production or switch to PostgreSQL)

4. **Note on SQLite on Render**
   - Render's filesystem is ephemeral. For production, consider:
     - Adding a [Render Disk](https://render.com/docs/disks) and setting `DATABASE_URL` to the disk path, or
     - Switching to PostgreSQL and using `render.com` PostgreSQL addon.

## API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/signup` | No | Create user, return JWT |
| POST | `/auth/login` | No | Login, return JWT |
| GET | `/auth/me` | Yes | Current user |
| GET | `/budgets` | Yes | List user's budgets |
| POST | `/budgets` | Yes | Create budget |
| PATCH | `/budgets/{id}` | Yes | Update budget |
| DELETE | `/budgets/{id}` | Yes | Delete budget |
| GET | `/budgets/{id}/activities` | Yes | List activities |
| POST | `/budgets/{id}/activities` | Yes | Create activity |
| GET | `/budgets/{id}/revisions` | Yes | List revisions |
| POST | `/budgets/{id}/revisions` | Yes | Create revision |
| POST | `/budgets/{id}/shares` | Yes | Create share |
| GET | `/shares/{shareId}` | Yes | Get share |
| PATCH | `/shares/{shareId}` | Yes | Update share |

## Example Fetch Requests (React)

```javascript
const API_URL = "http://localhost:8000"; // or your Render URL
let token = null; // store after login/signup

// Auth
async function signup(email, password, fullName) {
  const res = await fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
  const data = await res.json();
  token = data.access_token;
  return data;
}

async function login(email, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  const data = await res.json();
  token = data.access_token;
  return data;
}

// Helper for authenticated requests
function authHeaders() {
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

// Budgets
async function getBudgets() {
  const res = await fetch(`${API_URL}/budgets`, { headers: authHeaders() });
  return res.json();
}

async function createBudget(budget) {
  const res = await fetch(`${API_URL}/budgets`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(budget),
  });
  return res.json();
}

async function updateBudget(id, updates) {
  const res = await fetch(`${API_URL}/budgets/${id}`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(updates),
  });
  return res.json();
}

async function deleteBudget(id) {
  await fetch(`${API_URL}/budgets/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
}

// Activities
async function getActivities(budgetId) {
  const res = await fetch(`${API_URL}/budgets/${budgetId}/activities`, {
    headers: authHeaders(),
  });
  return res.json();
}

async function createActivity(budgetId, action, details) {
  const res = await fetch(`${API_URL}/budgets/${budgetId}/activities`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ action, details }),
  });
  return res.json();
}

// Revisions
async function getRevisions(budgetId) {
  const res = await fetch(`${API_URL}/budgets/${budgetId}/revisions`, {
    headers: authHeaders(),
  });
  return res.json();
}

async function createRevision(budgetId, revision) {
  const res = await fetch(`${API_URL}/budgets/${budgetId}/revisions`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(revision),
  });
  return res.json();
}

// Shares
async function createShare(budgetId, share) {
  const res = await fetch(`${API_URL}/budgets/${budgetId}/shares`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify(share),
  });
  return res.json();
}

async function getShare(shareId) {
  const res = await fetch(`${API_URL}/shares/${shareId}`, {
    headers: authHeaders(),
  });
  return res.json();
}

async function updateShare(shareId, updates) {
  const res = await fetch(`${API_URL}/shares/${shareId}`, {
    method: "PATCH",
    headers: authHeaders(),
    body: JSON.stringify(updates),
  });
  return res.json();
}
```
