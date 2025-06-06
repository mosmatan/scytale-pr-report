import json
import os
import pandas as pd

from src.GitHubClient import GitHubClient


def run_transformation(config : dict):
    github_cfg = config['github']
    repo_name = github_cfg['repository']

    raw_dir_path = config['data']['raw_dir_path']
    processed_dir_path = config['data']['processed_dir_path']
    report_dir_path = config['output']['report_dir_path']

    raw_path = f'{raw_dir_path}/{repo_name}_merged_prs.json'
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_prs = json.load(f)

    print(f'Processing {repo_name} merged PRs')

    # Initialize GitHubClient once
    github_client = GitHubClient(
        token=github_cfg['token'],
        base_url=github_cfg['api_base_url']
    )

    processed_prs = []

    for pr in raw_prs:
        pr_number = pr['number']
        merge_commit_sha = pr.get('merge_commit_sha')  # assume every PR dict has this

        # Build a “template” dict for this PR:
        entry = {
            'pr_number': pr_number,
            'pr_title': pr.get('title'),
            'author': pr.get('user', {}).get('login'),
            'merge_date': pr.get('merged_at'),
            'cr_passed': False,  # will update below
            'checks_passed': False,  # will update below
        }

        # Check for at least one approved review
        approved_reviews = github_client.fetch_approved_reviews(
            organization=github_cfg['organization'],
            repo=repo_name,
            pr_number=pr_number
        )
        if approved_reviews:
            entry['cr_passed'] = True

        # Fetch the check‐runs for the merge commit
        if merge_commit_sha:
            checks = github_client.fetch_pr_check_runs(
                organization=github_cfg['organization'],
                repo=repo_name,
                merge_commit_sha=merge_commit_sha
            )
            if checks:
                # All checks must have conclusion == 'success'
                all_success = all(check.get('conclusion') == 'success' for check in checks)
                entry['checks_passed'] = all_success

        processed_prs.append(entry)

    # Example: print a summary
    for p in processed_prs:
        print(
            f"PR #{p['pr_number']:<4} | title={ p['pr_title'] } | CR Passed={'✔' if p['cr_passed'] else '✘'} | Checks Passed={'✔' if p['checks_passed'] else '✘'}")

    os.makedirs(processed_dir_path, exist_ok=True)
    processed_path = os.path.join(processed_dir_path, f'{github_cfg["repository"]}_merged_prs.json')
    with open(processed_path, 'w', encoding='utf-8') as f:
        json.dump(processed_prs, f, ensure_ascii=False, indent=4)

    os.makedirs(report_dir_path, exist_ok=True)
    report_path = os.path.join(report_dir_path, f'{github_cfg["repository"]}_report.csv')
    df = pd.DataFrame.from_records(processed_prs)
    df.rename(columns={
        'pr_number': 'PR number',
        'pr_title' : 'PR title',
        'author' : 'Author',
        'merge_date' : 'Merge date',
        'cr_passed' : 'CR_Passed',
        'checks_passed' : 'CHECKS_PASSED',
    }, inplace=True)
    df.to_csv(report_path, index=False)




