# AI Task Manager 🤖📋

Task manager with AI-assisted categorization and priority suggestions.

> 🚧 **Status: work in progress.** The backend API is being built step by step.
> What is already in the repo is listed below.

## ✅ Done
- Project structure, `requirements.txt`, `.env.example`
- [Telegram bot part in `bot/`: describe in one line what it does]
- pytest set up

## 🔨 In progress / planned
- [ ] FastAPI app skeleton (`app/main.py`, `/health`)
- [ ] Task model and async SQLAlchemy 2.0 + PostgreSQL (asyncpg)
- [ ] CRUD endpoints with Pydantic schemas
- [ ] Alembic migrations
- [ ] OpenAI integration: suggest category and priority from a task description
- [ ] Tests for the API endpoints
- [ ] Dockerfile and docker-compose

## 🛠 Tech stack
Python 3.10+, FastAPI, SQLAlchemy 2.0 (async), PostgreSQL, Alembic, Pydantic,
OpenAI API, pytest

## ⚙️ Run locally
Currently only the part in `bot/` can be run:
1. `git clone https://github.com/DumanKas/ai-task-manager.git`
2. `pip install -r requirements.txt`
3. `cp .env.example .env` and fill in your credentials
4. [how to start the bot]

*Instructions for the API will be added when `app/` is ready.*

Author: Duman Kassymkul
