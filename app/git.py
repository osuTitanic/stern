
from app import session
from git import Repo

current_repository: Repo | None = None

def initialize_repository() -> None:
    global current_repository
    
    try:
        current_repository = Repo(search_parent_directories=True)
    except Exception as e:
        session.logger.warning(f"Failed to initialize git repository: '{e}'")
        current_repository = None

def fetch_latest_commit() -> str:
    if current_repository is None:
        return ""

    try:
        return current_repository.head.commit.hexsha
    except Exception as e:
        session.logger.warning(f"Failed to fetch latest commit: '{e}'")
        return ""

def fetch_latest_commit_for_file(file_path: str) -> str:
    if current_repository is None:
        return ""

    try:
        commits = list(current_repository.iter_commits(paths=file_path, max_count=1))
        commit = next(iter(commits), None)

        if not commit:
            return ""

        return commit.hexsha
    except Exception as e:
        session.logger.warning(f"Failed to fetch latest commit for file '{file_path}': '{e}'")
        return ""
