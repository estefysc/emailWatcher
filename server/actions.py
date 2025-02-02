import time
import os
import secrets
import threading

from flask import session
from tunnel.actions import closeNgrokConnection, getNgrokPid

class ServerManager:
    _manager_instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._manager_instance is None:
                cls._manager_instance = super().__new__(cls, *args, **kwargs)
            return cls._manager_instance

    def __init__(self):
        self.shutdown_flask_flag = False

    @classmethod
    def get_server_instance(cls):
        return cls._manager_instance
    
    def shutdown_flask(self):
        self.shutdown_flask_flag = True

    def monitor_shutdown_flag(self, logger):
        logger.debug('---- Monitoring shutdown flag ----')
        logger.debug(f'Shutdown flag: {self.shutdown_flask_flag}')
        while not self.shutdown_flask_flag:
            time.sleep(0.5)
        ngrokPidm = getNgrokPid(logger)
        closeNgrokConnection(logger, ngrokPidm)
        # will terminate the flask app
        os._exit(0)

    def generate_new_secret_key(self):
        return secrets.token_hex(16)

    