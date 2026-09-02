# Household Chore Manager Plan

## Product goal
Build a small web app for a household to manage shared chores with clear assignment, status tracking, and a shared household view.

## Target users
- household members with separate accounts
- one household per account
- same home, same chore board

## v1 scope
### Core features
- sign up and sign in
- create one household per account
- add household members
- create chores with:
  - title
  - description
  - assignee
  - due date
  - status
- update chore status: pending, in progress, completed
- mark chores complete
- filter chores by assignee and status
- view all chores in a shared dashboard
- simple activity log for who completed what and when

### UX goals
- simple, fast collaboration
- clear ownership of each task
- easy daily check of what is due or overdue

## Out of scope for v1
- recurring chore schedules
- reminders and notifications
- multi-household support
- points or fairness scoring
- advanced permissions or roles
- mobile app
- budgeting, inventory, or other household features

## MVP user stories
- As a member, I can sign in and see my household chores.
- As a member, I can create a chore for the household.
- As a member, I can assign a chore to another person.
- As a member, I can mark a chore as completed.
- As a member, I can filter chores by person or status.
- As a member, I can see recent activity in the household.

## Suggested architecture
- Frontend: web app UI for dashboard and chore management
- Backend: REST API or server-rendered app
- Database: users, households, members, chores, activity log
- Auth: email/password login with per-user sessions

## Suggested milestones
1. Project setup and database schema
2. User auth and household membership
3. Chore CRUD and assignment
4. Status tracking and activity log
5. Filtering and dashboard polish
6. Basic testing and deployment

## Risks and constraints
- keep the first version small and focused
- avoid overbuilding scheduling or automation before the core workflow works
- prioritize clarity of ownership over feature richness
