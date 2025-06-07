import yaml
from extract import run_extract
from transform import  run_transformation

from src.GitHubClient import GitHubClient


def load_config():
    with open('../config/settings.yaml', 'r') as ymlfile:
        return yaml.safe_load(ymlfile)

def main():
    config = load_config()

    succeed_extract = run_extract(config)

    if succeed_extract:
        run_transformation(config)
    else:
        print("No merged PRs found, skipping transformation step.")

    print("Done")


if __name__ == "__main__":
    main()