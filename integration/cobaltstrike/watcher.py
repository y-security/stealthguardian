import base64
import os
import requests
import socket
import time
from pathlib import Path
from subprocess import Popen, PIPE
from signal import SIGINT
import uuid
import urllib3
import re
import base64
import random

############################################################################
# GLOBAL VARIABLES
############################################################################

API_KEY = os.environ.get('APIKEY', str(uuid.uuid4()))
process = None
logprocess = None

try:
    MIDDLEWARE_IP = socket.getaddrinfo('stealthguardian-middleware',0)[0][4][0]
    MIDDLEWARE_PORT = 8000
except socket.gaierror:
    exit("Could not find stealthguardian-middleware")

MIDDLEWARE_PROTO = "https"
CS_DIRECTORY = "/cobaltstrike/cobaltstrike/"


# SSL Verification
disablesslverify = os.environ.get('DisableSSLVerification', "False")
sslverify = True
if(disablesslverify.lower() == "true"):
    sslverify = False
    urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)

############################################################################
# Various Helper Functions
############################################################################

def read_until(process, target_string):
    """
    Read lines from a process until a specific string is found

    :param process: process to read from
    :param target_string: the string we are looking for while reading
    """
    output_lines = []
    while True:
        line = process.stdout.readline()
        print(line)
        if not line:
            break  # End of output
        output_lines.append(line)
        if target_string in line:
            break
    return ''.join(output_lines)

