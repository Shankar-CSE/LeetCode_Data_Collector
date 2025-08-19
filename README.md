## LeetCode Data Collector
This Python script fetches LeetCode statistics for multiple users in parallel and generates a comprehensive CSV report with student information and their coding performance metrics.

## Features
- Fetches LeetCode user statistics using GraphQL API
- Processes multiple users concurrently for fast performance (up to 1000 threads)
- Handles missing or invalid usernames gracefully
- Generates a detailed CSV report preserving original student data
- Adds LeetCode metrics to existing student records
- Progress tracking with real-time console updates

## Data Collected
For each user, the script retrieves:

**Problem Solving Statistics:**
- Easy problems solved
- Medium problems solved  
- Hard problems solved
- Total problems solved

**Contest Performance:**
- Number of contests attended
- Current contest rating
- Global ranking

## Usage
1. Prepare an `input.csv` file with student data including a "Leetcode ID" column
2. Run the script: `python data_collector.py`
3. Results will be saved to `output.csv`

## Input CSV Requirements
The input file must contain these columns:
- S.no
- RANK
- Roll No
- Name
- DEPT
- GENDER
- PHONE NUMBER
- EMAIL ID
- IT/Core/Not Interested
- Interested Catagory
- Leetcode ID
- BATCH

## Output Format
The generated CSV includes all input columns plus LeetCode metrics:
- Easy (problems solved)
- medium (problems solved)
- hard (problems solved)
- Problem Count (total solved)
- Contest Attended
- Contest Rating
- Global Ranking

## Configuration
- `max_threads`: Controls concurrent requests (default: 1000)
- Invalid usernames are marked as "N/A" in output
- Output is sorted by "S.no" to maintain original order

## Requirements
```bash
pip install pandas requests
```

## Error Handling
- Gracefully handles API errors and timeouts
- Missing usernames are filled with "N/A"
- Invalid usernames are reported in console with warning messages
- Network issues are handled without crashing the script

## Performance
- Uses ThreadPoolExecutor for concurrent processing
- Progress tracking shows completion status
- Optimized for large datasets with hundreds of users