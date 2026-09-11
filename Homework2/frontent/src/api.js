const API_BASE_URL = 'http://127.0.0.1:8000';

const mockGroup = {
  id: 'group-1',
  name: 'Weekend Trip',
  members: [
    { id: 'm1', name: 'Alice' },
    { id: 'm2', name: 'Bob' },
    { id: 'm3', name: 'Charlie' }
  ],
  expenses: [
    {
      id: 'e1',
      description: 'Groceries',
      amount: 120,
      date: '2026-09-05',
      payerId: 'm1',
      splitType: 'equal',
      participantIds: ['m1', 'm2', 'm3'],
      customShares: {},
      createdAt: '2026-09-05T09:15:00.000Z'
    },
    {
      id: 'e2',
      description: 'Train tickets',
      amount: 90,
      date: '2026-09-07',
      payerId: 'm2',
      splitType: 'equal',
      participantIds: ['m1', 'm2', 'm3'],
      customShares: {},
      createdAt: '2026-09-07T12:00:00.000Z'
    }
  ],
  balances: []
};

const normalizeExpense = (expense) => ({
  id: expense.id,
  description: expense.description,
  amount: Number(expense.amount || 0),
  date: expense.date,
  payerId: expense.payer_id || expense.payerId,
  splitType: expense.split_type || expense.splitType || 'equal',
  participantIds: expense.participant_ids || expense.participantIds || [],
  customShares: expense.custom_shares || expense.customShares || {},
  createdAt: expense.createdAt || expense.date
});

const normalizeMember = (member) => ({
  id: member.id,
  name: member.name,
  groupId: member.group_id || member.groupId
});

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  });

  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;

  if (!response.ok) {
    const detail = payload?.detail || payload?.message || 'Request failed';
    throw new Error(detail);
  }

  return payload;
}

async function withFallback(fetcher, fallbackData) {
  try {
    return await fetcher();
  } catch (error) {
    console.warn('Backend unavailable; falling back to mock data.', error);
    return fallbackData;
  }
}

export const api = {
  async getGroups() {
    return withFallback(async () => request('/groups'), [{ id: mockGroup.id, name: mockGroup.name }]);
  },

  async getGroupById(groupId) {
    return withFallback(async () => {
      const [groupList, members, expenses, balances] = await Promise.all([
        request('/groups'),
        request(`/groups/${groupId}/members`),
        request(`/groups/${groupId}/expenses`),
        request(`/groups/${groupId}/balances`)
      ]);

      const group = groupList.find((item) => item.id === groupId) || { id: groupId, name: 'Group' };

      return {
        ...group,
        members: (members || []).map(normalizeMember),
        expenses: (expenses || []).map(normalizeExpense),
        balances: balances || []
      };
    }, { ...mockGroup, id: groupId, members: mockGroup.members, expenses: mockGroup.expenses, balances: [] });
  },

  async createGroup(name) {
    return withFallback(async () => {
      const newGroup = await request('/groups', {
        method: 'POST',
        body: JSON.stringify({ name: name.trim() || 'New group' })
      });
      return { ...newGroup, members: [], expenses: [], balances: [] };
    }, { ...mockGroup, id: `group-${Date.now()}`, name: name.trim() || 'New group', members: [], expenses: [], balances: [] });
  },

  async addMember(groupId, name) {
    const trimmed = name.trim();
    if (!trimmed) {
      throw new Error('Member name is required.');
    }

    return withFallback(async () => {
      const member = await request(`/groups/${groupId}/members`, {
        method: 'POST',
        body: JSON.stringify({ name: trimmed })
      });
      return normalizeMember(member);
    }, { id: `m-${Date.now()}`, name: trimmed, groupId });
  },

  async addExpense(groupId, expensePayload) {
    const normalizedPayload = {
      description: expensePayload.description,
      amount: Number(expensePayload.amount),
      payer_id: expensePayload.payerId,
      split_type: expensePayload.splitType,
      participant_ids: expensePayload.participantIds || [],
      custom_shares: expensePayload.customShares || {},
      date: expensePayload.date
    };

    return withFallback(async () => {
      const expense = await request(`/groups/${groupId}/expenses`, {
        method: 'POST',
        body: JSON.stringify(normalizedPayload)
      });
      return normalizeExpense(expense);
    }, {
      id: `e-${Date.now()}`,
      description: normalizedPayload.description,
      amount: normalizedPayload.amount,
      payerId: normalizedPayload.payer_id,
      splitType: normalizedPayload.split_type,
      participantIds: normalizedPayload.participant_ids,
      customShares: normalizedPayload.custom_shares,
      date: normalizedPayload.date
    });
  }
};

export function getGroupSnapshot(group = mockGroup) {
  const members = group.members ?? [];
  const expenses = group.expenses ?? [];

  const paidByMember = Object.fromEntries(members.map((member) => [member.id, 0]));
  const owedByMember = Object.fromEntries(members.map((member) => [member.id, 0]));

  for (const expense of expenses) {
    const participants = expense.participantIds ?? members.map((member) => member.id);
    const total = Number(expense.amount || 0);

    if (expense.splitType === 'equal') {
      const share = total / participants.length;
      for (const participantId of participants) {
        owedByMember[participantId] += share;
      }
    } else {
      const customShares = expense.customShares ?? {};
      for (const participantId of participants) {
        owedByMember[participantId] += Number(customShares[participantId] || 0);
      }
    }

    paidByMember[expense.payerId] += total;
  }

  const balances = members.map((member) => {
    const balance = paidByMember[member.id] - owedByMember[member.id];
    return {
      id: member.id,
      name: member.name,
      balance: Number(balance.toFixed(2))
    };
  });

  const totalExpenses = expenses.reduce((acc, expense) => acc + Number(expense.amount || 0), 0);

  return {
    members,
    expenses,
    balances,
    totalExpenses: Number(totalExpenses.toFixed(2))
  };
}
