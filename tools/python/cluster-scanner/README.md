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


Example Use:
----------------

```
➜ ./cluster-scanner.py
════════════════════════════════════╣ Starting Scan ╠════════════════════════════════════

OpenShift version: 
 4.7.11

+------------------+
| Empty namespaces |
+------------------+
|     for-test     |
|      hello       |
+------------------+

Number of empty namespaces:  2

Routes:

+----------------------------------------------------------------------------------+-------------+-------------+
|                                      Route                                       | Status Code | Termination |
+----------------------------------------------------------------------------------+-------------+-------------+
|            oauth-openshift.apps.cluster-7d2e.my-lab-1738.example.com             |     403     | passthrough |
|       console-openshift-console.apps.cluster-7d2e.my-lab-1738.example.com        |     200     |  reencrypt  |
|      downloads-openshift-console.apps.cluster-7d2e.my-lab-1738.example.com       |     200     |     edge    |
|    canary-openshift-ingress-canary.apps.cluster-7d2e.my-lab-1738.example.com     |     200     |     edge    |
| alertmanager-main-openshift-monitoring.apps.cluster-7d2e.my-lab-1738.example.com |     403     |  reencrypt  |
|      grafana-openshift-monitoring.apps.cluster-7d2e.my-lab-1738.example.com      |     403     |  reencrypt  |
|  prometheus-k8s-openshift-monitoring.apps.cluster-7d2e.my-lab-1738.example.com   |     403     |  reencrypt  |
|  thanos-querier-openshift-monitoring.apps.cluster-7d2e.my-lab-1738.example.com   |     403     |  reencrypt  |
|    prometheus-example-app-vpa-demo.apps.cluster-7d2e.my-lab-1738.example.com     |     200     |     http    |
+----------------------------------------------------------------------------------+-------------+-------------+

Failed pods:

+-----------+----------+--------+
| Namespace | Pod name | Status |
+-----------+----------+--------+
+-----------+----------+--------+

Number of failed pods:  0

Node usage: 

+-----------------------------------------------+--------------------------------------------------------------------+------+------------+-----------+------------+
|                   Node name                   |                                Role                                | CPU  |   CPU %    |   Memory  |  Memory %  |
+-----------------------------------------------+--------------------------------------------------------------------+------+------------+-----------+------------+
| ip-10-0-130-112.eu-central-1.compute.internal |                 ['node-role.kubernetes.io/master']                 | 461m | ['12.10%'] | 5213544Ki | ['32.37%'] |
|  ip-10-0-139-78.eu-central-1.compute.internal | ['node-role.kubernetes.io/demo', 'node-role.kubernetes.io/worker'] | 480m | ['22.40%'] | 3167528Ki | ['39.90%'] |
| ip-10-0-171-134.eu-central-1.compute.internal |                 ['node-role.kubernetes.io/master']                 | 990m | ['25.25%'] | 8095620Ki | ['50.80%'] |
| ip-10-0-183-104.eu-central-1.compute.internal |                 ['node-role.kubernetes.io/worker']                 | 129m | ['7.85%']  | 2898588Ki | ['36.57%'] |
|  ip-10-0-209-85.eu-central-1.compute.internal |                 ['node-role.kubernetes.io/master']                 | 529m | ['14.85%'] | 5175748Ki | ['32.19%'] |
| ip-10-0-218-152.eu-central-1.compute.internal |                 ['node-role.kubernetes.io/worker']                 | 500m | ['24.45%'] | 3194620Ki | ['40.25%'] |
+-----------------------------------------------+--------------------------------------------------------------------+------+------------+-----------+------------+

Nodes in cluster:  6

 +--------------+-----------------------+
|    Users     |         Groups        |
+--------------+-----------------------+
|     ogge     |     system:masters    |
| system:admin | system:cluster-admins |
+--------------+-----------------------+

There are: 2 cluster-admins in the cluster

Workload running longer than 9 days:

+-----------+-----------------------------------------+
| Namespace |                   Pod                   |
+-----------+-----------------------------------------+
|  vpa-demo | prometheus-example-app-79697bd67f-x9j5v |
+-----------+-----------------------------------------+

Number of old pods: 	 1
════════════════════════════════════╣ Scan Complete ╠════════════════════════════════════
```

License
-------

BSD

Author Information
------------------

Oscar Lindholm 

olindhol@redhat.com