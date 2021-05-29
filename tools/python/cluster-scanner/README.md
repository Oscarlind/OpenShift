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

<br/>
The tool prints out the results directly in tables.

<br/>
Example Use:
----------------
```
➜ ./cluster-scanner.py

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
```

License
-------

BSD

Author Information
------------------

Oscar Lindholm 

olindhol@redhat.com