
bwt_api
=======

Python library to access the local API of BWT Perla devices.


Requirements
------------

- At least firmware version 2.02xx
- a network connection by LAN or WiFi
- device needs to be registered. You will receive a *login code* needed later
- enable the API in the menu (Settings > General > Connection)


Usage examples
--------------

    bwt --help

    bwt --host="<ip address>" --code="<login code>" current

    bwt --host="<ip address>" --code="<login code>" daily

    bwt --host="<ip address>" --code="<login code>" monthly

    bwt --host="<ip address>" --code="<login code>" yearly
