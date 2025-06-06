import json

import pandas as pd


def run_transformation(config : dict):
    github_cfg = config['github']
    repo_name = github_cfg['repository']
    raw_dir_path = config['data']['raw_dir_path']
    processed_dir_path = config['data']['processed_dir_path']
    report_dir_path = config['output']['report_dir_path']

    raw_path = f'{raw_dir_path}/{repo_name}_merged_prs.json'
    with open(raw_path, 'r', encoding='utf-8') as f:
        raw_prs = json.load(f)

    print(f'Processing {repo_name} merged PRs')

    df =pd.json_normalize(raw_prs)

    df_processed = pd.DataFrame({
        'pr_number' : df['number'],
        'title' : df['title'],
        'author' : df['user.login'],
        "merge_date": df["merged_at"],
        "cr_passed": False,
        "checks_passed": False,
    })

    print(f'Processing {repo_name} merged PRs')


    print(df_processed.head())


