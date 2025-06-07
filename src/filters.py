from datetime import datetime, timedelta


def add_filter_args(parser):
    """
    Register filter-related CLI flags onto the given ArgumentParser.
    """
    # PR-level filters
    parser.add_argument(
        "--merged-since", type=int,
        help="Only include PRs merged in the last N days"
    )
    parser.add_argument(
        "--only-authors", nargs='+',
        help="Only include PRs authored by these usernames"
    )

    # Review-level filters
    parser.add_argument(
        "--reviewers", nargs='+',
        help="Only include reviews by these usernames"
    )
    parser.add_argument(
        "--recent-reviews", type=int,
        help="Only include reviews in the last N days"
    )

    # Check-run filters
    parser.add_argument(
        "--check-names", nargs='+',
        help="Only include check runs with these names"
    )
    parser.add_argument(
        "--pass-only", action='store_true',
        help="Only include checks that succeeded"
    )


# --- Filter factories ------------------------------------

def merge_date_filter(days: int):
    cutoff = datetime.now() - timedelta(days=days)
    return lambda pr: datetime.fromisoformat(pr['merged_at'].replace('Z', '')) >= cutoff


def author_whitelist_filter(authors):
    whitelist = set(authors)
    return lambda pr: pr['user']['login'] in whitelist


def reviews_by_users_filter(reviewers):
    reviewers_set = set(reviewers)
    return lambda rev: rev['user']['login'] in reviewers_set


def recent_reviews_filter(days: int):
    cutoff = datetime.utcnow() - timedelta(days=days)
    return lambda rev: datetime.fromisoformat(rev['submitted_at'].replace('Z', '')) >= cutoff


def check_name_filter(names):
    print("Check names filter:", names)
    names_set = set(names)
    return lambda chk: chk['name'] in names_set


def pass_only_filter(_):
    return lambda chk: chk.get('conclusion') == 'success'


# --- Builders --------------------------------------------

def build_pr_filters(args):
    fns = []
    if args.merged_since is not None:
        fns.append(merge_date_filter(args.merged_since))
    if args.only_authors:
        fns.append(author_whitelist_filter(args.only_authors))
    return fns


def build_review_filters(args):
    fns = []
    if args.reviewers:
        fns.append(reviews_by_users_filter(args.reviewers))
    if args.recent_reviews is not None:
        fns.append(recent_reviews_filter(args.recent_reviews))
    return fns


def build_check_filters(args):
    fns = []
    if args.check_names:
        fns.append(check_name_filter(args.check_names))
    if args.pass_only:
        fns.append(pass_only_filter(True))
    return fns
