# Contributing to Bluelink FastAPI Gateway

Thank you for your interest in contributing to **Bluelink FastAPI Gateway**!  
This project aims to provide a clean, modern, extensible backend gateway for interacting with Hyundai/Kia Bluelink APIs, built with **FastAPI**, **SQLAlchemy**, **Alembic**, and **Docker**.

---

## 🧭 Project Structure Overview

```
app/
 ├── api/          # FastAPI routers (HTTP endpoints)
 ├── core/         # Settings, configuration, startup logic
 ├── db/           # Database models, migrations, sessions
 ├── schemas/      # Pydantic schemas
 ├── services/     # Business logic and Bluelink API wrappers
 └── main.py       # FastAPI entrypoint
```

---

## 🧱 How to Contribute

### 1. Fork the repository  
Create your own fork on GitHub to work independently.

### 2. Clone and set up your environment

```bash
git clone https://github.com/YOUR_USER/bluelink-fastapi-gateway.git
cd bluelink-fastapi-gateway
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Use Docker during development

```bash
docker compose up --build
```

### 4. Run Alembic migrations

```bash
alembic upgrade head
```

### 5. Code Format & Quality

This project follows:

- **black** for code formatting  
- **ruff** for linting  
- **isort** for import ordering  

Before submitting your changes:

```bash
black .
ruff check .
isort .
```

### 6. Testing

```bash
pytest -q
```

### 7. Commit & Push

Follow commit naming conventions:

```
feat: add new VIN validation logic  
fix: correct status update endpoint  
docs: update API usage  
refactor: clean service architecture  
```

### 8. Submit a Pull Request

Explain:

- what the change does  
- why it is needed  
- how to test it  

---

## 🧩 What You Can Work On

- Expand the Bluelink API wrapper (lock/unlock, climate control, battery status)
- Add JWT authentication
- Improve error handling
- Add unit & integration tests
- Implement rate limiting
- Add Redis caching layer
- Add device pairing / session refresh logic

---

## ❤️ Code of Conduct

Be respectful, constructive, and collaborative.  
All contributions are reviewed with kindness and professionalism.

---

Thank you for helping improve the project!
