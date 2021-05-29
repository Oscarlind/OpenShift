#!/usr/bin/python3
import openshift as oc
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from prettytable import PrettyTable
import itertools


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
