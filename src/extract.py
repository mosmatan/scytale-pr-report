import json
import os
import logging
from dataclasses import dataclass

from tqdm import tqdm

from GitHubClient import GitHubClient

logger = logging.getLogger(__name__)

# File name template for raw data output
RAW_FILENAME_TEMPLATE = "{org}_{repo}_merged_prs.json"

@dataclass(frozen=True)
class ExtractConfig:
    """
    Configuration for the extraction process.
    """
    token: str
    api_base_url: str
    repository: str
    organization: str
    raw_dir_path: str


def fetch_config(config) -> ExtractConfig:
    """
    Parses and validates the configuration dictionary for extraction.

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
    if not data_cfg or 'raw_dir_path' not in data_cfg:
        raise ValueError("Missing 'data.raw_dir_path' in configuration.")

    return ExtractConfig(
        token=github_cfg['token'],
        api_base_url=github_cfg['api_base_url'],
        repository=github_cfg['repository'],
        organization=github_cfg['organization'],
        raw_dir_path=data_cfg['raw_dir_path'],
    )


def fetch_data(fetch_fn, description: str, *args, **kwargs):
    """
    Wrapper to call a fetch function and log any exceptions.

    Returns:
        The result of fetch_fn.
    """
    try:
        return fetch_fn(*args, **kwargs)
    except Exception:
        logger.exception(f"Error fetching {description}.")
        raise


def save_raw_data(raw_payload, cfg):
    """
    Saves the raw data payload as JSON in the configured directory.

    Raises:
        IOError: if file write fails.
    """
    os.makedirs(cfg.raw_dir_path, exist_ok=True)
    filename = RAW_FILENAME_TEMPLATE.format(org=cfg.organization, repo=cfg.repository)
    path = os.path.join(cfg.raw_dir_path, filename)

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(raw_payload, f, ensure_ascii=False, indent=4)
    logger.info(f"Saved raw data to {path}")


def run_extract(config) -> bool:
    """
    the extraction pipeline:
      1. Validates configuration
      2. Fetches merged PRs
      3. Fetches reviews
      4. Fetches check runs
      5. Compiles and saves raw JSON

    Returns:
        True if successful, False otherwise.
    """
    # 1. Validate configuration
    try:
        cfg = fetch_config(config)
        logger.name = f"{__name__}_{cfg.organization}_{cfg.repository}"
        logger.info(f"Configuration validated for {cfg.organization}/{cfg.repository}")
    except Exception:
        logger.exception("Failed to validate configuration.")
        return False

    # Initialize GitHub client
    client = GitHubClient(cfg.token, cfg.api_base_url)
    logger.info(f"Initialized GitHubClient for {cfg.api_base_url}")

    # 2. Fetch merged PRs
    try:
        merged_prs = fetch_data(client.fetch_merged_prs,"merged PRs",cfg.organization,cfg.repository) or []

        if not merged_prs:
            logger.warning("No merged PRs found. Stopping extraction.")
            return False

        logger.info(f"Fetched {len(merged_prs)} merged PRs.")

    except Exception:
        # fetch_data logs the exception
        return False

    # 3. Fetch reviews
    try:
        reviews_list = []
        for pr in tqdm(merged_prs, desc="Fetching PR reviews", unit="PR"):
            num = pr['number']
            revs = (
                    fetch_data(client.fetch_approved_reviews,f"reviews for PR {num}",cfg.organization,cfg.repository,num)
                    or [])
            reviews_list.append((num, revs))

        reviews = {num: revs for num, revs in reviews_list}
        logger.info(f"Fetched reviews for {len(reviews)} PRs.")
    except Exception:
        # fetch_data logs the exception
        return False

    # 4. Fetch check runs
    try:
        checks_list = []
        for pr in tqdm(merged_prs, desc="Fetching check runs", unit="PR"):
            num = pr['number']
            checks = (
                fetch_data(client.fetch_pr_check_runs, f"check runs for PR {num}", cfg.organization, cfg.repository, pr['merge_commit_sha'])
                or [])
            checks_list.append((num, checks))

        check_statuses = {num: checks for num, checks in checks_list}
        logger.info(f"Fetched check runs for {len(check_statuses)} PRs.")
    except Exception:
        # fetch_data logs the exception
        return False

    # 5. Compile payload and save
    raw_payload = {
        'last_merged_date': max(merged_prs, key=lambda pr: pr['merged_at'])['merged_at'],
        'first_merged_date': min(merged_prs, key=lambda pr: pr['merged_at'])['merged_at'],
        'merged_prs': merged_prs,
        'reviews': reviews,
        'check_statuses': check_statuses,
    }
    try:
        save_raw_data(raw_payload, cfg)

    except Exception:
        logger.exception("Error saving raw data.")
        return False

    logger.info(f"Extraction completed successfully for {cfg.organization}/{cfg.repository}")
    return True
