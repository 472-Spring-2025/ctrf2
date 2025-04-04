from flask import Blueprint, Response, render_template, abort, jsonify
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
    file = open("/opt/CTFd/CTFd/themes/dojo_theme/levels/" + str(category) + "/" + str(level) + "/input.yml")
    response_data = {"input": file.readlines()}
    return jsonify(response_data), 200
