Maintaining a clean environment
=========
There are different ways of ensuring that your environment keeps from getting bogged up. Here I have gathered a few examples of stuff I have implemented before.

> **Note**: These are just examples and depending on use case might be unnecessary.


Removing namespaces after X time
------------
It can be a good idea to clear out certain namespaces in, for example, testing clusters. By doing this we can ensure that their main purpose stays the same - no testing/PoC:ing ending up as a full time used service and just as important making sure that the cluster resources are not being held by old unused projects. This is an example of how this can be achieved by using custom labels and a cronjob.

Command being used is:

`kubectl delete namespace $(kubectl get namespace -l=creation-date=$(date -d '1 week ago' '+%Y-%m-%d') --no-headers | awk '{print $1}')`

This looks for namespaces with the custom label **creation-date** and a value of the date a week ago, before deleting the resulting namespaces.


Clearing out all completed/failed pods
------------
To keep the number of **Completed** and **Failed** pods down, we can keep a cronjob or other process going to clear out these pods. A consideration here is to keep newly failed/completed pods in order to allow for troubleshooting. This can be done by looking at the **Age** of the pods.

The command being run in the container is this:

`kubectl delete pods --all-namespaces --field-selector=status.phase=Failed | awk 'match($6,/[1-9]+d/)' | grep -v -e 'default' -e 'openshift' -e 'kube'`

This command looks for pods in all namespaces with the **Failed** status, prints the 6th column which is the **Age** one and only takes the pods with the specified age in **d** (for days). Then it reverse greps the default namespaces in OpenShift to ensure we are not deleting any pods in those. 

> **Note**: This includes pods that failed due to errors such as "ContainerCannotRun", "Error", etc.