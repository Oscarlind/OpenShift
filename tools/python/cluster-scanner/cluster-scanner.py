#!/usr/bin/python3
import openshift as oc
from openshift.dynamic import DynamicClient
from kubernetes import client, config
# The different checks
import checks.admin_check as admin_check
import checks.check_empty_namespaces as ns_check
import checks.check_routes as check_routes
import checks.get_failed_pods as failed_pods
import checks.node_check as node_check
import checks.workload_age  as workload_age
import checks.check_istags as check_istags

def main():
    config.load_kube_config()
    k8s_client = config.new_client_from_config()
    dyn_client = DynamicClient(k8s_client)
    v1=client.CoreV1Api()
    is_ocp = True
    k8s_version = client.VersionApi().get_code()
    try:
        oc_version = dyn_client.resources.get(api_version='config.openshift.io/v1', kind='ClusterOperator')
    except Exception:
        is_ocp = False

    print('\033[1m' + '════════════════════════════════════╣ Starting Scan ╠════════════════════════════════════' + '\033[0m')

    if is_ocp == False:
        print('\n\033[1m' + 'OpenShift API not found. Skipping these checks...' + '\033[0m\n')
        print('\n\033[1m' + 'Kubernetes version: ' + '\033[0m\n' ,k8s_version.git_version)
        try:
            ns_check.check_empty_namespaces(v1)
            failed_pods.get_failed_pods(v1)
            workload_age.workload_age(v1)
            node_check.node_check(v1)
        except KeyboardInterrupt:
            print("\nUser interruption")
    else:
        try:
            print('\n\033[1m' + 'OpenShift version: ' + '\033[0m\n' ,oc_version.get().items[0].status.versions[0].version)
            ns_check.check_empty_namespaces(v1)
            check_routes.check_routes(dyn_client)
            failed_pods.get_failed_pods(v1)
            admin_check.admin_check(v1)
            workload_age.workload_age(v1)
            check_istags.check_istags(dyn_client)
            node_check.node_check(v1)
        except KeyboardInterrupt:
            print("\nUser interruption")
        
    print('\033[1m' + '════════════════════════════════════╣ Scan Complete ╠════════════════════════════════════' + '\033[0m')

if __name__ == "__main__":
    main()

