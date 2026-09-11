# Expense Splitter - Project Specification

## Overview
This project is a very basic expense-splitting application for a small group of people. The app helps users track shared expenses and quickly see who owes whom after a group purchase.

## Goal
Create a simple web application where users can:
- add people to a group
- add expenses with a payer and amount
- choose how the total should be split
- see the final balances for each person

The app should be easy to understand and run locally.

## Tech Stack
- Backend: Python with uv
- Frontend: Node.js
- Data storage: SQLite (local file database)
- Web framework: FastAPI (Python) for the API
- Frontend framework: simple HTML + JavaScript or a lightweight frontend stack such as Vite + vanilla JS

## Functional Requirements

### 1. Group Setup
- The user can create a group with a name.
- The app can store multiple people in that group.
- Each person should have a display name.

### 2. Add Expenses
- The user can add an expense entry with:
  - description
  - amount
  - payer (one of the group members)
  - date
- The app should allow the expense to be split among group members.

### 3. Split Options
Support at least two simple split methods:
- Equal split: total cost divided equally among group members
- Custom split: each person can be assigned a specific share

### 4. Balance Calculation
- The app calculates each person's balance.
- If a person paid more than their share, they are owed money.
- If a person paid less than their share, they owe money.
- The system should show balances in a clear summary.

### 5. Expense List
- The app displays all recorded expenses.
- Each expense shows:
  - description
  - amount
  - payer
  - date
  - participants

### 6. Dashboard
The main page should show:
- group members
- total expenses
- each person's net balance
- a simple list of recent expenses

## Non-Functional Requirements
- The application should be easy to run with a local setup.
- The backend should expose a simple API for expenses and members.
- The frontend should be simple and responsive.
- Application logic should be small and readable.

## Suggested Project Structure

```text
Homework2/
  _docs/
    spec.md
  backend/
    app/
    pyproject.toml
    uv.lock
  frontend/
    package.json
    src/
    public/
```

## Minimal API Design

### Endpoints
- GET /health
- GET /groups
- POST /groups
- GET /groups/{id}/members
- POST /groups/{id}/members
- GET /groups/{id}/expenses
- POST /groups/{id}/expenses
- GET /groups/{id}/balances

### Example Expense Payload
```json
{
  "description": "Groceries",
  "amount": 120.00,
  "payer_id": 1,
  "split_type": "equal",
  "participant_ids": [1, 2, 3]
}
```

## Basic Acceptance Criteria
The project is successful if:
1. A user can add members to a group.
2. A user can add an expense and assign the payer.
3. The app calculates balances correctly for equal split.
4. The system displays a list of expenses.
5. The frontend and backend run locally without major setup issues.

## Scope Limitations
This is intentionally a basic version. It does not need:
- authentication
- multiple groups per user
- advanced settlement optimization
- recurring expenses
- payment tracking integration
- real-time collaboration

## Notes for Implementation
Keep the first version simple:
- one group at a time
- one user interface page
- direct form submissions
- straightforward balance logic

This should be enough to demonstrate a useful MVP for an expense splitter.
