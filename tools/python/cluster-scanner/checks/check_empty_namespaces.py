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
    number_of_empty_ns = 0
    all_ns = get_all_namespaces(v1)
    empty_ns_table = PrettyTable(['Empty namespaces'])
    all_pods = v1.list_pod_for_all_namespaces()
    all_pods_ns = []
    for pod in all_pods.items:
        all_pods_ns.append(pod.metadata.namespace)
    # Removing duplicates
    all_pods_ns = list(dict.fromkeys(all_pods_ns))
    # Getting the difference, the empty namespaces that is.
    empty_namespace_set = list(set(all_ns).difference(all_pods_ns))
    # Converting set to list for easier conditional check.
    empty_ns_list = list(empty_namespace_set)
    for i in empty_ns_list:
        if "openshift" in i or "kube" in i or "default" in i:
            pass
        else:
            empty_ns_table.add_row([i])
            number_of_empty_ns +=1
    print("\n\033[95mEmpty namespaces\033[0m\n", empty_ns_table)
    print("\nNumber of empty namespaces: ", number_of_empty_ns)
    return empty_ns_list
