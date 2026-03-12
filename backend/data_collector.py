import requests
import pandas as pd
import time
from .db import check_mongodb_connection, insert_data
from concurrent.futures import ThreadPoolExecutor, as_completed

start = time.time()
# ==========================================================
# CONFIGURATION SECTION (Easy to modify while testing)
# ==========================================================

print(check_mongodb_connection())

MAX_THREADS = 10
REQUEST_TIMEOUT = 30
RETRY_LIMIT = 3
RETRY_DELAY = 2
REQUEST_DELAY = 0.05

INPUT_FILE = "input.csv"

# ==========================================================
# CREATE A GLOBAL SESSION
# ==========================================================

session = requests.Session()

HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64)",
    "Referer": "https://leetcode.com",
}

# ==========================================================
# GRAPHQL QUERY
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
# FETCH LEETCODE DATA
# ==========================================================

def get_leetcode_stats(username):

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

            if response.status_code == 200:
                return username, response.json()

            if response.status_code in [429, 403]:
                print(f"⚠ Rate limit hit for {username}, retrying...")
                time.sleep(RETRY_DELAY)

        except requests.exceptions.RequestException:
            print(f"⚠ Network error for {username}, retrying...")

        time.sleep(RETRY_DELAY)

    return username, None


# ==========================================================
# PROCESS USER
# ==========================================================

def process_user(row):

    username = str(row.get("Leetcode ID", "")).strip()

    # Missing username
    if not username:
        return build_row(row, username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"), False

    username, stats = get_leetcode_stats(username)

    # Invalid or API failure
    if not stats or stats["data"]["matchedUser"] is None:
        print(f"⚠ Invalid username: {username}")
        return build_row(row, username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"), False

    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    try:
        easy = matched_user["submitStats"]["acSubmissionNum"][1]["count"]
        medium = matched_user["submitStats"]["acSubmissionNum"][2]["count"]
        hard = matched_user["submitStats"]["acSubmissionNum"][3]["count"]
        total = matched_user["submitStats"]["acSubmissionNum"][0]["count"]
    except:
        easy = medium = hard = total = "N/A"

    contest_attended = contest_info["attendedContestsCount"] if contest_info else "N/A"
    contest_rating = contest_info["rating"] if contest_info else "N/A"
    global_ranking = contest_info["globalRanking"] if contest_info else "N/A"

    time.sleep(REQUEST_DELAY)

    return (
        build_row(
            row,
            matched_user["username"],
            easy,
            medium,
            hard,
            total,
            contest_attended,
            contest_rating,
            global_ranking,
        ),
        True,
    )


# ==========================================================
# BUILD ROW STRUCTURE
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

    valid_results = []
    invalid_results = []

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:

        futures = [executor.submit(process_user, row) for _, row in df_input.iterrows()]

        for idx, future in enumerate(as_completed(futures), start=1):

            try:
                row_data, is_valid = future.result()

                if is_valid:
                    valid_results.append(row_data)
                else:
                    invalid_results.append(row_data)

                print(f"[{idx}/{len(futures)}] ✅ Processed")

            except Exception as e:
                print(f"❌ Error processing row: {e}")

    # ======================================================
    # SAVE VALID USERS
    # ======================================================

    df_output = pd.DataFrame(valid_results)
    df_output = df_output.sort_values(by="S.no")

    df_output = df_output.drop(columns=["S.no"])
    records = df_output.to_dict("records")
    records = df_output.fillna("N/A").to_dict("records")

    insert_data("leetcodedata", "validusers", records)


    # ======================================================
    # SAVE INVALID USERS
    # ======================================================

    df_invalid = pd.DataFrame(invalid_results)
    df_invalid = df_invalid.sort_values(by="S.no")
    
    df_invalid = df_invalid.drop(columns=["S.no"])
    records = df_invalid.fillna("N/A").to_dict("records")

    # Print the first record
    print(records[0])



    insert_data("leetcodedata", "invalidusers", records)

    print("\n🎉 Scraping Completed!")


end = time.time()

print("Time taken:", end - start, "seconds")