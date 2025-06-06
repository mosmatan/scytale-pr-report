import yaml
from extract import run_extract
from transform import  run_transformation

from src.GitHubClient import GitHubClient


def load_config():
    with open('../config/settings.yaml', 'r') as ymlfile:
        return yaml.safe_load(ymlfile)

def main():
    config = load_config()
#    github_cfg = config['github']


 #   client = GitHubClient(github_cfg['token'], github_cfg['api_base_url'])
 #   prs = client.fetch_merged_prs(github_cfg['organization'], github_cfg['repository'])

  #  for pr in prs:
   #     print(json.dumps(pr))

    run_extract(config)

    run_transformation(config)




if __name__ == "__main__":
    main()