def getMiddlewareConfig():
    """
    Get Configuration of Middleware
    """
    headers = {'StealthGuardianAPIKey': API_KEY}
    r = requests.get(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/middlewareconfiguration", headers=headers, verify=sslverify)
    config = r.json()
    return config

def getCSConfig():
    """
    Load config into an object
    """
    middlewareConfig = getMiddlewareConfig()
    csconfig = {}
    for item in middlewareConfig:
        if not item["key"] in csconfig:
            csconfig[item["key"]] = item["value"]
    return csconfig

def testMiddlewareconnection():
    """
    Helper function to identify if Middleware is reachable
    """
    try:
        requests.get(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/", verify=sslverify)
    except:
        print("[-] No connection to middleware possible.")
        return False
    return True

def testCSConnection(csconfig, timeout):
    """
    Test a TCP connection to the specified host and port.

    :param csconfig: Reference to configuration settings
    :param timeout: The timeout in seconds for the connection attempt.
    :return: True if the connection was successful, False otherwise.
    """
    host = csconfig["cs_teamserver_ip"]
    port = int(csconfig["cs_teamserver_port"])
    try:
        # Create a TCP socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Set the timeout for the connection attempt
            s.settimeout(timeout)
            # Attempt to connect to the specified host and port
            s.connect((host, port))
        return True
    except (socket.timeout, socket.error) as e:
        print(e)
        return False
    
def checkCobaltInstallation(path):
    """
    Simple function to check if required Cobalt Strike files are available to the script
    """
    cspath = Path(path)
    if not cspath.exists():
        print("[-] CobaltStrike Path doesn't exist")
        return False
    if not cspath.joinpath("cobaltstrike.jar").exists():
        print("[-] invalid installation: cobaltstrike.jar not found.")
        return False
    if not cspath.joinpath("agscript").exists():
        print("[-] invalid installation: agscript not found.")
        return False
    return True
    
def beaconLog(csconfig, beaconId, text, logtype="log"):
    """
    Inform the Beacon about detections

    :param csconfig: Reference to configuration settings
    :param beaconId: The beacon to which the notification is send
    :param text: Text to send
    :param logtype: Type of log to be send
    """

    # Test for a working TCP Connection to the teamserver
    if not testCSConnection(csconfig, 5):
        print("[-] Connection to CobaltStrike Teamserver failed in beaconLog.")
        return False
    
    teamserver_ip = csconfig["cs_teamserver_ip"]
    teamserver_port = csconfig["cs_teamserver_port"]
    user = "StealthGuardianLog" + str(random.randint(10000, 99999))
    password = csconfig["cs_teamserver_password"]
    cobaltstrike_directory = CS_DIRECTORY

    new_env = os.environ.copy()  # Start with a copy of the current environment
    new_env['PWD'] = cobaltstrike_directory # Set working directory to cobaltstrike directory
    agscript_path = Path(cobaltstrike_directory).joinpath('agscript')

    global logprocess

    if(logprocess == None):
        logprocess = Popen([agscript_path, teamserver_ip, str(teamserver_port), user, password], stdout=PIPE, stderr=PIPE, stdin=PIPE, env=new_env, cwd=cobaltstrike_directory, bufsize=1, text=True)
        out = read_until(logprocess, "Windows error codes loaded")

    try:
        print("New log for: " + str(beaconId))
        logprocess.stdin.write("load /cobaltstrike/logger.cna\n")
        time.sleep(1.5)
        textList = text.split('\n')
        for textItem in textList:
            if logtype == "log":
                logprocess.stdin.write(f"beaconLog {beaconId} \"{textItem}\"\n")
            elif logtype == "error":
                logprocess.stdin.write(f"beaconError {beaconId} \"{textItem}\"\n")
        time.sleep(0.5)
    except Exception as e:
        print(e)
        logprocess = None
        beaconLog(csconfig, beaconId, text, logtype)
    finally:
        print("Done")


def writeFileForCommand(taskid, tfile, filecontent):
    """
    Function to upload files to the Docker environment of the headless CS

    :param taskid: Reference to the taskid (uuid), used as part of directory structure
    :param tfile: Filename 
    :param filecontent: The content of the file
    :return: Path to the file on disk
    """
    tmpdir = "/tmpfiles/"

    filepath = Path(tfile)
    base_name = filepath.name

    path = Path(tmpdir + taskid)
    path.mkdir(parents=True, exist_ok=True)
    print(filecontent)

    with open(str(path) + "/" + base_name, 'wb') as file:
        file.write(base64.b64decode(filecontent))

    return str(path) + "/" + base_name

############################################################################
# Function that will execute a single StealthGuardian Task
############################################################################

def executeTask(task):
    """
    Executes headless cobalt strike

    :param task: The task to execute
    possible return values:
     - True:  Command was successfully executed => Status of task can be changed
     - False  Command was not executed due to an error
    """
    # Grab config from middleware
    csconfig = getCSConfig()
    global process
    
    # Test for a working TCP Connection to the teamserver
    if not testCSConnection(csconfig, 5):
        print("[-] Connection to CobaltStrike Teamserver failed in executeTask.")
        return False
    
    # Initialize Variables with config values
    teamserver_ip = csconfig["cs_teamserver_ip"]
    teamserver_port = csconfig["cs_teamserver_port"]
    user = "StealthGuardianTask" + str(random.randint(10000, 99999))
    password = csconfig["cs_teamserver_password"]
    cobaltstrike_directory = CS_DIRECTORY
    beaconid = task["targetBeacon"]

    # Heuristic checks for valid cobaltstrike installation
    if not checkCobaltInstallation(cobaltstrike_directory):
        return False

    # base64 decode command, decode to type str
    try:
        command = base64.b64decode(task["command"]).decode('utf-8')
    except Exception as e:
        print("Not a base64 command - skipping this command")
        headers = {'StealthGuardianAPIKey': API_KEY}
        update = {"taskid":task["taskid"], "status":"executed", "result":"Failed - Command not base64 encoded"}
        beaconLog(getCSConfig(), task["sourceBeacon"], "StealthGuardian Task failed to execute.", logtype="error")
        r = requests.post(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/tasks/update", headers=headers, json=update, verify=sslverify)
        return False

    # some commands require a file, such as upload, execute-assembly, powershell-import,....
    # this file is saved in the additionalcomandinfos table
    pattern = r'\"[^\"]*\"|\S+'
    commandparams = re.findall(pattern, command)
    commandparams[0]  = commandparams[0].replace("-","_")

    if(commandparams[0] == "upload"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[1], task["additionalcomandinfos"])
        commandparams[1] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "powershell_import"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[1], task["additionalcomandinfos"])
        commandparams[1] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "dllinject"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[2], task["additionalcomandinfos"])
        commandparams[2] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "kerberos_ccache_use"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[1], task["additionalcomandinfos"])
        commandparams[1] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "kerberos_ticket_use"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[1], task["additionalcomandinfos"])
        commandparams[1] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "spunnel"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[3], task["additionalcomandinfos"])
        commandparams[3] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "spunnel_local"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[3], task["additionalcomandinfos"])
        commandparams[3] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "shspawn"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[2], task["additionalcomandinfos"])
        commandparams[2] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "shinject"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[3], task["additionalcomandinfos"])
        commandparams[3] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "inline_execute"):
        # Upload the file to the local system into /tmpfiles/taskid/
        newfilepath = writeFileForCommand(task["taskid"], commandparams[1], task["additionalcomandinfos"])
        commandparams[1] = newfilepath
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "execute_assembly"):
        # In a execute-assembly command, the file path is either the first argument or the second
        # If it is in the second, the command starts with "[PATCHES:

        if(commandparams[1].startswith('"[PATCHES:')):
            newfilepath = writeFileForCommand(task["taskid"], commandparams[2], task["additionalcomandinfos"])
            commandparams[2] = newfilepath
        else: 
            newfilepath = writeFileForCommand(task["taskid"], commandparams[1], task["additionalcomandinfos"])
            commandparams[1] = newfilepath

        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "ls"):
        # ls is an internal agscript command and needs to be rewritten to dir in headless
        commandparams[0] = "dir"
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "psinject"):
        commandparams[0] = "powerpick_inject"
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "socks" and commandparams[1] == "stop"):
        # socks stop is included in socks command, we need to rewrite this
        commandparams[0] = "socks_stop"
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "exit" ):
        # exit is an internal agscript command
        commandparams[0] = "_exit"
        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "token_store" ):
        # token_store is one command in CS; but different agscript functions exist
        if( commandparams[1] == "steal"):
            commandparams[0] = "token_store_steal"
            commandparams[1] = commandparams[2]
            commandparams[2] = commandparams[3]

        elif(commandparams[1] == "steal-and-use"):
            commandparams[0] = "token_store_steal_and_use"
            commandparams[1] = commandparams[2]
            commandparams[2] = commandparams[3]

        elif(commandparams[1] == "use"):
            commandparams[0] = "token_store_use"
            commandparams[1] = commandparams[2]

        elif(commandparams[1] == "show"):
            commandparams[0] = "token_store_show"

        elif(commandparams[1] == "remove"):
            commandparams[0] = "command token_store_remove"
            commandparams[1] = commandparams[2]

        elif(commandparams[1] == "command token_store_remove_all"):
            commandparams[0] = "socks_stop"

        updated_command = " ".join(commandparams)
        command = updated_command


    elif(commandparams[0] == "data_store" ):
        # data_store is one command in CS; but different agscript functions exist
        if( commandparams[1] == "load"):
            if(len(commandparams) > 4):
                commandparams[0] = "data_store_load_name"
                newfilepath = writeFileForCommand(task["taskid"], commandparams[4], task["additionalcomandinfos"])
                commandparams[1] = commandparams[2]
                commandparams[2] = commandparams[3]
                commandparams[3] = newfilepath
            else:
                commandparams[0] = "data_store_load"
                print(commandparams[3])
                newfilepath = writeFileForCommand(task["taskid"], commandparams[3], task["additionalcomandinfos"])
                commandparams[1] = commandparams[2]
                commandparams[2] = newfilepath
                print(newfilepath)
                commandparams[3] = ""

        elif(commandparams[1] == "unload"):
            commandparams[0] = "data_store_unload"
            commandparams[1] = commandparams[2]

        elif(commandparams[1] == "list"):
            commandparams[0] = "data_store_list"

        updated_command = " ".join(commandparams)
        command = updated_command

    elif(commandparams[0] == "argue" ):
        if( len(commandparams) == 1):
            commandparams[0] = "argue_list"

        elif( len(commandparams) == 2):
            commandparams[0] = "argue_remove"

        elif( len(commandparams) > 2):
            commandparams[0] = "argue_add"
           
        updated_command = " ".join(commandparams)
        command = updated_command

    else:
        command = " ".join(commandparams)


    #######################################
    # Executing commands using agscript
    #######################################
    print("Executing: " + command)

    agscript_path = Path(cobaltstrike_directory).joinpath('agscript')

    new_env = os.environ.copy()  # Start with a copy of the current environment
    new_env['PWD'] = cobaltstrike_directory # Set working directory to cobaltstrike directory

    # Start new agscript process with given arguments
    if(process == None):
        process = Popen([agscript_path, teamserver_ip, str(teamserver_port), user, password], stdout=PIPE, stderr=PIPE, stdin=PIPE, env=new_env, cwd=cobaltstrike_directory, bufsize=1, text=True)
        out = read_until(process, "Windows error codes loaded")

    # commands that will be executed in aggressor script console
    ag_commands = [
        'load /cobaltstrike/headless-strike.cna', # load headless script
        f'use {beaconid}', # select correct beacon
        command, # the command to run
    ]

    try:
        # loop over commands
        for ag_cmd in ag_commands:
            print(ag_cmd)
            process.stdin.write(ag_cmd)
            process.stdin.write('\n')
            time.sleep(1.5) # wait for commands to process (load takes a bit)
    except Exception as e:
        print(e)
        process = None
        executeTask(task)
        return False
    finally:
        print("Done")

    return True

