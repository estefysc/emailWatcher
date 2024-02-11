import time
import os
import secrets
import threading

from flask import session
from tunnel.actions import closeNgrokConnection, getNgrokPid

class ServerManager:
    _server_instance = None
    _lock = threading.Lock()

    def __init__(self):
        self.shutdown_flask_flag = False

    @classmethod
    def init_server_manager(cls):
        with cls._lock:
            if cls._server_instance is None:
                cls._server_instance = ServerManager()
            else:
                print('Server manager already exists')

    @classmethod
    def get_server_instance(cls):
        return cls._server_instance
    
    def shutdown_flask(self):
        self.shutdown_flask_flag = True

    def monitor_shutdown_flag(self, logger):
        while not self.shutdown_flask_flag:
            time.sleep(1)
        ngrokPidm = getNgrokPid(logger)
        closeNgrokConnection(logger, ngrokPidm)
        # will terminate the flask app
        os._exit(0)

    def generate_new_secret_key(self):
        return secrets.token_hex(16)

    