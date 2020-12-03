# network_tool
Network Automation Tool

This Network Automation Tool helps Network Engineers to Send Commands and Configurations to HP Comware 5.2, Cisco Switches with IOS or IOS-XE and Cisco Wireless Controllers with AireOS

In order to make this to work well, please add your HP Supervisor password and Cisco Secret into Lines 78 and 79. After that run the script with python 3.8.6 preferrable, script will ask your tacacs or radius credentials that you use to connect to those network devices or you can simply use username and password you connect to them if you are not using tacacs or radius.

The Menu will look like this below, select the option to go to next sub menus. You can send commands or configs on screen or using a file:

    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                                                                     ┃
    ┃                              Main Menu                              ┃
    ┃                                                                     ┃
    ┃               Network Automation Tool - Version 1.3a                ┃
    ┃                                                                     ┃
    ┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
    ┃                                                                     ┃
    ┃    1 - HP Switches (Comware 5.2)                                    ┃
    ┃    2 - Cisco Switches (IOS and IOS-XE)                              ┃
    ┃    3 - Cisco Wireless LAN Controller (AireOS)                       ┃
    ┃    4 - Exit                                                         ┃
    ┃                                                                     ┃
    ┃                                                                     ┃
    ┃  Author: Marcelo Ferreira CCIE #65117 - mferreira85@gmail.com       ┃
    ┃                                                                     ┃
    ┃                                                                     ┃
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
    SELECT>
