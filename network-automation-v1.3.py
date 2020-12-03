# ==============================================================================
#   Network Automation Tool 
# ==============================================================================
# Language	    	: Python
# Name		    	: network_automation-v1.3.py
# Author	    	: Marcelo Ferreira CCIE #65117 - mferreira85@gmail.com
# Creation Date  	: 23/May/2020
# Version	    	: 1.3
# Update Date       : 11/Jun/2020
# Objective         : Send Commands and Configurations to HP, Cisco Switches and Wireless Controllers
# ==============================================================================

import os, sys ,socket, signal, re, datetime, logging
import telnetlib
import ipaddress

from consolemenu import *
from consolemenu.items import *
from consolemenu.format import *
from getpass import getpass
from netmiko import ConnectHandler
from netmiko.ssh_exception import NetMikoTimeoutException
from paramiko.ssh_exception import SSHException
from netmiko.ssh_exception import AuthenticationException

# These capture errors relating to hitting ctrl+C (I forget the source)
signal.signal(signal.SIGFPE, signal.SIG_DFL)  # IOError: Broken pipe
signal.signal(signal.SIGINT, signal.SIG_DFL)  # KeyboardInterrupt: Ctrl-C

# Class for Lines with Color to identify Errors and other highlights
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Define the Print number of ---- between messages
width1 = 80
width3 = 23
width4 = 8

# Max Attempt for error handling
max_attempts = 3

# Clear Input Lines after input Commands
screen_code = "\033[1A[\033[2K"

print("".center(width1,'-'))
print("Before you Start, please enter your Network Credentials".center(width1,' '))
print("".center(width1,'-'))

# Commom Credentials
for remaining in range(max_attempts-1, -1, -1):
    un = input("Enter your Username: ")
    if(len(un) != 0):
        break
    print("-> Fields Cannot be Blank, You have", remaining, "attempt(s) left")
else:
    input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
    exit()

# Commom Credentials
for remaining in range(max_attempts-1, -1, -1):
    pw = getpass("Enter your Password: ")
    if(len(pw) != 0):
        break
    print("-> Fields Cannot be Blank, You have", remaining, "attempt(s) left")
else:
    input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
    exit()

# Super User Credentials used for Comware Devices
sup_user = ("sup")
sup_pass = ("Type Password for Supervisor Here")
secret = ("Cisco123")

