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
    # proc = subprocess.Popen(["cmd.exe"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    proc = subprocess.Popen(
        ["ngrok", "http", f"--domain={nDomain}", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    # Send the ngrok command to the command prompt
    # proc.stdin.write(f"ngrok http --domain={nDomain} 8000\n")
    # proc.stdin.flush()
    # If we do not wait for the process to terminate, the process will shutdown before the ngrok tunnel is opened and a
    # "Tried to write to non-existent pipe" error will be thrown.
    time.sleep(3)
    # proc.terminate()

def getNgrokPid(logger):
    pid = None

    # NOTE: Use the commented out code in Windows.
    # process = subprocess.Popen("netstat -ano | findStr 4040", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # # Needs some time to obtain the pid. 
    # time.sleep(3)
    # for line in process.stdout: 
    #     logger.debug("After executing command in getNgrokPid: " + line.decode().strip())
    #     pid = line.decode().strip().split(' ')[-1]
    # process.communicate()
    # if process.returncode != 0:
    #     logger.debug("An error occurred while obtaining pid -> function getNgrokPid.")
    # else:
    #     logger.debug("Successfully obtained pid: " + pid)
    # return pid

    command = "lsof -i :4040 -t"  
    
    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for command to finish (no need for `time.sleep`)
    stdout, stderr = process.communicate()
    logger.debug(f"This is stdout from getNgrokPid: {stdout}")
    pids = stdout.strip().split()
    if pids:
        pid = pids[0]  
    
    # Log errors
    if process.returncode != 0:
        logger.debug(f"Error getting PID: {stderr.strip()}")
    else:
        logger.debug(f"Successfully obtained PID: {pid}")
    
    return pid

def closeNgrokConnection(logger, pidToKill):
    # NOTE: Use the commented out code in Windows.
    # process = subprocess.Popen(f"taskkill /F /PID {pidToKill}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # # If we do not wait for the process to terminate, the flask app will shutdown before the ngrok tunnel is closed and
    # # "Tried to write to non-existent pipe" error will be thrown.
    # time.sleep(3)
    # process.communicate()
    # if process.returncode != 0:
    #     logger.debug("An error occurred in closing the ngrok tunnel -> function closeNgrokConnection.")
    # else:
    #     logger.debug("Successfully killed process " + pidToKill)
    # process.terminate()

    # Use 'kill -9' for Linux to forcefully terminate the process
    process = subprocess.Popen(
        ["kill", "-9", str(pidToKill)],  # Command as a list for security
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE
    )
    
    process.communicate()  # Wait for the kill command to complete
    # Making sure the ngrok tunnel is closed before the app shuts down - other solutions were more complex.
    time.sleep(3)
    
    if process.returncode != 0:
        logger.debug("An error occurred in closing the ngrok tunnel -> function closeNgrokConnection.")
    else:
        logger.debug(f"Successfully killed process {pidToKill}")
    
    process.terminate()  # Redundant but kept for consistency

    # should use???
    # process = subprocess.Popen(
    #     ["kill", "-9", str(pidToKill)],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE
    # )
    
    # try:
    #     # Wait up to 3 seconds for kill command to complete
    #     stdout, stderr = process.communicate(timeout=3)
    # except subprocess.TimeoutExpired:
    #     logger.error(f"Timeout killing PID {pidToKill}")
    #     process.kill()  # Force-terminate the kill command itself if stuck
    #     stdout, stderr = process.communicate()  # Cleanup
        
    # if process.returncode != 0:
    #     logger.error(f"Failed to kill PID {pidToKill}: {stderr.decode()}")
    #     raise RuntimeError("Ngrok cleanup failed")
    
    # logger.debug(f"Killed PID {pidToKill}")
