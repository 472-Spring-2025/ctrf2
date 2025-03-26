from flask import Flask, render_template, request, redirect, url_for, flash
from flask import Blueprint, Response, render_template, abort
from CTFd.utils.user import get_current_user
from CTFd.utils.decorators import authed_only

new_ctf = Blueprint("pwncollege_new_ctf", __name__)
new_ctf.secret_key = 'your_secret_key'
@new_ctf.route('/new-ctf', methods=['GET', 'POST'])
@authed_only
def create_ctf():
    return render_template('new_ctf.html')
