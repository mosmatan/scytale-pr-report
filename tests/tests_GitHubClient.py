import yaml

from src.GitHubClient import GitHubClient

def load_config():
    with open('../config/settings.yaml', 'r') as ymlfile:
        return yaml.safe_load(ymlfile)



def test_fetch_merged_prs():
    cfg = load_config()
    cfg = cfg['tests']
    github_cfg = cfg['github']

    github_client = GitHubClient(token=github_cfg['token'], base_url=github_cfg['api_base_url'])
    merged_prs = github_client.fetch_merged_prs(organization=github_cfg['organization'], repo=github_cfg['repository'])
    assert len(merged_prs) == 4

def test_fetch_merged_reviews():
    cfg = load_config()
    cfg = cfg['tests']
    github_cfg = cfg['github']

    github_client = GitHubClient(token=github_cfg['token'], base_url=github_cfg['api_base_url'])
    approved_reviews = github_client.fetch_approved_reviews(organization=github_cfg['organization'], repo=github_cfg['repository'], pr_number=github_cfg['pr_number'])

    assert True #not crashing
