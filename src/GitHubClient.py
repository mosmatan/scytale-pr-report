
import logging
import requests

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, token, base_url, page_size=50):
        self.base_url = base_url.rstrip('/')
        self.page_size = page_size
        self.token = token

        self.headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
        }

        logger.debug(f"GitHubClient initialized with base_url={self.base_url}, page_size={self.page_size}")

    def _get_json(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()

        return response.json()

    def _paginate(self, endpoint, params=None, data_key=None):
        page = 1

        while True:
            page_params = dict(params or {}, per_page=self.page_size, page=page)
            payload = self._get_json(endpoint, page_params)

            items = payload.get(data_key) if data_key else payload
            if not items:
                break

            for item in items: # iterate over items in the current page (iterator dp)
                yield item

            page += 1

    def fetch_merged_prs(self, org, repo, filters=None):
        logger.info(f"Fetching merged PRs for {org}/{repo}")

        endpoint = f"/repos/{org}/{repo}/pulls"
        params = {
            'state': 'closed',
            'sort': 'updated',
            'direction': 'desc',
        }

        prs = []
        for pr in self._paginate(endpoint, params):
            if not pr.get('merged_at'):
                continue

            if filters and not all(fn(pr) for fn in filters): # apply filters if provided
                continue

            prs.append(pr)

        logger.info(f"Found {len(prs)} merged PRs for {org}/{repo}")
        return prs

    def fetch_approved_reviews(self, org, repo, pr_number, filters=None):
        logger.debug(f"Fetching approved reviews for PR #{pr_number} in {org}/{repo}")

        endpoint = f"/repos/{org}/{repo}/pulls/{pr_number}/reviews"

        reviews = []
        for review in self._paginate(endpoint):
            if review.get('state') != 'APPROVED':
                continue

            if filters and not all(fn(review) for fn in filters): # apply filters if provided
                continue

            reviews.append(review)

        logger.debug(f"Retrieved {len(reviews)} approved reviews for PR #{pr_number}")
        return reviews

    def fetch_pr_check_runs(self, org, repo, commit_sha, status='completed', filters=None):
        logger.debug(f"Fetching check runs for commit {commit_sha} in {org}/{repo} (status={status})")

        endpoint = f"/repos/{org}/{repo}/commits/{commit_sha}/check-runs"
        params = {'status': status}

        runs = []
        for check in self._paginate(endpoint, params, data_key='check_runs'):
            if filters and not all(fn(check) for fn in filters): # apply filters if provided
                continue

            runs.append(check)

        logger.debug(f"Found {len(runs)} check runs for commit {commit_sha}")
        return runs
