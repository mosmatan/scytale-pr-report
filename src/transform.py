import json

import pandas as pd

from src.GitHubClient import GitHubClient


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

    github_client = GitHubClient(token=github_cfg['token'], base_url=github_cfg['api_base_url'])

    for pr_number in df['number']:
        approved_reviews = github_client.fetch_approved_reviews(organization=github_cfg['organization'],repo=repo_name,pr_number=pr_number)
        if len(approved_reviews) > 0:
            df_processed.loc[df_processed['pr_number'] == pr_number,'cr_passed'] = True

        merge_commit_sha = df.loc[df['number'] == pr_number]['merge_commit_sha'].values[0]
        checks =  github_client.fetch_pr_check_runs(organization=github_cfg['organization'],repo=repo_name,merge_commit_sha=merge_commit_sha)
        if len(checks) > 0:
            all_completed = True
            for check in checks:
                if check['conclusion'] != 'success':
                    all_completed = False

            df_processed.loc[df_processed['pr_number'] == pr_number, 'checks_passed'] = all_completed


    print(df_processed.head())


