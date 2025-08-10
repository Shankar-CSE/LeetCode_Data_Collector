# 📊 LeetCode Data Scraper

A Python-based tool to fetch and compile **LeetCode user statistics** into a CSV file.  
This script reads an input CSV with user details and fetches problem count, ranking, reputation, contest stats, and more from LeetCode's API.

---

## 🚀 Features
- Reads input file with user details (S.no, Roll No, Name, DEPT, Interested Category, BATCH, Leetcodeid)
- Fetches:
  - Problem Count
  - General Ranking
  - Reputation
  - Contest Rating
  - Contest Attended
  - Global Ranking
- Handles missing usernames by marking stats as `N/A`
- Saves results into a CSV file

---

## 📂 Input CSV Format
| S.no | Roll No | Name | DEPT | Interested Catagory | BATCH | Leetcodeid |
|------|---------|------|------|---------------------|-------|------------|
| 1    | 12345   | John | CSE  | DSA                 | 2023  | john123    |
| 2    | 12346   | Jane | IT   | CP                  | 2023  | jane_coder |

---

## 🛠 Installation
1. Clone the repository or download the script.
2. Install required dependencies:
   ```bash
   pip install pandas requests


##Usage
Place your input CSV file in the script's folder.

Update the file path in the script:

  ```
input_file = "input.csv"
output_file = "output.csv"
```
Run the script:

```
cd LeetCode_Data_Collector
python data_collector.py
```


| S.no | Roll No | Name | DEPT | Interested Catagory | BATCH | Leetcodeid | Problem Count | General Ranking | Reputation | Contest Rating | Contest Attended | Global Ranking |
| ---- | ------- | ---- | ---- | ------------------- | ----- | ---------- | ------------- | --------------- | ---------- | -------------- | ---------------- | -------------- |


 
## Notes
If Leetcodeid is empty, script will skip fetching and fill stats with N/A.

For large datasets, execution time can be high because of multiple API calls.

You can improve performance by:

Using asynchronous requests

Running multiple threads

Caching API responses

## Real-World Uses
Academic performance tracking for coding contests

Batch coding skill analysis

Generating student performance reports

Preparing leaderboards for hackathons

## License
This project is open-source under the MIT License.
