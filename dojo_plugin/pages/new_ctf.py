from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import Blueprint, Response, render_template, abort
import yaml
import runpy
import os
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import authed_only

new_ctf = Blueprint("pwncollege_new_ctf", __name__)
new_ctf.secret_key = 'your_secret_key'
@new_ctf.route('/new-ctf', methods=['GET', 'POST'])
@authed_only
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

        data = request.get_json()

        # Filter data to include only the allowed keys
        filtered_data = {key: data[key] for key in allowed_keys if key in data}
        yaml.dump(filtered_data, open(levelPath + "/tmp/tmp.yml", "w"))
        dirs = os.listdir(levelPath)
        runnable = [f for f in dirs if f.endswith(".py")]
        runpy.run_path(levelPath + "/" + runnable[0], levelPath + "/tmp/tmp.yml")
    return render_template('new_ctf.html')


    
