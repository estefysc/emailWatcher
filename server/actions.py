import time
import os
import secrets
from tunnel.actions import closeNgrokConnection, getNgrokPid

shutdown_flask_flag = False

def shutdown_flask():
    global shutdown_flask_flag
    shutdown_flask_flag = True

def monitor_shutdown_flag(logger):
    global shutdown_flask_flag
    while not shutdown_flask_flag:
        time.sleep(1)
    ngrokPidm = getNgrokPid(logger)
    closeNgrokConnection(logger, ngrokPidm)
    # will terminate the flask app
    os._exit(0)

def generate_new_secret_key():
    return secrets.token_hex(16)