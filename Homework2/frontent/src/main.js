import { api, getGroupSnapshot } from './api.js';

const state = {
  group: null,
  selectedGroupId: null
};

const elements = {
  groupName: document.querySelector('#group-name'),
  groupNameInput: document.querySelector('#group-name-input'),
  createGroupBtn: document.querySelector('#create-group-btn'),
  memberNameInput: document.querySelector('#member-name-input'),
  addMemberBtn: document.querySelector('#add-member-btn'),
  expenseForm: document.querySelector('#expense-form'),
  expenseDescription: document.querySelector('#expense-description'),
  expenseAmount: document.querySelector('#expense-amount'),
  expenseDate: document.querySelector('#expense-date'),
  expensePayer: document.querySelector('#expense-payer'),
  expenseSplitType: document.querySelector('#expense-split-type'),
  participantSelection: document.querySelector('#participant-selection'),
  customSplitSection: document.querySelector('#custom-split-section'),
  customSplitInputs: document.querySelector('#custom-split-inputs'),
  balancesList: document.querySelector('#balances-list'),
  expenseList: document.querySelector('#expense-list'),
  totalExpense: document.querySelector('#total-expense'),
  memberTotal: document.querySelector('#member-total'),
  memberCountPill: document.querySelector('#member-count-pill'),
  settledStatus: document.querySelector('#settled-status')
};

function formatCurrency(value) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD'
  }).format(value || 0);
}

function formatDate(dateStr) {
  if (!dateStr) return 'No date';
  const date = new Date(dateStr);
  return Number.isNaN(date.getTime()) ? dateStr : date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  });
}

function getActiveMembers() {
  return state.group?.members ?? [];
}

function refreshFormControls() {
  const members = getActiveMembers();
  elements.expensePayer.innerHTML = members
    .map((member) => `<option value="${member.id}">${member.name}</option>`)
    .join('');

  elements.participantSelection.innerHTML = members
    .map(
      (member) => `
        <label class="check-row">
          <input type="checkbox" name="participant" value="${member.id}" checked />
          <span>${member.name}</span>
        </label>
      `
    )
    .join('');

  elements.customSplitInputs.innerHTML = members
    .map(
      (member) => `
        <label>
          <span>${member.name}</span>
          <input type="number" min="0" step="0.01" data-custom-share="${member.id}" value="0" />
        </label>
      `
    )
    .join('');
};

function renderBalances() {
  const { balances, totalExpenses, members } = getGroupSnapshot(state.group);

  elements.totalExpense.textContent = formatCurrency(totalExpenses);
  elements.memberTotal.textContent = String(members.length);
  elements.memberCountPill.textContent = `${members.length} members`;

  const hasUnsettled = balances.some((entry) => Math.abs(entry.balance) > 0.01);
  elements.settledStatus.textContent = hasUnsettled ? 'Open balances' : 'Balanced';

  if (!balances.length) {
    elements.balancesList.innerHTML = '<p class="empty-state">No balances yet. Add members to get started.</p>';
    return;
  }

  const sortedBalances = [...balances].sort((a, b) => b.balance - a.balance);
  elements.balancesList.innerHTML = sortedBalances
    .map((entry) => {
      const positive = entry.balance > 0;
      const valueText = `${positive ? 'Gets back' : 'Owes'} ${formatCurrency(Math.abs(entry.balance))}`;
      return `
        <div class="balance-row ${positive ? 'positive' : 'negative'}">
          <div>
            <strong>${entry.name}</strong>
          </div>
          <span>${valueText}</span>
        </div>
      `;
    })
    .join('');
}

function renderExpenses() {
  const expenses = state.group?.expenses ?? [];

  if (!expenses.length) {
    elements.expenseList.innerHTML = '<li class="empty-state">No expenses added yet.</li>';
    return;
  }

  elements.expenseList.innerHTML = expenses
    .map((expense) => {
      const payer = state.group.members.find((member) => member.id === expense.payerId)?.name ?? 'Unknown';
      const participants = (expense.participantIds ?? [])
        .map((id) => state.group.members.find((member) => member.id === id)?.name)
        .filter(Boolean)
        .join(', ');

      return `
        <li class="expense-item">
          <div class="expense-meta">
            <div>
              <h4>${expense.description}</h4>
              <p>${payer} paid • ${participants || 'No participants'}</p>
            </div>
            <strong>${formatCurrency(expense.amount)}</strong>
          </div>
          <div class="expense-footer">
            <span>${formatDate(expense.date)}</span>
            <span>${expense.splitType === 'equal' ? 'Equal split' : 'Custom split'}</span>
          </div>
        </li>
      `;
    })
    .join('');
}

