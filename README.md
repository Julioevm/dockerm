# dockerm
Manage appium docker containers with this little program.

## requires
`pip install docker`

## setup

Create a file on the same directory the script is in, by default devices.txt, with a list of device names and ports like:
```
galaxya5;4001
galaxys7;4002
galaxys8;4003
```

These names will be used to look for the same device name in the /dev/ folder  to link it with the docker container. 