from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room
import subprocess
import threading
import tailer

app = Flask(__name__)
socketio = SocketIO(app)

#Just for debug
sudo_password = 'Blank'

def check_service_status(service_name):
    status = subprocess.run(['systemctl', 'is-active', service_name], stdout=subprocess.PIPE)
    return status.stdout.decode('utf-8').strip()

def sudo_systemctl(action, service_name):
    command = f'echo {sudo_password} | sudo -S systemctl {action} {service_name}.service'
    subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

@app.route('/')
def index():
    services = {
        'fooocus': check_service_status('fooocus.service'),
        'kohya': check_service_status('kohya.service'),
        'a1111': check_service_status('a1111.service')
    }
    return render_template('index.html', services=services)

@app.route('/manage_service/<action>/<service_name>')
def manage_service(action, service_name):
    sudo_systemctl(action, service_name)
    return redirect(url_for('index'))

@app.route('/logs/<service_name>')
def logs(service_name):
    return render_template('logs.html', service_name=service_name)

@socketio.on('join', namespace='/logs')
def on_join(data):
    service_name = data['service_name']
    join_room(service_name)
    start_tail_log_file(service_name)

def start_tail_log_file(service_name):
    threading.Thread(target=tail_log_file, args=(service_name,)).start()

def tail_log_file(service_name):
    log_files = {
        'fooocus': '/var/www/flaskapp/servicelogs/Fooocus.txt',
        'kohya': '/var/www/flaskapp/servicelogs/kohya.txt',
        'a1111': '/var/www/flaskapp/servicelogs/a1111.txt',
    }
    log_file_path = log_files.get(service_name)
    if log_file_path:
        for line in tailer.follow(open(log_file_path)):
            socketio.emit('log_update', {'data': line}, room=service_name, namespace='/logs')

if __name__ == '__main__':
    socketio.run(app, debug=True)
