import subprocess 
import configparser
import time

def startNgrok():
    """
    This function starts the ngrok tunnel without opening a separate cmd window
    """
    config = configparser.ConfigParser()
    config.read('config.cfg')
    nDomain = config['NGROK']['DOMAIN']
    proc = subprocess.Popen(["cmd.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    # Send the ngrok command to the command prompt
    proc.stdin.write(f"ngrok http --domain={nDomain} 8000\n")
    proc.stdin.flush()
    # If we do not wait for the process to terminate, the process will shutdown before the ngrok tunnel is opened and a
    # "Tried to write to non-existent pipe" error will be thrown.
    time.sleep(3)
    proc.terminate()

def getNgrokPid(logger):
    pid = None
    process = subprocess.Popen("netstat -ano | findStr 4040", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Needs some time to obtain the pid. 
    time.sleep(3)
    for line in process.stdout: 
        logger.debug("After executing command in getNgrokPid: " + line.decode().strip())
        pid = line.decode().strip().split(' ')[-1]
    process.communicate()
    if process.returncode != 0:
        logger.debug("An error occurred while obtaining pid -> function getNgrokPid.")
    else:
        logger.debug("Successfully obtained pid: " + pid)
    return pid

def closeNgrokConnection(logger, pidToKill):
    process = subprocess.Popen(f"taskkill /F /PID {pidToKill}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # If we do not wait for the process to terminate, the flask app will shutdown before the ngrok tunnel is closed and
    # "Tried to write to non-existent pipe" error will be thrown.
    time.sleep(3)
    process.communicate()
    if process.returncode != 0:
        logger.debug("An error occurred in closing the ngrok tunnel -> function closeNgrokConnection.")
    else:
        logger.debug("Successfully killed process " + pidToKill)
    process.terminate()
