# LabManager
This app is meant for automating tasks like updating machines, rebooting, and gathering info. 

## Current Features

- Gather info for devices
- Reboot and shutdown devices.

## Dependencies
- Python3.10+
- Running instance of MongoDB

## Installation 

1. Extract the zip to a folder.
2. Open a terminal to the extracted terminal.
3. Run:

```bash
python3 -m pip install -r 'requirements.txt'
```
4. Now add devices to the database using "database_interface.py" inside of /bin/db
5. Run the app by using main.py (For testing)

## Usage guide

**Devices**

The device db is located inside of the mongodb. Devices are added, modified, and removed using database_interface.py. For now passwords are stored in plain text. 

Each device in the Json db are initialled to the dictionary called "Device_instances" as a class. Device actions are called by using the DNS name of the device and calling a method to it. This looks like this:

```python
output = Device_instances["dns_name"].dynamic_method_call("update_info")
```

**Custom device types**

One can create a new device class by following the format of 

## Contribute

If you found bugs, report them on the issues page. If you modified something, make a pull request.

## Author Notes

This my first large project. There will be weird things in the source code... Please reach out to me for suggestions on improvements!  

The end goal is to create a flask app to administrate the lab. 

**Planned Features:**
- CSV DB importer. 
- Device roles (ex: domain controller, pxe server, dns server, dhcp host, end user device)
- Cli interface 
- Move device creation to a front end with automation with device roles.