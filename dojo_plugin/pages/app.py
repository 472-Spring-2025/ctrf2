from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'
@app.route('/', methods=['GET', 'POST'])
def create_ctf():
    if request.method == 'POST':
        ctf_name = request.form.get('ctf_name')
        if ctf_name == "Existing Name":  # Simulating a duplicate name
            flash("Error: Name already exists", "danger")
        else:
            flash("CTF Challenge Created Successfully!", "success")
            return redirect(url_for('create_ctf'))
    return render_template('new_ctf.html')
if __name__ == '__main__':
    app.run(debug=True)