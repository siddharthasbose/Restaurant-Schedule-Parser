## README - Restaurant Schedule Processor

### Introduction
This Python module processes restaurant schedules from multiple CSV files and provides functionalities to query restaurant opening hours. The module supports retrieving restaurants open at a specific day and time, getting the schedule for a given list of restaurants, and more.

### Code Structure

1. **Main.py**: This script serves as the main entry point for the entire program. It loads the CSV files, processes the data, and then performs some basic queries for demonstration purposes.
  
2. **Datareader.py**: Responsible for reading the CSV files. This file:
    - Reads data from CSV
    - Validates the data format
    - Uses regular expressions to handle edge cases (like missing commas)
    - Generates a DataFrame with restaurant names and timings

3. **Data_processer.py**: Responsible for processing the data into a structured format. It:
    - Parses the timings from the string format
    - Splits timings based on day and time intervals
    - Handles edge cases like timings that go past midnight

4. **Query_processor.py**: Used for querying the processed data. It supports:
    - Retrieving restaurants open at a given day and/or time
    - Getting opening timings for specific restaurants
    - Generating insights from the restaurant data

5. **Utils.py**: Provides utility functions used across all modules. Contains:
    - A function to extract days from a given string format
    - A function to extract time intervals from a given string format
    - String cleaning utility
    - CSV validation utility

### Important Concepts

#### Regular Expressions (Regex):
Regex is heavily used throughout the codebase to extract and validate data from the CSV files and the strings within them. 

For instance, in **Datareader.py**:
```python
match = re.search(r"(.*?)((?:mon|tue|wed|thu|fri|sat|sun).*?(?:am|pm).*$)", line, re.IGNORECASE)
```
This regex captures restaurant names and their timings. It's designed to capture a pattern starting with days (like Mon, Tue, etc.) and ending with times (like am, pm) to isolate an index for spliting (for handling irregular data)

Similarly, in **Data_processer.py**:
```python
weektimings = re.match(r"(.*?)\s+(?=\d+)(.*)", timing.strip())
```
This regex captures the days and timings from the given input string.

in **utils.py**:
```python
times = re.findall(r'(\d{1,2}(?::\d{2})?\s*[apm]{2})', time_str, re.IGNORECASE)
```
This regex captures timings from the given input string. Handles optional minutes (1 am and 1:00 am)
Will accept 1:00 pa, 10:30 ap and 9 mp  (instead of am/pm)  

### Running the Code

To execute the program:

1. Ensure that all required libraries are installed. The main libraries used are `pandas`, `datetime`, and `logging`.
2. Place your input CSV files in the `input_files` directory.
3. Update the `filenames` list in **Main.py** to point to your CSV files.
4. Run `Main.py`.

### Logging

The codebase uses Python's built-in logging module to log various messages at different severity levels (DEBUG, INFO, ERROR). By default, it's set to display INFO level logs, but you can adjust this to see more detailed debug logs or just critical errors.
