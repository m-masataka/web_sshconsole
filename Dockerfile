FROM ubuntu:14.04

RUN apt-get update
RUN apt-get -y install openssh-server git supervisor
RUN cat /etc/ssh/sshd_config | sed -e 's/PermitRootLogin\ without-password/PermitRootLogin\ yes/g' > /etc/ssh/sshd_config 
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN service ssh restart
RUN echo 'root:mizukoshi' | chpasswd
RUN apt-get -y install python-pip python2.7-dev libffi-dev libssl-dev
RUN pip install jinja2 itsdangerous click cryptography gevent gevent-websocket paramiko flask
RUN mkdir templates
ADD templates/index.html /templates/
ADD websocket_ssh.py /

CMD ["/usr/bin/supervisord"] 