############################################################################
# Loop that processes new Tasks
############################################################################

def processTasks():
    if not testMiddlewareconnection():
        return False
    
    # Test for a working TCP Connection to the teamserver
    if not testCSConnection(getCSConfig(), 5):
        print("[-] Connection to CobaltStrike Teamserver failed in processTasks.")
        return False
    
    headers = {'StealthGuardianAPIKey': API_KEY}

    r = requests.get(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/tasks/cobaltstrike", headers=headers, verify=sslverify)

    # return on error
    if r.status_code != 200 and r.status_code != 404:
        return False
    
    if(r.status_code == 200):
        # automatically sort tasks by timestamp
        tasksJson = sorted(r.json(), key=lambda x: x["timestamp"])
        for task in tasksJson:

            if task["status"] == "queued":
                print("[+] Executing queued command.")
                print(task)

                if executeTask(task):
                    print("[+] Successfully executed task. Changing status")
                    update = {"taskid":task["taskid"], "status":"executed", "result":""}
                    beaconLog(getCSConfig(), task["sourceBeacon"], "StealthGuardian Task Successfully executed.")
                    
                else:
                    print("[-] Failed to execute task. Setting error result")
                    update = {"taskid":task["taskid"], "status":"executed", "result":"Error: Failed to execute task."}
                    beaconLog(getCSConfig(), task["sourceBeacon"], "StealthGuardian Task failed to execute.", logtype="error")
                r = requests.post(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/tasks/update", headers=headers, json=update, verify=sslverify)

def processAgentLogs():
    if not testMiddlewareconnection():
        return False
    
    headers = {'StealthGuardianAPIKey': API_KEY}
    
    r = requests.get(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/agentlogs/0", headers=headers, verify=sslverify)

    # return on error
    if r.status_code != 200 and r.status_code != 404:
        return False

    logsJson = r.json()
    if(r.status_code == 200):
        for logEntry in logsJson:
            if (logEntry["notified"] == 0 and logEntry["status"] == "detected") or logEntry["check_type"] == "manual":
                # notify only once
                beaconId = logEntry["buid"]
                csconfig=getCSConfig()
                notifyText  = "New Agent Log:\n"
                notifyText += " - timestamp: {}\n".format(logEntry["timestamp"])
                notifyText += " - status: {}\n".format(logEntry["status"])
                notifyText += " - id: {}".format(logEntry["id"])
                # beaconLog might fail with incorrect config or beaconid
                beaconLog(csconfig, beaconId, notifyText)

                # update status after processing
                update = {"logcheck":logEntry["logcheck"], "notified": 1}
                r = requests.post(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/agentlogs/update", headers=headers, json=update, verify=sslverify)
            else:
                print("Unknown status - do not care")
                update = {"logcheck":logEntry["logcheck"], "notified": 1}
                r = requests.post(f"{MIDDLEWARE_PROTO}://{MIDDLEWARE_IP}:{MIDDLEWARE_PORT}/api/agentlogs/update", headers=headers, json=update, verify=sslverify)



############################################################################
# Main function
############################################################################

def main():
    commandFound = False
    while not commandFound:
        processTasks()
        processAgentLogs()
        time.sleep(1)

if __name__ == '__main__':
    main()
