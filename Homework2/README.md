# Expense Splitter

A simple expense-splitting application built as a small project for Homework 2.

## Stack
- Backend: Python with uv
- Frontend: Node.js
- Database: SQLite

## Purpose
This app lets a group of people:
- add members
- add shared expenses
- split costs
- view balances and who owes whom

## Folder Structure

```text
Homework2/
  _docs/
    spec.md
  README.md
  AGENTS.md
  .gitignore
  backend/
  frontend/
```

## Getting Started

### Backend
```bash
cd Homework2/backend
uv venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
uv pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd Homework2/frontend
npm install
npm run dev
```

## Screenshot

![SplitEase dashboard](assets/splitease-dashboard.png)

## Notes
This is an intentionally simple MVP and is meant to follow the project specification in `_docs/spec.md`.