function renderGroup() {
  const group = state.group;
  if (!group) return;

  elements.groupName.textContent = group.name;
  elements.groupNameInput.value = group.name;
  refreshFormControls();
  renderBalances();
  renderExpenses();
}

async function loadGroup() {
  const groups = await api.getGroups();

  if (!groups || groups.length === 0) {
    const createdGroup = await api.createGroup('Weekend Trip');
    state.group = await api.getGroupById(createdGroup.id);
    state.selectedGroupId = createdGroup.id;
    renderGroup();
    return;
  }

  const firstGroup = groups[0];
  state.group = await api.getGroupById(firstGroup.id);
  state.selectedGroupId = firstGroup.id;
  renderGroup();
}

async function handleCreateGroup(event) {
  event.preventDefault();
  const name = elements.groupNameInput.value.trim();
  if (!name) {
    window.alert('Please enter a group name.');
    return;
  }

  const createdGroup = await api.createGroup(name);
  state.group = await api.getGroupById(createdGroup.id);
  state.selectedGroupId = createdGroup.id;
  renderGroup();
}

async function handleAddMember() {
  const name = elements.memberNameInput.value.trim();
  if (!name) {
    window.alert('Please provide a member name.');
    return;
  }

  await api.addMember(state.selectedGroupId, name);
  state.group = await api.getGroupById(state.selectedGroupId);
  elements.memberNameInput.value = '';
  renderGroup();
}

function toggleCustomSplitVisibility() {
  const isCustom = elements.expenseSplitType.value === 'custom';
  elements.customSplitSection.classList.toggle('hidden', !isCustom);
}

function getSelectedParticipants() {
  return [...document.querySelectorAll('input[name="participant"]:checked')].map((input) => input.value);
}

function getCustomShareValues() {
  const customShares = {};
  const inputs = document.querySelectorAll('[data-custom-share]');
  inputs.forEach((input) => {
    const memberId = input.dataset.customShare;
    const value = Number(input.value || 0);
    if (value > 0) {
      customShares[memberId] = value;
    }
  });
  return customShares;
}

async function handleExpenseSubmit(event) {
  event.preventDefault();

  if (!state.group || !state.group.members.length) {
    window.alert('Add at least one member before creating an expense.');
    return;
  }

  const description = elements.expenseDescription.value.trim();
  const amount = Number(elements.expenseAmount.value);
  const date = elements.expenseDate.value;
  const payerId = elements.expensePayer.value;
  const splitType = elements.expenseSplitType.value;
  const participantIds = getSelectedParticipants();

  if (!description || !amount || !date || !payerId || !participantIds.length) {
    window.alert('Please fill in all required expense fields.');
    return;
  }

  await api.addExpense(state.selectedGroupId, {
    description,
    amount,
    date,
    payerId,
    splitType,
    participantIds,
    customShares: splitType === 'custom' ? getCustomShareValues() : {}
  });

  state.group = await api.getGroupById(state.selectedGroupId);
  elements.expenseForm.reset();
  elements.expenseDate.value = new Date().toISOString().split('T')[0];
  renderGroup();
  toggleCustomSplitVisibility();
}

function bindEvents() {
  elements.createGroupBtn.addEventListener('click', handleCreateGroup);
  elements.addMemberBtn.addEventListener('click', handleAddMember);
  elements.expenseSplitType.addEventListener('change', toggleCustomSplitVisibility);
  elements.expenseForm.addEventListener('submit', handleExpenseSubmit);
  elements.expenseDate.value = new Date().toISOString().split('T')[0];
}

async function init() {
  bindEvents();
  await loadGroup();
  toggleCustomSplitVisibility();
}

init();
