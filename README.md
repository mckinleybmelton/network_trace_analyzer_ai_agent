# network_trace_analyzer_ai_agent
The network trace analyzer AI Agent deploys on edge and automatically triggers when a har file or log file is downloaded form an external source. It scans the files for safety, and then parses them and runs real time analysis on the files to help with tracking specific issues. 

# Setup

1. Clone the repository
2. Open the repository and create a Constants.py file in the root of the project
3. Add the following code to your constants.py file and update the "PATH ROOT" to the location you cloned the repo to:
```
class Constants:
    WATCH_DIR = r"<PATH ROOT>\Downloads"
    PROCESS_DIR = r"<PATH ROOT>\network_trace_analyzer_ai_agent\run_output"
```
