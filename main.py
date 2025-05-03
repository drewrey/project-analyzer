import argparse
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import datetime
from collections import defaultdict
from datetime import date
import os


def main():
    parser = argparse.ArgumentParser(
                        prog='Projects Analyzer',
                        description='Analyze the commits for all git repos in a directory',
                        epilog='Make suggestions on github\nhttps://github.com/drewrey/project-analyzer')
    parser.add_argument('directory')
    parser.add_argument('-d', '--days', type=int, default=30, help="How many days to go back?")
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    args = parser.parse_args()
    print(f"Analyzing projects in {args.directory} ...")

    paths = find_directories(args.directory)
    commits_by_path = calculate_commits_by_path(paths, args.days)
    print_results(commits_by_path)

def calculate_commits_by_path(paths: list[str], days: int) -> dict[str, int]:
    res = {}
    for path in paths:
        commits = get_commits_for_repo(path, days)
        total_commits = get_total_commits(commits)
        res[path] = total_commits
    return sorted(res.items(), key=lambda item: item[1], reverse=True)

def print_results(commits_by_path: dict[str, int]):
    print("----------------")
    print("Commits per repo")
    print("----------------")
    for k, v in commits_by_path:
        if v > 0:
            print(f"{k.split("/")[-1]}: {v}")

def find_directories(parent_dir="./") -> list[str]:
    paths = []
    for entry in os.listdir(parent_dir):
        full_path = os.path.join(parent_dir, entry)
        if os.path.isdir(full_path):
            if is_git_repo(full_path):
                paths.append(full_path)
    return paths

def is_git_repo(path) -> bool:
    try:
        Repo(path)
        return True
    except (InvalidGitRepositoryError, NoSuchPathError):
        return False

def get_commits_for_repo(repo_path="./", days=30) -> dict[date, int]:
    repo = Repo(repo_path)

    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=days)

    commit_counts = defaultdict(int)

    if not has_commits(repo):
        return {}

    for commit in repo.iter_commits(since=start_date, until=end_date):
        commit_date = datetime.datetime.fromtimestamp(commit.committed_date).date()
        commit_counts[commit_date] += 1

    sorted_commit_counts = sorted(commit_counts.items())
    return sorted_commit_counts

def has_commits(repo: Repo) -> bool:
    try:
        repo.head.commit
        return True
    except ValueError:
        return False

def get_total_commits(commit_counts: dict[date, int]) -> int:
    return sum([x for (k, x) in commit_counts])

if __name__ == "__main__":
    main()
