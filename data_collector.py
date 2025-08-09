import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to get stats from Leetcode GraphQL
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
    try:
        response = requests.post(url, json={"query": query, "variables": variables})
        if response.status_code == 200:
            return username, response.json()
    except Exception:
        pass
    return username, None

# Function to process a single user
def process_user(row, titles):
    username = str(row["Leetcodeid"]).strip()
    
    # If username missing → N/A for scraped fields
    if not username:
        return pd.DataFrame([[row["S.no"], row["Roll No"], row["Name"], row["DEPT"],
                               row["Interested Catagory"], row["BATCH"], username] +
                              ["N/A"] * (len(titles) - 7)], columns=titles)

    username, stats = get_leetcode_stats(username)

    # If no data found → N/A for scraped fields
    if not stats or stats["data"]["matchedUser"] is None:
        print(f"⚠ Username '{username}' not found. Filling with N/A.")
        return pd.DataFrame([[row["S.no"], row["Roll No"], row["Name"], row["DEPT"],
                               row["Interested Catagory"], row["BATCH"], username] +
                              ["N/A"] * (len(titles) - 7)], columns=titles)

    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    return pd.DataFrame([[
        row["S.no"], row["Roll No"], row["Name"], row["DEPT"],
        row["Interested Catagory"], row["BATCH"], matched_user["username"],
        matched_user["submitStats"]["acSubmissionNum"][0]["count"],
        matched_user["profile"]["ranking"],
        matched_user["profile"]["reputation"],
        contest_info["rating"] if contest_info else "N/A",
        contest_info["attendedContestsCount"] if contest_info else "N/A",
        contest_info["globalRanking"] if contest_info else "N/A"
    ]], columns=titles)

# Setup column names
titles = [
    "S.no", "Roll No", "Name", "DEPT", "Interested Catagory", "BATCH", "Leetcodeid",
    "Problem Count", "General Ranking", "Reputation",
    "Contest Rating", "Contest Attended", "Global Ranking"
]

# Read input
df_input = pd.read_csv('input.csv')
df_output = pd.DataFrame(columns=titles)

print(f"🚀 Starting LeetCode scraping for {len(df_input)} users...\n")

# Threaded execution
max_threads = 1000  # adjust based on network capacity
with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = [executor.submit(process_user, row, titles) for _, row in df_input.iterrows()]

    for idx, future in enumerate(as_completed(futures), start=1):
        result = future.result()
        df_output = pd.concat([df_output, result], ignore_index=True)
        print(f"[{idx}/{len(futures)}] ✅ Processed")

# Save output
df_output = df_output.sort_values(by='S.no')

df_output.to_csv('output.csv', index=False)
print("\n🎉 Finished! Saved as 'output.csv'")

