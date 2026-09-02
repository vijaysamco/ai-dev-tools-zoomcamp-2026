# Household Chore Manager Backlog

## Goal
Build a focused Django MVP for a shared household chore board, based on the plan in `_docs/plan.md`.

## Backlog

### 1. Project setup and Django scaffolding
- Create the Django project and app structure
- Add the `chores` app to `INSTALLED_APPS`
- Confirm the project runs locally via `manage.py runserver`
- Set up the initial SQLite database and migrations

### 2. User authentication and household membership
- Configure Django auth for separate member logins
- Create a user profile or household membership model
- Allow a user to create one household
- Allow household members to join a household
- Add basic login/logout pages
- Add simple sign-up flow

### 3. Chore data model
- Create `Household` model
- Create `Chore` model with fields:
  - title
  - description
  - assignee
  - due date
  - status
  - created_by
  - created_at
  - updated_at
- Add a status enum or choices for pending, in progress, and completed
- Add model validation for required fields

### 4. Chore CRUD and dashboard
- Create a dashboard page showing household chores
- Add a form to create a new chore
- Add edit and delete functionality for chores
- Allow assignment to household members
- Show chores grouped by status or assignee
- Add due-date display on the dashboard

### 5. Status tracking and activity log
- Add update actions for chore status changes
- Record chore activity such as:
  - created
  - assigned
  - marked complete
  - updated
- Show a recent activity list on the dashboard
- Ensure the activity shows which member performed the action

### 6. Filtering and usability
- Add filters by assignee and status
- Add search or simple query parameters for chores
- Improve layout for quick daily review of the household board
- Add basic styling for readability and usability

### 7. Testing and verification
- Add model tests for household and chore behavior
- Add tests for authentication and access control
- Add tests for the chore dashboard and status updates
- Run Django test suite and fix issues

### 8. Polish and deployment prep
- Add environment configuration for local development
- Review security settings for Django defaults
- Prepare project notes for deployment
- Confirm the app matches the MVP plan and avoids out-of-scope features

## Priority order
1. Project setup and auth
2. Household and chore models
3. CRUD for chores
4. Status tracking and activity log
5. Dashboard filters and UX polish
6. Tests and deployment prep

## Definition of done for MVP
- A user can sign up and log in
- A user can create or join a household
- Household members can create and assign chores
- Chores can be updated to completed status
- The shared household dashboard shows all current chores
- Activity is visible for key actions
- Basic tests pass for the main flows
