#!/usr/bin/env python
"""Generate a Graphviz visualization of GitHub PR branch relationships."""

import argparse
import os
import sys
from datetime import datetime

import requests

# Configuration
MAX_TITLE_LENGTH = 50
PRIMARY_BRANCH_NAMES = ["main", "master", "develop"]
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a Graphviz visualization of GitHub PR branch relationships"
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=os.environ.get("GITHUB_REPO"),
        help="Repository in 'owner/name' format (or set GITHUB_REPO env var)"
    )
    parser.add_argument(
        "--show-all-branches",
        action="store_true",
        help="Include branches without PRs (work not yet planned for release)"
    )
    args = parser.parse_args()

    if not args.repo:
        parser.error("Repository required: provide as argument or set GITHUB_REPO environment variable")

    if "/" not in args.repo:
        parser.error("Repository must be in 'owner/name' format (e.g., 'mycompany/private-repo')")

    owner, name = args.repo.split("/", 1)
    return owner, name, args.show_all_branches


def fetch_open_prs(owner, repo, token):
    """Fetch all open pull requests from GitHub."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_prs = []
    page = 1

    while True:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/pulls",
            headers=headers,
            params={"state": "open", "per_page": 100, "page": page}
        )

        if response.status_code != 200:
            error_msg = f"GitHub API error: {response.status_code}"
            if response.status_code == 404 and not token:
                error_msg += "\nNote: This might be a private repo. Set GITHUB_TOKEN environment variable."
            print(error_msg, file=sys.stderr)
            sys.exit(1)

        prs = response.json()
        if not prs:
            break

        all_prs.extend(prs)
        page += 1

    return all_prs

def fetch_all_branches(owner, repo, token):
    """Fetch all branches from GitHub."""
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_branches = []
    page = 1

    while True:
        response = requests.get(
            f"https://api.github.com/repos/{owner}/{repo}/branches",
            headers=headers,
            params={"per_page": 100, "page": page}
        )

        if response.status_code != 200:
            print(f"Warning: Could not fetch branches: {response.status_code}", file=sys.stderr)
            return []

        branches = response.json()
        if not branches:
            break

        all_branches.extend([b['name'] for b in branches])
        page += 1

    return all_branches


def print_pr_summary(prs):
    """Print a summary of pull requests."""
    print("\nPR Summary:")
    print("-" * 80)

    for pr in prs:
        source = pr['head']['ref']
        target = pr['base']['ref']
        title = pr['title'][:MAX_TITLE_LENGTH]
        print(f"#{pr['number']:4d}: {source:30s} -> {target:30s}")
        print(f"       {title}")
        print()


def collect_branches_and_edges(prs):
    """Extract branch relationships from PRs."""
    branches = set()
    target_branches = set()
    edges = []

    for pr in prs:
        source = pr['head']['ref']
        target = pr['base']['ref']

        # Sometimes, weird edge cases result in PRs that have branches
        # pointing to themselves. We skip these.
        if source == target:
            continue

        pr_title = pr['title'].replace('"', '\\"')
        pr_number = pr['number']

        branches.add(source)
        branches.add(target)
        target_branches.add(target)
        edges.append((source, target, pr_number, pr_title))

    return branches, target_branches, edges


def build_dot_content(branches, target_branches, edges, orphan_branches=None):
    """Build Graphviz DOT file content."""
    lines = [
        'digraph PRFlow {',
        '  rankdir=LR;',
        '  node [shape=box, style=rounded];',
        ''
    ]

    # Style primary branches

    # Find primary branches that are at the end of the chain
    # (they are targets but not sources, and contain primary branch names)
    source_branches = {source for source, _, _, _ in edges}
    primary_branches = [
        b for b in target_branches
        if b not in source_branches and any(
            name in [part.lower() for part in b.split('/')]
            for name in PRIMARY_BRANCH_NAMES
        )
    ]
    for branch in primary_branches:
        lines.append(f'  "{branch}" [style="rounded,filled", fillcolor=lightblue, fontweight=bold];')
    lines.append('')

    # Add orphan branches (branches without PRs)
    if orphan_branches:
        for branch in sorted(orphan_branches):
            lines.append(f'  "{branch}" [style="rounded,filled", fillcolor=lightyellow, fontweight=italic];')
        lines.append('')


    # Add edges with PR labels
    for source, target, pr_num, pr_title in edges:
        display_title = pr_title[:MAX_TITLE_LENGTH] + "..." if len(pr_title) > MAX_TITLE_LENGTH else pr_title
        label = f"PR #{pr_num}\\n{display_title}"
        lines.append(f'  "{source}" -> "{target}" [label="{label}"];')

    lines.append('}')
    return '\n'.join(lines)


def generate_dot_file(prs, orphan_branches=None):
    """Generate a Graphviz DOT file from PR data."""
    # Setup output paths
    date_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("dot", exist_ok=True)
    os.makedirs("png", exist_ok=True)
    os.makedirs("svg", exist_ok=True)
    output_file = f"dot/pr_graph_{date_str}.dot"

    # Build graph structure
    branches, target_branches, edges = collect_branches_and_edges(prs)
    dot_content = build_dot_content(branches, target_branches, edges, orphan_branches)

    # Write to file
    with open(output_file, 'w') as f:
        f.write(dot_content)

    return output_file, len(branches)


def print_visualization_instructions(dot_file, num_prs, num_branches):
    """Print summary and visualization instructions."""
    base_name = dot_file.rsplit('.', 1)[0].split('/')[-1]

    print(f"\nGenerated {dot_file}")
    print(f"Total PRs: {num_prs}")
    print(f"Unique branches: {num_branches}")
    print(f"\nTo visualize, run:")
    print(f"  dot -Tpng {dot_file} -o png/{base_name}.png")
    print(f"  dot -Tsvg {dot_file} -o svg/{base_name}.svg")


def main():
    # Parse arguments
    repo_owner, repo_name, show_all = parse_args()

    # Fetch data
    print(f"Fetching open PRs from {repo_owner}/{repo_name}...")
    prs = fetch_open_prs(repo_owner, repo_name, GITHUB_TOKEN)
    print(f"Found {len(prs)} open PRs")

    # Optionally fetch all branches
    orphan_branches = None
    if show_all:
        print("Fetching all branches...")
        all_branches = fetch_all_branches(repo_owner, repo_name, GITHUB_TOKEN)
        # Find branches that aren't in any PR
        pr_branches = set()
        for pr in prs:
            pr_branches.add(pr['head']['ref'])
            pr_branches.add(pr['base']['ref'])
        orphan_branches = set(all_branches) - pr_branches
        print(f"Found {len(orphan_branches)} branches without PRs")

    # Display summary
    print_pr_summary(prs)

    # Generate graph
    dot_file, num_branches = generate_dot_file(prs, orphan_branches)

    # Show instructions
    print_visualization_instructions(dot_file, len(prs), num_branches)


if __name__ == "__main__":
    main()
