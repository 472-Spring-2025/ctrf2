from flask import Blueprint, Response, render_template, abort, jsonify
import yaml
import os
templates = Blueprint("pwncollege_templates", __name__)





@templates.route("/templates")
def get_template_categories():
    dirs = os.listdir("/opt/CTFd/CTFd/themes/dojo_theme/levels")
    
    # Convert directory list into JSON format
    response_data = {"categories": dirs}

    return jsonify(response_data), 200

@templates.route("/templates/<category>")
def get_template_levels(category):
    dirs = os.listdir("/opt/CTFd/CTFd/themes/dojo_theme/levels/" + str(category))
    response_data = {"templates": dirs}
    return jsonify(response_data), 200

@templates.route("/templates/<category>/<level>")
def get_level_input(category, level):
    file_path = f"/opt/CTFd/CTFd/themes/dojo_theme/levels/{category}/{level}/input.yml"
    
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

    # Send just the keys or specific values you're interested in
    keys = list(data.keys())  # or extract specific ones
    return jsonify(keys), 200
