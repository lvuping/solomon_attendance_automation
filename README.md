# Solomon Attendance Automation

<Optional: A brief introduction about the project>

## Prerequisites

### GET API and USER ID

### Poetry Installation

This project uses Poetry for dependency management. If you haven't installed Poetry yet, you can do so by following these instructions:

#### macOS / Linux / BashOnWindows

```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Windows PowerShell
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
For detailed instructions, refer to the official Poetry documentation.

## How to Use

| Step | Description                     | Example                                 |
|------|---------------------------------|-----------------------------------------|
| 1    | Clone the repository            | `git clone <repository_url>`            |
| 2    | Install dependencies            | `poetry install`                        |
| 3    | Set up .env file                | Check [Setup Guide](#setup-guide) below |
| 4    | Run the script                  | `python main.py` (default = 15days)     |
| 5    | Run the script with custom days | `python main.py --daysago 2` (Two days) |

### Setup Guide

1. Create a `.env` file in the project root.
2. Add the following variables:
    - USER_ID=your_user_id
    - API_KEY=your_api_key

3. Save the file and you're good to go!

Remember to replace `your_user_id` and `your_api_key` with your actual credentials.
