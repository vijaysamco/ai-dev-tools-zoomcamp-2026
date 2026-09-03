# Household Chore Manager

A small web app for managing shared household chores.

## Overview
This project helps a household coordinate day-to-day chores with a shared task board. Each household member has their own login, and all members in the same home can see the same chores, assign work, and track completion.

## Core idea
- everyone in the household shares one chore board
- each chore has an owner and a status
- tasks are visible, easy to update, and easy to complete
- the household can quickly understand what is left to do

## Planned v1 features
- member sign up and login
- one household per account
- add, edit, and delete chores
- assign chores to household members
- track status: pending, in progress, completed
- filter chores by assignee or status
- due dates
- simple household activity log

## Not planned for v1
- recurring chore automation
- reminders and push notifications
- multiple households per user
- fairness points or scoreboards
- mobile app

## Local development setup
1. Create a local virtual environment.
2. Install dependencies from `requirements.txt`.
3. Copy `.env.example` to `.env` and update the values for your local environment.
4. Run database migrations.
5. Start the app with `python manage.py runserver`.

Example:

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
```

## Deployment notes
- Keep `DEBUG=False` in production.
- Use a strong secret key via `DJANGO_SECRET_KEY`.
- Configure `DJANGO_ALLOWED_HOSTS` for the production host.
- Use a production database and secure credentials instead of the default local SQLite setup.

## Project status
This repository is currently in the MVP phase for a shared household chore app. The project is scoped to the essentials: household membership, chore assignment, status tracking, dashboard filtering, testing, and deployment-ready configuration.

## Next steps
1. Finalize deployment configuration
2. Add a production database setup
3. Review security settings before deployment
4. Expand only after the MVP is stable
