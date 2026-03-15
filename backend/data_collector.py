from tenacity import retry, stop_after_attempt, wait_exponential
from loguru import logger
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import pandas as pd
import requests

from db import check_mongodb_connection, insert_data

# ==========================================================
# CONFIGURATION
# ==========================================================
MAX_THREADS = 20
REQUEST_TIMEOUT = 15
# No longer needed with tenacity
# RETRY_LIMIT = 3
# RETRY_DELAY = 2
# REQUEST_DELAY = 0.05
INPUT_FILE = "./backend/input.csv"


# ==========================================================
# SETUP
# ==========================================================
session = requests.Session()
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Referer": "https://leetcode.com",
}
LEETCODE_QUERY = """
query getUserProfile($username: String!) {
  matchedUser(username: $username) {
    username
    submitStats {
      acSubmissionNum {
        difficulty
        count
      }
    }
    profile {
      ranking
      reputation
    }
  }
  userContestRanking(username: $username) {
    rating
    attendedContestsCount
    globalRanking
  }
}
"""


# ==========================================================
# FETCH LEETCODE DATA
# =_=_========================================================
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry_error_callback=lambda retry_state: None,  # Return None on failure
)
def get_leetcode_stats(username):
    """Fetch user stats from LeetCode API with retries."""
    url = "https://leetcode.com/graphql"
    variables = {"username": username}
    try:
        response = session.post(
            url,
            json={"query": LEETCODE_QUERY, "variables": variables},
            headers=HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        return username, response.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Network error for {username}: {e}. Retrying...")
        raise  # Re-raise to trigger tenacity retry


# ==========================================================
# PROCESS USER
# ==========================================================
def process_user(row):
    """Process a single user row from the input CSV."""
    username = str(row.get("Leetcode ID", "")).strip()

    if not username:
        return build_row(row, "", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"), False

    result = get_leetcode_stats(username)
    if not result or result[1]["data"]["matchedUser"] is None:
        logger.warning(f"Invalid or failed to fetch user: {username}")
        return build_row(row, username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"), False

    _, stats = result
    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    try:
        easy = next((s["count"] for s in matched_user["submitStats"]["acSubmissionNum"] if s["difficulty"] == "Easy"), 0)
        medium = next((s["count"] for s in matched_user["submitStats"]["acSubmissionNum"] if s["difficulty"] == "Medium"), 0)
        hard = next((s["count"] for s in matched_user["submitStats"]["acSubmissionNum"] if s["difficulty"] == "Hard"), 0)
        total = sum([easy, medium, hard])
    except (TypeError, StopIteration):
        easy, medium, hard, total = "N/A", "N/A", "N/A", "N/A"

    contest_attended = contest_info["attendedContestsCount"] if contest_info else "N/A"
    contest_rating = contest_info["rating"] if contest_info else "N/A"
    global_ranking = contest_info["globalRanking"] if contest_info else "N/A"

    return build_row(row, matched_user["username"], easy, medium, hard, total, contest_attended, contest_rating, global_ranking), True


# ==========================================================
# BUILD ROW STRUCTURE
# ==========================================================
def build_row(row, username, easy, medium, hard, total, contests, rating, ranking):
    """Build the dictionary for a user's data."""
    return {
        "S.no": row.get("S.no", "N/A"),
        "Roll No": row.get("Roll No", "N/A"),
        "Name": row.get("Name", "N/A"),
        "DEPT": row.get("DEPT", "N/A"),
        "GENDER": row.get("GENDER", "N/A"),
        "PHONE NUMBER": row.get("PHONE NUMBER", "N/A"),
        "EMAIL ID": row.get("EMAIL ID", "N/A"),
        "IT/Core/Not Interested": row.get("IT/Core/Not Interested", "N/A"),
        "Interested Catagory": row.get("Interested Catagory", "N/A"),
        "Leetcode ID": username,
        "BATCH": row.get("BATCH", "N/A"),
        "Easy": easy,
        "medium": medium,
        "hard": hard,
        "Problem Count": total,
        "Contest Attended": contests,
        "Contest Rating": rating,
        "Global Ranking": ranking,
    }


# ==========================================================
# MAIN
# ==========================================================
def main():
    """Main execution block."""
    start_time = time.time()
    logger.add("data_collector.log", rotation="5 MB", level="INFO")
    logger.info("Starting LeetCode data collection...")

    if not check_mongodb_connection():
        logger.error("MongoDB connection failed. Exiting.")
        return

    try:
        df_input = pd.read_csv(INPUT_FILE)
        logger.info(f"Loaded {len(df_input)} users from {INPUT_FILE}")
    except FileNotFoundError:
        logger.error(f"Input file not found: {INPUT_FILE}")
        return

    valid_results, invalid_results = [], []
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = {executor.submit(process_user, row) for _, row in df_input.iterrows()}
        for i, future in enumerate(as_completed(futures), 1):
            try:
                row_data, is_valid = future.result()
                (valid_results if is_valid else invalid_results).append(row_data)
                logger.info(f"Processed {i}/{len(futures)}")
            except Exception as e:
                logger.error(f"Error processing a row: {e}")

    if valid_results:
        df_output = pd.DataFrame(valid_results).sort_values(by="S.no").drop(columns=["S.no"])
        records = df_output.fillna("N/A").to_dict("records")
        insert_data("validusers", records)
        logger.success(f"Inserted {len(records)} valid users into the database.")

    if invalid_results:
        df_invalid = pd.DataFrame(invalid_results).sort_values(by="S.no").drop(columns=["S.no"])
        records = df_invalid.fillna("N/A").to_dict("records")
        insert_data("invalidusers", records)
        logger.info(f"Inserted {len(records)} invalid users into the database.")

    duration = time.time() - start_time
    logger.success(f"Scraping completed in {duration:.2f} seconds.")


if __name__ == "__main__":
    main()