import json
import os
from src.GitHubClient import GitHubClient


def save_raw_data_to_file(raw_data,org_name, raw_dir_path, repo_name):
    os.makedirs(raw_dir_path, exist_ok=True)

    raw_path = os.path.join(raw_dir_path, f'{org_name}_{repo_name}_merged_prs.json')

    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)

    print(f'Extracted {len(raw_data)} merged PRs to {raw_path}.')


def fetch_data(fetch_function, description, *args, **kwargs):
    try:
        return fetch_function(*args, **kwargs)
    except Exception as e:
        print(f'Error fetching {description}: {e}')
        return None



def run_extract(config: dict) -> bool:
    github_cfg = config['github']
    raw_dir_path = config['data']['raw_dir_path']
    repo_name = github_cfg['repository']
    org_name = github_cfg['organization']

    print(f'Extracting {org_name}/{repo_name}...')

    client = GitHubClient(github_cfg['token'], github_cfg['api_base_url'])

    merged_prs = fetch_data(client.fetch_merged_prs, "merged PRs", github_cfg['organization'], repo_name)
    if not merged_prs:
        print(f'No merged PRs found in {org_name}/{repo_name}.')
        return False

    print(f'Found {len(merged_prs)} merged PRs in {org_name}/{repo_name}.')

    reviews = fetch_data(
        lambda: [(pr['number'], client.fetch_approved_reviews(
            organization=github_cfg['organization'],
            repo=repo_name,
            pr_number=pr['number']
        )) for pr in merged_prs],
    "reviews"
    )

    if reviews is None:
        return False
    reviews = {pr_number: review for pr_number, review in reviews}

    check_statuses = fetch_data(
        lambda: [(pr['number'], client.fetch_pr_check_runs(
            organization=github_cfg['organization'],
            repo=repo_name,
            merge_commit_sha=pr['merge_commit_sha']
        )) for pr in merged_prs],
     "check runs"
    )

    if check_statuses is None:
        return False
    check_statuses = {pr_number: checks for pr_number, checks in check_statuses}

    raw_data = {
        'last_merged_date': max(merged_prs, key=lambda pr: pr['merged_at'])['merged_at'],
        'first_merged_date': min(merged_prs, key=lambda pr: pr['merged_at'])['merged_at'],
        'merged_prs': merged_prs,
        'reviews': reviews,
        'check_statuses': check_statuses
    }
    save_raw_data_to_file(raw_data,org_name ,raw_dir_path, repo_name)

    return True

