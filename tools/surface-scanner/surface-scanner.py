#!/usr/bin/python3
import openshift as oc
import requests
from openshift.dynamic import DynamicClient
from kubernetes import client, config


# For OCP resources, use dyn_client instead of 'v1'

# Api check
#url = 'https://api.cluster-54d4.sandbox965.opentlc.com:6443'
#url_ssl = False
#r = requests.get(url, verify=url_ssl)
#print(r.status_code)
#print(r.json)


# TO DO - Create a requirement.txt - e.g. requires "openshift" "requests"
# TO DO - Remove all API SPAM!
# TO DO - New def to check only for SSL routes - which TLS route is broken

# Get all namespaces
def get_all_namespaces(v1):
    namespace_list = []
    for i in v1.list_namespace().items:
      namespace_list.append(i.metadata.name)
    return namespace_list


def check_empty_namespaces(v1):
    all_ns = get_all_namespaces(v1)
    empty_ns = []
    for ns in all_ns:
        pod_list = v1.list_namespaced_pod(ns).items
        # Easy to add resoruces 
        #cm_list = v1.list_namespaced_config_map(ns).items
       # if pod_list == [] and cm_list == []:
        if pod_list == []:
            empty_ns.append(ns)
    return empty_ns


# To do - check route if spec.tls exists, this means it is https so we can adjust "verify=False"
# Easy workaround = hardcode verify=False 
# If statement to run with verify=False on non-tls routes?
def check_routes(dyn_client):
    all_routes = get_all_routes(dyn_client)
    with requests.Session() as session:
        response = session.get('https://argocd-prometheus-argo-test.apps.cluster-54d4.sandbox965.opentlc.com', verify=False)
    print(response.status_code)

def get_all_routes(dyn_client):
    route_list = []
    v1_routes = dyn_client.resources.get(api_version='route.openshift.io/v1', kind='Route')
    for route in v1_routes.get().items:
      route_list.append(route.spec.host)
    return route_list

def get_endpoint(session, url, ssl=True):
    r = requests.get(url, verify=ssl)
    return r.status_code

def main():
    config.load_kube_config()
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1=client.CoreV1Api()
   # print(check_empty_namespaces(v1))
   # print(get_all_routes(dyn_client))
    check_routes(dyn_client)




if __name__ == "__main__":
    main()