Installation Instructions
-------------------------

1. On a setup running OpenStack or Devstack, download the zip file containing the source code.
2. Edit the connection.conf file to record the Controller, Compute and database connection information. Please note that it is okay if they are all on the same machine.
3. Start the program by running `python main.py`

Note: Please note that to get any meaningful predictions, you would need existing virtual machines on OpenStack that are generating data in a repeated pattern.

File Description
----------------

Filename | Purpose | New/Modified | Comments
------------ | ------------- | ------------ | -------------
Holt_Winters.py | Machine learning algorithm which predicts user's bandwidth for next hour and stores value in database | new | Added LOC-115
README.md | List of files and it's purpose and comments | new | Added LOC-13
connection.conf | Configure file having all the configuration details for host  | new | Added LOC-14
dataCollection.py | collects data to the database | new | Added LOC-87
dataDump.py | Dumps data to the database | new | Added LOC-90
portsInfo.py | Collects bandwidth corresponding to each VMs of tenant per port basis | new | Added LOC-93
presentation.py | script that invokes the jinja/django template from template/presentation.html | new | Added LOC-152
rule_generator.py | Rules for the OVS | new | Added LOC-178
setup.py | Install package required | new | Added LOC-28
tox.ini | runs test suite on supported python versions | new | Added LOC-14
template/presentation.html | presentation html for each tenant with bandwidth and predicted bandwidth graphs | new | Added LOC-150
