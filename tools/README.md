Surface Scanner
=========

A simple cluster scanner tool.

Performs a surface scan on a cluster to identify it's general state. Currently does:
- Simple curl check to the API endpoints.
- Looks at the node compute usage.
- Identifies namespaces that currently has no workload
- Checks the status code for all routes.
- Scans the cluster for Pending, Failed and CrashLoop pods.
- Checks for pods that has been running for more than 9 days.

The tool prints out the results directly while also dumping everything to a report file that can be viewed later.

To do
------------

Better data handling - cleaner format of the report etc.

Requirements
------------

The tool is created for OpenShift clusters and thus requires the OC client to be installed and a user with sufficient privileges for running these commands.
- oc
- privileged user

The tool does a check to see if these requirements are fullfilled during start.

Options
--------------

* -s  Performs the scan
* -h  Prints a help message and exits

Example Use
----------------
```
   _____             __                  _____                                 
  / ____|           / _|                / ____|                                
 | (___  _   _ _ __| |_ __ _  ___ ___  | (___   ___ __ _ _ __  _ __   ___ _ __ 
  \___ \| | | | '__|  _/ _` |/ __/ _ \  \___ \ / __/ _` | '_ \| '_ \ / _ \ '__|
  ____) | |_| | |  | || (_| | (_|  __/  ____) | (_| (_| | | | | | | |  __/ |   
 |_____/ \__,_|_|  |_| \__,_|\___\___| |_____/ \___\__,_|_| |_|_| |_|\___|_|   
                                                                               
                                                                               
 Detected OpenShift version: oc v3.11.43

Usage: surface-scanner.sh [options]

Options:
    -s      Performs a surface scan of the cluster - reports the results and sends it to /tmp/ClusterReport.txt
    -h		  Prints this messages and exits.

```

License
-------

BSD

Author Information
------------------

Oscar Lindholm 

olindhol@redhat.com