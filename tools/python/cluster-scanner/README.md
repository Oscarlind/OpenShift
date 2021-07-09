Cluster Scanner
=========

A simple cluster scanner tool for k8s & OpenShift.

If the OpenShift API is detected, it will run checks specific for OpenShift in addition to the others.

Performs a surface scan on a cluster to identify it's general state. Currently does:

| Check      | K8s | OCP     |
| ----------- | ----------- |  -----------  |
| Scans the nodes for their usage.      | Yes       | Yes   |
| Identifies namespaces that currently has no workload  | Yes        | Yes      |
| Does a check on all routes in the cluster. | No       | Yes   |
| Scans the cluster for failed pods. | Yes       | Yes   |
| Checks for pods that has been running for more than 9 days. | Yes       | Yes   |
| Identifies all users with cluster-admin rights. | No       | Yes   |
| Counts the number of ImageStreamTags per ImageStream. | No       | Yes   |
| Locates all pods that have no resource requests set. | Yes       | Yes   |
| Checks the ingress certificate and for router-sharding. | No       | Yes   |

<br/>
The tool prints out the results directly in tables.

Explaination of the checks
----------------
These checks targets different potential problem areas one might encounter in a Kubernetes/OpenShift cluster. They have been designed to give the user a quick overview of the cluster health and what areas might need intervention.

The scan is primarily intended to give a new administrator information of the cluster but could just as well be used by someone administrating it for a longer period of time.

### Node Scan
This check is replicating the command: `oc adm top node` while giving additional information to the user, such as the **roles** of the nodes. This since we have different expectations and requirements of our nodes depending on what workload they are holding. 

We might have certain nodes dedicated for ML/AI and that might be a reason why their resource usage differs compared to standard worker nodes. This check intends to make these subtleties visible at a first glance.

### Empty namespaces
While namespaces themselves do not use or reserve any resources, there might be reasons to want to know why there are unused ones in your cluster. They might hold a specific name that someone wants to reuse or might be for entirely esthetical reasons of not wanting extra namespaces without meaning.

>INFO: This check looks only for running workloads (pods) there might be other resources that one wants to keep, e.g. configmaps, secrets etc.

### Route check
Many of the applications running on the cluster will have their own routes. This check intends to give the user a quick rundown of the routes that exist and their current status.

### Failed Pods
That pods are failing or getting stuck due to various reasons is to be expected. This check allows the user to see in which **namespace** the issue occured, which **pod** is having issues and also **what** the issue is.

### Long running workload
While pods can run without issues for a long period of time, it might be advantageous to let them "reboot" once in a while. Maybe there are pods running without being used that could actually be removed. There could be unidentified issues when the underlying application has been running for a long period of time. It might also not be any problem at all, just information that could be interesting.

Whatever the reason might be, this scan intends to let the user know about these pods and let them make a decision based on the information.

### Cluster-Admin check
Depending on how your organization handles administrative rights to your clusters this can be a very quick and easy way of determining who actually has these privileges or not. 

Many organizations use some sort of ***service form template*** that a user is required to fill in to request privileged access. These might be approved by managers without a full understanding of the impact the approval might have.

Another, not uncommon, scenario is when access is given while bypassing the standardized process. E.g an administrator gives a colleague the privileges directly without them having gone through their service form.

This can lead to the wrong people having administrative rights, an unusual high number of cluster-administrators etc. This is exactly what this check is intended to watch out for. 

### ImageStreamTag check
Something I have noticed is that ImageStreams and the way of using tags in OpenShift is not always done right and can have pretty significant complications with time. While it is recommended to use a small but significant amount of different tags for **ImageStreams**, sometimes you will see some using unique tags for each build. 

A consequence of this is that each tag is referring to an image. This image wont be available for pruning while it is being referred to. Over time this can lead to a large amount of unused images being stored due to their tags never getting removed.

This check helps the user look out for this pattern. 

### Resource request check
Best practice is to always include requests (and limits) to your workloads. This can be done either directly in the deployment or by using a limitRange with defaults set. This check is intended to scan the cluster for those pods that are not having their resource requests set.
### Ingress
Simple check to see the validity of the ingress certificate. Issuer, issued to and expiration date is shown. Will also notify if the cluster is using the out of the box certificate instead of a custom one. Will also look for router-sharding but as of right now it won't validate these certificates.

Example Use:
----------------

