#!/usr/bin/python3
import openshift as oc
import datetime
import pytz
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from prettytable import PrettyTable
import itertools
# TO DO - Create a requirement.txt - e.g. requires "openshift" "requests"

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
        # Easy to add resoruces 
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
    print(empty_ns_table)
    print("\nNumber of empty namespaces: ", nr_of_empty_ns)
    return empty_ns


# Checking each route with either http or https depending on termination.
def check_routes(dyn_client):
    all_routes = get_all_routes(dyn_client)
    route_table = PrettyTable(['Route', 'Status Code', 'Termination'])
    checked_routes = {}
    print("\nRoutes:\n")
    for route, value in all_routes.items():
        with requests.Session() as session:
            if value is None:
                response = session.get("http://" + route, verify=False)
                checked_routes.update({route: response.status_code})
                route_table.add_row([route, response.status_code, "http"])
            else:
                response = session.get("https://" + route, verify=False)
#                response = session.get("https://" + route, verify=True)
                checked_routes.update({route: response.status_code})
                route_table.add_row([route, response.status_code, value.termination])
    print(route_table)
    return checked_routes


# Saving all routes with their termination (edge, passthrough, reencrypt or None)
def get_all_routes(dyn_client):
    route_dict = {}
    v1_routes = dyn_client.resources.get(api_version='route.openshift.io/v1', kind='Route')
    for route in v1_routes.get().items:
          route_dict.update({route.spec.host: route.spec.tls})
    return route_dict


# Getting the failed pods and appending them to their namespaces.
def get_failed_pods(v1):
    number_of_failed_pods = 0
    failed_pods = {}
    response = v1.list_pod_for_all_namespaces()
    failed_pods_table = PrettyTable(['Namespace', 'Pod name', 'Status'])
    for pod in response.items:
        failed_pods[pod.metadata.namespace] = []
    for pod in response.items:
        if not pod.status.container_statuses[0].state.running and "Succeeded" not in pod.status.phase:
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
    print("\nFailed pods:\n")
    print(failed_pods_table)
    print("\nNumber of failed pods: ", number_of_failed_pods)
    return(failed_pods)

# Prints a table of resource usage. Calls the percentage calc to add a % of resource usage of the nodes.
def node_check(v1):
    api = client.CustomObjectsApi()
    cluster_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    node_table = PrettyTable(['Node name', 'Role', 'CPU', 'CPU %', 'Memory', 'Memory %'])
    node_cpu = cpu_check(v1)
    node_mem = mem_check(v1)
    node_status = []
    cpu = Percentage_calc(cpu_check(v1), cpu_cap(v1))
    cpu.percentage()
    mem = Percentage_calc(mem_check(v1), mem_cap(v1))
    mem.percentage()
  
    print("\nNode usage: \n")
    for node, v, v2 in zip(cluster_nodes['items'], cpu.percentage().values(), mem.percentage().values()):
        node_table.add_row([node['metadata']['name'], [string for string in node['metadata']['labels'] if "node-role.kubernetes" in string], node['usage']['cpu'], [v], node['usage']['memory'], [v2]])
    print(node_table)
    print("\nNodes in cluster: ",(len(cluster_nodes['items'])))


# Current millicore usage / (cores * 1000) 
# Saving CPU capacity of the nodes
def cpu_cap(v1):
    r = v1.list_node()
    cpu_cap_node = {}
    for node_item in r.items:
        cpu_cap_node.update({node_item.metadata.name: int(node_item.status.capacity['cpu'])})
    for key, value in cpu_cap_node.items():
        cpu_cap_node.update({key: value * 1000})
    return cpu_cap_node


# Saving memory capacity of the nodes
def mem_cap(v1):
    r = v1.list_node()
    mem_cap_node = {}
    for node_item in r.items:
        mem_cap_node.update({node_item.metadata.name: int(node_item.status.capacity['memory'][:-2])})
    for key, value in mem_cap_node.items():
        mem_cap_node.update({key: value // 1024})
    return mem_cap_node


# Gathering the node CPU usage
def cpu_check(v1):
    api = client.CustomObjectsApi()
    node_cpu_usage = {}
    cluster_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    for node in cluster_nodes['items']:
        node_cpu_usage.update([(node['metadata']['name'],int(node['usage']['cpu'][:-1]))])
    return node_cpu_usage


# Gathering the node memory usage in MB
def mem_check(v1):
    api = client.CustomObjectsApi()
    node_mem_usage = {}
    cluster_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    for node in cluster_nodes['items']:
        node_mem_usage.update([(node['metadata']['name'],int(node['usage']['memory'][:-2]))])
    for key, value in node_mem_usage.items():
        node_mem_usage.update({key: value // 1024})
    return node_mem_usage

# Trying to create a class and call a general percentage calc function for CPU and Memory.
class Percentage_calc:
    """
    Convert resource usage to percentage
    """
    def __init__(self, usage, capacity):
        self.usage = usage
        self.capacity = capacity


    def percentage(self):
        perc_dict = {}
        for (k, v), (k2, v2) in zip(self.usage.items(), self.capacity.items()):
            perc_dict.update({k: v / v2 * 100})
        for k,v in perc_dict.items():
            perc_dict.update({k: "%.2f" % v + "%"})
        return perc_dict


# List users with cluster-admin rights
# Multiple cluster-admin/s rolebindings. Need to loop through them all and gather all "subjects" to add to table.
def admin_check(v1):
    api = client.RbacAuthorizationV1Api()
    admin_table = PrettyTable(['Users', 'Groups'])
    cluster_items = []
    cluster_items2 = []
    cluster_admin_groups = []
    cluster_admin_users = []
    response = api.list_cluster_role_binding().items
    for role in response:
        if "cluster-admin" in role.metadata.name:
            cluster_items.append(role.subjects)
    for index in range(len(cluster_items)):
        for index2 in range(len(cluster_items[index])):
            cluster_items2.append(cluster_items[index][index2])
    for item in cluster_items2:
        if "Group" in item.kind:
            cluster_admin_groups.append(item.name)
        elif "User" in item.kind:
            cluster_admin_users.append(item.name)


    # Changing API to collect group info
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1_groups = dyn_client.resources.get(api_version='user.openshift.io/v1', kind='Group')

    # If a group is part of a cluster-admin group, add the users to the cluster admins list.
    for group in v1_groups.get().items:
        if group.metadata.name in cluster_admin_groups:
            cluster_admin_users.extend(group.users)
    
    # Removing duplicate entries from cluster admins list.
    cluster_admin_users = list(dict.fromkeys(cluster_admin_users))
    for admin, admin_group in itertools.zip_longest(cluster_admin_users, cluster_admin_groups, fillvalue=' '):
            admin_table.add_row([admin, admin_group])
    admin_counter = len(cluster_admin_users)
    print("\n",admin_table)
    print("\nThere are:", admin_counter, "cluster-admins in the cluster")
    return cluster_admin_users


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
    print("\nWorkload running longer than 9 days:\n")    
    print(old_workload_table)
    print("\nNumber of old pods: \t", (len(old_pods)))
    return old_pods

def main():
    config.load_kube_config()
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1=client.CoreV1Api()
    check_empty_namespaces(v1)
    check_routes(dyn_client)
    get_failed_pods(v1)
    node_check(v1)
    admin_check(v1)
    workload_age(v1)

if __name__ == "__main__":
    main()