def hp_telnet(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN + "*** HP Switch Connection via TELNET - [On Screen Commands] ***".center(width1,' ') + bcolors.ENDC)
    print(bcolors.OKGREEN + "Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ') + bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Error Handling for Hosts
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    # Error Handling for Commands
    for remaining in range(max_attempts-1, -1, -1):
        cmd = input("Enter Command(s) seperated by ',' : ")
        if(len(cmd) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    sys.stdout.write( screen_code )
    hosts = host.split()
    sys.stdout.write( screen_code )
    commands = [x.strip() for x in cmd.split(',')]

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)

    start_time = datetime.datetime.now()

    # Loop with the data received above
    for HOST in hosts:
        print('\n'+'-> Establishing Telnet Connection to IP ' + HOST + '...')
        # sys.stdout.write( screen_code )
        try:
            tn = telnetlib.Telnet(HOST)
            # tn = telnetlib.Telnet(HOST, 23, 4)
            # tn.set_debuglevel(9)
            tn.read_until(b"Username:")
            tn.write(un.encode('ascii') + b"\r\n")
            tn.read_until(b"Password:")
            tn.write(pw.encode('ascii') + b"\r\n")
            tn.write(sup_user.encode('ascii') + b"\r\n")
            prompt = tn.read_until(b">")
            tn.read_until(b"Password:")
            tn.write(sup_pass.encode('ascii') + b"\r\n")
            tn.write(b"screen-length disable\r\n")
            tn.write(b"\r\n")
            # Get Prompt from Device
            a = prompt.replace(b'\r\n', b'')
            b = a.decode('utf-8')
            regex = r'^\<(.*)\>'
            regmatch = re.match(regex, b)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n' + '-> Connected to Device Name: ' + hostname + '\n')
            else:
                print(bcolors.FAIL + "-> Hostname Not Found!" + bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", HOST + bcolors.ENDC)
            continue

        # Variables for saving results after commands executed
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        config_filename = "./results/hp_switches/" + hostname + "_" + filetime + ".txt"

        # Loop for each command from the array
        for CMD in commands:
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + CMD + bcolors.ENDC)
            print("".center(width1,'-'))
            tn.write(CMD.encode('ascii') + b"\r\n")
            tn.write(b"\r\n")
        tn.write(b"quit\r\n")
        # Save Commands to a file and close session
        readoutput = tn.read_all().decode('ascii')
        print(readoutput)
        os.makedirs(os.path.dirname(config_filename), exist_ok=True)
        saveoutput = open(config_filename, 'a')
        saveoutput.write("".center(width1,'-')+'\r')
        saveoutput.write('-> Command(s) Executed:\r')
        saveoutput.write("".center(width1,'-')+'\r')
        saveoutput.write(readoutput+'\n')
        saveoutput.write('\n')
        saveoutput.close()
        tn.close()
        # Print Results in the Screen
        print("".center(width1,'-'))
        print(bcolors.WARNING+'File Generated: '+ config_filename+bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def hp_ssh(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN + "*** HP Switch Connection via SSH - [On Screen Commands] ***".center(width1,' ') + bcolors.ENDC)
    print(bcolors.OKGREEN + "Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ') + bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        cmd = input("Enter Command(s) seperated by ',' : ")
        if(len(cmd) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()
    sys.stdout.write( screen_code )
    commands = [x.strip() for x in cmd.split(',')]

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)
    logger = logging.getLogger("hp_switch_ssh")

    # Empty array to store hosts and Filenames
    devices = []
    files = []

    start_time = datetime.datetime.now()

    # Netmiko Variables and Loop
    for ip in hosts:
        hp_comware_ssh = {
            'device_type': 'hp_comware',
            'ip': ip,
            'username': un,
            'password': pw,
            'global_delay_factor': 0.2,
            # 'timeout':4,
        }
        devices.append(hp_comware_ssh)

    # Loop for the commands received from Array
    for device in devices:
        print('\n'+'-> Establishing SSH2 Connection to IP ' + device['ip'] + '...')
        try:
            net_connect = ConnectHandler(**device, timeout=6)
            prompt = net_connect.find_prompt()
            logger.debug("prompt: %s", prompt)
            regex = r'^\<(.*)\>'
            regmatch = re.match(regex, prompt)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n'+'-> Connected to Device Name: ' + hostname+'\n')
            else:
                print(bcolors.FAIL+"-> Hostname Not Found!"+bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", device['ip'] + bcolors.ENDC)
            continue

        # TimeStamp to save the files with date and time 
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        # Generating directory and filename after commands executed
        config_filename = "./results/hp_switches/" + hostname + "_" + filetime + ".txt"
        files.append(config_filename)

        # Loop of execution of commands received from Array and Saving Results
        for cmd in commands:
            net_connect.send_command_timing(sup_user)
            net_connect.send_command_timing(sup_pass)
            net_connect.send_command_timing("screen-length disable")
            this_cmd = net_connect.send_command_timing(cmd)
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + cmd + bcolors.ENDC)
            print("".center(width1,'-'))
            print(this_cmd)
            os.makedirs(os.path.dirname(config_filename), exist_ok=True)
            config_filename_f = open(config_filename, 'a')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write('-> Command Executed: '+cmd+'\r')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write(this_cmd+'\n')
            config_filename_f.write('\n')
            config_filename_f.close()
        net_connect.disconnect()
        print("".center(width1,'-'))
        print(bcolors.WARNING+'File Generated: '+ config_filename+bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def cisco_switch(name):
    # print("".center(width1,'-'))
    # print(bcolors.OKGREEN+"*** Cisco Switch Connection via SSH - [On Screen Commands] ***".center(width1,' ')+bcolors.ENDC)
    # print(bcolors.OKGREEN+"Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ')+bcolors.ENDC)
    # print("".center(width1,'-'))
    # print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("\nEnter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        cmd = input("Enter Command(s) seperated by ',' : ")
        if(len(cmd) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return
    
    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()
    sys.stdout.write( screen_code )
    commands = [x.strip() for x in cmd.split(',')]

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)

    # Empty array to store hosts and Filenames
    devices = []
    files = []

    start_time = datetime.datetime.now()

    # Netmiko Variables and Loop
    for ip in hosts:
        cisco_switch_ssh = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': un,
            'password': pw,
            'secret': secret,
            'global_delay_factor': 0.2,
            'fast_cli': True,
            # 'session_log': './results/cisco_switches/session.log'
            # 'timeout':4,
        }
        devices.append(cisco_switch_ssh)

    # Loop for the commands received from Array
    for device in devices:
        print('\n'+bcolors.WARNING +'-> Establishing SSH2 Connection to IP ' + device['ip'] + '...'+bcolors.ENDC)
        try:
            net_connect = ConnectHandler(**device, timeout=6)
            net_connect.enable()
            prompt = net_connect.find_prompt()
            # logger.debug("prompt: %s", prompt)
            regex = r'^(.*)\#'
            regmatch = re.match(regex, prompt)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n'+'-> Connected to Device Name: ' + hostname+'\n')
            else:
                print(bcolors.FAIL +"-> -> Hostname Not Found!"+ bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", device['ip'] + bcolors.ENDC)
            continue

        # TimeStamp to save the files with date and time 
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        # Generating directory and filename after commands executed
        config_filename = "./results/cisco_switches/" + hostname + "_" + filetime + ".txt"
        files.append(config_filename)

        # Loop of execution of commands received from Array and Saving Results
        for cmd in commands:
            this_cmd = net_connect.send_command_timing(cmd)
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '>> Command Executed: ' + cmd + bcolors.ENDC)
            print("".center(width1,'-'))
            print(this_cmd)
            os.makedirs(os.path.dirname(config_filename), exist_ok=True)
            config_filename_f = open(config_filename, 'a')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write('-> Command Executed: '+cmd+'\r')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write(this_cmd+'\n')
            config_filename_f.write('\n')
            config_filename_f.close()
        net_connect.disconnect()
        print(bcolors.OKBLUE+'\n-> File Generated: '+ config_filename+bcolors.ENDC)

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    ans = input(bcolors.WARNING+"\nWould you like to execute more commands? <y/n> "+bcolors.ENDC)
    if ans == "y":
        cisco_switch(name)
    else:
        Screen().input('\nPress [Enter] to Return to Main Menu')

def wlc(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN+"*** WLC Connection via SSH - [On Screen Commands] ***".center(width1,' ')+bcolors.ENDC)
    print(bcolors.OKGREEN+"Parts of code from Nick Bettison (Thanks)".center(width1,' ')+bcolors.ENDC)
    print(bcolors.OKGREEN+"Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ')+bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        cmd = input("Enter Command(s) seperated by ',' : ")
        if(len(cmd) != 0):
            break
        print(bcolors.FAIL +"-> -> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> -> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()
    sys.stdout.write( screen_code )
    commands = [x.strip() for x in cmd.split(',')]

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)
    logger = logging.getLogger("cisco_wlc")

    # Empty array to store hosts and Filenames
    devices = []
    files = []

    start_time = datetime.datetime.now()

    # Netmiko Variables and Loop
    for ip in hosts:
        cisco_wlc = {
            'device_type': 'cisco_wlc',
            'ip': ip,
            'username': un,
            'password': pw,
            'global_delay_factor': 0.2,
            # 'fast_cli': True,
            # 'timeout':6,
        }
        devices.append(cisco_wlc)

    # Loop for the commands received from Array
    for device in devices:
        print('\n'+'-> Establishing SSH2 Connection to IP ' + device['ip'] + '...')
        try:
            net_connect = ConnectHandler(**device, timeout=10)
            # get the prompt as a string
            prompt = net_connect.find_prompt()
            logger.debug("prompt: %s", prompt)
            regex = r'^\((.*)\)[\s]>'
            regmatch = re.match(regex, prompt)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n'+'-> Connected to Device Name: ' + hostname+'\n')
            else:
                print(bcolors.FAIL+"-> -> Hostname Not Found!"+bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", device['ip'] + bcolors.ENDC)
            continue

        # TimeStamp to save the files with date and time 
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        # Generating directory and filename after commands executed
        config_filename = "./results/wlcs/" + hostname + "_" + filetime + ".txt"
        files.append(config_filename)

        # Loop of execution of commands received from Array and Saving Results
        for cmd in commands:
            this_cmd = net_connect.send_command_w_enter(cmd, delay_factor=10, max_loops=1000)
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + cmd + bcolors.ENDC)
            print("".center(width1,'-'))
            print(this_cmd)
            os.makedirs(os.path.dirname(config_filename), exist_ok=True)
            config_filename_f = open(config_filename, 'a')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write('-> Command Executed: '+cmd+'\r')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write(this_cmd+'\n')
            config_filename_f.write('\n')
            config_filename_f.close()
        net_connect.disconnect()
        print("".center(width1,'-'))
        print(bcolors.WARNING+'File Generated: '+ config_filename+bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def wlc_from_file(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN+"*** WLC Connection via SSH - [On Screen Commands] ***".center(width1,' ')+bcolors.ENDC)
    print(bcolors.OKGREEN+"Parts of code from Nick Bettison (Thanks)".center(width1,' ')+bcolors.ENDC)
    print(bcolors.OKGREEN+"Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ')+bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    try:
        commands = open('wlc_commands.txt','r')
        commands = commands.read()
        commands = commands.strip().splitlines()
    except:
        input("\n" + bcolors.FAIL +"-> File 'wlc_commands.txt' not found!, You need to create it first, Press [ENTER] to Exit"+ bcolors.ENDC)
        return

    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)
    logger = logging.getLogger("cisco_wlc")

    # Empty array to store hosts and Filenames
    devices = []
    files = []

    start_time = datetime.datetime.now()

    # Netmiko Variables and Loop
    for ip in hosts:
        cisco_wlc = {
            'device_type': 'cisco_wlc',
            'ip': ip,
            'username': un,
            'password': pw,
            'global_delay_factor': 0.2,
            # 'fast_cli': True,
            # 'timeout':6,
        }
        devices.append(cisco_wlc)

    # Loop for the commands received from Array
    for device in devices:
        print('\n'+'-> Establishing SSH2 Connection to IP ' + device['ip'] + '...')
        try:
            net_connect = ConnectHandler(**device, timeout=10)
            # get the prompt as a string
            prompt = net_connect.find_prompt()
            logger.debug("prompt: %s", prompt)
            regex = r'^\((.*)\)[\s]>'
            regmatch = re.match(regex, prompt)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n'+'-> Connected to Device Name: ' + hostname+'\n')
            else:
                print(bcolors.FAIL+"-> -> Hostname Not Found!"+bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", device['ip'] + bcolors.ENDC)
            continue

        # TimeStamp to save the files with date and time 
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        # Generating directory and filename after commands executed
        config_filename = "./results/wlcs/" + hostname + "_" + filetime + ".txt"
        files.append(config_filename)

        # Loop of execution of commands received from Array and Saving Results
        for cmd in commands:
            this_cmd = net_connect.send_command_w_enter(cmd)
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + cmd + bcolors.ENDC)
            print("".center(width1,'-'))
            print(this_cmd)
            os.makedirs(os.path.dirname(config_filename), exist_ok=True)
            config_filename_f = open(config_filename, 'a')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write('-> Command Executed: '+cmd+'\r')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write(this_cmd+'\n')
            config_filename_f.write('\n')
            config_filename_f.close()
        net_connect.disconnect()
        print("".center(width1,'-'))
        print(bcolors.WARNING+'File Generated: '+ config_filename+bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def cisco_pre_def_sw_1(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN + "*** Cisco Switch Connection via SSH - [From File Commands] ***".center(width1,' ') + bcolors.ENDC)
    print(bcolors.OKGREEN + "Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ') + bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    try:
        commands = open('cisco_commands.txt','r')
        commands = commands.read()
        commands = commands.strip().splitlines()
    except:
        input("\n" + bcolors.FAIL +"-> File 'cisco_commands.txt' not found!, You need to create it first, Press [ENTER] to Exit"+ bcolors.ENDC)
        return

    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)
    logger = logging.getLogger("cisco_switch_ssh")

    # Empty array to store hosts and Filenames
    devices = []
    files = []

    start_time = datetime.datetime.now()

    # Netmiko Variables and Loop
    for ip in hosts:
        cisco_switch_ssh = {
            'device_type': 'cisco_ios',
            'ip': ip,
            'username': un,
            'password': pw,
            'secret': secret,
            'global_delay_factor': 0.2,
            # 'timeout':4,
        }
        devices.append(cisco_switch_ssh)

    # Loop for the commands received from Array
    for device in devices:
        print('\n'+'-> Establishing SSH2 Connection to IP ' + device['ip'] + '...')
        try:
            net_connect = ConnectHandler(**device, timeout=6)
            net_connect.enable()
            prompt = net_connect.find_prompt()
            logger.debug("prompt: %s", prompt)
            regex = r'^(.*)\#'
            regmatch = re.match(regex, prompt)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n'+'-> Connected to Device Name: ' + hostname+'\n')
            else:
                print(bcolors.FAIL +"-> Hostname Not Found!"+ bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", device['ip'] + bcolors.ENDC)
            continue

        # TimeStamp to save the files with date and time 
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        # Generating directory and filename after commands executed
        config_filename = "./results/cisco_switches/" + hostname + "-" + filetime + ".txt"
        files.append(config_filename)

        # Loop of execution of commands received from Array and Saving Results
        for cmd in commands:
            this_cmd = net_connect.send_command_timing(cmd)
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + cmd + bcolors.ENDC)
            print("".center(width1,'-'))
            print(this_cmd)
            os.makedirs(os.path.dirname(config_filename), exist_ok=True)
            config_filename_f = open(config_filename, 'a')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write('-> Command Executed: '+cmd+'\r')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write(this_cmd+'\n')
            config_filename_f.write('\n')
            config_filename_f.close()
        net_connect.disconnect()
        print('\n'+"".center(width1,'-'))
        print(bcolors.WARNING + 'File Generated: '+ config_filename + bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def hp_pre_def_telnet_1(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN + "*** HP Switch Connection via TELNET - [From File Commands] ***".center(width1,' ') + bcolors.ENDC)
    print(bcolors.OKGREEN + "Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ') + bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    try:
        commands = open('hp_commands.txt','r')
        commands = commands.read()
        commands = commands.strip().splitlines()
    except:
        input("\n" + bcolors.FAIL +"-> File 'hp_commands.txt' not found!, You need to create it first, Press [ENTER] to Exit"+ bcolors.ENDC)
        return

    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)

    start_time = datetime.datetime.now()

    # Loop with the data received above
    for HOST in hosts:
        print('\n'+'-> Establishing Telnet Connection to IP ' + HOST + '...')
        # sys.stdout.write( screen_code )
        try:
            tn = telnetlib.Telnet(HOST)
            # tn = telnetlib.Telnet(HOST, 23, 4)
            # If you want to use a debug please uncomment line below
            # tn.set_debuglevel(9)
            tn.read_until(b"Username:")
            tn.write(un.encode('ascii') + b"\r\n")
            tn.read_until(b"Password:")
            tn.write(pw.encode('ascii') + b"\r\n")
            tn.write(sup_user.encode('ascii') + b"\r\n")
            prompt = tn.read_until(b">")
            tn.read_until(b"Password:")
            tn.write(sup_pass.encode('ascii') + b"\r\n")
            tn.write(b"screen-length disable\r\n")
            tn.write(b"\r\n")
            # Get Prompt from Device
            a = prompt.replace(b'\r\n', b'')
            b = a.decode('utf-8')
            regex = r'^\<(.*)\>'
            regmatch = re.match(regex, b)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n' + '-> Connected to Device Name: ' + hostname + '\n')
            else:
                print(bcolors.FAIL + "-> Hostname Not Found!" + bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", HOST + bcolors.ENDC)
            continue

        # Variables for saving results after commands executed
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        config_filename = "./results/hp_switches/" + hostname + "_" + filetime + ".txt"

        # Loop for each command from the array
        for CMD in commands:
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + CMD + bcolors.ENDC)
            print("".center(width1,'-'))
            tn.write(CMD.encode('ascii') + b"\r\n")
            tn.write(b"\r\n")
        tn.write(b"quit\r\n")
        # Save Commands to a file and close session
        readoutput = tn.read_all().decode('ascii')
        print(readoutput)
        os.makedirs(os.path.dirname(config_filename), exist_ok=True)
        saveoutput = open(config_filename, 'a')
        saveoutput.write("".center(width1,'-')+'\r')
        saveoutput.write('-> Command(s) Executed:\r')
        saveoutput.write("".center(width1,'-')+'\r')
        saveoutput.write(readoutput+'\n')
        saveoutput.write('\n')
        saveoutput.close()
        tn.close()
        # Print Results in the Screen
        print("".center(width1,'-'))
        print(bcolors.WARNING+'File Generated: '+ config_filename+bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def hp_pre_def_ssh_1(name):
    print("".center(width1,'-'))
    print(bcolors.OKGREEN + "*** HP Switch Connection via SSH - [From File Commands] ***".center(width1,' ') + bcolors.ENDC)
    print(bcolors.OKGREEN + "Script Created by Marcelo Ferreira - Enjoy :-)".center(width1,' ') + bcolors.ENDC)
    print("".center(width1,'-'))
    print()

    # Hosts and Commands
    for remaining in range(max_attempts-1, -1, -1):
        host = input("Enter IPs separated by SPACE: ")
        if(len(host) != 0):
            break
        print(bcolors.FAIL +"-> Fields Cannot be Blank, You have", remaining, "attempt(s) left"+ bcolors.ENDC)
    else:
        Screen().input("-> Sorry...Execution Terminated, Press [ENTER] to Exit")
        return

    try:
        commands = open('hp_commands.txt','r')
        commands = commands.read()
        commands = commands.strip().splitlines()
    except:
        input("\n" + bcolors.FAIL +"-> File 'hp_commands.txt' not found!, You need to create it first, Press [ENTER] to Exit"+ bcolors.ENDC)
        return

    # Split Hosts and Commands for the Array below
    sys.stdout.write( screen_code )
    hosts = host.split()

    # Logging for the results below
    logging.basicConfig(format='[%(levelname)s] %(asctime)s %(message)s', level=logging.ERROR)
    logger = logging.getLogger("hp_switch_ssh")

    # Empty array to store hosts and Filenames
    devices = []
    files = []

    start_time = datetime.datetime.now()

    # Netmiko Variables and Loop
    for ip in hosts:
        hp_comware_ssh = {
            'device_type': 'hp_comware',
            'ip': ip,
            'username': un,
            'password': pw,
            'global_delay_factor': 0.2,
            # 'timeout':4,
        }
        devices.append(hp_comware_ssh)

    # Loop for the commands received from Array
    for device in devices:
        print('\n'+'-> Establishing SSH2 Connection to IP ' + device['ip'] + '...')
        # sys.stdout.write( screen_code )
        # Exception Handling
        try:
            net_connect = ConnectHandler(**device, timeout=6)
            prompt = net_connect.find_prompt()
            logger.debug("prompt: %s", prompt)
            regex = r'^\<(.*)\>'
            regmatch = re.match(regex, prompt)
            if regmatch:
                hostname = regmatch.group(1)
                print('\n' + '-> Connected to Device Name: ' + hostname + '\n')
            else:
                print(bcolors.FAIL+"-> Hostname Not Found!"+bcolors.ENDC)
        except:
            print(bcolors.FAIL +"-> Failed to connect to device", device['ip'] + bcolors.ENDC)
            continue

        # TimeStamp to save the files with date and time 
        filetime = datetime.datetime.now().strftime("%m-%d-%Y-%H-%M")
        # Generating directory and filename after commands executed
        config_filename = "./results/hp_switches/" + hostname + "_" + filetime + ".txt"
        files.append(config_filename)

        # Loop of execution of commands received from Array and Saving Results
        for cmd in commands:
            net_connect.send_command_timing(sup_user)
            net_connect.send_command_timing(sup_pass)
            net_connect.send_command_timing("screen-length disable")
            this_cmd = net_connect.send_command_timing(cmd)
            print("".center(width1,'-'))
            print(bcolors.OKBLUE + '-> Command Executed: ' + cmd + bcolors.ENDC)
            print("".center(width1,'-'))
            print(this_cmd)
            os.makedirs(os.path.dirname(config_filename), exist_ok=True)
            config_filename_f = open(config_filename, 'a')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write('-> Command Executed: '+cmd+'\r')
            config_filename_f.write("".center(width1,'-')+'\r')
            config_filename_f.write(this_cmd+'\n')
            config_filename_f.write('\n')
            config_filename_f.close()
        net_connect.disconnect()
        print("".center(width1,'-'))
        print(bcolors.WARNING+'File Generated: '+ config_filename+bcolors.ENDC)
        print("".center(width1,'-'))

    end_time = datetime.datetime.now()
    print('\n'+"Script Execution Finished in: {}".format(end_time - start_time).center(width1,'-'))
    Screen().input('\nPress [Enter] to Return to Main Menu')

def main():
    menu_format = MenuFormatBuilder().set_border_style_type(MenuBorderStyleType.HEAVY_BORDER) \
        .set_prompt("SELECT>") \
        .set_title_align('center') \
        .set_subtitle_align('center') \
        .set_left_margin(4) \
        .set_right_margin(4) \
        .show_header_bottom_border(True)

    ##################### ROOT MENU #####################    
    menu = ConsoleMenu("Main Menu", "Network Automation Tool - Version 1.3a",
                       epilogue_text=("Author: Marcelo Ferreira CCIE #65117 - mferreira85@gmail.com"), formatter=menu_format)

#----------------------------------------------------------------------------------------------------------------------------------------------#
    ##################### SUBMENU FOR HP SWITCHES #####################
    hp_commands = ConsoleMenu("HP Comware 5.2 Switches", "Please select desired option and corresponding number below",
                            formatter=menu_format)
    
    function_hp_telnet = FunctionItem("HP Switch (Telnet) - Commands on Screen", hp_telnet, args=['MF'])
    function_hp_ssh = FunctionItem("HP Switch (SSH) - Commands on Screen", hp_ssh, args=['MF'])
    function_hp_sw_1 = FunctionItem("HP Switch (Telnet) - Commands from [TXT FILE]", hp_pre_def_telnet_1, args=['MF'])
    function_hp_sw_2 = FunctionItem("HP Switch (SSH) - Commands from [TXT FILE]", hp_pre_def_ssh_1, args=['MF'])
    hp_commands.append_item(function_hp_telnet)
    hp_commands.append_item(function_hp_ssh)
    hp_commands.append_item(function_hp_sw_1)
    hp_commands.append_item(function_hp_sw_2)

    # Menu item for opening submenu hp switch
    submenu_item_hp_switch = SubmenuItem("HP Switches (Comware 5.2)", submenu=hp_commands)
    submenu_item_hp_switch.set_menu(menu)
#-----------------------------------------------------------------------------------------------------------------------------------------------#
    ##################### SUBMENU FOR CISCO PRE-DEFINED SWITCHES #####################
    cisco_sw_predefined = ConsoleMenu("Cisco Switches On [Screen] Commands and from [TXT FILE] Commands",
                                    prologue_text="For Commands from [FILE], please create a text filename called \
    <cisco_commands.txt> and add all the commands you want to be executed.",
                                    formatter=MenuFormatBuilder()
                                    .set_prompt("SELECT>")
                                    .set_title_align('center')
                                    .set_subtitle_align('center')
                                    .set_border_style_type(MenuBorderStyleType.HEAVY_BORDER)
                                    .show_prologue_top_border(True)
                                    .show_prologue_bottom_border(True))

    function_cisco_sw_0 = FunctionItem("Cisco Switches - On [Screen] Commands", cisco_switch, args=['MF'])
    function_cisco_sw_1 = FunctionItem("Cisco Switches - From [File] Commands", cisco_pre_def_sw_1, args=['MF'])
    cisco_sw_predefined.append_item(function_cisco_sw_0)
    cisco_sw_predefined.append_item(function_cisco_sw_1)

    # Pre-defined Submenu for Cisco SW
    submenu_item_cisco_sw_pre_defined = SubmenuItem("Cisco Switches (IOS and IOS-XE)", submenu=cisco_sw_predefined)
    submenu_item_cisco_sw_pre_defined.set_menu(menu)
#-----------------------------------------------------------------------------------------------------------------------------------------------#
    ##################### SUBMENU FOR CISCO PRE-DEFINED WLANs #####################
    cisco_wlc_predefined = ConsoleMenu("WLAN Menu", "Please select the desired Option below",
                            formatter=menu_format)

    function_cisco_wlc_0 = FunctionItem("Wireless LAN - On [Screen] Commands", wlc, args=['MF'])
    function_cisco_wlc_0_1 = FunctionItem("Wireless LAN - From [File] Commands", wlc_from_file, args=['MF'])
    cisco_wlc_predefined.append_item(function_cisco_wlc_0)
    cisco_wlc_predefined.append_item(function_cisco_wlc_0_1)

    # Pre-defined Submenu for Cisco WLC
    submenu_item_cisco_wlc_pre_defined = SubmenuItem("Cisco Wireless LAN Controller (AireOS)", submenu=cisco_wlc_predefined)
    submenu_item_cisco_wlc_pre_defined.set_menu(menu)
#-----------------------------------------------------------------------------------------------------------------------------------------------#
    ##################### CALL MENU ITEMS #####################
    menu.append_item(submenu_item_hp_switch)
    menu.append_item(submenu_item_cisco_sw_pre_defined)
    menu.append_item(submenu_item_cisco_wlc_pre_defined)

    # Show the menu
    menu.start()
    menu.join()

if __name__ == "__main__":
    main()
