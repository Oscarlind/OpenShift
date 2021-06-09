#!/usr/bin/python3
import openshift as oc
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from openshift.dynamic import DynamicClient
from kubernetes import client, config
from prettytable import PrettyTable


def check_istags(dyn_client):
    tag_dict = {}
    istag_table = PrettyTable(['Namespace', 'ImageStream', 'Number of tags'])
    v1_istags = dyn_client.resources.get(api_version='image.openshift.io/v1', kind='ImageStream')
    for tag in v1_istags.get().items:
        if "openshift" in tag.metadata.namespace or 10 >= len(tag.status.tags):
            pass
        else:
            tag_dict[tag.metadata.namespace] = []
    for tag in v1_istags.get().items:
        if "openshift" in tag.metadata.namespace:
            pass
        elif 10 >= len(tag.status.tags):
            pass
        else:
            istag_table.add_row([tag.metadata.namespace, tag.metadata.name, len(tag.status.tags)])
            tag_dict[tag.metadata.namespace].append(tag.metadata.name + " " + str(len(tag.status.tags)))
    print("\nNumber of ImageStreamTags used per ImageStream")
    print("\n", istag_table)
    return tag_dict
