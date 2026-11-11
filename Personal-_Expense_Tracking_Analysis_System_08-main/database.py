"""
Database Connection and Data Access Layer for MySQL
Strictly uses MySQL with categories and expenses tables.
All database credentials are read directly from .env via Config.
"""

import os
from decimal import Decimal
import mysql.connector
import certifi
from mysql.connector import Error as MySQLError
from config import Config

def get_db_connection(include_database=True):
    """
    Establish a connection to MySQL/TiDB server using credentials from environment variables.
    Configures TLS/SSL automatically for cloud databases like TiDB Cloud while supporting local MySQL.
    """
    conn_params = {
        'host': Config.MYSQL_HOST,
        'port': Config.MYSQL_PORT,
        'user': Config.MYSQL_USER,
        'password': Config.MYSQL_PASSWORD,
        'connection_timeout': 10
    }
    if include_database:
        conn_params['database'] = Config.MYSQL_DB

    # TLS/SSL Configuration for TiDB Cloud & Remote Hosts
    is_local_host = Config.MYSQL_HOST in ('localhost', '127.0.0.1', '')
    should_use_ssl = (not Config.MYSQL_SSL_DISABLED) and (Config.MYSQL_USE_SSL or not is_local_host)

    if should_use_ssl:
        # For Aiven, set MYSQL_SSL_CA to the CA certificate downloaded
        # from the Aiven console. certifi is a fallback for public CAs.
        ca_path = Config.MYSQL_SSL_CA if Config.MYSQL_SSL_CA else certifi.where()
        conn_params['ssl_ca'] = ca_path
        conn_params['ssl_verify_cert'] = True
        if Config.MYSQL_SSL_CA:
            conn_params['ssl_verify_identity'] = True

    return mysql.connector.connect(**conn_params)

