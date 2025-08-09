import requests

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
print(stats)
