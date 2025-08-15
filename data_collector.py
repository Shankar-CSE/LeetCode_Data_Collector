import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Fetch LeetCode stats
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


# Process single user
def process_user(row, titles_output):
    username = str(row.get("Leetcode ID", "")).strip()

    # If no username, fill N/A
    if not username:
        return pd.DataFrame([[row.get("S.no", "N/A"),
                              row.get("RANK", "N/A"),
                              row.get("Roll No", "N/A"),
                              row.get("Name", "N/A"),
                              row.get("DEPT", "N/A"),
                              row.get("GENDER", "N/A"),
                              row.get("PHONE NUMBER", "N/A"),
                              row.get("EMAIL ID", "N/A"),
                              row.get("IT/Core/Not Interested", "N/A"),
                              row.get("Interested Catagory", "N/A"),
                              username,
                              row.get("BATCH", "N/A"),
                              "N/A",  # medium
                              "N/A",  # hard
                              "N/A",  # problem count
                              "N/A",  # contest attended
                              "N/A",  # contest rating
                              "N/A",   # global ranking
                              "N/A"
                             ]], columns=titles_output)

    username, stats = get_leetcode_stats(username)

    # If not found, fill N/A for stats
    if not stats or stats["data"]["matchedUser"] is None:
        print(f"⚠ Username '{username}' not found. Filling with N/A.")
        return pd.DataFrame([[row.get("S.no", "N/A"),
                              row.get("RANK", "N/A"),
                              row.get("Roll No", "N/A"),
                              row.get("Name", "N/A"),
                              row.get("DEPT", "N/A"),
                              row.get("GENDER", "N/A"),
                              row.get("PHONE NUMBER", "N/A"),
                              row.get("EMAIL ID", "N/A"),
                              row.get("IT/Core/Not Interested", "N/A"),
                              row.get("Interested Catagory", "N/A"),
                              username,
                              row.get("BATCH", "N/A"),
                              "N/A",
                              "N/A",
                              "N/A",
                              "N/A",
                              "N/A",
                              "N/A",
                              "N/A"
                             ]], columns=titles_output)

    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    # Extract stats safely
    easy = matched_user["submitStats"]["acSubmissionNum"][1]["count"]
    medium = matched_user["submitStats"]["acSubmissionNum"][2]["count"]
    hard = matched_user["submitStats"]["acSubmissionNum"][3]["count"]
    total = matched_user["submitStats"]["acSubmissionNum"][0]["count"]

    return pd.DataFrame([[row.get("S.no", "N/A"),
                          row.get("RANK", "N/A"),
                          row.get("Roll No", "N/A"),
                          row.get("Name", "N/A"),
                          row.get("DEPT", "N/A"),
                          row.get("GENDER", "N/A"),
                          row.get("PHONE NUMBER", "N/A"),
                          row.get("EMAIL ID", "N/A"),
                          row.get("IT/Core/Not Interested", "N/A"),
                          row.get("Interested Catagory", "N/A"),
                          matched_user["username"],
                          row.get("BATCH", "N/A"),
                          easy,
                          medium,
                          hard,
                          total,
                          contest_info["attendedContestsCount"] if contest_info else "N/A",
                          contest_info["rating"] if contest_info else "N/A",
                          contest_info["globalRanking"] if contest_info else "N/A"
                         ]], columns=titles_output)


# Output columns in correct order
titles_output = [
    "S.no",
    "RANK",
    "Roll No",
    "Name",
    "DEPT",
    "GENDER",
    "PHONE NUMBER",
    "EMAIL ID",
    "IT/Core/Not Interested",
    "Interested Catagory",
    "Leetcode ID",
    "BATCH",
    "Easy",
    "medium",
    "hard",
    "Problem Count",
    "Contest Attended",
    "Contest Rating",
    "Global Ranking",
]

# Read input CSV
df_input = pd.read_csv("input.csv")
df_output = pd.DataFrame(columns=titles_output)

print(f"🚀 Starting LeetCode scraping for {len(df_input)} users...\n")

max_threads = 1000  # Lower to avoid API bans
with ThreadPoolExecutor(max_workers=max_threads) as executor:
    futures = [executor.submit(process_user, row, titles_output) for _, row in df_input.iterrows()]
    for idx, future in enumerate(as_completed(futures), start=1):
        result = future.result()
        df_output = pd.concat([df_output, result], ignore_index=True)
        print(f"[{idx}/{len(futures)}] ✅ Processed")

df_output = df_output.sort_values(by="S.no")
df_output.to_csv("output.csv", index=False)
print("\n🎉 Finished! Saved as 'output.csv'")