def init_db():
    """Create or migrate the schema for strict per-user data ownership.

    Legacy rows receive NULL owner IDs and are deliberately not exposed to users.
    """
    try:
        conn = get_db_connection(include_database=True)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
            category_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            category_name VARCHAR(100) NOT NULL,
            INDEX idx_categories_user (user_id),
            UNIQUE KEY uq_user_category (user_id, category_name)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS expenses (
            expense_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NULL,
            expense_date DATE NOT NULL,
            category_id INT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            description VARCHAR(255) NOT NULL,
            payment_method VARCHAR(50) NOT NULL,
            INDEX idx_expenses_user_date (user_id, expense_date),
            INDEX idx_expenses_user_category (user_id, category_id),
            CONSTRAINT chk_positive_amount CHECK (amount > 0),
            FOREIGN KEY (category_id) REFERENCES categories(category_id) ON DELETE RESTRICT ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        # Account and OTP tables are created here so a single initialization
        # command prepares every table required by the application.
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            email VARCHAR(254) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            verified TINYINT(1) NOT NULL DEFAULT 0,
            created_at VARCHAR(32) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS pending_otps (
            email VARCHAR(254) NOT NULL PRIMARY KEY,
            name VARCHAR(120) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            otp_hash CHAR(64) NOT NULL,
            expires_at VARCHAR(32) NOT NULL,
            attempts INT NOT NULL DEFAULT 0
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""")
        # Upgrade installations created with the older shared-data schema.
        cursor.execute("SHOW COLUMNS FROM categories LIKE 'user_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE categories ADD COLUMN user_id INT NULL")
        cursor.execute("SHOW INDEX FROM categories")
        indexes = cursor.fetchall()
        unique_category_indexes = {}
        for row in indexes:
            # MySQL tuple layout: Table, Non_unique, Key_name, Seq_in_index, Column_name, ...
            if row[1] == 0 and row[4] == 'category_name':
                unique_category_indexes[row[2]] = True
        for index_name in unique_category_indexes:
            if index_name != 'uq_user_category':
                cursor.execute(f"ALTER TABLE categories DROP INDEX `{index_name}`")
        cursor.execute("SHOW INDEX FROM categories WHERE Key_name='uq_user_category'")
        if not cursor.fetchall():
            cursor.execute("ALTER TABLE categories ADD UNIQUE KEY uq_user_category (user_id, category_name)")
        cursor.execute("SHOW COLUMNS FROM expenses LIKE 'user_id'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE expenses ADD COLUMN user_id INT NULL")
        cursor.execute("SHOW INDEX FROM expenses WHERE Key_name='idx_expenses_user_date'")
        if not cursor.fetchall():
            cursor.execute("ALTER TABLE expenses ADD INDEX idx_expenses_user_date (user_id, expense_date)")
        cursor.execute("SHOW INDEX FROM expenses WHERE Key_name='idx_expenses_user_category'")
        if not cursor.fetchall():
            cursor.execute("ALTER TABLE expenses ADD INDEX idx_expenses_user_category (user_id, category_id)")
        conn.commit()
        cursor.close()
        conn.close()
        return True, "Per-user MySQL schema verified and migrated."
    except MySQLError as err:
        return False, f"Database Error: {err}"

DEFAULT_CATEGORIES = [
    'Food & Dining', 'Rent & Utilities', 'Transportation', 'Groceries',
    'Entertainment', 'Healthcare & Medical', 'Education & Books',
    'Personal Care & Shopping'
]

def create_user_categories(user_id):
    """Create a private starter category set for a newly verified account."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT IGNORE INTO categories (user_id, category_name) VALUES (%s, %s)",
            [(int(user_id), name) for name in DEFAULT_CATEGORIES]
        )
        conn.commit()
        cursor.close()
    finally:
        conn.close()


def get_categories(user_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT category_id, category_name FROM categories WHERE user_id=%s ORDER BY category_name ASC", (int(user_id),))
        return cursor.fetchall()
    finally:
        conn.close()


def add_category(user_id, category_name):
    name = (category_name or '').strip()
    if not name:
        return False, "Category name cannot be empty."
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (user_id, category_name) VALUES (%s, %s)", (int(user_id), name))
        conn.commit()
        return True, "Category added successfully."
    except Exception as e:
        return False, f"Error adding category: {str(e)}"
    finally:
        conn.close()


def delete_category(user_id, category_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expenses WHERE user_id=%s AND category_id=%s", (int(user_id), int(category_id)))
        count = cursor.fetchone()[0]
        if count:
            return False, f"Cannot delete category: {count} expense records are linked to it."
        cursor.execute("DELETE FROM categories WHERE category_id=%s AND user_id=%s", (int(category_id), int(user_id)))
        conn.commit()
        return (cursor.rowcount > 0), ("Category deleted successfully." if cursor.rowcount else "Category not found.")
    except Exception as e:
        return False, f"Error deleting category: {str(e)}"
    finally:
        conn.close()


def get_expenses(user_id, start_date=None, end_date=None, category_id=None, search=None):
    conn = get_db_connection()
    query = """SELECT e.expense_id, e.expense_date, e.category_id, c.category_name,
        e.amount, e.description, e.payment_method FROM expenses e
        JOIN categories c ON e.category_id=c.category_id AND c.user_id=e.user_id
        WHERE e.user_id=%s"""
    params = [int(user_id)]
    if start_date:
        query += " AND e.expense_date >= %s"; params.append(start_date)
    if end_date:
        query += " AND e.expense_date <= %s"; params.append(end_date)
    if category_id:
        query += " AND e.category_id=%s"; params.append(int(category_id))
    if search:
        query += " AND (e.description LIKE %s OR e.payment_method LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY e.expense_date DESC, e.expense_id DESC"
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        for row in rows:
            row['amount'] = float(row['amount'])
            row['expense_date'] = str(row['expense_date'])
        return rows
    finally:
        conn.close()


def get_expense_by_id(user_id, expense_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""SELECT e.expense_id,e.expense_date,e.category_id,c.category_name,
            e.amount,e.description,e.payment_method FROM expenses e
            JOIN categories c ON e.category_id=c.category_id AND c.user_id=e.user_id
            WHERE e.user_id=%s AND e.expense_id=%s""", (int(user_id), int(expense_id)))
        expense = cursor.fetchone()
        if expense:
            expense['amount'] = float(expense['amount'])
            expense['expense_date'] = str(expense['expense_date'])
        return expense
    finally:
        conn.close()


def _owned_category(cursor, user_id, category_id):
    cursor.execute("SELECT category_id FROM categories WHERE category_id=%s AND user_id=%s", (int(category_id), int(user_id)))
    return cursor.fetchone() is not None


def add_expense(user_id, expense_date, category_id, amount, description, payment_method):
    try:
        amount_val = round(float(amount), 2)
        if amount_val <= 0: return False, "Expense amount must be strictly greater than zero."
        if not expense_date: return False, "Expense date is required."
        if not description or not description.strip(): return False, "Expense description is required."
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if not _owned_category(cursor, user_id, category_id): return False, "Please select one of your own categories."
            cursor.execute("INSERT INTO expenses (user_id,expense_date,category_id,amount,description,payment_method) VALUES (%s,%s,%s,%s,%s,%s)",
                (int(user_id), expense_date, int(category_id), amount_val, description.strip(), (payment_method or 'Cash').strip()))
            conn.commit()
            return True, "Expense recorded successfully!"
        finally: conn.close()
    except (ValueError, TypeError): return False, "Amount must be a valid number."
    except Exception as e: return False, f"Failed to record expense: {str(e)}"


def update_expense(user_id, expense_id, expense_date, category_id, amount, description, payment_method):
    try:
        amount_val = round(float(amount), 2)
        if amount_val <= 0: return False, "Expense amount must be strictly greater than zero."
        if not expense_date: return False, "Expense date is required."
        if not description or not description.strip(): return False, "Expense description is required."
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            if not _owned_category(cursor, user_id, category_id): return False, "Please select one of your own categories."
            cursor.execute("UPDATE expenses SET expense_date=%s,category_id=%s,amount=%s,description=%s,payment_method=%s WHERE expense_id=%s AND user_id=%s",
                (expense_date,int(category_id),amount_val,description.strip(),(payment_method or 'Cash').strip(),int(expense_id),int(user_id)))
            conn.commit()
            return (cursor.rowcount > 0), ("Expense updated successfully!" if cursor.rowcount else "Expense not found.")
        finally: conn.close()
    except (ValueError, TypeError): return False, "Amount must be a valid number."
    except Exception as e: return False, f"Failed to update expense: {str(e)}"


def delete_expense(user_id, expense_id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE expense_id=%s AND user_id=%s", (int(expense_id), int(user_id)))
        conn.commit()
        return (cursor.rowcount > 0), ("Expense deleted successfully!" if cursor.rowcount else "Expense not found.")
    except Exception as e:
        return False, f"Failed to delete expense: {str(e)}"
    finally:
        conn.close()

def get_database_status():
    """Returns MySQL connection details and status."""
    return {
        'engine': 'MySQL',
        'host': Config.MYSQL_HOST,
        'port': Config.MYSQL_PORT,
        'db': Config.MYSQL_DB,
        'user': Config.MYSQL_USER
    }
