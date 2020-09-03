# Gateway Pi 
Gateway Pi is a python program that acts as a gateway between the Smart Home Assistant and the sensors and actuators connected to the Pi.

## Setup
Run the script
```bash
source setup.sh
```
to install the virtual environment necessary for the application to run.

### Standalone Script
To run as a standalone program enter the virtual environment with
```bash
source ./virtual/bin/activate
```
and then run the main.py script
```bash
python main.py
```

### Service 
To run the program as a service on the raspberry pi you need to:

#### 1. Copy the file gateway-pi.service to /lib/systemd/system
```bash
cp gateway-pi.service /lib/systemmd/system
```

#### 2. Execute these commands in the terminal
```bash
sudo systemctl daemon-reload
sudo systemctl enable gateway-pi.service
sudo systemctl start gateway-pi.service
```

You can then check if the service is running by typing
```bash
systemctl status gateway-pi.service
```
