#!/usr/bin/python3
import openshift as oc
from kubernetes import client, config
from prettytable import PrettyTable


# Get all namespaces
def get_all_namespaces(v1):
    namespace_list = []
    for i in v1.list_namespace().items:
      namespace_list.append(i.metadata.name)
    return namespace_list

# Checks for namespaces without pods.
def check_empty_namespaces(v1):
    all_ns = get_all_namespaces(v1)
    nr_of_empty_ns = 0
    empty_ns = []
    empty_ns_table = PrettyTable(['Empty namespaces'])
    for ns in all_ns:
        pod_list = v1.list_namespaced_pod(ns).items
        # Easy to add resoruces, problem is performance
        #cm_list = v1.list_namespaced_config_map(ns).items
       # if pod_list == [] and cm_list == []:
        if pod_list == []: 
            empty_ns.append(ns)
    for item in empty_ns:
        if "openshift" in item or "kube" in item or "default" in item:
            pass
        else:
            empty_ns_table.add_row([item])
            nr_of_empty_ns +=1
    print("\n", empty_ns_table)
    print("\nNumber of empty namespaces: ", nr_of_empty_ns)
    return empty_ns
