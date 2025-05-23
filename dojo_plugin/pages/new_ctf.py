from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import Blueprint, Response, render_template, abort
import yaml
import subprocess
import runpy
import os
import shutil
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import authed_only
from CTFd.plugins import bypass_csrf_protection
import requests
from ..api.v1.dojo import create_dojo
from ..utils.dojo import generate_ssh_keypair

repo_dir = "/data/generated_repos/"

new_ctf = Blueprint("pwncollege_new_ctf", __name__)
@new_ctf.route('/new-ctf', methods=['GET', 'POST'])
@bypass_csrf_protection
def create_ctf():
    if request.method == 'POST':
        #Needs to grab the runnable script, a viable input file, and the scripts specific __init__ file
        #After, it should take these, run the file population script, and run the repo generation script
        #Push that repository to github, then get the repository and add it to the global dojo list (post request on /create-dojo or something)

        ctf_category = request.form.get("ctf_category")
        challenge_list = request.form.get("challenge_list")

        if ctf_category and challenge_list:
            levelPath = f"/opt/CTFd/CTFd/themes/dojo_theme/levels/{ctf_category}/{challenge_list}"
            print("Level path:", levelPath)
        else:
            print("Missing data!")
        with open(levelPath + "/" + "input.yml", "r") as f:
            allowed_keys = yaml.safe_load(f)

        data = request.form.to_dict()

        # Filter data to include only the allowed keys
        filtered_data = {key: data[key] for key in allowed_keys if key in data}
        for key in filtered_data.keys():
            try:
                filtered_data[key] = int(filtered_data[key])
            except:
                try:
                    filtered_data[key] = float(filtered_data[key])
                except:
                    print("Do nothing")

        with open( "/opt/CTFd/CTFd/plugins/dojo_plugin/scripts/input.yml", "r") as f:
            allowed_keys = yaml.safe_load(f)
        filtered_file_gen = {key: data["ctf_" + key] for key in allowed_keys if "ctf_" + key in data}
        dirs = os.listdir(levelPath)
        
        shutil.rmtree(repo_dir)
        os.makedirs(repo_dir + "repoDir")
        os.makedirs(repo_dir + "file_gen")
        os.makedirs(repo_dir + "githubRepo")
        result = subprocess.run(["python", "/opt/CTFd/CTFd/plugins/dojo_plugin/scripts/init_or_clone_repo.py", filtered_file_gen["name"]], capture_output=True, text=True)
        

        directory_in_chal = []
        for file in dirs:
            try:
                shutil.copy(levelPath + "/" + file, repo_dir + "repoDir/"+file)
            except:
                directory_in_chal.append(file)
        for dir in directory_in_chal:
            shutil.copytree(levelPath + "/" + dir, repo_dir + "repoDir/"+dir)
        
        
        
        
        
        #Grab all data about challenge input
        with open( repo_dir + "repoDir/input.yml", "w") as f:
            yaml.dump(filtered_data, f)
        files = []
        for file in os.listdir(repo_dir + "repoDir"):
            files.append(repo_dir + "repoDir/" + file)
        filtered_file_gen["modules"] = [["mod-name", "mod-id", "mod-desc", [["chal-name", files]]]]
        #Grab all necessary data from post request for repo file   
        with open(repo_dir + "file_gen/input.yml", "w") as f:
            yaml.dump(filtered_file_gen, f)
        
        subprocess.run(["python", "/opt/CTFd/CTFd/plugins/dojo_plugin/scripts/file_gen.py", repo_dir + "file_gen/input.yml", repo_dir + "githubRepo/"], capture_output=True, text=True)
        result = subprocess.run(["python", "/opt/CTFd/CTFd/plugins/dojo_plugin/scripts/push_repo.py", filtered_file_gen["name"], "afluffybunny7"], capture_output=True, text=True)
        input = yaml.safe_load(open(repo_dir + "githubRepo/mod-name/module.yml"))
        
        user = get_current_user()
        
        repository = f"afluffybunny7/{filtered_file_gen['name']}".replace(" ", "-")
        spec = ""
        public_key = request.form.get("public_key")
        private_key = (request.form.get("private_key") or "").replace("\r\n", "\n")
        
        create_dojo(user, repository, public_key, private_key, None)
        return redirect(url_for("pwncollege_dojos.listing"))
        
    public_key, private_key = generate_ssh_keypair()
    return render_template(
        "new_ctf.html",
        public_key=public_key,
        private_key=private_key,
    )


    
