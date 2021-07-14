#!/usr/bin/python3
from kubernetes import client, config
from prettytable import PrettyTable


# Getting the failed pods and appending them to their namespaces.
def get_failed_pods(v1):
    number_of_failed_pods = 0
    failed_pods = {}
    response = v1.list_pod_for_all_namespaces()
    failed_pods_table = PrettyTable(['Namespace', 'Pod name', 'Status'])
    for pod in response.items:
        failed_pods[pod.metadata.namespace] = []
    for pod in response.items:
        if not pod.status.container_statuses:
            failed_pods[pod.metadata.namespace].append(pod.metadata.name + ": " + pod.status.phase)
            failed_pods_table.add_row([pod.metadata.namespace, pod.metadata.name, pod.status.phase])
        elif not pod.status.container_statuses[0].state.running and "Succeeded" not in pod.status.phase:
            if pod.status.container_statuses[0].state.waiting:
                failed_pods[pod.metadata.namespace].append(pod.metadata.name + ": " + pod.status.container_statuses[0].state.waiting.reason)
                failed_pods_table.add_row([pod.metadata.namespace, pod.metadata.name, pod.status.container_statuses[0].state.waiting.reason])
                number_of_failed_pods +=1
            elif "Error" in pod.status.container_statuses[0].state.terminated.reason:
                failed_pods[pod.metadata.namespace].append(pod.metadata.name + ": " + pod.status.container_statuses[0].state.terminated.reason)
                failed_pods_table.add_row([pod.metadata.namespace, pod.metadata.name, pod.status.container_statuses[0].state.terminated.reason])
            else:
                failed_pods[pod.metadata.namespace].append(pod.metadata.name + ": " + pod.status.phase)
                failed_pods_table.add_row([pod.metadata.namespace, pod.metadata.name, pod.status.phase])
                number_of_failed_pods +=1
    print("\n\033[95mFailed pods:\n\033[0m")
    print(failed_pods_table)
    print("\nNumber of failed pods: ", number_of_failed_pods)
    return(failed_pods)
