import subprocess
import os

def run_cmd(cmd, timeout=60):
    try:
        output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=timeout).decode('utf-8')
        return output.strip()
    except subprocess.CalledProcessError as e:
        return (e.output.decode('utf-8') if e.output else str(e)).strip()
    except Exception as e:
        return str(e)

def collect(paths=["/home", "/app", "/srv"]):
    results = []
    evidence = []
    ledger = []

    all_git_dirs = []
    for loc in paths:
        if os.path.exists(loc):
            dirs = run_cmd(f"find {loc} -maxdepth 4 -name .git -type d 2>/dev/null").split('\n')
            all_git_dirs.extend([d for d in dirs if d])

    for git_dir in all_git_dirs:
        repo_path = os.path.dirname(git_dir)
        repo_name = os.path.basename(repo_path)
        os.chdir(repo_path)

        branch = run_cmd("git rev-parse --abbrev-ref HEAD")
        head_sha = run_cmd("git rev-parse HEAD")
        dirty = bool(run_cmd("git status --porcelain"))

        git_log_24h = run_cmd("git log --since='24 hours ago'")

        results.append({
            "absolute_path": repo_path,
            "repository_name": repo_name,
            "current_branch": branch,
            "current_HEAD_SHA": head_sha,
            "dirty_status": dirty,
            "commits_made_in_the_past_24_hours": git_log_24h.count("commit "),
        })

        evidence.append({
            "claim": f"Repository {repo_name} state retrieved",
            "confidence": "VERIFIED",
            "collector": "git_repo.py",
            "command": "git log --since='24 hours ago'",
            "stdout": git_log_24h
        })

        for line in git_log_24h.split('\n'):
            if line.startswith("commit "):
                sha = line.split()[1]
                ledger.append({
                    "activity_ID": sha[:8],
                    "system_affected": repo_name,
                    "repository": repo_name,
                    "commit_SHA": sha,
                    "completion_status": "UNKNOWN_REQUIRES_REVIEW"
                })

    os.chdir("/app")
    return results, ledger, evidence
