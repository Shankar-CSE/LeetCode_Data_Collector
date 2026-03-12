import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# ==========================================================
# CONFIGURATION SECTION (Easy to modify while testing)
# ==========================================================

MAX_THREADS = 10             # Safe thread count (LeetCode blocks >20)
REQUEST_TIMEOUT = 30        # Timeout for each API request
RETRY_LIMIT = 3             # Retry failed requests
RETRY_DELAY = 2             # Delay between retries
REQUEST_DELAY = 0.05        # Small delay to avoid burst traffic

INPUT_FILE = "input.csv"
OUTPUT_FILE = "output.csv"

# ==========================================================
# CREATE A GLOBAL SESSION (Improves performance)
# ==========================================================

session = requests.Session()

# Browser-like headers (important to avoid bot detection)
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Referer": "https://leetcode.com",
}

# ==========================================================
# GRAPHQL QUERY (Used to fetch user statistics)
# ==========================================================

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
# FETCH LEETCODE DATA (with retry protection)
# ==========================================================

def get_leetcode_stats(username):
    """
    Fetch LeetCode stats for a given username.
    Includes retry mechanism to handle temporary failures.
    """

    url = "https://leetcode.com/graphql"
    variables = {"username": username}

    for attempt in range(RETRY_LIMIT):

        try:
            response = session.post(
                url,
                json={"query": LEETCODE_QUERY, "variables": variables},
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )

            # Successful request
            if response.status_code == 200:
                return username, response.json()

            # Rate limit or blocked
            if response.status_code in [429, 403]:
                print(f"⚠ Rate limit hit for {username}, retrying...")
                time.sleep(RETRY_DELAY)

        except requests.exceptions.RequestException:
            print(f"⚠ Network error for {username}, retrying...")

        # Wait before retry
        time.sleep(RETRY_DELAY)

    # If all retries fail
    return username, None


# ==========================================================
# PROCESS EACH USER ROW
# ==========================================================

def process_user(row):

    """
    Extract username from CSV row and fetch stats.
    Returns structured data for final dataframe.
    """

    username = str(row.get("Leetcode ID", "")).strip()

    # ------------------------------------------------------
    # If username is empty
    # ------------------------------------------------------

    if not username:
        return build_row(row, username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

    # ------------------------------------------------------
    # Fetch LeetCode stats
    # ------------------------------------------------------

    username, stats = get_leetcode_stats(username)

    if not stats or stats["data"]["matchedUser"] is None:
        print(f"⚠ Username '{username}' not found or API failed")
        return build_row(row, username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")

    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    # ------------------------------------------------------
    # Extract problem counts
    # ------------------------------------------------------

    try:
        easy = matched_user["submitStats"]["acSubmissionNum"][1]["count"]
        medium = matched_user["submitStats"]["acSubmissionNum"][2]["count"]
        hard = matched_user["submitStats"]["acSubmissionNum"][3]["count"]
        total = matched_user["submitStats"]["acSubmissionNum"][0]["count"]
    except:
        easy = medium = hard = total = "N/A"

    # ------------------------------------------------------
    # Extract contest info
    # ------------------------------------------------------

    contest_attended = contest_info["attendedContestsCount"] if contest_info else "N/A"
    contest_rating = contest_info["rating"] if contest_info else "N/A"
    global_ranking = contest_info["globalRanking"] if contest_info else "N/A"

    # Small delay to avoid API bursts
    time.sleep(REQUEST_DELAY)

    return build_row(
        row,
        matched_user["username"],
        easy,
        medium,
        hard,
        total,
        contest_attended,
        contest_rating,
        global_ranking,
    )


# ==========================================================
# BUILD OUTPUT ROW
# (Centralized function → easier to maintain)
# ==========================================================

def build_row(row, username, easy, medium, hard, total, contests, rating, ranking):

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
        "SKILLRACK ID": row.get("SKILLRACK ID", "N/A"),
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
# MAIN EXECUTION
# ==========================================================

if __name__ == "__main__":

    df_input = pd.read_csv(INPUT_FILE)

    print(f"\n🚀 Starting LeetCode scraping for {len(df_input)} users...\n")

    results = []

    # Thread pool execution
    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        futures = [executor.submit(process_user, row) for _, row in df_input.iterrows()]

        for idx, future in enumerate(as_completed(futures), start=1):

            try:
                results.append(future.result())
                print(f"[{idx}/{len(futures)}] ✅ Processed")

            except Exception as e:
                print(f"❌ Error processing row: {e}")

    # ------------------------------------------------------
    # Convert results list to dataframe (faster than concat)
    # ------------------------------------------------------

    df_output = pd.DataFrame(results)

    # Sort by S.no
    df_output = df_output.sort_values(by="S.no")

    # Save output
    df_output.to_csv(OUTPUT_FILE, index=False)

    print("\n🎉 Finished! Saved as 'output.csv'")