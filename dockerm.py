#!/usr/bin/env python3

# dockerm.py - Program to manage the docker containers running appium.
# made by Julio Eliseo Valls Martínez
import os
import sys
import docker
import socket

data = {}
client = docker.from_env()
FILENAME = 'devices.txt'
pwd = os.getcwd() + "/"
home = os.getenv("HOME")
RUN = True

LOCAL_IP = ""
HUB_IP = "172.16.0.2"
HUB_PORT = "5566"

def load_containers():
    return client.containers.list(all=True)

def print_containers(containers):
    print('0. Exit')
    for x in range(len(containers)):
        container = containers[x]
        print(str(x + 1) + '. ' + container.name + ' => ' + container.status)

def remove_container(container):
    print('Stopping container...')
    container.stop()

    print('Removing container...')
    container.remove()

def create_container(name):
    print('Creating container...')

    #get the device port
    port = data[name]
    #get the device location
    syslink = os.readlink('/dev/' + name)
    client.containers.run(
    'appium/appium:latest',
    detach=True,
    name=name,
    environment=["CONNECT_TO_GRID=true",
                "CUSTOM_NODE_CONFIG=true",
                "APPIUM_HOST='"+ LOCAL_IP +"'",
                "APPIUM_PORT=" + port,
                "SELENIUM_HOST='" + HUB_IP + "'",
                "SELENIUM_PORT=" + HUB_PORT],
    ports={'4723/tcp': port},
    devices=["/dev/" + syslink + ":/dev/" + syslink + ":rwm"],
    volumes={home + '.android': {'bind':'/root/.android'},
           pwd + name + '.json':{'bind':'/root/nodeconfig.json'}})

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def load_data():
    if os.path.isfile(FILENAME):
        print('Devices data found, loading...')
        with open(FILENAME) as fh:
            data = dict(line.strip().split(';', 1) for line in fh)

        print(data)
    else:
        print('No device data found. Make sure to have devices.txt in the same dir you run the script!')
        quit()
    return data

def get_input():
    mode = input('Enter a number or A for all, N to create a new container:')
    if not mode.isdigit and mode not in ('A', 'a', 'N', 'n'):
        print("Not a valid option.")
        return None
    return mode

def select_new_container():
    print("List containers from data set.")

    devices = list(data.keys())
    print('0. Cancel')
    for x in range(len(devices)):
        print(str(x + 1) + '. ' + devices[x])

    mode = get_input()
    
    if mode > 0 and mode <= len(devices) + 1:
        device = devices[mode - 1] 
        print('Selected ' + device)
        #check that its not running already
        containers = client.containers.list(all=True, sparse=True, filters={'name': device})
        if len(containers) > 0:
            print('Theres already a container of that type running, go back and restart it or choose a different one')
        else:
            return device

    return None

def restart_container(container):
    print('Restarting container ' + container.name)
    remove_container(container)   
    create_container(container.name)

def restart_all_containers(containers):
    print('Restarting all available containers...')
    for container in containers:
        restart_container(container)

LOCAL_IP = get_ip()
data = load_data()

# If we pass the -a or --all argument, we restart all containers and skip interactive mode.
if len(sys.argv) > 1 and sys.argv[1] in ('-a', '--all'):
    restart_all_containers(load_containers())
    RUN = False

while RUN:
    containers = load_containers()
    print_containers(containers)

    if len(containers) > 0:
        print('What container do you want to restart?')
    else:
        print('No existing containers found.')
    mode = get_input()

    if mode == 0:
        break
    elif mode in ('N', 'n'):
        new_container = select_new_container()
        if new_container is not None:
            create_container(new_container)
    elif mode in ('A', 'a'):
        restart_all_containers(containers)
    elif mode.isdigit():
        container = containers[int(mode) - 1]
        restart_container(container)
