# Personal Expense Tracking and Analysis System

An academic, beginner-friendly web application designed to help individuals record personal expenses and gain clear, data-driven insights into their monthly spending patterns and category-wise expenditure.

---

## 📌 Project Overview

- **Project Objective:** Record personal expenses and help users understand monthly spending and category-wise expenditure.
- **Academic Scope:** Single-user learning project using fictional or voluntarily entered expense data. It is an educational tracking system, not a banking or financial-advice system.
- **Key Modules:**
  1. **Expense Management (CRUD):** Add, edit, delete, and list expenses with positive amount enforcement and decimal-safe handling.
  2. **Filtering Engine:** Filter records dynamically by date range (`start_date` to `end_date`), category, and description search. Totals automatically reflect the filtered view.
  3. **Data Analysis with Pandas & NumPy:**
     - **Pandas:** Grouping expenses by month and category, calculating expenditure percentages.
     - **NumPy:** Statistical measures including Mean, Median, Standard Deviation, Min, Max, and Daily Average.
  4. **Data Visualization with Matplotlib:** Category-wise donut/pie chart and month-wise bar chart rendered cleanly on the dashboard.
  5. **Monthly Reports:** Itemized monthly statements with printable/exportable views.

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3, Vanilla JavaScript | Responsive financial dashboard, modern dark sidebar, KPI summary cards, filter bars, modals |
| **Backend** | Python Flask (v3.x) | Web routing, form validation, request handling, JSON APIs |
| **Database** | MySQL | Persistent storage for expenses, categories, accounts, and email verification |
| **Data Analysis** | Pandas & NumPy | Grouping by month/category, numerical summary statistics |
| **Data Visualization** | Matplotlib | High-DPI pie and bar chart image generation (rendered as Base64) |

---

## 📂 Project Directory Structure

```text
PersonalExpense tracker/
├── app.py                 # Flask web application entry point and routes
├── config.py              # Configuration loader for environment variables
├── database.py            # MySQL database connection, queries, and CRUD helpers
├── analytics.py           # Pandas, NumPy, and Matplotlib data analysis pipeline
├── init_db.py             # One-click database initialization & test script
├── schema.sql             # MySQL schema definitions + sample fictional data
├── requirements.txt       # Python dependencies list
├── .gitignore             # Git ignore file (keeps .env and caches untracked)
├── .env.example           # Example configuration template
├── README.md              # Project documentation and setup guide
├── static/
│   ├── css/
│   │   └── style.css      # Vanilla CSS styling with modern financial theme
│   └── js/
│       └── app.js         # Client-side validation, AJAX modals, print trigger
└── templates/
    ├── base.html          # Base layout with sidebar, navbar, and modals
    ├── index.html         # Dashboard overview (KPIs, charts, recent transactions)
    ├── expenses.html      # Expense ledger with date/category filters and CRUD
    ├── analytics.html     # Statistical analytics table (NumPy & Pandas)
    ├── reports.html       # Monthly expense report generator & printable view
    └── categories.html    # Category management view
```

---

## 🗄️ Database Schema

### Table 1: `categories`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `category_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique category identifier |
| `category_name` | VARCHAR(100) | NOT NULL, UNIQUE | Name of expense category |

### Table 2: `expenses`
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `expense_id` | INT | PRIMARY KEY, AUTO_INCREMENT | Unique expense identifier |
| `expense_date` | DATE | NOT NULL | Date when the expense occurred |
| `category_id` | INT | FOREIGN KEY (`category_id`) | Category classification reference |
| `amount` | DECIMAL(10, 2) | NOT NULL, CHECK (`amount` > 0) | Monetary amount spent |
| `description` | VARCHAR(255) | NOT NULL | Short note / purpose of expense |
| `payment_method` | VARCHAR(50) | NOT NULL | e.g. UPI, Cash, Credit Card, Debit Card |

---

## 🚀 Step-by-Step Setup Guide

### 1. Prerequisites
- **Python 3.9+** installed on your computer.
- **MySQL Server** (via MySQL Community Server, MySQL Workbench, or XAMPP / WampServer).

---

### 2. Install Python Dependencies
Open your terminal or command prompt inside the project folder:
```bash
cd "PersonalExpense tracker"
pip install -r requirements.txt
```

---

### 3. Configure Database Settings (`.env`)
Copy `.env.example` to `.env` (or edit the existing `.env`):
```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DB=expense_tracker_db

# Flask Application Secret Key
SECRET_KEY=your_secure_random_flask_secret_key_here
```
> **Security Note:** Never commit your `.env` file to version control. The included `.gitignore` file automatically ensures `.env` stays private on your local machine.

