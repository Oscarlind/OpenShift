#!/usr/bin/python3
from kubernetes import client, config
from prettytable import PrettyTable

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
