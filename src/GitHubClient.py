import requests

class GitHubClient:
    def __init__(self, token, base_url):
        self._token = token
        self._base_url = base_url
        self._headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github.v3+json",
        }

        self._PAGE_SIZE = 50


    def fetch_merged_prs(self, organization: str, repo: str, filters = None):
        merged_prs = []
        page = 1

        params = {
            'state': 'closed',
            'per_page': self._PAGE_SIZE,
            'page': page,
            'sort': 'updated',
            'direction': 'desc',
        }

        while True:
            params['page'] = page

            url = f"{self._base_url}/repos/{organization}/{repo}/pulls"
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            prs_items = response.json()

            if not prs_items: #when the page is empty and there is no more data to retrieve
                break

            for pr in prs_items:
                if pr['merged_at']: # check if it really merged and not open or denied
                    if not filters or all(f(pr) for f in filters): # runs all the filters and only if pass all of them then added to merged_prs
                        merged_prs.append(pr)

            page += 1

        return merged_prs

    def fetch_approved_reviews(self, organization: str, repo: str, pr_number : int, filters = None) -> list :
        reviews_comments = []
        page = 1

        params = {
            'per_page': self._PAGE_SIZE,
            'page': page,
        }

        while True:
            params['page'] = page

            url = f"{self._base_url}/repos/{organization}/{repo}/pulls/{pr_number}/reviews"
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()
            reviews_items = response.json()

            if not reviews_items: #when the page is empty and there is no more data to retrieve
                break

            for review in reviews_items:
                if review['state'] == 'APPROVED': # only approved reviews can add to the result
                    if not filters or all(f(review) for f in filters): # runs all the filters and only if pass all of them then added to reviews_comments
                            reviews_comments.append(review)

            page += 1

        return reviews_comments

    def fetch_pr_check_runs(self, organization : str, repo : str ,merge_commit_sha : str, status = None, filters = None) -> list:
        check_runs = []
        page = 1

        params = {
            'per_page': self._PAGE_SIZE,
            'page': page,
            'status': status if status else 'completed',
        }

        while True:
            params['page'] = page

            url = f"{self._base_url}/repos/{organization}/{repo}/commits/{merge_commit_sha}/check-runs"
            response = requests.get(url, headers=self._headers, params=params)
            response.raise_for_status()

            check_items = response.json().get('check_runs', [])

            if len(check_items) == 0: # when the page is empty and there is no more data to retrieve
                break

            if filters:
                check_items = [check for check in check_items if all(f(check) for f in filters)]

            check_runs += check_items

            page += 1

        return check_runs