---

### 4. Initialize Database & Load Sample Data

#### Option A: One-click Python script (Recommended)
Simply run:
```bash
python init_db.py
```
This script will connect to your database, create the tables, and insert 30 fictional expense records across various categories and months.

#### Option B: Via MySQL Command Line or Workbench
You can also run the SQL commands directly from `schema.sql`:
```bash
mysql -u root -p < schema.sql
```

---

### 5. Run the Flask Web Application
Start the Flask development server:
```bash
python app.py
```

You should see output similar to:
```text
[*] Starting Personal Expense Tracking and Analysis System on http://127.0.0.1:5000 ...
 * Running on http://127.0.0.1:5000
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🧪 Testing Acceptance Criteria

1. **Add an Expense:** Click `+ Add Expense` in the top bar. Try entering a negative number or `0` — notice the client and server validation stops it and enforces positive values. Enter a valid expense (e.g. `250.00`) and verify it appears in the ledger.
2. **Edit & Delete:** In the Expenses Ledger, click the pencil icon to edit an expense via the pop-up modal. Click the trash icon to test deletion with a confirmation prompt.
3. **Date & Category Filters:** Go to **Expenses Ledger**, select a date range (e.g. from `2026-09-01` to `2026-09-30`) or pick `Food & Dining`. Click **Apply Filters**. Verify the **Filtered Total** and matching records update accurately.
4. **Data Analytics:** Navigate to **Data Analytics** to inspect the **NumPy** statistics table (`np.mean`, `np.median`, `np.std`, `np.min`, `np.max`) and the **Pandas** category breakdown table.
5. **Matplotlib Visualizations:** Review the Category Donut/Pie Chart and Monthly Bar Chart on both the Dashboard and the Data Analytics tab.
6. **Monthly Reports:** Click **Monthly Reports**, pick a month (e.g. `2026-10`), and inspect the itemized ledger and category breakdown. Click **Print / Export Statement** to open a print-ready view.
7. **Empty Data Handling:** If all expenses are deleted or no records match a filter, clean, graceful empty state cards appear instead of server errors.

---

## ☁️ Cloud Deployment (Render + Aiven MySQL)

This project is a Flask web service. Deploy it as a **Render Web Service**, not a Static Site. Render runs the app with Gunicorn and connects to your existing hosted Aiven MySQL database.

### 1. Push the project to GitHub

1. Extract this ZIP file.
2. Open the extracted folder (the folder containing `app.py` and `render.yaml`).
3. Create a GitHub repository and upload the project files. Do **not** upload `.env`, passwords, or CA private keys. `.gitignore` already excludes `.env`.

### 2. Prepare Aiven MySQL

In Aiven Console, open your MySQL service and copy the connection details from **Overview → Connection information**. Use the values shown in your own console; do not assume a port or hostname from an old connection.

For the previously configured service, the expected values were:

- `MYSQL_HOST`: `mysql-37794b0-pardhupachipala22-9205b.aivencloud.com`
- `MYSQL_PORT`: `22358`
- `MYSQL_USER`: `avnadmin`
- `MYSQL_DB`: `defaultdb`

Confirm these still match the live Aiven service. Download its **CA certificate** from the Aiven console as `ca.pem`.

### 3. Create the Render service

1. Sign in at https://dashboard.render.com/.
2. Choose **New → Blueprint** if you want Render to read `render.yaml`, or **New → Web Service** and connect the GitHub repository.
3. For a manual Web Service, choose **Python** with:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python init_db.py && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`
4. Choose a plan and create the service. The free service can sleep when inactive.

### 4. Add environment variables in Render

Open the service → **Environment** and add:

| Key | Value |
|---|---|
| `MYSQL_HOST` | Host copied from Aiven |
| `MYSQL_PORT` | Port copied from Aiven (previously `22358`) |
| `MYSQL_USER` | Username copied from Aiven (previously `avnadmin`) |
| `MYSQL_PASSWORD` | Your Aiven password (secret) |
| `MYSQL_DB` | Existing database name (previously `defaultdb`) |
| `MYSQL_USE_SSL` | `true` |
| `MYSQL_SSL_CA` | `/etc/secrets/ca.pem` |
| `SECRET_KEY` | A long random secret; Render Blueprint can generate this automatically |
| `SMTP_HOST` | `smtp.gmail.com` (only if using email verification) |
| `SMTP_PORT` | `587` (only if using email verification) |
| `SMTP_USER` | Your sending Gmail address |
| `SMTP_FROM` | Same sending Gmail address |
| `SMTP_PASSWORD` | Gmail App Password (secret; only if using email verification) |

