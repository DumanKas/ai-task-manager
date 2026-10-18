# AI Task Manager API 🤖📋

A robust backend application for task management, integrated with AI for smart task categorization and priority setting.

## 🚀 Features
*   **Task Management:** Full CRUD operations for tasks.
*   **AI Integration:** Uses OpenAI API to analyze task descriptions and automatically suggest priorities/categories.
*   **Asynchronous Architecture:** Built with FastAPI and SQLAlchemy (async) for high performance.
*   **Database Migrations:** Managed via Alembic for reliable schema updates.
*   **Security:** Environment variables managed via `.env` (template provided in `.env.example`).

## 🛠 Tech Stack
*   **Framework:** FastAPI (Python 3.10+)
*   **Database:** PostgreSQL (via SQLAlchemy 2.0 / asyncpg)
*   **Migrations:** Alembic
*   **AI Integration:** OpenAI API
*   **Tools:** Pydantic, Git, Uvicorn

## ⚙️ How to run locally
1. Clone the repository:
   `git clone https://github.com/DumanKas/ai-task-manager.git`
2. Install dependencies:
   `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and add your credentials:
   `cp .env.example .env`
4. Run database migrations:
   `alembic upgrade head`
5. Start the server:
   `uvicorn app.main:app --reload`

---
*Developed by Duman Kasymkul*
