📑 **Summary Page: Endpoints & Authentication**

---

### Authentication

* **PAT via `.env`**
  Loaded from the `GITHUB_TOKEN` environment variable using `load_dotenv()` in **extract.py**, then validated with `os.getenv("GITHUB_TOKEN")`&#x20;
* **Request Headers**
  Set once in `GitHubClient.__init__` as:

  ```http
  Authorization: Bearer <GITHUB_TOKEN>
  Accept: application/vnd.github.v3+json
  ```


* **Base URL**
  Configured in **settings.yaml** under `github.api_base_url` (default: `https://api.github.com`)&#x20;

---

### GitHub API Endpoints

| Endpoint & Params                                                                            | Purpose                                                                                | Method | Implementation              |
| -------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- | :----: | --------------------------- |
| **`/repos/{org}/{repo}/pulls`**<br/>`state=closed`,<br/>`sort=updated`,<br/>`direction=desc` | Fetch closed PRs; client retains only those with `merged_at != null`                   |   GET  | `fetch_merged_prs()`        |
| **`/repos/{org}/{repo}/pulls/{pr_number}/reviews`**                                          | Fetch all reviews for a PR; client keeps only those where `state == "APPROVED"`        |   GET  | `fetch_approved_reviews()`  |
| **`/repos/{org}/{repo}/commits/{commit_sha}/check-runs`**<br/>`status=completed`             | Fetch check runs for a commit; client filters for runs where `conclusion == "success"` |   GET  | `fetch_pr_check_runs()`     |

---

### Pagination

Handled by `GitHubClient._paginate()`, which loops through pages using `?per_page=<size>&page=<n>` until no more items are returned .

---

### Optional Filters

Defined in **filters.py**, with factories for:

* **PR-level**: `merge_date_filter()`, `author_whitelist_filter()`
* **Review-level**: `reviews_by_users_filter()`, `recent_reviews_filter()`
* **Check-level**: `check_name_filter()`

Built via `build_pr_filters()`, `build_review_filters()`, and `build_check_filters()` and applied client-side after fetching raw data .
