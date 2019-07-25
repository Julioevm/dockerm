#! python3

# dockerm.py - Program to manage the docker containers running appium.
# made by Julio Eliseo Valls Martínez 

import os
import docker

data = {}
client = docker.from_env()
filename = 'devices.txt'
pwd = os.getcwd() + "/"
home = os.getenv("HOME")
run = True

local_ip = "10.248.56.225"
hub_ip = "172.16.0.2"
hub_port = "5566"

def load_containers():
    print("Loading current running containers:")
    containers = client.containers.list(all=True)

    print('0. Exit')
    for x in range(len(containers)):
        container = containers[x]
        print(str(x + 1) + '. ' + container.name + ' => ' + container.status)
    print(str(len(containers) + 2) + '. Create new container')
    return containers

def remove_container(container):
    print('Stopping container...')
    container.stop()

    print('Removing container...')
    container.remove()

def create_container(name):
    print('Creating container...')

    #get the device port
    port=data[name]
    #get the device location
    syslink = os.readlink('/dev/' + name)
    client.containers.run(
    'appium/appium:latest',
    detach=True,
    name=name,
    environment=["CONNECT_TO_GRID=true",
                "CUSTOM_NODE_CONFIG=true",
                "APPIUM_HOST='"+ local_ip +"'",
                "APPIUM_PORT=" + port,
                "SELENIUM_HOST='" + hub_ip + "'",
                "SELENIUM_PORT=" + hub_port],
    ports={'4723/tcp': port},
    devices=["/dev/" + syslink + ":/dev/" + syslink + ":rwm"],
    volumes={home + '.android': {'bind':'/root/.android'},
           pwd + name + '.json':{'bind':'/root/nodeconfig.json'}})

def load_data():
    if os.path.isfile(filename):
        print('Devices data found, loading...')
        with open(filename) as fh:
            data = dict(line.strip().split(';', 1) for line in fh)

        print(data)
    else:
        print('No device data found. Make sure to have devices.txt in the same dir you run the script!')
    return data

def get_input():
    try:
        mode = int(input('Enter a number:'))
    except ValueError:
        print("Not a number.")
    return mode

def select_new_container():
    print("List containers from data set.")

    devices = list(data.keys())
    print('0. Cancel')
    for x in range(len(devices)):
        print(str(x + 1) + '. ' + devices[x])

    mode = get_input()
    
    if mode > 0 or mode <= len(devices) + 1:
        device = devices[mode - 1] 
        print('Selected ' + device)
        #check that its not running already
        containers = client.containers.list(all=True, sparse=True, filters={'name': device})
        if len(containers) > 0:
            print('Theres already a container of that type running, go back and restart it or choose a different one')
        else:
            return device

    return None
data = load_data()

while run:

    containers = load_containers()
    
    print('What container do you want to restart?')
    mode = get_input()

    if mode == 0:
        break;
    elif mode == len(containers) + 2:
        new_container = select_new_container()
        if new_container != None:
            create_container(new_container)
        
    else:
        container = containers[mode - 1]
        name = container.name
        print('Restarting container ' + name)
        remove_container(container)   
        create_container(name)

