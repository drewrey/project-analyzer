import argparse
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import datetime
from collections import defaultdict
from datetime import date
import os


def main():
    print("Hello from python-parser!")
    print("Starting...")
    parser = argparse.ArgumentParser(
                        prog='ProgramName',
                        description='What the program does',
                        epilog='Text at the bottom of help')
    parser.add_argument('directory')
    parser.add_argument('-d', '--days', type=int, default=30, help="How many days to go back?")
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    args = parser.parse_args()
    print(args.directory, args.days, args.verbose)
    paths = find_directories(args.directory)
    res = {}
    for path in paths:
        commits = get_commits_for_repo(path, days=args.days)
        total_commits = get_total_commits(commits)
        res[path] = total_commits
    sorted_items = sorted(res.items(), key=lambda item: item[1], reverse=True)
    for k, v in sorted_items:
        if v > 0:
            print(f"{k.split("/")[-1]}: {v}")

def find_directories(parent_dir="./") -> list[str]:
    paths = []
    for entry in os.listdir(parent_dir):
        full_path = os.path.join(parent_dir, entry)
        if os.path.isdir(full_path):
            if is_git_repo(full_path):
                paths.append(full_path)
    print(f"paths are #{paths}")
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
    print(f"path is #{repo_path}")
    print(f"end date is #{end_date}")
    print(f"start date is #{start_date}")

    commit_counts = defaultdict(int)


    if not has_commits(repo):
        return {}

    for commit in repo.iter_commits(since=start_date, until=end_date):
        commit_date = datetime.datetime.fromtimestamp(commit.committed_date).date()
        commit_counts[commit_date] += 1

    sorted_commit_counts = sorted(commit_counts.items())
    return sorted_commit_counts

def has_commits(repo: Repo):
    try:
        repo.head.commit
        return True
    except ValueError:
        return False

def get_total_commits(commit_counts: dict[date, int]) -> int:
    return sum([x for (k, x) in commit_counts])

def read_file(path="./"):
    with open(path, 'r') as f:
        for line in f:
            print(line.strip())


if __name__ == "__main__":
    main()
