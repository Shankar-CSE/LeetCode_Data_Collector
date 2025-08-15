## LeetCode Stats Scraper
This Python script fetches LeetCode statistics for multiple users in parallel and generates a comprehensive CSV report.

## Features
Fetches LeetCode user statistics using GraphQL API

Processes multiple users concurrently for fast performance

Handles missing or invalid usernames gracefully

Generates a detailed CSV report with user information and stats

Preserves original input data while adding LeetCode metrics

## Data Collected
For each user, the script retrieves:

Basic profile information (username, ranking, reputation)

Problem solving stats:

Easy, Medium, and Hard problems solved

Total problem count

Contest participation:

Number of contests attended

Current rating

Global ranking

## Usage
Prepare an input.csv file with user data including a "Leetcode ID" column

Run the script: python leetcode_scraper.py

Results will be saved to output.csv

## Input CSV Requirements
The input file should contain these columns (at minimum):

Leetcode ID

S.no

RANK

Roll No

Name

DEPT

GENDER

PHONE NUMBER

EMAIL ID

IT/Core/Not Interested

Interested Catagory

BATCH

## Output Columns
The generated CSV will include all input columns plus:

Easy (problems solved)

medium (problems solved)

hard (problems solved)

Problem Count (total solved)

Contest Attended

Contest Rating

Global Ranking

## Configuration
Adjust max_threads to control concurrent requests (default: 1000)

The script handles API errors gracefully and will mark unavailable data as "N/A"

Requirements
Python 3.x

pandas

requests

Install dependencies with:

```bash
pip install pandas requests
```
## Notes
The script may be rate-limited by LeetCode's API if too many requests are made

Invalid usernames will be reported in the console and marked as "N/A" in output

Output is sorted by the original "S.no" column to maintain input order