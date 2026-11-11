/**
 * Personal Expense Tracking and Analysis System
 * Frontend Client Logic (Vanilla JavaScript)
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Auto-dismiss alerts after 4 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 4000);
    });

    // 2. Add Expense Modal Elements
    const addModal = document.getElementById('addExpenseModal');
    const openAddBtn = document.getElementById('openAddExpenseModal');
    const closeAddBtn = document.getElementById('closeAddExpenseModal');
    const cancelAddBtn = document.getElementById('cancelAddExpenseModal');

    if (openAddBtn && addModal) {
        openAddBtn.addEventListener('click', () => {
            addModal.classList.add('active');
            // Default date to today if empty
            const dateInput = addModal.querySelector('input[name="expense_date"]');
            if (dateInput && !dateInput.value) {
                dateInput.value = new Date().toISOString().split('T')[0];
            }
        });
    }

    if (closeAddBtn && addModal) {
        closeAddBtn.addEventListener('click', () => addModal.classList.remove('active'));
    }
    if (cancelAddBtn && addModal) {
        cancelAddBtn.addEventListener('click', () => addModal.classList.remove('active'));
    }

    // 3. Edit Expense Modal Elements
    const editModal = document.getElementById('editExpenseModal');
    const closeEditBtn = document.getElementById('closeEditExpenseModal');
    const cancelEditBtn = document.getElementById('cancelEditExpenseModal');
    const editForm = document.getElementById('editExpenseForm');

    if (closeEditBtn && editModal) {
        closeEditBtn.addEventListener('click', () => editModal.classList.remove('active'));
    }
    if (cancelEditBtn && editModal) {
        cancelEditBtn.addEventListener('click', () => editModal.classList.remove('active'));
    }

    // Attach click handlers to all Edit buttons
    const editButtons = document.querySelectorAll('.btn-edit-expense');
    editButtons.forEach(btn => {
        btn.addEventListener('click', async (e) => {
            e.preventDefault();
            const expenseId = btn.getAttribute('data-id');
            if (!expenseId || !editModal || !editForm) return;

            try {
                // Fetch expense details from API
                const response = await fetch(`/api/expenses/${expenseId}`);
                const data = await response.json();

                if (data.success && data.expense) {
                    const exp = data.expense;
                    editForm.action = `/expenses/edit/${exp.expense_id}`;
                    
                    const dateInput = editForm.querySelector('input[name="expense_date"]');
                    const catSelect = editForm.querySelector('select[name="category_id"]');
                    const amtInput = editForm.querySelector('input[name="amount"]');
                    const descInput = editForm.querySelector('input[name="description"]');
                    const paySelect = editForm.querySelector('select[name="payment_method"]');

                    if (dateInput) dateInput.value = exp.expense_date;
                    if (catSelect) catSelect.value = exp.category_id;
                    if (amtInput) amtInput.value = parseFloat(exp.amount).toFixed(2);
                    if (descInput) descInput.value = exp.description;
                    if (paySelect) paySelect.value = exp.payment_method;

                    editModal.classList.add('active');
                } else {
                    alert('Could not load expense data: ' + (data.message || 'Unknown error'));
                }
            } catch (err) {
                console.error('Failed to fetch expense details:', err);
                alert('An error occurred while loading the expense record.');
            }
        });
    });

    // 4. Delete Confirmation Handler
    const deleteForms = document.querySelectorAll('.delete-expense-form');
    deleteForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const confirmed = confirm('Are you sure you want to delete this expense record? This action cannot be undone.');
            if (!confirmed) {
                e.preventDefault();
            }
        });
    });

    // 5. Positive Amount Form Validation (Acceptance Criteria: Amount > 0)
    const expenseForms = document.querySelectorAll('.validate-expense-form');
    expenseForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const amountInput = form.querySelector('input[name="amount"]');
            if (amountInput) {
                const amountVal = parseFloat(amountInput.value);
                if (isNaN(amountVal) || amountVal <= 0) {
                    e.preventDefault();
                    alert('Error: Expense amount must be a positive number strictly greater than 0.');
                    amountInput.focus();
                    return false;
                }
            }
            const dateInput = form.querySelector('input[name="expense_date"]');
            if (dateInput && !dateInput.value) {
                e.preventDefault();
                alert('Error: Please select a valid expense date.');
                dateInput.focus();
                return false;
            }
            const descInput = form.querySelector('input[name="description"]');
            if (descInput && !descInput.value.trim()) {
                e.preventDefault();
                alert('Error: Expense description cannot be empty.');
                descInput.focus();
                return false;
            }
        });
    });

    // 6. Close modal when clicking outside modal window
    window.addEventListener('click', (e) => {
        if (addModal && e.target === addModal) {
            addModal.classList.remove('active');
        }
        if (editModal && e.target === editModal) {
            editModal.classList.remove('active');
        }
    });

    // 7. Print Report Helper
    const printBtn = document.getElementById('btnPrintReport');
    if (printBtn) {
        printBtn.addEventListener('click', () => {
            window.print();
        });
    }
});


// Persistent light/dark theme toggle (shared by public pages and dashboard).
(function () {
    const key = 'spendwise-theme';
    const root = document.documentElement;
    const saved = localStorage.getItem(key);
    if (saved === 'dark' || saved === 'light') root.dataset.theme = saved;
    function paintButtons() {
        const dark = root.dataset.theme === 'dark';
        document.querySelectorAll('[data-theme-toggle]').forEach((button) => {
            button.textContent = dark ? '☀️ Light mode' : '🌙 Dark mode';
            button.setAttribute('aria-label', dark ? 'Switch to light mode' : 'Switch to dark mode');
            button.setAttribute('aria-pressed', String(dark));
        });
    }
    document.addEventListener('DOMContentLoaded', paintButtons);
    document.addEventListener('click', (event) => {
        const button = event.target.closest('[data-theme-toggle]');
        if (!button) return;
        root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem(key, root.dataset.theme);
        paintButtons();
    });
})();
