import requests
import pandas as pd

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
        return response.json()
    else:
        raise Exception(f"Query failed with status code {response.status_code}")

# Column titles
titles = [
    "User Name", "Problem Count", "General Ranking", "Reputation",
    "Contest Rating", "Contest Attended", "Global Ranking"
]

# Empty DataFrame
df_output = pd.DataFrame(columns=titles)

# Read input CSV
df_input = pd.read_csv('input.csv')

total_users = len(df_input['Leetcodeid'])
processed_count = 0

print(f"🔍 Starting LeetCode scraping for {total_users} users...\n")

for username in df_input['Leetcodeid']:
    processed_count += 1
    username = str(username).strip()

    if not username:
        print(f"[{processed_count}/{total_users}] ⏭ Skipped empty username.")
        continue

    print(f"[{processed_count}/{total_users}] ⏳ Fetching data for: {username}...")
    stats = get_leetcode_stats(username)

    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    if matched_user is None:
        print(f"[{processed_count}/{total_users}] ⚠ Username '{username}' not found. Skipping...")
        continue

    user_name = matched_user["username"]
    problem_count = matched_user["submitStats"]["acSubmissionNum"][0]["count"]
    general_ranking = matched_user["profile"]["ranking"]
    reputation = matched_user["profile"]["reputation"]

    if contest_info is not None:
        contest_rating = contest_info["rating"]
        contest_attended = contest_info["attendedContestsCount"]
        global_ranking = contest_info["globalRanking"]
    else:
        contest_rating = None
        contest_attended = None
        global_ranking = None

    new_row = pd.DataFrame([[
        user_name, problem_count, general_ranking, reputation,
        contest_rating, contest_attended, global_ranking
    ]], columns=titles)

    df_output = pd.concat([df_output, new_row], ignore_index=True)

    print(f"[{processed_count}/{total_users}] ✅ Data fetched for: {username}")

# Save output CSV
df_output.to_csv('output.csv', index=False)
print("\n🎉 All done! Data saved as 'output.csv'")
