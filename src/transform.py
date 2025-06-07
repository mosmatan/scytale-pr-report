import json
import logging
import os
import pandas as pd

logger = logging.getLogger()
def load_raw_prs(raw_path):
    with open(raw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get('merged_prs', []), data.get('reviews', {}), data.get('check_statuses', {})


def process_pr(pr, reviews, check_statuses):
    entry = {
        'pr_number': pr['number'],
        'pr_title': pr.get('title'),
        'author': pr.get('user', {}).get('login'),
        'merge_date': pr.get('merged_at'),
        'cr_passed': bool(reviews),
        'checks_passed': bool(check_statuses)
    }

    return entry


def save_processed_prs(processed_prs, processed_dir_path,org_name, repo_name):
    os.makedirs(processed_dir_path, exist_ok=True)
    with open(f"{processed_dir_path}/{org_name}_{repo_name}_merged_prs.json", 'w', encoding='utf-8') as f:
        json.dump(processed_prs, f, ensure_ascii=False, indent=4)


def save_report(processed_prs, report_dir_path,org_name, repo_name):
    os.makedirs(report_dir_path, exist_ok=True)
    df = pd.DataFrame.from_records(processed_prs).rename(columns={
        'pr_number': 'PR number',
        'pr_title': 'PR title',
        'author': 'Author',
        'merge_date': 'Merge date',
        'cr_passed': 'CR_Passed',
        'checks_passed': 'CHECKS_PASSED',
    })
    df.to_csv(f"{report_dir_path}/{org_name}_{repo_name}_report.csv", index=False)


def print_processed_prs(processed_prs):
    for p in processed_prs:
        print(
            f"PR #{p['pr_number']:<4} | title={p['pr_title']} | CR Passed={'✔' if p['cr_passed'] else '✘'} | Checks Passed={'✔' if p['checks_passed'] else '✘'}"
        )


def run_transformation(config: dict):
    github_cfg = config['github']
    repo_name = github_cfg['repository']
    org_name = github_cfg['organization']

    logger.name = f'{__name__}_{org_name}_{repo_name}'
    logger.info(f"Transforming data...")
    raw_path = f"{config['data']['raw_dir_path']}/{org_name}_{repo_name}_merged_prs.json"

    try:
        raw_prs, reviews, check_statuses  = load_raw_prs(raw_path)
    except FileNotFoundError:
        logger.exception(f"Raw data file {raw_path} not found. Please run the extraction step first. exeption: {e}")
        return

    logger.info(f'Processing {repo_name} merged PRs')

    try:
        processed_prs = [process_pr(pr, reviews[str(pr['number'])], check_statuses[str(pr['number'])]) for pr in raw_prs]
    except KeyError as e:
        logger.exception(f"Missing data for PR number {e}. Please check the raw data file.")
        return
    except Exception as e:
        logger.exception(f"An error occurred during processing: {e}")
        return

    logger.info(f'saving processed data...')
    try:
        save_processed_prs(processed_prs, config['data']['processed_dir_path'],org_name, repo_name)
        save_report(processed_prs, config['output']['report_dir_path'],org_name, repo_name)
    except Exception as e:
        logger.exception(f"An error occurred while saving processed data: {e}")
        return

    logger.info(f"Transformation completed for {org_name}/{repo_name}.")