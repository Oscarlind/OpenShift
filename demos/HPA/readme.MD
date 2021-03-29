HPA - Horizontal Auto Scaler
=========
Short demo on the HPA function in K8s/OCP

HPA or Horizontal Auto Scaler is a function that allows for automated scaling of applications based on CPU, Memory or even custom metrics. Below is an example of how to utilize the function on an example application based on CPU load.

More information can be found here: https://docs.openshift.com/container-platform/4.7/nodes/pods/nodes-pods-autoscaling.html

Step 1 - The Namespace and the Application
------------
In order to demonstrate the HPA functionality we need an application as well as a namespace to host it.
An example application taken from the OpenShift documentation is used here as <code> <i> example-app.yaml</i> </code>

https://docs.openshift.com/container-platform/4.7/monitoring/managing-metrics.html#deploying-a-sample-service_managing-metrics

`oc apply -f example-app.yaml`

This will gives us a example application with a /metrics endpoint

Lets expose the application as well by running:

`oc expose svc hpa-demo`

Verify the route by running:

`curl $(oc get route --no-headers | awk '{print $2}')`

Ensure that the metrics endpoint is up:

`curl $(oc get route --no-headers | awk '{print $2}')/metrics`

Step 2 - Creating the LimitRange
------------

Before we can start working with our auto-scaler we want to create ourselves a LimitRange to work with.

`oc apply -f limitrange.yaml -n hpa-demo`

A limit range is an object that can be used to restrict resource consumtion in projects/namespaces.

When set, it requires future resource requests, e.g. deployments and deploymentconfigs to evaluate against the limitRange in order to see if the request should be accepted or not.

For more information: https://docs.openshift.com/container-platform/4.7/nodes/clusters/nodes-cluster-limit-ranges.html

Step 3 - The Horizontal Auto Scaler
------------
The horizontal pod autoscaler works by querying configured metrics on the resource, often deployment or deploymentconfig, and scales it up or down according to its configuration.

More information can be found here: https://docs.openshift.com/container-platform/4.7/nodes/pods/nodes-pods-autoscaling.html

To create the HPA resource, run:

`oc apply -f hpa.yaml` 

Before the HPA takes effect, it needs to collect enough metrics in order to calculate a current status. Run:

`oc get hpa hpa-demo`

To see the current status. 

Until it is ready you will most likely end up seeing <unknown/50%> under TARGETS.

```
NAME       REFERENCE                   TARGETS         MINPODS   MAXPODS   REPLICAS   AGE
hpa-demo   Deployment/hpa-demo   <unknown>/50%   1         5         0          3s
```

By running: 

`oc describe hpa hpa-demo` 

Any potential errors will be visible. 


Step 4 - Generate load
------------
Now that the HPA is set-up, we will need to generate load on the pod to test the autoscaling.

Open another terminal and
rsh into the pod:

`oc get pods -n hpa-demo`

&

`oc rsh <pod-name>`

run this to generate some artificial CPU load:

```
while true; do
echo "DEMO"
done
```
Back in your first terminal run:

`watch oc get hpa hpa-demo`

Note: The autoscaling is not a instantaneous process. 