#!/usr/bin/python3
import openshift as oc
import requests
import urllib3
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from prettytable import PrettyTable
# For OCP resources, use dyn_client instead of 'v1'

# Api check
#url = ''
#url_ssl = False
#r = requests.get(url, verify=url_ssl)
#print(r.status_code)
#print(r.json)


# TO DO - Create a requirement.txt - e.g. requires "openshift" "requests"
# TO DO - New def to check only for SSL routes - which TLS route is broken

# Get all namespaces
def get_all_namespaces(v1):
    namespace_list = []
    for i in v1.list_namespace().items:
      namespace_list.append(i.metadata.name)
    return namespace_list

# Checks for namespaces without pods
def check_empty_namespaces(v1):
    all_ns = get_all_namespaces(v1)
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
        if ("openshift" or "kube" or "default") in item:
            pass
        else:
            empty_ns_table.add_row([item])
    print(empty_ns_table)
    return empty_ns

# To do - check route if spec.tls exists, this means it is https so we can adjust "verify=False"
# Easy workaround = hardcode verify=False 
# If statement to run with verify=False on non-tls routes?
def check_routes(dyn_client):
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    all_routes = get_all_routes(dyn_client)
#    checked_routes = []
    checked_routes = {}
    for route in all_routes:
        with requests.Session() as session:
            response = session.get("http://" + route, verify=False)
        checked_routes.update({route: response.status_code})
#        checked_routes.append(route + " " + str(response.status_code))
    print("\nRoutes:\n")
    route_table = PrettyTable(['Route', 'Status Code'])
    for key, value in checked_routes.items():
        route_table.add_row([key, value])
    print(route_table)
    return checked_routes

def get_all_routes(dyn_client):
    route_list = []
    v1_routes = dyn_client.resources.get(api_version='route.openshift.io/v1', kind='Route')
    for route in v1_routes.get().items:
      route_list.append(route.spec.host)
    return route_list

# Not in use - replaced by check_routes. Might come back to.
def get_endpoint(session, url, ssl=True):
    r = requests.get(url, verify=ssl)
    return r.status_code

# Getting the failed pods and appending them to their namespaces.
def get_failed_pods(v1):
    number_of_failed_pods = 0
    failed_pods = {}
    response = v1.list_pod_for_all_namespaces()
    failed_pods_table = PrettyTable(['Namespace', 'Pod name', 'Status'])
    for pod in response.items:
        failed_pods[pod.metadata.namespace] = []
    for pod in response.items:
        if "Running" not in pod.status.phase and "Succeeded" not in pod.status.phase:
            failed_pods[pod.metadata.namespace].append(pod.metadata.name + ": " + pod.status.phase)
            failed_pods_table.add_row([pod.metadata.namespace, pod.metadata.name, pod.status.phase])
            number_of_failed_pods +=1
    print("\nNumber of failed pods: ", number_of_failed_pods)
    print("\nFailed pods:\n")
#    for namespace, item in failed_pods.items():
#        if item:
#            failed_pods_table.add_row([namespace, item])
    print(failed_pods_table)
    return(failed_pods)

# Convert Ki to Mb and add % of CPU/Mem. For CPU do a check to see how many cores are available/node and
def node_check(v1):
    api = client.CustomObjectsApi()
    cluster_nodes = api.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    node_count = 0
    node_table = PrettyTable(['Node name', 'Role', 'CPU', 'Memory'])
    print("\nNode info: \n")
    for node in cluster_nodes['items']:
            node_count +=1
            node_table.add_row([node['metadata']['name'], [string for string in node['metadata']['labels'] if "node-role.kubernetes" in string], node['usage']['cpu'], node['usage']['memory']])
    print(node_table)
    print("\nAmount of nodes in cluster: ",node_count)

# Maybe should be it's own function even?
# Current millicore usage / (cores * 1000) Use to calculate "%"
# Memory also needs to be converted to Mb. Maybe after having calculated "%"
    r = v1.list_node()
    cpu_per_node = {}
    mem_per_node = {}
    for node_item in r.items:
        # Maybe remake to a list?
        cpu_per_node = {node_item.metadata.name: int(node_item.status.capacity['cpu'])}
        mem_per_node = {node_item.metadata.name: int(node_item.status.capacity['memory'][:-2])}
  #  for node_mem in mem_per_node.keys():
        
#    print(r)
#    print(cpu_per_node)
#    print(mem_per_node)
# Converting Kb to Mb
#    for value in mem_per_node.values():
#        print(value // 1024)

def main():
    config.load_kube_config()
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1=client.CoreV1Api()
    check_empty_namespaces(v1)
    #print(get_all_routes(dyn_client))
    check_routes(dyn_client)
    get_failed_pods(v1)
#    print(node_check(v1))
    node_check(v1)




if __name__ == "__main__":
    main()