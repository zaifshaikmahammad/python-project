"""Initialize all required tables in the configured existing MySQL database."""
import sys
import database
from config import Config


def main():
    print(f"Connecting to MySQL database {Config.MYSQL_DB} at {Config.MYSQL_HOST}:{Config.MYSQL_PORT} ...")
    ok, message = database.init_db()
    print(message)
    if not ok:
        return 1
    print("MySQL is ready. Categories, expenses, users, and pending OTP tables are available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
