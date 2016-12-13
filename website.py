from flask import Flask, session, request, redirect, render_template, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('test.html')

if __name__ == '__main__':
    from jinja2 import FileSystemLoader
    import os
    root_path = os.path.dirname('/root/websocket_ssh/')
    app.jinja_loader = FileSystemLoader(root_path)

    app.run(host='0.0.0.0',port=80,debug=True)

