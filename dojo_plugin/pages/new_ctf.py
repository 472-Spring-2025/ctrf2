from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask import Blueprint, Response, render_template, abort
import yaml
import runpy
import os
import shutil
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import authed_only
from CTFd.plugins import bypass_csrf_protection




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
        dirs = os.listdir(levelPath)
        os.makedirs("/tmp/repoDir", exist_ok=True)
        os.makedirs("/tmp/file_gen", exist_ok=True)  # Create directory if it doesn't exist
        with open("/tmp/file_gen/input.yml", "w") as f:
            f.write("your data here")
        
        for file in dirs:
            shutil.copy(levelPath + "/" + file, "/tmp/repoDir/"+file)

        with open("/tmp/repoDir/input.yml", "w") as f:
            f.write("your data here")

        #return redirect(url_for("pwncollege_dojos.listing"))

    return render_template('new_ctf.html')


    
