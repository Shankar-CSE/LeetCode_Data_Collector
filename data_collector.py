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

# Example usage
username = "LeetCode"  # change this to the user's ID
stats = get_leetcode_stats(username)
# print(stats)
user_name = ''
problem_count =''
General_Ranking = ''
Reputation = ''
Contest_rating = ''
Contest_attended =''
Global_Ranking = ''
 
stats = get_leetcode_stats(username)
    
user_name = stats["data"]["matchedUser"]["username"]

problem_count = stats["data"]["matchedUser"]["submitStats"]["acSubmissionNum"][0]["count"]

General_Ranking = stats["data"]["matchedUser"]["profile"]["ranking"]

Reputation = stats["data"]["matchedUser"]["profile"]["reputation"]
    
if stats["data"]["userContestRanking"] is not None:
    Contest_rating = stats["data"]["userContestRanking"]["rating"]

    Contest_attended = stats["data"]["userContestRanking"]["attendedContestsCount"]

    Global_Ranking = stats["data"]["userContestRanking"]["globalRanking"]

data = [user_name, problem_count, General_Ranking, Reputation, Contest_rating, Contest_attended, Global_Ranking]

titles = ['user_name', 'problem_count', 'General_Ranking', 'Reputation', 'Contest_rating', 'Contest_attended', 'Global_Ranking']

df = pd.DataFrame([data], columns=titles)

df.to_csv('LeetCode_Data.csv', index=False)

print(df)