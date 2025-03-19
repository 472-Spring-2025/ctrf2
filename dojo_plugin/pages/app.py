from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Blueprint, Response, render_template, abort

appbp = Blueprint("pwncollege_app", __name__)
appbp.secret_key = 'your_secret_key'
@appbp.route('/test-add-page', methods=['GET', 'POST'])
def create_ctf():
    return render_template('new_ctf.html')
