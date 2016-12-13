from gevent import monkey
monkey.patch_all()

from flask import Flask, request, abort, render_template
from werkzeug.exceptions import BadRequest
import gevent
from gevent.socket import wait_read, wait_write

import paramiko
from paramiko import PasswordRequiredException
from paramiko.dsskey import DSSKey
from paramiko.rsakey import RSAKey
from paramiko.ssh_exception import SSHException

import socket
import time

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/web/')
def webS():
    bridge = WSSHBridge(request.environ['wsgi.websocket'])
    bridge.execute()

class WSSHBridge(object):
    def __init__(self,websocket):
        self._websocket = websocket
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.open('localhost',22,'root','mizukoshi')
        self._transport = self._ssh.get_transport()
        self._channel = self._transport.open_session()
        self._channel.get_pty('xterm')
        self._tasks = []

    def open(self, hostname, port=22, username=None,password=None,private_key=None, key_passphrase=None, allow_agent=False,timeout=None):
        pkey = None
        self._ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            pkey=pkey,
            timeout=timeout,
            allow_agent=allow_agent,
            look_for_keys=False)

    def _forward_inbound(self):
        try:
            while True:
                data = self._websocket.receive()
                self._channel = self._transport.open_session()
                self._channel.get_pty('xterm')
                self._channel.exec_command(data)
                while True:
                    data = self._channel.recv(1024)
                    self._websocket.send(data)
                    if len(data) == 0:
                        break
        finally:
            self.close()

    def _bridge(self):
        self._channel.setblocking(False)
        self._channel.settimeout(0.0)
        self._tasks = [
            gevent.spawn(self._forward_inbound)
        ]
        gevent.joinall(self._tasks)

    def execute(self):
        self._bridge()
        self._channel.close()

    def close(self):
        gevent.killall(self._tasks, block = True)
        self._tasks = []
        self._ssh.close()


if __name__ == "__main__":
    from gevent.pywsgi import WSGIServer
    from geventwebsocket.handler import WebSocketHandler
    from jinja2 import FileSystemLoader
    import os
    root_path = os.path.dirname('/')
    app.jinja_loader = FileSystemLoader(os.path.join(root_path,'templates'))
    http_server = WSGIServer(('0.0.0.0',5000),app,log=None,handler_class=WebSocketHandler)
    try:
        http_server.serve_forever()
    except KeyboardInterrupt:
        pass

