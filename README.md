Scytale PR Report

Requirements:

* Python 3.8 or newer

Setup Instructions:

If using python3 write "python3" insted of "python"

1. Clone the repository and enter the directory:

   ```bash
   git clone https://github.com/mosmatan/scytale-pr-report.git
   cd scytale-pr-report/src
   ```

2. (Optional) Create and activate a virtual environment:

   **macOS/Linux:**

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

   **Windows (CMD):**

   ```batch
   python -m venv venv
   venv\Scripts\activate.bat
   ```

   **Windows (PowerShell):**

   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure your GitHub token:

   You can provide `GITHUB_TOKEN` via a `.env` file or environment variable.

   **.env file (project root):**

   ```ini
   GITHUB_TOKEN=your_personal_access_token
   ```

   **macOS/Linux:**

   ```bash
   export GITHUB_TOKEN=your_personal_access_token
   ```

   **Windows (CMD):**

   ```batch
   set GITHUB_TOKEN=your_personal_access_token
   ```

   **Windows (PowerShell):**

   ```powershell
   $Env:GITHUB_TOKEN = "your_personal_access_token"
   ```

5. Edit the configuration file:

   Open `config/settings.yaml` and update:

   ```yaml
   github:
     organization: your_org
     repository: your_repo
     api_base_url: https://api.github.com

   data:
     raw_dir_path: data/raw
     processed_dir_path: data/processed

   output:
     report_dir_path: output/reports
   ```

6. Run the full pipeline:

   ```bash
   python main.py [OPTIONS]
   ```

   Available Filter Options:

   ```
   --merged-since N           Only include PRs merged in the last N days
   --only-authors USER [..]   Only include PRs authored by these usernames
   --reviewers USER [..]      Only include reviews by these usernames
   --recent-reviews N         Only include reviews submitted in the last N days
   --check-names NAME [..]    Only include check runs with these names
   --pass-only                Only include only passing check runs
   ```

   For detailed help on flags:

   ```bash
   python main.py --help
   ```

Examples:

* Extract and transform all PRs:

  ```bash
  python main.py
  ```

* Only include PRs merged in the last 7 days by author "alice":

  ```bash
  python main.py --merged-since 7 --only-authors alice
  ```

* Only include only passing check runs and reviews by "bob":

  ```bash
  python main.py --pass-only --reviewers bob
  ```

Outputs:

* **Raw data JSON:** `data/raw/{org}_{repo}_merged_prs.json`
* **Processed data JSON:** `data/processed/{org}_{repo}_processed_prs.json`
* **CSV report:** `output/reports/{org}_{repo}_report.csv`

Enjoy using Scytale PR Report!
