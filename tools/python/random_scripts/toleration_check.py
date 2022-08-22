from kubernetes import client, config

tolerationToFind = "node-role.kubernetes.io/infra"

def tolerationCheck(v1):
    response = v1.list_pod_for_all_namespaces()
    for pod in response.items:
        if pod.spec.tolerations:
            for toleration in pod.spec.tolerations:
                if toleration.key is not None:
                    if tolerationToFind in toleration.key:
                        print("\n", "NAMESPACE: ", pod.metadata.namespace, "NAME: ", pod.metadata.name, u'\u2713')
                else:
                    pass


def main():
    config.load_kube_config()
    k8s_client = config.new_client_from_config()
    v1=client.CoreV1Api()
    tolerationCheck(v1)

if __name__ == "__main__":
    print("Looking for pods with toleration:", tolerationToFind)
    main()
