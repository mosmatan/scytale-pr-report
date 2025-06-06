import json
import os
from src.GitHubClient import GitHubClient


def save_merged_prs_to_file(merged_prs, raw_dir_path, repo_name):
    os.makedirs(raw_dir_path, exist_ok=True)

    raw_path = os.path.join(raw_dir_path, f'{repo_name}_merged_prs.json')

    with open(raw_path, 'w', encoding='utf-8') as f:
        json.dump(merged_prs, f, ensure_ascii=False, indent=4)

    print(f'Extracted {len(merged_prs)} merged PRs to {raw_path}.')



def run_extract(config: dict):
    github_cfg = config['github']
    raw_dir_path = config['data']['raw_dir_path']
    repo_name = github_cfg['repository']

    print(f'Extracting {github_cfg["organization"]}/{repo_name}...')

    client = GitHubClient(github_cfg['token'], github_cfg['api_base_url'])
    merged_prs = client.fetch_merged_prs(github_cfg['organization'], repo_name)

    save_merged_prs_to_file(merged_prs, raw_dir_path, repo_name)

