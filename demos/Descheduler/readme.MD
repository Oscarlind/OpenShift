Descheduler
=========
Demo of the Descheduler operator on OpenShift

Where pods get scheduled on OpenShift is determined at the time of deployment by the Scheduler. The Scheduler does this by selecting the most appropriate node at that time. Anything that happens afterwards is out of its job description so to speak. What was once the most appropriate node may not always be. This is where the Descheduler comes in, by running periodic checks it tries to determine the most appropriate nodes for the pods and ensure that they are scheduled there. This by evicting the pods and letting the Scheduler re-deploy them.
 
The Descheduler Operator works by using "Profiles". These contain a set of conditions from which an eviction should take place. There is currently three different profiles available through the operator:

* AffinityAndTaints
* TopologyAndDuplicates
* LifecyleAndUtilization

More information can be found here: https://docs.openshift.com/container-platform/4.7/nodes/scheduling/nodes-descheduler.html

Requirements
------------
* An OpenShift cluster, 4.7 or later.

Step 1 - Installing the Operator
------------
We will prepare the environment with some workload that can be evicted by the operator at a later time.

First, create a dummy namespace:

`oc new-project descheduler-demo`

`oc create -f load-deploy.yaml -n descheduler-demo`

The operator should be installed in the *openshift-kube-descheduler-operator* namespace.

Let's begin by creating the namespace:

`oc new-project openshift-kube-descheduler-operator`

From here we can deploy the Operator:

Easiest way is through operatorhub, otherwise deploy:

`oc apply -f sub-descheduler.yaml`

Step 2 - Creating a Descheduler object
------------
Now that we have our operator, we can start by creating our descheduler.

Same here, easiest way is through the GUI, otherwise:
`oc apply -f descheduler.yaml`

The configuration we are deploying is using only the LifecycleAndUtilization profile. As mentioned earlier, a profile is essentially a bundle of *strategies* or conditions that the descheduler will use in order to determine which pods should be evicted.

This configuration is taken from the configMap "cluster" that comes with the deployment of the descheduler.

The LifecycleAndUtilization profile will ensure that pods with too many restarts (100+), are older than 24 hours will get evicted. It will also utilization checks on the nodes and determine which are, in the deschedulers perspective, under or overutilized. If applicable it will then evict pods from the overutilized nodes in order to keep a more even usage level.
 
For this demo we will change the standard PodLifeTime eviction rule of 24 hours to 400 seconds.
> NOTE: The configmap will get returned to its original state - this is only a temporary change.

`oc edit cm cluster -n openshift-kube-descheduler-operator`

Now we need to redeploy our scheduler in order for it to take affect:

`oc patch deployment cluster -p "{\"spec\": {\"template\": {\"metadata\": { \"labels\": {  \"redeploy\": \"$(date +%s)\"}}}}}"`

Lets look at the logs from the descheduler.

`oc logs -n openshift-kube-descheduler-operator $(oc get pods -n openshift-kube-descheduler-operator --no-headers | awk '{print $1}' | grep cluster)`

We will se something similar to:

```
I0518 10:57:12.705841       1 lownodeutilization.go:271] "Node is overutilized" node="my.compute-1.internal" usage=map[cpu:1339m memory:6392Mi pods:43] usagePercentage=map[cpu:100 memory:97.6962729366699 pods:17.2]
I0518 10:57:12.705883       1 lownodeutilization.go:274] "Node is appropriately utilized" node="my.compute2.internal" usage=map[cpu:1730m memory:6059Mi pods:41] usagePercentage=map[cpu:50 memory:41.48213125232335 pods:16.4]
I0518 10:57:12.705919       1 lownodeutilization.go:271] "Node is overutilized" node="my.compute3.internal" usage=map[cpu:600m memory:3612Mi pods:24] usagePercentage=map[cpu:50 memory:54.506549590260086 pods:9.6]
I0518 10:57:12.705943       1 lownodeutilization.go:274] "Node is appropriately utilized" node="my.compute4.internal" usage=map[cpu:1694m memory:5981Mi pods:34] usagePercentage=map[cpu:50 memory:40.948114708721896 pods:13.6]
I0518 10:57:12.705967       1 lownodeutilization.go:271] "Node is overutilized" node="my.compute5.internal" usage=map[cpu:684m memory:3714Mi pods:26] usagePercentage=map[cpu:50 memory:56.76532504486733 pods:10.4]
I0518 10:57:12.705989       1 lownodeutilization.go:274] "Node is appropriately utilized" node="my.compute6.internal" usage=map[cpu:1745m memory:6215Mi pods:39] usagePercentage=map[cpu:50 memory:43.04526646541504 pods:15.6]
I0518 10:57:12.706003       1 lownodeutilization.go:116] "Criteria for a node under utilization" CPU=20 Mem=20 Pods=20
I0518 10:57:12.706014       1 lownodeutilization.go:120] "No node is underutilized, nothing to do here, you might tune your thresholds further"
```

