
import os
import subprocess
import requests
import sys

def create_org_repo(org, repo_name, token, private=True):
    url = f"https://api.github.com/user/repos"
    headers = {"Authorization": f"token {token}"}
    data = {
        "name": repo_name,
        "private": private
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print(f"✅ Created repo '{repo_name}")
        return response.json()["clone_url"]
    else:
        print(f"❌ Failed to create repo: {response.status_code} - {response.text}")
        return None
    
def get_org_repo_count(org, token=None):
    url = f"https://api.github.com/orgs/{org}"
    headers = {}
    if token:
        headers["Authorization"] = f"token {token}"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data.get("public_repos")
    else:
        print(f"❌ Failed to fetch repo count: {response.status_code} - {response.text}")
        return None




def init_git_and_push(path, repo_url):
    os.chdir(path)
    
    if not os.path.isdir(os.path.join(path, ".git")):
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-am", "Initial commit"], check=True)
    else:
        print("📝 Git repo already initialized.")
    
    subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
    subprocess.run(["git", "branch", "-M", "main"], check=True)
    subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
    print("🚀 Code pushed to GitHub.")

def main():
    path = "/data/generated_repos/githubRepo"
    token = ""
    with open("/opt/CTFd/CTFd/plugins/dojo_plugin/env/.env", "r") as f:
        token = f.readline()[5:] 
    private = False
    org = "472-Spring-2025"
    repo_name = sys.argv[1] + "-"
    

    if not os.path.isdir(path):
        print("❌ Invalid directory path.")
        return

    repo_url = create_org_repo(org, repo_name, token, private)
    if repo_url:
        try:
            init_git_and_push(path, repo_url)
        except subprocess.CalledProcessError as e:
            print(f"💥 Git error: {e}")
        except Exception as e:
            print(f"💥 Unexpected error: {e}")

if __name__ == "__main__":
    main()