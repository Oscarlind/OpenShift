#!/usr/bin/python3
import openshift as oc
import datetime
import pytz
from kubernetes import client, config
from prettytable import PrettyTable


# Scanning for pods that are older than 9 days and not in any cluster specific namespace.
def workload_age(v1):
    response = v1.list_pod_for_all_namespaces()
    date_now = datetime.datetime.now(pytz.utc)
    cut_off_date = date_now - datetime.timedelta(days=9)
    old_pods = {}
    old_workload_table = PrettyTable(['Namespace', 'Pod'])
    # Simple for loop to get the old pods.
    for pod in response.items:
        if "openshift" not in pod.metadata.namespace and "kube" not in pod.metadata.namespace:
                if cut_off_date >= pod.metadata.creation_timestamp:
                    old_pods[pod.metadata.name] = pod.metadata.namespace
                    old_workload_table.add_row([pod.metadata.namespace, pod.metadata.name])
    print("\n\033[95mWorkload running longer than 9 days:\033[0m\n")    
    print(old_workload_table)
    print("\nNumber of old pods: \t", (len(old_pods)))
    return old_pods
