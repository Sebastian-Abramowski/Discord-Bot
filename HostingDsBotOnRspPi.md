# How to prepare Raspberry Pi to host a discord bot

## Configurating Rasberry Pi

#### Python

Python comes preinstalled in Raspberry Pi OS, but you check it:

```bash
python3 --version
```

Install required dependencies:

If your bot has requirements.txt

```bash
pip install -r requirements.txt
```

If your bot doesn't have requirements.txt, you can just pip install required packages one by one.

#### FFMPEG

Music bot requires the ffmpeg executable in your path environment to work
(if you want to host a bot that doesn't need it, skip this step)

FFMPEG can also come preinstalled in Raspberry Pi OS

```bash
ffmpeg -version
```

If you don't have it

```bash
sudo apt-get install ffmpeg
ffmpeg -version
```

## Hosting discord bot

Using systemd to automatically start my program which run the bot.
<service_name> can be for example 'run_bot'

Creating a new custom service

```bash
sudo nano /lib/systemd/system/<service_name>.service
```

Writing to this file:

```bash
[Unit]
Description=<description of your bot>
After=multi-user.target

[Service]
Type=simple
User=<user_name_is_raspberry_pi>
WorkingDirectory=/absolute/path/to/your/working/directory
ExecStart=python <absolute_path_to_your_file.py_that_runs_the_bot>
Restart=always

[Install]
WantedBy=multi-user.target
```

Enabling the system service

```bash
sudo systemctl enable <service_name>.service
```

Starting service

```bash
sudo systemctl start <service_name>
```

Check status of the service

```bash
sudo systemctl status <service_name>
```

To check logs of the service

```bash
journalctl -u <service_name>.service
```

If you want to check if you did everything correctly, reboot the system for example by 'sudo reboot' and check if your program in service was run correctly

---

Other comments that might be helpful in case of some problems

```bash
sudo systemctl daemon-reload # if you changed content of .service file and you wish to reload them
sudo systemctl stop <service_name> # if you want to stop the service
sudo systemctl kill <service_name> # if you want to simulate some problems in a service, if you have set 'Restart=always' in .service file, then the program will be restarted
sudo systemctl disable <service_name> # if you want to disable service, so that it wouldn't start automatically
sudo systemctl restart <service_name>.service # if you want to restart your program put in service
```

## Appendix: Connecting to Raspberry Pi through computer with the same WIFI connection

#### Setting up static IP address for SSH and VNC

Although it is not needed, it might help, if you wanted to change something without directly using your Raspberry Pi through ssh (IP of your Raspberry Pi will remain the same, so everytime you connect to your Raspberry Pi via ssh you will be able to use the same IP address).

Turn on connection through SSH in Raspberry Pi: Click icon in left top corner -> Preferences -> Raspberry Pi Configuration -> Interfaces -> Turn on SSH

Setting up static IP:

```bash
sudo nano /etc/dhcpcd.conf
```

Here add to the existing file:

```bash
interface eht0
interface wlan0
static ip_address=<address_ip_that_you_want_to_set_to>
static routers=<address_ip_of_your_router>
static domain_name_servers=<some DNS e.g. 8.8.8.8>
```

Don't remove dhcp configuration, just set static ip_address to some very high or very low depending on your possible address range (so that DNS couldn't give your address to some other device - ideally you should check DNS range, but if your router's IP is e.g. 198.168. 1.1, you can set static IP to 198.168.1.2 and it should be working fine). Remember that if you were to connect your device to some other WIFI, you should comment pieces of code responsible for static IP configuration in order to dynamically get an IP.

#### Connecting via SSH

Then from your computer that uses the same WIFI as your Raspberry Pi:

```bash
ssh -v <user_name_in_raspberry_pi>@<ip_address_of_respberry_pi>
```

If something went wrong, you can check SSH logs on Raspberry Pi:

```bash
sudo cat /var/log/auth.log
```

---

If you wanted to connect to your Raspberry Pi through ssh via some different network compared to network that Raspberry Pi is connected to, you should do something with port 22 forwarding on your router (I didn't do it), how to do it: https://www.youtube.com/watch?v=ZKfnGqMrnug

#### Connecting to graphical interface via VNC viewer

VNC viewer allow you remotely using graphical interface of Raspberry Pi through.

Download VNC Viewer: https://www.realvnc.com/en/connect/download/viewer/

Turn on VNC setting on Raspberry Pi: Click icon in left top corner -> Preferences -> Raspberry Pi Configuration -> Interfaces -> Turn on VNC

Open VNC viewer and connect to your Raspberry Pi through its IP address, after that you will be told to pass the user name and password of your Rasbperry Pi and eveyrthing is set.
