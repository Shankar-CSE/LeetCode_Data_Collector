import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# Function to fetch LeetCode user statistics using GraphQL API
def get_leetcode_stats(username):
    """
    Retrieves LeetCode user statistics for a given username via GraphQL API.
    
    Args:
        username (str): LeetCode username to query.
    
    Returns:
        tuple: (username, response_data) if successful, (username, None) if failed.
    """
    url = "https://leetcode.com/graphql"
    # GraphQL query to fetch user profile, submission stats, and contest ranking
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
        # Send POST request to LeetCode GraphQL API
        response = requests.post(url, json={"query": query, "variables": variables})
        if response.status_code == 200:
            return username, response.json()
    except Exception:
        # Handle network or API errors gracefully
        pass
    return username, None

# Function to process a single user's data
def process_user(row, titles_output):
    """
    Processes a single user's data, fetching LeetCode stats and formatting output.
    
    Args:
        row (pd.Series): Row from input DataFrame containing user information.
        titles_output (list): List of column names for the output DataFrame.
    
    Returns:
        pd.DataFrame: Single-row DataFrame with user's data or N/A for missing fields.
    """
    username = str(row["LeetCodeid"]).strip()

    # Handle missing or empty username
    if not username:
        return pd.DataFrame(
            [
                [
                    row["S.no"],
                    row["ROLL NO"],
                    row["Name"],
                    row["DEPT"],
                    row["Interested Catagory"],
                    row["BATCH"],
                    username,
                ]
                + ["N/A"] * (len(titles_output) - 7)  # Fill remaining columns with N/A
            ],
            columns=titles_output,
        )

    # Fetch user statistics from LeetCode
    username, stats = get_leetcode_stats(username)

    # Handle case where user data is not found or invalid
    if not stats or stats["data"]["matchedUser"] is None:
        print(f"⚠ Username '{username}' not found. Filling with N/A.")
        user = [row["Name"], row["ROLL NO"], row["DEPT"], row["BATCH"], username]
        invalid_users.append(user)  # Track invalid users
        return pd.DataFrame(
            [
                [
                    row["S.no"],
                    row["ROLL NO"],
                    row["Name"],
                    row["DEPT"],
                    row["Interested Catagory"],
                    row["BATCH"],
                    username,
                ]
                + ["N/A"] * (len(titles_output) - 7)  # Fill remaining columns with N/A
            ],
            columns=titles_output,
        )

    # Extract relevant data from API response
    matched_user = stats["data"]["matchedUser"]
    contest_info = stats["data"]["userContestRanking"]

    # Create DataFrame row with all user data
    return pd.DataFrame(
        [
            [
                row["S.no"],
                row["ROLL NO"],
                row["Name"],
                row["DEPT"],
                row["Interested Catagory"],
                row["BATCH"],
                matched_user["username"],
                matched_user["submitStats"]["acSubmissionNum"][0]["count"],  # Total problems
                matched_user["profile"]["ranking"],  # General ranking
                matched_user["profile"]["reputation"],  # Reputation score
                contest_info["rating"] if contest_info else "N/A",  # Contest rating
                contest_info["attendedContestsCount"] if contest_info else "N/A",  # Contests attended
                contest_info["globalRanking"] if contest_info else "N/A",  # Global contest ranking
                matched_user["submitStats"]["acSubmissionNum"][1]["count"],  # Easy problems
                matched_user["submitStats"]["acSubmissionNum"][2]["count"],  # Medium problems
                matched_user["submitStats"]["acSubmissionNum"][3]["count"],  # Hard problems
            ]
        ],
        columns=titles_output,
    )

# Define column names for output DataFrame
titles_output = [
    "S.no",
    "ROLL NO",
    "Name",
    "DEPT",
    "Interested Catagory",
    "BATCH",
    "Leetcodeid",
    "Problem Count",
    "General Ranking",
    "Reputation",
    "Contest Rating",
    "Contest Attended",
    "Global Ranking",
    "easy",
    "medium",
    "hard",
]

# Define column names for invalid users DataFrame
titles_invalid = ["Name", "ROLL NO", "Dept", "Batch", "username"]

# Initialize list to track invalid users and empty DataFrame for invalid users
invalid_users = []
df_invalid = pd.DataFrame(columns=titles_invalid)

# Read input data from CSV file
df_input = pd.read_csv("input.csv")

# Initialize empty DataFrame for output
df_output = pd.DataFrame(columns=titles_output)

# Log start of scraping process
print(f"🚀 Starting LeetCode scraping for {len(df_input)} users...\n")

# Use ThreadPoolExecutor for concurrent API requests
max_threads = 10  # Adjust based on network capacity and API rate limits
with ThreadPoolExecutor(max_workers=max_threads) as executor:
    # Submit tasks for each user
    futures = [
        executor.submit(process_user, row, titles_output)
        for _, row in df_input.iterrows()
    ]

    # Process completed tasks and collect results
    for idx, future in enumerate(as_completed(futures), start=1):
        result = future.result()
        df_output = pd.concat([df_output, result], ignore_index=True)
        print(f"[{idx}/{len(futures)}] ✅ Processed")

# Sort output DataFrame by S.no
df_output = df_output.sort_values(by="S.no")

# Save output to CSV
df_output.to_csv("output.csv", index=False)
print("\n🎉 Finished! Saved as 'output.csv'")

# Save invalid users to CSV, sorted by department
for user in invalid_users:
    df_invalid.loc[len(df_invalid)] = user

df_invalid = df_invalid.sort_values(by="Dept")
df_invalid.to_csv("invalid_users.csv", index=False)
print("\n🎉 Finished! Saved as 'invalid_users.csv'")