import json
import os
import pandas as pd
from src.GitHubClient import GitHubClient


def load_raw_prs(raw_path):
    with open(raw_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def process_pr(pr, github_client, github_cfg, repo_name):
    entry = {
        'pr_number': pr['number'],
        'pr_title': pr.get('title'),
        'author': pr.get('user', {}).get('login'),
        'merge_date': pr.get('merged_at'),
        'cr_passed': bool(github_client.fetch_approved_reviews(
            organization=github_cfg['organization'],
            repo=repo_name,
            pr_number=pr['number']
        )),
        'checks_passed': False
    }

    # Handle the checks_passed logic
    # Fetch checks for the PR using the merge commit SHA
    merge_commit_sha = pr.get('merge_commit_sha')
    if merge_commit_sha:
        checks = github_client.fetch_pr_check_runs(
            organization=github_cfg['organization'],
            repo=repo_name,
            merge_commit_sha=merge_commit_sha
        )
        entry['checks_passed'] = all(check.get('conclusion') == 'success' for check in checks) if checks else False

    return entry


def save_processed_prs(processed_prs, processed_dir_path, repo_name):
    os.makedirs(processed_dir_path, exist_ok=True)
    with open(f"{processed_dir_path}/{repo_name}_merged_prs.json", 'w', encoding='utf-8') as f:
        json.dump(processed_prs, f, ensure_ascii=False, indent=4)


def save_report(processed_prs, report_dir_path, repo_name):
    os.makedirs(report_dir_path, exist_ok=True)
    df = pd.DataFrame.from_records(processed_prs).rename(columns={
        'pr_number': 'PR number',
        'pr_title': 'PR title',
        'author': 'Author',
        'merge_date': 'Merge date',
        'cr_passed': 'CR_Passed',
        'checks_passed': 'CHECKS_PASSED',
    })
    df.to_csv(f"{report_dir_path}/{repo_name}_report.csv", index=False)


def print_processed_prs(processed_prs):
    for p in processed_prs:
        print(
            f"PR #{p['pr_number']:<4} | title={p['pr_title']} | CR Passed={'✔' if p['cr_passed'] else '✘'} | Checks Passed={'✔' if p['checks_passed'] else '✘'}"
        )


def run_transformation(config: dict):
    github_cfg = config['github']
    repo_name = github_cfg['repository']

    raw_path = f"{config['data']['raw_dir_path']}/{repo_name}_merged_prs.json"
    raw_prs = load_raw_prs(raw_path)

    print(f'Processing {repo_name} merged PRs')

    github_client = GitHubClient(
        token=github_cfg['token'],
        base_url=github_cfg['api_base_url']
    )

    processed_prs = [process_pr(pr, github_client, github_cfg, repo_name) for pr in raw_prs]

    print_processed_prs(processed_prs)
    save_processed_prs(processed_prs, config['data']['processed_dir_path'], repo_name)
    save_report(processed_prs, config['output']['report_dir_path'], repo_name)