Step 3 AffinityAndTaints
------------
For the second part we are going to explore the AffinityAndTaints profile.
Lets start by deleting the previous KubeDescheduler.

`oc delete kubedescheduler cluster -n openshift-kube-descheduler-operator`

Lets redeploy our "application load" as well.

`oc delete -f load-deploy.yaml`

and:

`oc apply -f load-deploy.yaml`

Now we want to see where the pods are currently running:

`oc get pods -o wide`

Should return something similar to:

```
NAME                    READY   STATUS    RESTARTS   AGE     IP             NODE                 
load-785dff9c7b-4jhkj   1/1     Running   0          3m54s   10.128.5.130   my.compute-1.internal
load-785dff9c7b-5lctp   1/1     Running   0          3m54s   10.128.5.129   my.compute-1.internal
load-785dff9c7b-6bvdm   1/1     Running   0          3m54s   10.131.2.68    my.compute-2.internal
load-785dff9c7b-6tmzj   1/1     Running   0          3m54s   10.128.5.131   my.compute-1.internal
load-785dff9c7b-6x99n   1/1     Running   0          3m54s   10.131.2.67    my.compute-2.internal
load-785dff9c7b-7gxj8   1/1     Running   0          3m54s   10.129.3.45    my.compute-3.internal
load-785dff9c7b-855v2   1/1     Running   0          3m54s   10.128.5.132   my.compute-1.internal
load-785dff9c7b-b9kjg   1/1     Running   0          3m54s   10.129.3.48    my.compute-3.internal
load-785dff9c7b-ggdkg   1/1     Running   0          3m54s   10.131.2.65    my.compute-2.internal
load-785dff9c7b-gs9r4   1/1     Running   0          3m54s   10.129.3.47    my.compute-3.internal
load-785dff9c7b-nj7hf   1/1     Running   0          3m54s   10.129.3.44    my.compute-3.internal
load-785dff9c7b-nz7qs   1/1     Running   0          3m54s   10.131.2.64    my.compute-2.internal
load-785dff9c7b-rsnkf   1/1     Running   0          3m54s   10.129.3.46    my.compute-3.internal
load-785dff9c7b-z8j4w   1/1     Running   0          3m54s   10.131.2.66    my.compute-2.internal
load-785dff9c7b-zfx25   1/1     Running   0          3m54s   10.128.5.133   my.compute-1.internal
```

As we can see there are 3 different nodes that the pods are running on. Let's chose one that we will apply a taint on.
> INFO: Taints are a mechanism that allows us to deny scheduling of workload onto nodes unless a matching toleration exists.
> Read more here: https://docs.openshift.com/container-platform/4.7/nodes/scheduling/nodes-scheduler-taints-tolerations.html

`oc adm taint nodes <node-name> demo=true:NoSchedule`

This taint ensures that only pods with the toleration demo=true can be scheduled on it.

If we once again run:

`oc get pods -o wide`

We can see that the pods are still running on this node. If we were to manually remove them, they would be scheduled onto another node instead.

The descheduler with the AffinityAndTaints profile would detect that there are pods running on a node where there are no matching taint/toleration. The descheduler would then start the eviction process to ensure that there are no pods running on the tainted node/s.

For now we will apply the new descheduler with that profile.

`oc apply -f descheduler2.yaml`

If we check the pods now, we should see that they are getting evicted from our tainted node:

`oc get pods -o wide`

To check the logs:

`oc logs -n openshift-kube-descheduler-operator $(oc get pods -n openshift-kube-descheduler-operator --no-headers | awk '{print $1}' | grep cluster)`

As we can see, the pods have gotten evicted.

Step 4
------------
