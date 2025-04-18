import os
import subprocess
import sys

def init_git_repo(path):
    os.chdir(path)

    if not os.path.isdir(os.path.join(path, ".git")):
        print("🔧 Initializing Git repo...")
        subprocess.run(["git", "init"], check=True)

    # Always set local identity (safe in automation)
    subprocess.run(["git", "config", "user.name", "afluffybunny7"], check=True)
    subprocess.run(["git", "config", "user.email", "andrewalfredparr@yahoo.com"], check=True)

    subprocess.run(["git", "add", "."], check=True)

    # Only commit if there are changes
    status = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if status.stdout.strip():
        subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)
        print("✅ Commit created.")
    else:
        print("⚠️ No changes to commit.")

def push_to_remote(path, repo_url, token):
    os.chdir(path)

    # Replace https://github.com/... with token-authenticated version
    secure_url = repo_url.replace("https://", f"https://afluffybunny7:{token}@")


    # Avoid duplicate remotes
    remotes = subprocess.run(["git", "remote"], capture_output=True, text=True).stdout.strip().splitlines()
    if "origin" not in remotes:
        subprocess.run(["git", "remote", "add", "origin", secure_url], check=True)
    subprocess.run(["git", "config", "--local", "credential.helper", ""], check=True)
    subprocess.run(["git", "remote", "set-url", "origin", secure_url], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print("🚀 Code pushed to GitHub.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python push_repo.py <repo-name> <username>")
        return

    repo_name = sys.argv[1].strip().replace(" ", "-")
    username = sys.argv[2].strip()
    path = "/data/generated_repos/githubRepo"
    repo_url = f"https://github.com/{username}/{repo_name}.git"
    token = ""
    with open("/opt/CTFd/CTFd/plugins/dojo_plugin/env/.env", "r") as f:
        for line in f:
            if line.startswith("PAT="):
                token = line.strip().split("=", 1)[1]
    if not os.path.isdir(path):
        print("❌ Invalid directory path.")
        return

    try:
        init_git_repo(path)
        push_to_remote(path, repo_url, token)
    except subprocess.CalledProcessError as e:
        print(f"💥 Git error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()
