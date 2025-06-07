import yaml
from extract import run_extract
from transform import  run_transformation
from logger import  setup_logging
import logging

logger = logging.getLogger(__name__)

def load_config(path : str):
    """Load configuration from settings.yaml."""
    logger.info("Loading configuration from settings.yaml.")
    with open(path, 'r') as ymlfile:
        return yaml.safe_load(ymlfile)

def main():
    setup_logging(name=__name__)

    logger.info("Starting Scytale PR Report...")
    try:
        config = load_config('../config/settings.yaml')
    except FileNotFoundError:
        logger.error("Configuration file settings.yaml not found. Exiting.")
        return

    # extract all merged PRs from GitHub
    succeed_extract = run_extract(config)

    if succeed_extract: # if extraction was successful, run transformation step
        try:
            run_transformation(config)
            logger.info(f"Report for {config['github']['organization']}_{config['github']['repository']} created successfully.")

        except Exception as e:
            logger.exception(f"An error occurred during the transformation step: {e}")
            logger.info(f"Report for {config['github']['organization']}_{config['github']['repository']} not created due to transformation failure.")

    else:
        logger.error("No merged PRs found, skipping transformation step.")
        logger.info(f"Report for {config['github']['organization']}_{config['github']['repository']} not created due to extraction failure.")




if __name__ == "__main__":
    main()