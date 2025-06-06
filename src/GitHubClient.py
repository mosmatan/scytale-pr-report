import requests

class GitHubClient:
    def __init__(self, token, base_url):
        self._token = token
        self._base_url = base_url
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }

        self._PAGE_SIZE = 100


    def fetch_merged_prs(self, organization: str, repo: str, filters = None):
        merged_prs = []
        page = 1

        while True:
            params = {
                'state': 'closed',
                'per_page': self._PAGE_SIZE,
                'page': page,
                'sort': 'updated',
                'direction': 'desc',
            }

            url = f"{self._base_url}/repos/{organization}/{repo}/pulls"
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            page_items = response.json()

            if not page_items:
                break

            for pr in page_items:
                if pr['merged_at']:
                    should_merge = True
                    if filters:
                        for f in filters:
                            if not f(pr):
                                should_merge = False

                    if should_merge:
                        merged_prs.append(pr)

            page += 1

        return merged_prs

    def fetch_approved_reviews(self, organization: str, repo: str, pr_number : int) -> list :
        reviews_comments = []
        page = 1

        while True:
            params = {
                'per_page': self._PAGE_SIZE,
                'page': page,
            }

            url = f"{self._base_url}/repos/{organization}/{repo}/pulls/{pr_number}/reviews"
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()

            reviews_items = response.json()
            if not reviews_items:
                break

            for review in reviews_items:
                if review['state'] == 'APPROVED':
                    reviews_comments.append(review)

            page += 1

        return reviews_comments

    def fetch_pr_check_runs(self, organization : str, repo : str ,merge_commit_sha : str, status = None) -> list:
        check_runs = []
        page = 1

        while True:
            params = {
                'per_page': self._PAGE_SIZE,
                'page': page,
                'status': status if status else 'completed',
            }

            url = f"{self._base_url}/repos/{organization}/{repo}/commits/{merge_commit_sha}/check-runs"
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()

            check_items = response.json().get('check_runs', [])

            if len(check_items) == 0:
                break

            check_runs += check_items

            page += 1

        return check_runs










