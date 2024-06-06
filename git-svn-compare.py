#!/usr/bin/python3

import os
import re
import subprocess
import sys
from collections import defaultdict

def parse_svn_dump(dump_file):
    """
    Parses the SVN dump file to extract all revision numbers.

    Args:
        dump_file (str): Path to the SVN dump file.

    Returns:
        list: List of revision numbers found in the dump file.
    """
    revisions = []
    with open(dump_file, 'rb') as file:
        for line in file:
            match = re.match(rb'^Revision-number: (\d+)', line)
            if match:
                revisions.append(int(match.group(1)))
    return revisions

def get_git_commits(repo_path):
    """
    Extracts git commit hashes and their corresponding SVN revision numbers from the git repository.

    Args:
        repo_path (str): Path to the local git repository.

    Returns:
        dict: A dictionary where keys are SVN revision numbers and values are lists of git commit hashes.
    """
    os.chdir(repo_path)
    output = subprocess.check_output(['git', 'log', '--all', '--grep=git-svn-id:']).decode('utf-8')
    commits = defaultdict(list)
    current_commit = None

    for line in output.splitlines():
        commit_match = re.match(r'^commit (\w+)', line)
        if commit_match:
            current_commit = commit_match.group(1)
        else:
            svn_match = re.search(r'git-svn-id: .*@(\d+) ', line)
            if svn_match and current_commit:
                svn_revision = int(svn_match.group(1))
                commits[svn_revision].append(current_commit)
    return commits

def summarize_commits(repo_path):
    """
    Summarizes the total number of commits in the repository.

    Args:
        repo_path (str): Path to the local git repository.

    Returns:
        dict: A dictionary with the total number of commits in each branch.
    """
    os.chdir(repo_path)
    branches_output = subprocess.check_output(['git', 'branch', '-r']).decode('utf-8').splitlines()
    branch_commits = {}

    for branch in branches_output:
        branch = branch.strip()
        # Ignore symbolic references
        if '->' in branch:
            continue
        if branch:
            commit_count = subprocess.check_output(['git', 'rev-list', '--count', branch]).decode('utf-8').strip()
            branch_commits[branch] = int(commit_count)

    return branch_commits

def main(dump_file, repo_path):
    """
    Main function that coordinates the parsing of the SVN dump file and git repository,
    and prints out the corresponding git commits for each SVN revision.

    Args:
        dump_file (str): Path to the SVN dump file.
        repo_path (str): Path to the local git repository.
    """
    svn_revisions = parse_svn_dump(dump_file)
    git_commits = get_git_commits(repo_path)
    branch_commit_counts = summarize_commits(repo_path)
    unique_git_commits = {commit for commits in git_commits.values() for commit in commits}

    for revision in svn_revisions:
        if revision in git_commits:
            commits = git_commits[revision]
            print(f'Revision {revision}: {len(commits)} git commits; {", ".join(commits)}')
        else:
            print(f'Revision {revision}: 0 git commits')

    print("\nSummary:")
    print(f"Total SVN revisions: {len(svn_revisions)}")
    print(f"Total unique Git commits across all branches: {len(unique_git_commits)}")
    for branch, count in branch_commit_counts.items():
        print(f"{branch}: {count} commits")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: compare.py <svn_dump_file> <full_path_to_git_repo>')
        sys.exit(1)

    dump_file = sys.argv[1]
    repo_path = sys.argv[2]

    main(dump_file, repo_path)
