import yaml
from extract import run_extract
from transform import  run_transformation
from logger import  setup_logging
import logging

logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from settings.yaml."""
    logger.info("Loading configuration from settings.yaml.")
    with open('../config/settings.yaml', 'r') as ymlfile:
        return yaml.safe_load(ymlfile)

def main():
    setup_logging(name=__name__)
    config = load_config()

    succeed_extract = run_extract(config)

    if succeed_extract:
        run_transformation(config)
    else:
        print("No merged PRs found, skipping transformation step.")

    print("Done")


if __name__ == "__main__":
    main()