```
➜ ./cluster-scanner.py 
════════════════════════════════════╣ Starting Scan ╠════════════════════════════════════

OpenShift version: 
 4.8.0-rc.3

Empty namespaces
 +------------------+
| Empty namespaces |
+------------------+
|    app-test1     |
+------------------+

Number of empty namespaces:  1

Routes: 

+----------------------------------------------------------------------------------+-------------+-------------+
|                                      Route                                       | Status Code | Termination |
+----------------------------------------------------------------------------------+-------------+-------------+
|             my-route-hello.apps.cluster-94cd.my-lab-1733.example.com             |     200     |     edge    |
|     rails-postgresql-example-hello.apps.cluster-94cd.my-lab-1733.example.com     |     200     |     http    |
|            oauth-openshift.apps.cluster-94cd.my-lab-1733.example.com             |     403     | passthrough |
|       console-openshift-console.apps.cluster-94cd.my-lab-1733.example.com        |     200     |  reencrypt  |
|      downloads-openshift-console.apps.cluster-94cd.my-lab-1733.example.com       |     200     |     edge    |
|    canary-openshift-ingress-canary.apps.cluster-94cd.my-lab-1733.example.com     |     200     |     edge    |
| alertmanager-main-openshift-monitoring.apps.cluster-94cd.my-lab-1733.example.com |     403     |  reencrypt  |
|      grafana-openshift-monitoring.apps.cluster-94cd.my-lab-1733.example.com      |     403     |  reencrypt  |
|  prometheus-k8s-openshift-monitoring.apps.cluster-94cd.my-lab-1733.example.com   |     403     |  reencrypt  |
|  thanos-querier-openshift-monitoring.apps.cluster-94cd.my-lab-1733.example.com   |     403     |  reencrypt  |
+----------------------------------------------------------------------------------+-------------+-------------+

Failed pods:

+-----------+-----------------------------------+------------------+
| Namespace |              Pod name             |      Status      |
+-----------+-----------------------------------+------------------+
|  app-dev1 | nginx-deployment-66b6c48dd5-5q68z |      Error       |
|  app-dev1 | nginx-deployment-66b6c48dd5-9j5rg | CrashLoopBackOff |
|  app-dev1 | nginx-deployment-66b6c48dd5-c5nvz | CrashLoopBackOff |
+-----------+-----------------------------------+------------------+

Number of failed pods:  2

Cluster-admins  
 +--------------+-----------------------+
|    Users     |         Groups        |
+--------------+-----------------------+
|     ogge     |     system:masters    |
| system:admin |    platform-admins    |
|     ljkb     | system:cluster-admins |
+--------------+-----------------------+

There are: 3 cluster-admins in the cluster

Workload running longer than 9 days:

+-----------+-----+
| Namespace | Pod |
+-----------+-----+
+-----------+-----+

Number of old pods: 	 0

ImageStreamTags over 10 per ImageStream 

 +-----------+-------------+----------------+
| Namespace | ImageStream | Number of tags |
+-----------+-------------+----------------+
+-----------+-------------+----------------+

Ingress certificate: OPENSHIFT GENERATED INGRESS CERTIFCATE IN USE: Please configure a custom certificate 

 +---------------------------------------------+-----------------------------+---------------------+
|                  Issued to                  |          Issued by          |   Expiration date   |
+---------------------------------------------+-----------------------------+---------------------+
| *.apps.cluster-94cd.my-lab-1733.example.com | ingress-operator@1625737162 | 2023-07-08 09:40:46 |
+---------------------------------------------+-----------------------------+---------------------+ 

Days until expiration:  728

Node usage: 

+-----------------------------------------------+------------------------------------+------+------------+-----------+------------+
|                   Node name                   |                Role                | CPU  |   CPU %    |   Memory  |  Memory %  |
+-----------------------------------------------+------------------------------------+------+------------+-----------+------------+
| ip-10-0-139-241.eu-central-1.compute.internal | ['node-role.kubernetes.io/worker'] | 704m | ['35.20%'] | 4574740Ki | ['58.28%'] |
| ip-10-0-155-167.eu-central-1.compute.internal | ['node-role.kubernetes.io/master'] | 886m | ['22.15%'] | 8753700Ki | ['54.94%'] |
|  ip-10-0-164-56.eu-central-1.compute.internal | ['node-role.kubernetes.io/master'] | 655m | ['16.38%'] | 7703820Ki | ['47.83%'] |
|  ip-10-0-186-95.eu-central-1.compute.internal | ['node-role.kubernetes.io/worker'] | 194m | ['9.70%']  | 2334268Ki | ['29.41%'] |
| ip-10-0-214-241.eu-central-1.compute.internal | ['node-role.kubernetes.io/master'] | 830m | ['20.75%'] | 7935808Ki | ['49.27%'] |
| ip-10-0-215-145.eu-central-1.compute.internal | ['node-role.kubernetes.io/worker'] | 736m | ['36.80%'] | 3522848Ki | ['44.39%'] |
+-----------------------------------------------+------------------------------------+------+------------+-----------+------------+

Nodes in cluster:  6

Pods without requests specifed: 

 +-----------+-----------------------------------+
| Namespace |              Pod name             |
+-----------+-----------------------------------+
|  app-dev1 | nginx-deployment-66b6c48dd5-5q68z |
|  app-dev1 | nginx-deployment-66b6c48dd5-9j5rg |
|  app-dev1 | nginx-deployment-66b6c48dd5-c5nvz |
| app-test2 |    hello-node-6565c8c875-kjbnb    |
|   hello   |        postgresql-1-deploy        |
|   hello   |  rails-postgresql-example-1-build |
|   hello   | rails-postgresql-example-1-deploy |
+-----------+-----------------------------------+

Number of pods without requests specified:  7
════════════════════════════════════╣ Scan Complete ╠════════════════════════════════════


```

License
-------

BSD

Author Information
------------------

Oscar Lindholm 

olindhol@redhat.com