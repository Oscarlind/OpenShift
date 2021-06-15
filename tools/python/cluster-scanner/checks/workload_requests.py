#!/usr/bin/python3
from prettytable import PrettyTable

# Checks for containers that have not set any resource REQUESTS.
def check_requests(v1):
    no_requests = {}
    no_requests_counter = 0
    res_pods = v1.list_pod_for_all_namespaces()
    no_requests_table = PrettyTable(['Namespace', 'Pod name'])
    for pod in res_pods.items:
        no_requests[pod.metadata.namespace] = []
    for i in res_pods.items:
        for j in i.spec.containers:
            if not j.resources.requests and "openshift" not in i.metadata.namespace and "kube" not in i.metadata.namespace and "default" not in i.metadata.namespace:
                no_requests_table.add_row([i.metadata.namespace, i.metadata.name])
                no_requests[i.metadata.namespace].append(i.metadata.name)
                no_requests_counter += 1
    if no_requests_counter <= 50:
        print("\n",no_requests_table)
    else:
        print("\nLarge number of pods with no REQUEST set, assuming resource requests not widely used. - EXCLUDING TABLE")
    print("\nNumber of pods without requests specified: ",no_requests_counter)