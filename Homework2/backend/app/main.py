from __future__ import annotations

from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title='SplitEase API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://127.0.0.1:4173', 'http://localhost:4173', 'http://127.0.0.1:5173', 'http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class Group(BaseModel):
    id: str
    name: str


class Member(BaseModel):
    id: str
    group_id: str
    name: str


class Expense(BaseModel):
    id: str
    group_id: str
    description: str
    amount: float
    payer_id: str
    split_type: str
    participant_ids: List[str]
    custom_shares: Dict[str, float] | None = None
    date: str


class Balance(BaseModel):
    member_id: str
    name: str
    balance: float


class CreateGroupRequest(BaseModel):
    name: str = Field(min_length=1)


class CreateMemberRequest(BaseModel):
    name: str = Field(min_length=1)


class CreateExpenseRequest(BaseModel):
    description: str = Field(min_length=1)
    amount: float = Field(gt=0)
    payer_id: str = Field(min_length=1)
    split_type: str
    participant_ids: List[str] = Field(min_length=1)
    custom_shares: Dict[str, float] | None = None
    date: str


mock_groups: Dict[str, Group] = {}
mock_members: Dict[str, List[Member]] = {}
mock_expenses: Dict[str, List[Expense]] = {}


def ensure_group(group_id: str):
    if group_id not in mock_groups:
        raise HTTPException(status_code=404, detail='Group not found')


def get_group_members(group_id: str):
    return mock_members.setdefault(group_id, [])


def get_group_expenses(group_id: str):
    return mock_expenses.setdefault(group_id, [])


@app.get('/health')
def health_check():
    return {'status': 'ok'}


@app.get('/groups', response_model=List[Group])
def list_groups():
    return list(mock_groups.values())


@app.post('/groups', response_model=Group, status_code=201)
def create_group(payload: CreateGroupRequest):
    group_id = f'group-{len(mock_groups) + 1}'
    group = Group(id=group_id, name=payload.name)
    mock_groups[group_id] = group
    mock_members[group_id] = []
    mock_expenses[group_id] = []
    return group


@app.get('/groups/{group_id}/members', response_model=List[Member])
def list_members(group_id: str):
    ensure_group(group_id)
    return get_group_members(group_id)


@app.post('/groups/{group_id}/members', response_model=Member, status_code=201)
def add_member(group_id: str, payload: CreateMemberRequest):
    ensure_group(group_id)
    member_id = f'member-{len(get_group_members(group_id)) + 1}'
    member = Member(id=member_id, group_id=group_id, name=payload.name)
    get_group_members(group_id).append(member)
    return member


@app.get('/groups/{group_id}/expenses', response_model=List[Expense])
def list_expenses(group_id: str):
    ensure_group(group_id)
    return get_group_expenses(group_id)


@app.post('/groups/{group_id}/expenses', response_model=Expense, status_code=201)
def add_expense(group_id: str, payload: CreateExpenseRequest):
    ensure_group(group_id)

    if payload.payer_id not in {member.id for member in get_group_members(group_id)}:
        raise HTTPException(status_code=400, detail='Payer must be a group member')

    participant_ids = list(payload.participant_ids)
    valid_ids = {member.id for member in get_group_members(group_id)}
    if not set(participant_ids).issubset(valid_ids):
        raise HTTPException(status_code=400, detail='Expense participants must be group members')

    if payload.split_type == 'custom':
        custom_shares = payload.custom_shares or {}
        if not custom_shares:
            raise HTTPException(status_code=400, detail='Custom split requires custom_shares')
        total = sum(float(value) for value in custom_shares.values())
        if abs(total - float(payload.amount)) > 0.01:
            raise HTTPException(status_code=400, detail='Custom shares must add up to the total amount')
    elif payload.split_type == 'equal':
        custom_shares = {}
    else:
        raise HTTPException(status_code=400, detail='split_type must be equal or custom')

    expense_id = f'expense-{len(get_group_expenses(group_id)) + 1}'
    expense = Expense(
        id=expense_id,
        group_id=group_id,
        description=payload.description,
        amount=float(payload.amount),
        payer_id=payload.payer_id,
        split_type=payload.split_type,
        participant_ids=participant_ids,
        custom_shares=custom_shares,
        date=payload.date,
    )
    get_group_expenses(group_id).append(expense)
    return expense


@app.get('/groups/{group_id}/balances', response_model=List[Balance])
def get_balances(group_id: str):
    ensure_group(group_id)
    members = get_group_members(group_id)
    expenses = get_group_expenses(group_id)

    if not members:
        return []

    total_paid = {member.id: 0.0 for member in members}
    total_owed = {member.id: 0.0 for member in members}

    for expense in expenses:
        for participant_id in expense.participant_ids:
            if expense.split_type == 'equal':
                share = float(expense.amount) / len(expense.participant_ids)
                total_owed[participant_id] += share
            else:
                share = float((expense.custom_shares or {}).get(participant_id, 0.0))
                total_owed[participant_id] += share

        total_paid[expense.payer_id] += float(expense.amount)

    balances = []
    for member in members:
        balance = total_paid.get(member.id, 0.0) - total_owed.get(member.id, 0.0)
        balances.append(
            Balance(
                member_id=member.id,
                name=member.name,
                balance=round(balance, 2),
            )
        )

    return balances
