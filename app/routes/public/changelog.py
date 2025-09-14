
from app.common.helpers.caching import ttl_cache
from flask import Blueprint, redirect, request
from collections import defaultdict
from typing import Tuple, List
from datetime import datetime

import app

router = Blueprint('changelog', __name__)

skip_keywords = (
    'merge',
    'rebase',
    'bump',
    'submodule',
    'update'
)

fix_keywords = (
    'fix',
    'fixed'
)

repos = (
    'anchor',
    'stern',
    'deck'
)

repo_alias = {
    'anchor': 'Bancho',
    'stern': 'Web',
    'deck': 'API'
}

@router.get('/p/changelog')
def changelog():
    # NOTE: This endpoint was used for changelogs to the osu! client
    #       I will be using it to display recent commits to the github repositories
    updater = request.args.get(
        'updater',
        default=0,
        type=int
    )

    # TODO: Implement changelog page for non-osu requests
    if updater != 3:
        return redirect('/changelog')

    return get_changelog()

@ttl_cache(ttl=60*15)
def get_changelog() -> str:
    # Get commits for all repos & sort them by date
    formatted_commits = [
        (f"{message} ({repo_alias[repo]})", date)
        for repo in repos
        for message, date in format_commits(get_latest_commits(repo))
    ]

    sorted_commits = sorted(
        formatted_commits,
        key=lambda commit: commit[1],
        reverse=True
    )

    # Split commits into days
    commit_dict = defaultdict(list)

    for commit in sorted_commits:
        commit_dict[commit[1].date()].append(commit[0])

    # Combine them into a string
    changelog_result = '\n'.join(
        f'({date.month}/{date.day}/{date.year})\n' +
        '\n'.join(commits)
        for date, commits in commit_dict.items()
    )

    return (
        'Titanic GitHub Updates\n\n' +
        changelog_result
    )

def format_commits(commits: List[dict]) -> List[Tuple[str, datetime]]:
    formatted_commits: List[Tuple[str, datetime]] = []

    for commit in commits:
        message = commit['commit']['message']
        date = datetime.fromisoformat(commit['commit']['author']['date'])

        if any(kw in message.lower() for kw in skip_keywords):
            # We don't need to include this
            continue

        if any(kw in message.lower() for kw in fix_keywords):
            # "Fix" commit
            message = f'*\t\t{message}'

        else:
            # "Add" commit
            message = f'+\t\t{message}'

        # NOTE: There is also a formatting without the
        #       "Added" or "Fixed" prefixes

        formatted_commits.append((
            message, date
        ))

    return formatted_commits

def get_latest_commits(repo: str, user: str = 'osuTitanic', amount: int = 50) -> List[dict]:
    response = app.session.requests.get(
        f'https://api.github.com/repos/{user}/{repo}/commits',
        params={
            'sha': get_branch_hash(user, repo),
            'per_page': amount
        }
    )

    if not response.ok:
        return []

    return response.json()

def get_branch_hash(user: str, repo: str, branch_name: str = 'dev') -> str:
    response = app.session.requests.get(
        f'https://api.github.com/repos/{user}/{repo}/branches'
    )

    if not response.ok:
        return

    branches = response.json()

    for branch in branches:
        if branch['name'] != branch_name:
            continue

        return branch['commit']['sha']

    return branches[0]['commit']['sha']