**Upload the Aiven CA certificate:** in the Render service's Environment page, add it under **Secret Files** with filename `ca.pem`. Its mounted path should be `/etc/secrets/ca.pem`. Keep `MYSQL_SSL_CA` equal to that exact path. Aiven recommends TLS and its CA certificate for verified connections.

Do not paste your password or App Password into GitHub, README files, screenshots, or chat.

### 5. Deploy and verify

Save the environment settings and trigger **Manual Deploy → Deploy latest commit** if Render does not deploy automatically. The start command runs `init_db.py` first, which creates or migrates the required tables inside the existing `MYSQL_DB`; it does not attempt to create a new database. Then Gunicorn starts the Flask app.

When the service is Live, open its `https://<your-service>.onrender.com` address. Test registration (SMTP must be configured), email OTP verification, login, add/edit/delete expense, and confirm records remain after restarting the service.

### Troubleshooting

- **`Access denied for user`**: re-copy Aiven username/password and check the allowed IP/network settings in Aiven.
- **`Unknown MySQL server host` / timeout**: re-copy hostname and port from the active Aiven service and check that it is running.
- **SSL certificate verification error**: confirm the Aiven CA secret file exists at `/etc/secrets/ca.pem` and `MYSQL_SSL_CA` matches exactly.
- **`Table doesn't exist`**: inspect Render deploy logs; the `python init_db.py` step must finish successfully before Gunicorn starts.
- **OTP email failure**: configure Gmail SMTP credentials and use a Gmail App Password with 2-Step Verification enabled. Otherwise registration email verification will not work.

A successful Python syntax check does not guarantee that a live database or SMTP account is reachable. The final confirmation is a successful Render deploy plus live registration and database-write tests.

---

## 📚 Academic Submission Notes
- **Independent Project:** Developed strictly within academic scope without third-party payment gateways, banking APIs, or authentication overhead.
- **Data Integrity:** Strict decimal formatting (`DECIMAL(10,2)` in MySQL, `float` rounded to 2 places in Python) guarantees no fractional currency drift.
- **Code Readability:** Every file contains clear docstrings and comments explaining how backend routes interact with the analytical libraries.



## New account and landing-page features
- Public Home, About, Features and Contact pages.
- Registration, password login, and 6-digit email OTP verification.
- OTP email delivery uses SMTP environment variables documented in `.env.example`. If SMTP is not configured, a development-only OTP is printed to the server log; configure SMTP before public deployment.
- Dashboard pages require a signed-in session and show a time-based greeting.
- Dashboard category donut chart is interactive: click a slice to highlight it and display its value and percentage.
- Playful Neo-Brutalist coral/lime/off-white styling with responsive layouts and motion.

### Important deployment notes
Set a strong random `SECRET_KEY` and configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, and `SMTP_FROM` as Render environment variables. Expense, category, account, and OTP records are stored in MySQL. In this iteration, expense/category records are partitioned by account using `user_id`.

Contact page currently contains a placeholder. Add your preferred public email address and mobile number when ready.


## Gmail email OTP setup

The registration flow sends a six-digit OTP through Gmail SMTP. Set these variables in your deployment environment:

- `SMTP_HOST=smtp.gmail.com`
- `SMTP_PORT=587`
- `SMTP_USER=25102a04009@gmail.com`
- `SMTP_FROM=25102a04009@gmail.com`
- `SMTP_PASSWORD` = the Gmail App Password you generated (secret; never commit it)
- `SECRET_KEY` = a long, random Flask session secret

For Render, open your service **Environment** settings and add `SMTP_PASSWORD` there. The `render.yaml` intentionally marks it `sync: false`, so the secret is not included in this ZIP or Git repository.

The OTP expires after 10 minutes and allows at most five attempts. Passwords are stored as secure password hashes, not plain text.

### Before real multi-user production use

The existing expense and category database is currently shared by the original project. Registration and login now verify individual accounts, but the existing MySQL expense/category queries have not yet been changed to filter by account owner. Do not use this version for real multi-user private financial data until per-user ownership has been added throughout the database layer.

The account/OTP tables are stored in MySQL, so a local SQLite file or persistent host disk is not required.

## Multi-user data separation

Each verified account has a unique account ID in the authentication database. Every MySQL category and expense row is stored with that account ID (`user_id`). Dashboard totals, charts, analytics, reports, category lists, expense edits, deletes, and the expense JSON endpoint all query by the logged-in account ID. Category ownership is checked before an expense can be added or edited, and record IDs cannot be used to read or modify another account's rows.

