import argparse
import logging
import sys
import yaml

from logger import setup_logging
from extract import run_extract
from transform import run_transformation
import filters

logger = logging.getLogger(__name__)

def load_config(path : str):
    """Load configuration from settings.yaml."""
    logger.info("Loading configuration from settings.yaml.")
    with open(path, 'r') as ymlfile:
        return yaml.safe_load(ymlfile)

def main():
    # Initialize logging
    setup_logging(name=__name__)

    # --- CLI setup ---
    parser = argparse.ArgumentParser(description="Scytale PR Report")
    parser.add_argument("--config", default="config/settings.yaml",
        help="Path to your settings.yaml"
    )
    # register all filter flags
    filters.add_filter_args(parser)
    args = parser.parse_args()

    logger.info("Starting Scytale PR Report…")

    # load YAML config
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)

    # build filter lists from args
    pr_filters     = filters.build_pr_filters(args)
    review_filters = filters.build_review_filters(args)
    check_filters  = filters.build_check_filters(args)

    # run extraction (applies the filters internally)
    succeeded = run_extract(config, pr_filters, review_filters, check_filters)
    if not succeeded:
        logger.error("Extraction failed or no PRs matched filters. Exiting.")
        sys.exit(1)

    # then run your transformation step
    try:
        run_transformation(config)
        org = config['github']['organization']
        repo = config['github']['repository']
        logger.info(f"Report for {org}/{repo} created successfully.")
    except Exception as e:
        logger.exception(f"Transformation step failed: {e}")
        sys.exit(1)



if __name__ == "__main__":
    main()