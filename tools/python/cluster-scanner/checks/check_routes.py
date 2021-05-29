#!/usr/bin/python3
import openshift as oc
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from prettytable import PrettyTable


# Saving all routes with their termination (edge, passthrough, reencrypt or None)
def get_all_routes(dyn_client):
    route_dict = {}
    v1_routes = dyn_client.resources.get(api_version='route.openshift.io/v1', kind='Route')
    for route in v1_routes.get().items:
          route_dict.update({route.spec.host: route.spec.tls})
    return route_dict

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