Run `python init_db.py` after configuring MySQL. It creates the database if needed and migrates `categories` and `expenses` to include `user_id`. Existing legacy rows are retained with a NULL owner and are deliberately not displayed to any account; they are not automatically assigned to the first person who registers. If you need to preserve old shared records, back up the database and explicitly assign them to the correct account before using the new multi-user version.

Account authentication and financial records are both stored in the configured MySQL database. The Flask session signing key and SMTP credentials must be set as private environment variables on the deployment platform.

---

## Deploy on Render with Aiven MySQL

This repository is configured as a regular Flask web service on Render (not a Vercel serverless function). The Render start command initializes the required tables in the existing Aiven database and then starts Gunicorn.

### 1. Prepare Aiven MySQL

1. Open your Aiven MySQL service and make sure its status is **Running**.
2. Open **Overview / Connection information** and copy the host, port, user, and password for the MySQL service.
3. Use the existing database name shown by Aiven. For the usual Aiven default database this is `defaultdb`; do not create a database with SQL if it already exists.
4. Download the service CA certificate (`ca.pem`) from the Aiven service's connection/security page. Keep it private.
5. In Aiven, ensure the service allows connections from Render. If using an IP allowlist, configure it according to Render's outbound IP guidance or the Aiven networking option available on your plan. Do not expose MySQL to unrestricted public access unless required and understood.

### 2. Deploy the GitHub repository to Render

1. Push this project folder to GitHub. Do not upload `.env`, `.env.txt`, a virtual environment, or any password file.
2. In Render choose **New + → Blueprint** (recommended) and select the GitHub repository containing `render.yaml`; alternatively create a **Web Service** with the settings below.
3. Runtime: **Python**; Build command: `pip install -r requirements.txt`.
4. Start command: `python init_db.py && gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 120`.
5. Set the health check path to `/health`.

### 3. Set Render environment variables

In the Render service's **Environment** page, set these values using the Aiven connection details (do not copy example values from old screenshots or README history):

| Key | Value |
|---|---|
| `MYSQL_HOST` | Aiven **host** (hostname only; no `https://`) |
| `MYSQL_PORT` | Aiven **port** (number) |
| `MYSQL_USER` | Aiven **user** |
| `MYSQL_PASSWORD` | Aiven MySQL password |
| `MYSQL_DB` | Existing database name, usually `defaultdb` |
| `MYSQL_USE_SSL` | `true` |
| `MYSQL_SSL_CA` | `/etc/secrets/ca.pem` |
| `SECRET_KEY` | Generate a long random secret; keep private. Blueprint can generate it. |

Under **Secret Files**, add a file named `ca.pem` and paste the full contents of the CA certificate downloaded from Aiven. Render mounts it at `/etc/secrets/ca.pem`. If your Render plan does not offer Secret Files, use a plan/configuration that supports it; do not disable TLS certificate verification to work around the issue.

Email OTP registration also needs `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_FROM`, and `SMTP_PASSWORD`. `SMTP_PASSWORD` must be a Gmail App Password (not your normal Gmail password). Email settings are optional for deployment, but registration/OTP email will not work until they are configured.

### 4. Deploy and verify

1. Save the environment variables and deploy the latest commit.
2. Check **Render → Logs**. The startup command should print `MySQL is ready` before Gunicorn starts.
3. Open `https://YOUR-RENDER-SERVICE.onrender.com/health`. A successful response is `{"status":"ok","database":"connected"}`.
4. Open the site, register, verify the OTP (if SMTP is configured), and add a test expense. Refresh the page and confirm it remains present.

### Troubleshooting

- **Access denied**: re-copy the Aiven username/password and confirm they belong to the selected service.
- **Can't connect / timeout**: check that Aiven is running, host and port are exact, and networking/allowlist rules permit Render.
- **SSL / certificate error**: confirm the downloaded Aiven CA is uploaded as Render Secret File `ca.pem` and `MYSQL_SSL_CA=/etc/secrets/ca.pem`.
- **Unknown database**: set `MYSQL_DB` to the database that already exists in Aiven (commonly `defaultdb`).
- **OTP email fails**: configure all SMTP variables and use a Gmail App Password.

The application cannot connect to your private Aiven service until you enter its actual credentials in Render. Never send database passwords, Gmail App Passwords, or the CA private material in chat or commit them to GitHub.


### Landing page preview images
The feature preview images are bundled locally in `static/images/` and referenced with Flask `url_for('static', ...)`, so they load on localhost and on deployment without external image hosting.


### Public page layout update
- Home: introductory hero and short feature highlights only.
- Features: contains the Feature Preview gallery.
- About: contains the everyday-spending interface preview gallery.
- Preview artwork remains bundled under `static/images/` and is served through Flask static URLs.
