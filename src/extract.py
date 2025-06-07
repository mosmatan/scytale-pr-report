import json
import os
import logging
from src.GitHubClient import GitHubClient

logger = logging.getLogger()

def save_raw_data_to_file(raw_data,org_name, raw_dir_path, repo_name):
    os.makedirs(raw_dir_path, exist_ok=True)

    raw_path = os.path.join(raw_dir_path, f'{org_name}_{repo_name}_merged_prs.json')

    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(raw_data, f, ensure_ascii=False, indent=4)

    logger.info(f'Extracted {len(raw_data)} merged PRs to {raw_path}.')


def fetch_data(fetch_function, description, *args, **kwargs):
    try:
        return fetch_function(*args, **kwargs)
    except Exception as e:
        logger.exception(f'Error fetching {description}: {e}')
        return None

def fetch_config(config: dict):
    github_cfg = config.get('github', {})
    if not github_cfg:
        raise ValueError("GitHub configuration is missing in the provided config.")

    required_keys = ['token', 'api_base_url', 'repository', 'organization']
    for key in required_keys:
        if key not in github_cfg:
            raise ValueError(f"Missing required GitHub configuration key: {key}")

    data_cfg = config.get('data', {})
    if not data_cfg:
        raise ValueError("Data configuration is missing in the provided config.")
    if 'raw_dir_path' not in data_cfg:
        raise ValueError("Missing 'raw_dir_path' in data configuration.")

    return github_cfg, github_cfg['repository'], github_cfg['organization'], data_cfg['raw_dir_path']



def run_extract(config: dict) -> bool:
    try:
        github_cfg, repo_name, org_name, raw_dir_path = fetch_config(config)
    except Exception as e:
        logger.name = f'{__name__}'
        logger.exception(f'Error fetching configuration: {e}')
        return False

    logger.name = f'{__name__}_{org_name}_{repo_name}'
    logger.info(f'Extracting {org_name}/{repo_name}...')

    client = GitHubClient(github_cfg['token'], github_cfg['api_base_url'])

    logger.info(f'fetching merged PRs...')
    merged_prs = fetch_data(client.fetch_merged_prs, "merged PRs", github_cfg['organization'], repo_name)
    if not merged_prs:
        logger.warning(f'No merged PRs found.')
        return False

    logger.info(f'Found {len(merged_prs)} merged PRs.')
    logger.info(f'Fetching reviews')
    reviews = fetch_data(
        lambda: [(pr['number'], client.fetch_approved_reviews(
            organization=org_name,
            repo=repo_name,
            pr_number=pr['number']
        )) for pr in merged_prs],
    "reviews"
    )

    if reviews is None: # with fetch_approved_reviews it can't happen, but if we change it in the future, we should handle this case
        logger.warning('Reviews is None')
        reviews = []
    reviews = {pr_number: review for pr_number, review in reviews}
    logger.info(f'Found {len(reviews)} reviews for merged PRs.')

    logger.info(f'Fetching check runs')
    check_statuses = fetch_data(
        lambda: [(pr['number'], client.fetch_pr_check_runs(
            organization=org_name,
            repo=repo_name,
            merge_commit_sha=pr['merge_commit_sha']
        )) for pr in merged_prs],
     "check runs"
    )

    if check_statuses is None: # with fetch_pr_check_runs it can't happen, but if we change it in the future, we should handle this case
        logger.warning('check_statuses is None')
        check_statuses = []
    check_statuses = {pr_number: checks for pr_number, checks in check_statuses}
    logger.info(f'Found {len(check_statuses)} check runs for merged PRs.')


    raw_data = {
        'last_merged_date': max(merged_prs, key=lambda pr: pr['merged_at'])['merged_at'],
        'first_merged_date': min(merged_prs, key=lambda pr: pr['merged_at'])['merged_at'],
        'merged_prs': merged_prs,
        'reviews': reviews,
        'check_statuses': check_statuses
    }

    logger.info(f'Saving raw data to {raw_dir_path}/{org_name}_{repo_name}_merged_prs.json')
    try:
        save_raw_data_to_file(raw_data,org_name ,raw_dir_path, repo_name)
    except Exception as e:
        logger.exception(f'Error saving raw data: {e}')
        return False

    return True

