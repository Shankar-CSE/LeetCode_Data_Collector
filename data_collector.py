import requests
import pandas as pd

def get_leetcode_stats(username):
    url = "https://leetcode.com/graphql"
    
    # GraphQL query string
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
        data = response.json()
        return data
    else:
        raise Exception(f"Query failed with status code {response.status_code}")

# Column titles
titles = ["User Name", "Problem Count", "General Ranking", "Reputation", "Contest Rating", "Contest Attended", "Global Ranking"]

df_output = pd.DataFrame(columns=titles)

# Read input CSV
df_input = pd.read_csv('input.csv')

for username in df_input['Leetcodeid']:
    if username != "":
        stats = get_leetcode_stats(username)
        if "errors" in stats:
            print(f"Error fetching data for {username}: {stats['errors']}")
            continue
        user_name = stats["data"]["matchedUser"]["username"]
        problem_count = stats["data"]["matchedUser"]["submitStats"]["acSubmissionNum"][0]["count"]
        general_ranking = stats["data"]["matchedUser"]["profile"]["ranking"]
        reputation = stats["data"]["matchedUser"]["profile"]["reputation"]

        if stats["data"]["userContestRanking"] is not None:
            contest_rating = stats["data"]["userContestRanking"]["rating"]
            contest_attended = stats["data"]["userContestRanking"]["attendedContestsCount"]
            global_ranking = stats["data"]["userContestRanking"]["globalRanking"]
        else:
            contest_rating = None
            contest_attended = None
            global_ranking = None

        # FIX: use len(df_output) instead of count-based loc to avoid FutureWarning
        df_output.loc[len(df_output)] = [
            user_name, problem_count, general_ranking, reputation,
            contest_rating, contest_attended, global_ranking
        ]

# Save output
df_output.to_csv('output.csv', index=False)
