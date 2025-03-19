from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Blueprint, Response, render_template, abort

app = Blueprint("pwncollege_app", __name__)
app.secret_key = 'your_secret_key'
@app.route('/test-add-page', methods=['GET', 'POST'])
def create_ctf():
    return render_template('new_ctf.html')
