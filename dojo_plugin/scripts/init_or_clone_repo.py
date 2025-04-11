import os
import subprocess
import requests
import sys

def repo_exists(username, repo_name, token):
    url = f"https://api.github.com/repos/{username}/{repo_name}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    return response.status_code == 200

def create_personal_repo(repo_name, token, private=True):
    url = "https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    data = {
        "name": repo_name,
        "private": private
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ Created repo '{repo_name}'")
        return response.json()["clone_url"]
    else:
        print(f"❌ Failed to create repo: {response.status_code} - {response.text}")
        return None

def clone_repo_if_safe(repo_url, path):
    if os.path.exists(path) and os.listdir(path):
        print(f"📂 Directory '{path}' is not empty. Skipping clone to avoid overwriting.")
        return
    subprocess.run(["git", "clone", repo_url, path], check=True)
    print("📥 Repo cloned successfully.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python init_or_clone_repo.py <repo-name>")
        return

    repo_name = sys.argv[1].strip()
    path = "/data/generated_repos/githubRepo"
    username = "afluffybunny7"  # 🔒 Set your actual GitHub username
    private = False

    # 🔐 Load token
    token = ""
    with open("/opt/CTFd/CTFd/plugins/dojo_plugin/env/.env", "r") as f:
        for line in f:
            if line.startswith("PAT="):
                token = line.strip().split("=", 1)[1]

    repo_url = f"https://github.com/{username}/{repo_name}.git"

    if repo_exists(username, repo_name, token):
        print(f"ℹ️ Repo '{repo_name}' already exists.")
        try:
            clone_repo_if_safe(repo_url, path)
        except subprocess.CalledProcessError as e:
            print(f"💥 Git clone error: {e}")
    else:
        created_repo_url = create_personal_repo(repo_name, token, private)
        if created_repo_url:
            print(f"✅ Repo ready at: {created_repo_url}")

if __name__ == "__main__":
    main()