#!/usr/bin/python3
import openshift as oc
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from prettytable import PrettyTable


def check_istags(dyn_client):
    tag_list = []
    istag_table = PrettyTable(['Namespace', 'ImageStream', 'Number of tags'])
    v1_istags = dyn_client.resources.get(api_version='image.openshift.io/v1', kind='ImageStream')
    for tag in v1_istags.get().items:
        if "openshift" in tag.metadata.namespace:
            pass
        else:
            istag_table.add_row([tag.metadata.namespace, tag.metadata.name, len(tag.status.tags)])
        tag_list.append(tag.metadata.namespace + tag.metadata.name + str(len(tag.status.tags)))
    print("\nNumber of ImageStreamTags used per ImageStream")
    print("\n", istag_table)
    return tag_list
        
