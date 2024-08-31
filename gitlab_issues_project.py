import requests
import psycopg2
from psycopg2 import sql
from datetime import datetime, timedelta

# GitLab configuration
GITLAB_URL = "https://gitlab.com"
PRIVATE_TOKEN = "your_token"
GROUP_ID = "mayan-edms"

# PostgreSQL configuration
DB_HOST = "localhost"
DB_NAME = "gitlab_api"
DB_USER = "postgres"
DB_PASSWORD = "password"

# Function to get issues from GitLab API
def get_gitlab_issues(group_id):
    url = f"https://gitlab.com/api/v4/groups/{group_id}/issues"
    headers = {"PRIVATE-TOKEN": PRIVATE_TOKEN}
    params = {
        "per_page": 100,
        "state": "all",
    }

    issues = []
    page = 1

    while True:
        params['page'] = page
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Failed to fetch issues: {response.status_code}")
            break
        data = response.json()
        if not data:
            break
        issues.extend(data)
        page += 1

    return issues

# Function to save issues to PostgreSQL
def save_issues_to_postgresql(issues):
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        today = datetime.today().date()

        for issue in issues:
            cursor.execute(
                sql.SQL("""
                    INSERT INTO gitlab_issues (issue_id, title, state, created_at, closed_at, run_date)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (issue_id) DO NOTHING
                """),
                (
                    issue.get("id"),
                    issue.get("title"),
                    issue.get("state"),
                    issue.get("created_at"),
                    issue.get("closed_at"),
                    today
                )
            )

        conn.commit()
        print("Issues saved to the PostgreSQL database.")

    except Exception as e:
        print(f"Error saving issues to PostgreSQL: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to generate a quarterly report
def generate_quarterly_report():
    try:
        # Establish the connection to the database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        # Define the query to get the quarterly opened and closed issue counts
        query = """
        SELECT run_date, state, COUNT(*) as issue_count
        FROM gitlab_issues
        WHERE created_at >= run_date - INTERVAL '3 months' or closed_at >= run_date - INTERVAL '3 months'
        GROUP BY run_date, state
        ORDER BY run_date, state;
        """

        # Execute the query
        cursor.execute(query)
        results = cursor.fetchall()

        # Print the quarterly report
        print("Quarterly Issue Report:")
        for row in results:
            print(f"Date: {row[0]}, State: {row[1]}, Count: {row[2]}")

    except Exception as e:
        print(f"Error generating quarterly report: {e}")
    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Function to generate a yearly report
def generate_yearly_report():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()

        query = """
        SELECT run_date, state, COUNT(*) as issue_count
        FROM gitlab_issues
        WHERE created_at >= run_date - INTERVAL '365 days' or closed_at >= run_date - INTERVAL '365 days'
        GROUP BY run_date, state
        ORDER BY run_date, state;
        """

        cursor.execute(query)
        results = cursor.fetchall()

        print("Yearly Issue Report:")
        for row in results:
            print(f"Date: {row[0]}, State: {row[1]}, Count: {row[2]}")

    except Exception as e:
        print(f"Error generating yearly report: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Main function
def main():
    issues = get_gitlab_issues(GROUP_ID)
    save_issues_to_postgresql(issues)
    generate_quarterly_report()
    generate_yearly_report()

if __name__ == "__main__":
    main()
