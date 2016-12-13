from flask import Flask, session, request, redirect, render_template, url_for

app = Flask(__name__)

app.config['SECRET_KEY'] = 'The secret key which ciphers the cookie'

@app.before_request
def before_request():
    if session.get('username') is not None:
        return
    
    if request.path == '/login':
        return
    
    return redirect('/login')

@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST' and _is_account_valid():
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username',None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=80,debug=True)

