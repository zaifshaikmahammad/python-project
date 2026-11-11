"""
Personal Expense Tracking and Analysis System
Flask Web Application Main Entry Point
"""

import os
import secrets
import hashlib
from email_service import send_otp_email
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
import database
import analytics

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
    static_url_path='/static'
)
app.config.from_object(Config)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(days=7)
)

# Explicit static file handler ensuring correct CSS/JS MIME types and HTTP 200 on serverless
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static CSS, JS, and asset files with strict MIME type enforcement."""
    mimetype = None
    if filename.endswith('.css'):
        mimetype = 'text/css'
    elif filename.endswith('.js'):
        mimetype = 'application/javascript'
        
    return send_from_directory(
        app.static_folder,
        filename,
        mimetype=mimetype
    )


# Database tables are initialized by `python init_db.py` in the Render start command.

@app.context_processor
def inject_global_data():
    """Inject common metadata and categories into all templates."""
    try:
        categories_list = database.get_categories(session['user_id']) if session.get('user_id') else []
    except Exception:
        categories_list = []
    return {
        'current_year': datetime.now().year,
        'today_date': datetime.now().strftime('%Y-%m-%d'),
        'db_status': database.get_database_status(),
        'categories': categories_list,
        'user_name': session.get('user_name'),
        'is_demo': session.get('demo_mode', False),
        'time_greeting': ('Good morning' if datetime.now().hour < 12 else
                          'Good afternoon' if datetime.now().hour < 17 else 'Good evening')
    }




# --------------------------------------------------------------------
# Public pages, registration, and email OTP authentication
# --------------------------------------------------------------------
def auth_connection():
    """Use hosted MySQL for accounts so auth data survives serverless invocations."""
    return database.get_db_connection()








# Database tables are prepared by `python init_db.py` during deployment.
# Avoid connecting to the database at import time so Gunicorn can boot and
# report application errors cleanly if the database is temporarily offline.

@app.route('/health')
def health_check():
    """Render health check: verify the app and its configured MySQL database."""
    try:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({'status': 'ok', 'database': 'connected'}), 200
    except Exception:
        app.logger.exception('Health check could not connect to MySQL')
        return jsonify({'status': 'error', 'database': 'unavailable'}), 503


@app.route('/')
@app.route('/home')
def landing():
    if session.get('user_id'):
        return redirect(url_for('index'))
    return render_template('landing.html')

@app.route('/about')
def about():
    return render_template('public.html', page='About',
        subtitle='A clearer view of your everyday money.',
        body='Personal Expense Tracker and Analysis System brings daily spending into one organized place. Record purchases, sort them into categories, and review your history to understand where your money goes. Use monthly summaries and visual trends to support thoughtful budgeting and more confident day-to-day decisions. Your personal account keeps your records separate, while the demo uses sample data only.')

@app.route('/features')
def features():
    return render_template('public.html', page='Features',
        subtitle='Everything you need to understand your spending.',
        body='Record purchases with dates, amounts, descriptions, categories, and payment methods. Search and filter your expense ledger, edit records, and keep categories organized. Interactive charts show category shares and monthly trends; analytics summarize averages and payment methods. Monthly reports bring totals, category breakdowns, and transactions together in a print-friendly view. Try these screens with sample data in the read-only demo.')

@app.route('/demo')
def demo():
    """Start a read-only session using local sample data; no account or database writes."""
    if session.get('user_id'):
        return redirect(url_for('index'))
    session.clear()
    session['demo_mode'] = True
    session['user_name'] = 'Guest'
    return redirect(url_for('index'))

@app.route('/exit-demo')
def exit_demo():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/contact')
def contact():
    return render_template('public.html', page='Contact', subtitle='', body='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not name or len(name) > 120 or '@' not in email or len(password) < 8:
            flash('Enter your name, a valid email address, and a password with at least 8 characters.', 'error')
            return render_template('auth.html', mode='register')
        password_hash = generate_password_hash(password)
        otp = f"{secrets.randbelow(1000000):06d}"
        otp_hash = hashlib.sha256(otp.encode()).hexdigest()
        expires_at = (datetime.utcnow() + timedelta(minutes=10)).isoformat()
        conn = auth_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT id, verified FROM users WHERE email=%s', (email,))
            existing = cursor.fetchone()
            if existing and existing['verified']:
                flash('An account already exists for this email. Please log in.', 'error')
                return redirect(url_for('login'))
            cursor.execute("""INSERT INTO pending_otps(email,name,password_hash,otp_hash,expires_at,attempts)
                VALUES(%s,%s,%s,%s,%s,0)
                ON DUPLICATE KEY UPDATE name=VALUES(name), password_hash=VALUES(password_hash),
                otp_hash=VALUES(otp_hash), expires_at=VALUES(expires_at), attempts=0""",
                (email, name, password_hash, otp_hash, expires_at))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        try:
            send_otp_email(email, otp)
        except Exception as e:
            app.logger.exception("OTP email delivery failed: %s", str(e))
            flash(f"Email error: {str(e)}", "danger")
            return render_template('auth.html', mode='register')
        session['pending_email'] = email
        flash('A six-digit verification code has been sent to your email. It expires in 10 minutes.', 'success')
        return redirect(url_for('verify_email'))
    return render_template('auth.html', mode='register')

@app.route('/verify', methods=['GET', 'POST'])
def verify_email():
    email = session.get('pending_email')
    if not email:
        flash('Please register first to request a verification code.', 'error')
        return redirect(url_for('register'))
    if request.method == 'POST':
        otp = request.form.get('otp', '').strip()
        conn = auth_connection()
        cursor = conn.cursor(dictionary=True)
        verified_user = None
        try:
            cursor.execute('SELECT * FROM pending_otps WHERE email=%s', (email,))
            row = cursor.fetchone()
            if row and row['attempts'] < 5 and datetime.utcnow() < datetime.fromisoformat(row['expires_at']):
                candidate = hashlib.sha256(otp.encode()).hexdigest()
                if secrets.compare_digest(candidate, row['otp_hash']):
                    cursor.execute("""INSERT INTO users(name,email,password_hash,verified,created_at)
                        VALUES(%s,%s,%s,1,%s) ON DUPLICATE KEY UPDATE
                        name=VALUES(name),password_hash=VALUES(password_hash),verified=1""",
                        (row['name'], email, row['password_hash'], datetime.utcnow().isoformat()))
                    cursor.execute('DELETE FROM pending_otps WHERE email=%s', (email,))
                    cursor.execute('SELECT id,name FROM users WHERE email=%s', (email,))
                    verified_user = cursor.fetchone()
                    conn.commit()
                else:
                    cursor.execute('UPDATE pending_otps SET attempts=attempts+1 WHERE email=%s', (email,))
                    conn.commit()
        finally:
            cursor.close()
            conn.close()
        if verified_user:
            database.create_user_categories(verified_user['id'])
            session.clear()
            session['user_id'] = verified_user['id']
            session['user_name'] = verified_user['name']
            session.permanent = True
            flash('Your email is verified. Welcome!', 'success')
            return redirect(url_for('index'))
        flash('The code is incorrect, expired, or has reached the attempt limit. Please register again.', 'error')
    return render_template('auth.html', mode='verify', email=email)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        conn = auth_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute('SELECT * FROM users WHERE email=%s AND verified=1', (email,))
            user = cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session.clear()
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session.permanent = True
            return redirect(url_for('index'))
        flash('Email or password is incorrect, or the email has not been verified.', 'error')
    return render_template('auth.html', mode='login')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('landing'))

@app.before_request
def protect_tracker_pages():
    public_endpoints = {'landing', 'about', 'features', 'contact', 'register',
                        'verify_email', 'login', 'logout', 'demo', 'exit_demo', 'serve_static', 'static'}
    if session.get('demo_mode') and request.method == 'POST' and request.endpoint != 'logout':
        flash('Demo mode is read-only. Your sample data cannot be changed.', 'info')
        return redirect(request.referrer or url_for('index'))
    if request.endpoint and request.endpoint not in public_endpoints and not session.get('user_id') and not session.get('demo_mode'):
        return redirect(url_for('login', next=request.path))


def demo_data():
    """Fresh sample records, isolated from every account and database operation."""
    categories = [
        {'category_id': 1, 'category_name': 'Food & Dining'},
        {'category_id': 2, 'category_name': 'Transport'},
        {'category_id': 3, 'category_name': 'Shopping'},
        {'category_id': 4, 'category_name': 'Bills & Utilities'},
        {'category_id': 5, 'category_name': 'Health'},
    ]
    today = datetime.now().date()
    samples = [
        (0, 245, 'Lunch with colleagues', 1, 'UPI'), (1, 80, 'Metro ride', 2, 'Cash'),
        (2, 1299, 'Household essentials', 3, 'Credit Card'), (3, 620, 'Weekly groceries', 1, 'UPI'),
        (4, 450, 'Electricity bill', 4, 'Net Banking'), (6, 180, 'Pharmacy', 5, 'UPI'),
        (8, 320, 'Cab ride', 2, 'UPI'), (10, 890, 'Dinner', 1, 'Debit Card'),
        (13, 499, 'Internet bill', 4, 'Credit Card'), (17, 2150, 'Clothing', 3, 'Credit Card'),
        (22, 560, 'Groceries', 1, 'UPI'), (28, 150, 'Bus pass', 2, 'Cash'),
        (35, 330, 'Breakfast', 1, 'Cash'), (42, 990, 'Home supplies', 3, 'UPI'),
    ]
    expenses = []
    for number, (days_ago, amount, description, category_id, payment_method) in enumerate(samples, 1):
        cat = categories[category_id - 1]
        expenses.append({'expense_id': number, 'expense_date': str(today - timedelta(days=days_ago)),
                         'category_id': category_id, 'category_name': cat['category_name'],
                         'amount': float(amount), 'description': description, 'payment_method': payment_method})
    expenses.sort(key=lambda row: (row['expense_date'], row['expense_id']), reverse=True)
    return categories, expenses


# --------------------------------------------------------------------
# 1. Dashboard (Index)
# --------------------------------------------------------------------
@app.route('/index')
@app.route('/api')
@app.route('/api/index')
@app.route('/api/index.py')
@app.route('/index.py')
def index():
    """
    Main dashboard displaying summary KPI cards, Matplotlib charts,
    and recent expense records.
    """
    categories, all_expenses = demo_data() if session.get('demo_mode') else (database.get_categories(session['user_id']), database.get_expenses(session['user_id']))
    
    # Run Pandas/NumPy analytics pipeline
    analysis = analytics.analyze_expenses(all_expenses)
    
    # Calculate current month's spending
    current_month_str = datetime.now().strftime('%Y-%m')
    current_month_total = 0.0
    for m in analysis['monthly_totals']:
        if m['month_year'] == current_month_str:
            current_month_total = m['total_amount']
            break
            
    # Recent 7 expenses
    recent_expenses = all_expenses[:7] if all_expenses else []
    
    return render_template(
        'index.html',
        categories=categories,
        total_expenses=analysis['total_expenses'],
        current_month_total=current_month_total,
        transaction_count=analysis['transaction_count'],
        highest_category=analysis['highest_category'],
        summary_stats=analysis['summary_stats'],
        category_breakdown=analysis['category_breakdown'][:5],
        recent_expenses=recent_expenses,
        pie_chart=analysis['pie_chart'],
        bar_chart=analysis['bar_chart'],
        monthly_chart_data=analysis['monthly_totals'],
        has_data=analysis['has_data'],
        is_demo=session.get('demo_mode', False)
    )

# --------------------------------------------------------------------
# 2. Expenses Management (CRUD & Filters)
# --------------------------------------------------------------------
@app.route('/expenses')
def expenses_list():
    """
    List expenses with date range and category filters.
    Computes exact totals that match the filtered records.
    """
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()
    category_id = request.args.get('category_id', '').strip()
    search = request.args.get('search', '').strip()
    
    categories, demo_expenses = demo_data() if session.get('demo_mode') else (None, None)
    categories = categories if session.get('demo_mode') else database.get_categories(session['user_id'])
    filtered_expenses = ([row for row in demo_expenses
        if (not start_date or row['expense_date'] >= start_date)
        and (not end_date or row['expense_date'] <= end_date)
        and (not category_id or str(row['category_id']) == category_id)
        and (not search or search.casefold() in row['description'].casefold() or search.casefold() in row['payment_method'].casefold())]
        if session.get('demo_mode') else database.get_expenses(
        session['user_id'], start_date=start_date if start_date else None,
        end_date=end_date if end_date else None,
        category_id=category_id if category_id else None,
        search=search if search else None
    ))
    
    # Compute totals for filtered records (Acceptance Criteria)
    filtered_total = sum(exp['amount'] for exp in filtered_expenses)
    filtered_count = len(filtered_expenses)
    filtered_avg = (filtered_total / filtered_count) if filtered_count > 0 else 0.0
    
    return render_template(
        'expenses.html',
        expenses=filtered_expenses,
        categories=categories,
        filtered_total=round(filtered_total, 2),
        filtered_count=filtered_count,
        filtered_avg=round(filtered_avg, 2),
        start_date=start_date,
        end_date=end_date,
        selected_category=int(category_id) if category_id and category_id.isdigit() else '',
        search=search
    )

@app.route('/expenses/add', methods=['POST'])
def add_expense():
    """Record a new expense."""
    expense_date = request.form.get('expense_date')
    category_id = request.form.get('category_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    payment_method = request.form.get('payment_method', 'Cash')
    
    success, msg = database.add_expense(
        user_id=session['user_id'],
        expense_date=expense_date,
        category_id=category_id,
        amount=amount,
        description=description,
        payment_method=payment_method
    )
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
        
    redirect_target = request.referrer or url_for('expenses_list')
    return redirect(redirect_target)

@app.route('/expenses/edit/<int:expense_id>', methods=['POST'])
def edit_expense(expense_id):
    """Update an existing expense."""
    expense_date = request.form.get('expense_date')
    category_id = request.form.get('category_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    payment_method = request.form.get('payment_method')
    
    success, msg = database.update_expense(
        user_id=session['user_id'],
        expense_id=expense_id,
        expense_date=expense_date,
        category_id=category_id,
        amount=amount,
        description=description,
        payment_method=payment_method
    )
    
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
        
    return redirect(url_for('expenses_list'))

@app.route('/expenses/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    """Delete an expense record."""
    success, msg = database.delete_expense(session['user_id'], expense_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('expenses_list'))

# --------------------------------------------------------------------
# 3. Analytics & Visualizations (Pandas, NumPy, Matplotlib)
# --------------------------------------------------------------------
@app.route('/analytics')
def analytics_view():
    """
    Dedicated Data Analysis view highlighting:
    - NumPy summary statistics table
    - Pandas category breakdown table with percentages
    - Pandas monthly aggregation
    - Payment methods distribution
    - Full-sized Matplotlib charts
    """
    all_expenses = demo_data()[1] if session.get('demo_mode') else database.get_expenses(session['user_id'])
    analysis = analytics.analyze_expenses(all_expenses)
    
    return render_template(
        'analytics.html',
        analysis=analysis
    )

# --------------------------------------------------------------------
# 4. Monthly Expense Reports
# --------------------------------------------------------------------
@app.route('/reports')
def monthly_reports():
    """
    Generate and inspect monthly expense reports:
    - Selectable month dropdown
    - Monthly total, daily average, and highest category
    - Category percentage breakdown
    - Complete transaction ledger for that month
    - Printable report layout
    """
    all_expenses = demo_data()[1] if session.get('demo_mode') else database.get_expenses(session['user_id'])
    analysis = analytics.analyze_expenses(all_expenses)
    
    # Available months list
    available_months = [m['month_year'] for m in analysis['monthly_totals']]
    # Sort reverse chronological
    available_months.reverse()
    
    selected_month = request.args.get('month', '').strip()
    if not selected_month and available_months:
        selected_month = available_months[0]
        
    report_data = None
    if selected_month:
        report_data = analytics.generate_monthly_report_analysis(all_expenses, selected_month)
        
    return render_template(
        'reports.html',
        available_months=available_months,
        selected_month=selected_month,
        report=report_data
    )

# --------------------------------------------------------------------
# 5. Category Management
# --------------------------------------------------------------------
@app.route('/categories')
def categories_view():
    """Manage categories: list, add, delete."""
    categories, all_expenses = demo_data() if session.get('demo_mode') else (database.get_categories(session['user_id']), database.get_expenses(session['user_id']))
    
    # Count expenses in each category
    counts = {}
    totals = {}
    for exp in all_expenses:
        cid = exp['category_id']
        counts[cid] = counts.get(cid, 0) + 1
        totals[cid] = totals.get(cid, 0.0) + exp['amount']
        
    for cat in categories:
        cat['expense_count'] = counts.get(cat['category_id'], 0)
        cat['total_amount'] = round(totals.get(cat['category_id'], 0.0), 2)
        
    return render_template('categories.html', categories=categories)

@app.route('/categories/add', methods=['POST'])
def add_category():
    """Add a new expense category."""
    category_name = request.form.get('category_name', '')
    success, msg = database.add_category(session['user_id'], category_name)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('categories_view'))

@app.route('/categories/delete/<int:category_id>', methods=['POST'])
def delete_category(category_id):
    """Delete a category if no expenses are linked."""
    success, msg = database.delete_category(session['user_id'], category_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'error')
    return redirect(url_for('categories_view'))

# --------------------------------------------------------------------
# 6. JSON API Endpoints for UI / Modals
# --------------------------------------------------------------------
@app.route('/api/expenses/<int:expense_id>')
def api_get_expense(expense_id):
    """Returns single expense details in JSON format for the Edit modal."""
    expense = (next((row for row in demo_data()[1] if row['expense_id'] == expense_id), None)
               if session.get('demo_mode') else database.get_expense_by_id(session['user_id'], expense_id))
    if expense:
        return jsonify({'success': True, 'expense': expense})
    return jsonify({'success': False, 'message': 'Expense not found'}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"[*] Starting Personal Expense Tracking and Analysis System on http://0.0.0.0:{port} ...")
    app.run(debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true', host='0.0.0.0', port=port)
