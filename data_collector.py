import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    query = """
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
    variables = {"username": username}
    response = requests.post(url, json={"query": query, "variables": variables})
    if response.status_code == 200:
        return username, response.json()
    return username, None

def process_user(username, titles):
    username = str(username).strip()
    if not username:
        # Blank username → N/A for all fields
        return pd.DataFrame([[ "N/A" for _ in titles ]], columns=titles)

    username, stats = get_leetcode_stats(username)

    if not stats or stats["data"]["matchedUser"] is None:
        print(f"⚠ Username '{username}' not found. Filling with N/A.")
        return pd.DataFrame([[username, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"]], columns=titles)

    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    return pd.DataFrame([[
        matched_user["username"],
        matched_user["submitStats"]["acSubmissionNum"][0]["count"],
        matched_user["profile"]["ranking"],
        matched_user["profile"]["reputation"],
        contest_info["rating"] if contest_info else "N/A",
        contest_info["attendedContestsCount"] if contest_info else "N/A",
        contest_info["globalRanking"] if contest_info else "N/A"
    ]], columns=titles)

# Setup
titles = ["User Name", "Problem Count", "General Ranking", "Reputation",
          "Contest Rating", "Contest Attended", "Global Ranking"]

df_input = pd.read_csv('input.csv')
df_output = pd.DataFrame(columns=titles)

print(f"🚀 Starting LeetCode scraping for {len(df_input)} users...\n")

# Threaded execution
max_threads = 8  # Change based on internet speed
with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = [executor.submit(process_user, username, titles) for username in df_input['Leetcodeid']]

    for idx, future in enumerate(as_completed(futures), start=1):
        result = future.result()
        df_output = pd.concat([df_output, result], ignore_index=True)
        print(f"[{idx}/{len(futures)}] ✅ Processed")

# Save result
df_output.to_csv('output.csv', index=False)
print("\n🎉 Finished! Saved as 'output.csv'")
