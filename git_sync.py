#command to run
#python git_sync.py -m "Your commit message"#!/usr/bin/env python3
"""
git_sync.py — Stage, commit, and push your Codespaces changes in one shot.

Usage:
  python git_sync.py -m "Your commit message"
  python git_sync.py -m "msg" --remote origin --branch main

Notes:
- Respects .gitignore (uses `git add .`).
- If no changes are detected, exits cleanly.
- If upstream is missing, sets upstream to <remote>/<branch> automatically.
"""

import argparse
import subprocess
import sys

def sh(cmd, check=True, capture=False):
    result = subprocess.run(cmd, shell=True, check=check,
                            text=True, capture_output=capture)
    return result.stdout.strip() if capture else ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--message", required=True, help="Commit message")
    parser.add_argument("--remote", default="origin", help="Git remote name (default: origin)")
    parser.add_argument("--branch", default=None, help="Branch to push (default: current)")
    args = parser.parse_args()

    # 0) Sanity: inside a git repo?
    try:
        inside = sh("git rev-parse --is-inside-work-tree", capture=True)
    except subprocess.CalledProcessError:
        print("✖ Not inside a Git repository. Run this from your repo root.")
        sys.exit(1)
    if inside != "true":
        print("✖ Not inside a Git repository. Run this from your repo root.")
        sys.exit(1)

    # 1) Determine current branch if not provided
    if args.branch is None:
        try:
            current_branch = sh("git branch --show-current", capture=True)
        except subprocess.CalledProcessError:
            current_branch = ""
    else:
        current_branch = args.branch

    if not current_branch:
        # Could be a detached HEAD or brand-new repo; try to set main
        print("ℹ No current branch detected. Creating 'main' and switching to it…")
        sh("git checkout -b main")
        current_branch = "main"

    # 2) Show status
    status = sh("git status --porcelain", capture=True)
    if not status:
        print("✓ Nothing to commit (working tree clean).")
        # Still offer to push in case ahead-of-remote
        ahead = sh("git rev-list --left-right --count HEAD...@'{u}' 2>/dev/null || true", capture=True)
        if ahead and ahead.split()[0] != "0":
            print("↥ Local branch ahead, pushing anyway…")
        else:
            sys.exit(0)

    # 3) Add all (respects .gitignore)
    print("➕ Staging changes…")
    sh("git add .")

    # 4) Commit
    print(f'📝 Committing: "{args.message}"')
    try:
        sh(f'git commit -m "{args.message.replace(\'"\', r\'\\"\')}"')
    except subprocess.CalledProcessError:
        print("✖ Commit failed (perhaps nothing staged).")
        sys.exit(1)

    # 5) Ensure upstream exists; if not, set it
    print(f"⎇ Ensuring upstream {args.remote}/{current_branch}…")
    upstream_exists = True
    try:
        sh("git rev-parse --abbrev-ref @{u}", capture=True)
    except subprocess.CalledProcessError:
        upstream_exists = False

    if not upstream_exists:
        print(f"↥ Setting upstream to {args.remote}/{current_branch}…")
        try:
            sh(f"git push --set-upstream {args.remote} {current_branch}")
            print("✓ Pushed with new upstream.")
            sys.exit(0)
        except subprocess.CalledProcessError as e:
            print("✖ Failed to set upstream/push. Details:")
            print(e)
            sys.exit(1)
    else:
        # 6) Push normally
        print("↥ Pushing…")
        try:
            sh("git push")
            print("✓ Push complete.")
        except subprocess.CalledProcessError as e:
            print("✖ Push failed. Details:")
            print(e)
            sys.exit(1)

if __name__ == "__main__":
    main()
