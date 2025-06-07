

import json
import os
import logging
from dataclasses import dataclass

import pandas as pd

# Constants
MERGED_PRS_KEY = 'merged_prs'
REVIEWS_KEY = 'reviews'
CHECK_STATUSES_KEY = 'check_statuses'

PROCESSED_FILENAME_TEMPLATE = "{org}_{repo}_merged_prs.json"
REPORT_FILENAME_TEMPLATE = "{org}_{repo}_report.csv"

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class TransformConfig:
    """
    Configuration for the transformation process.
    """
    token: str
    api_base_url: str
    repository: str
    organization: str
    raw_dir_path: str
    processed_dir_path: str
    report_dir_path: str


def fetch_config(config):
    """
    Parses and validates the configuration dictionary.

    Raises:
        ValueError: if any required configuration is missing.
    """
    github_cfg = config.get('github')
    if not github_cfg:
        raise ValueError("Missing 'github' section in configuration.")

    for key in ('token', 'api_base_url', 'repository', 'organization'):
        if key not in github_cfg:
            raise ValueError(f"Missing GitHub config key: '{key}'")

    data_cfg = config.get('data')
    if not data_cfg:
        raise ValueError("Missing 'data' section in configuration.")
    if 'raw_dir_path' not in data_cfg:
        raise ValueError("Missing 'data.raw_dir_path' in configuration.")
    if 'processed_dir_path' not in data_cfg:
        raise ValueError("Missing 'data.processed_dir_path' in configuration.")

    output_cfg = config.get('output')
    if not output_cfg or 'report_dir_path' not in output_cfg:
        raise ValueError("Missing 'output.report_dir_path' in configuration.")

    return TransformConfig(
        token=github_cfg['token'],
        api_base_url=github_cfg['api_base_url'],
        repository=github_cfg['repository'],
        organization=github_cfg['organization'],
        raw_dir_path=data_cfg['raw_dir_path'],
        processed_dir_path=data_cfg['processed_dir_path'],
        report_dir_path=output_cfg['report_dir_path'],
    )


def load_raw_prs(raw_path):
    """
    Loads raw PR data from a JSON file.

    Returns:
        merged_prs: list of PR dictionaries
        reviews: mapping of PR number (as str) to list of review dicts
        check_statuses: mapping of PR number (as str) to list of check-status dicts
    """
    logger.debug(f"Loading raw PR data from {raw_path}")
    with open(raw_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    merged_prs = payload.get(MERGED_PRS_KEY, [])
    reviews = payload.get(REVIEWS_KEY, {})
    check_statuses = payload.get(CHECK_STATUSES_KEY, {})

    return merged_prs, reviews, check_statuses


def process_pr(pr, reviews, checks):
    """
    Transforms a single PR record into a flat dictionary for reporting.
    """
    pr_number = pr.get('number')

    # Code review passed if any review has state 'APPROVED'
    cr_passed = any(r.get('state') == 'APPROVED' for r in reviews)

    # Checks passed only if at least one completed check exists and all succeed
    completed_checks = [c for c in checks if c.get('status') == 'completed']
    checks_passed = bool(completed_checks) and all(c.get('conclusion') == 'success' for c in completed_checks)

    result = {
        'pr_number': pr_number,
        'pr_title': pr.get('title'),
        'author': pr.get('user', {}).get('login'),
        'merge_date': pr.get('merged_at'),
        'cr_passed': cr_passed,
        'checks_passed': checks_passed,
    }
    logger.debug(f"Processed PR data: {result}")
    return result


def save_processed_prs(processed, cfg: TransformConfig):

    try:
        os.makedirs(cfg.processed_dir_path, exist_ok=True)
        filename = PROCESSED_FILENAME_TEMPLATE.format(org=cfg.organization, repo=cfg.repository)
        path = os.path.join(cfg.processed_dir_path, filename)

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(processed, f, ensure_ascii=False, indent=4)

        logger.info(f"Saved processed PRs to {path}")
    except Exception:
        logger.exception(f"Failed to save processed PRs to {cfg.processed_dir_path}")
        raise


def save_report(processed_data, cfg: TransformConfig):

    try:
        os.makedirs(cfg.report_dir_path, exist_ok=True)
        df = pd.DataFrame.from_records(processed_data).rename(columns={
            'pr_number': 'PR number',
            'pr_title': 'PR title',
            'author': 'Author',
            'merge_date': 'Merge date',
            'cr_passed': 'CR_Passed',
            'checks_passed': 'CHECKS_PASSED',
        })

        filename = REPORT_FILENAME_TEMPLATE.format(org=cfg.organization, repo=cfg.repository)
        path = os.path.join(cfg.report_dir_path, filename)
        df.to_csv(path, index=False)

        logger.info(f"Saved report to {path}")
    except Exception:
        logger.exception(f"Failed to save report to {cfg.report_dir_path}")
        raise


def run_transformation(config_dict) -> None:
    """
    The transformation pipeline:
      1. Validates configuration
      2. Loads raw PR data
      3. Processes each PR
      4. Saves JSON and CSV outputs

    Raises:
        ValueError: if configuration is invalid
        KeyError: if any PR is missing required data
        Exception: for any other errors during processing

    """
    cfg = fetch_config(config_dict)
    logger.name = f'{__name__}_{cfg.organization}_{cfg.repository}'
    logger.info(f"Starting transformation")

    try:
        # Build raw data file path
        raw_filename = PROCESSED_FILENAME_TEMPLATE.format(org=cfg.organization, repo=cfg.repository)
        raw_path = os.path.join(cfg.raw_dir_path, raw_filename)

        # Load raw data
        merged_prs, reviews_map, checks_map = load_raw_prs(raw_path)

        if len(merged_prs) == 0:
            logger.warning(f"No merged PRs found. Skipping transformation")
            return

        # Process PRs
        processed_prs = []
        for pr in merged_prs:
            pr_key = str(pr.get('number'))
            if pr_key not in reviews_map or pr_key not in checks_map:
                raise KeyError(f"Missing data for PR number {pr_key}")
            processed_prs.append(process_pr(pr, reviews_map[pr_key], checks_map[pr_key]))

        # Save outputs
        save_processed_prs(processed_prs, cfg)
        save_report(processed_prs, cfg)

        logger.info(f"Transformation completed")

    except Exception as e:
        logger.exception(f"Transformation failed: {e}")
        raise
