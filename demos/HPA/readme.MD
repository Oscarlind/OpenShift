HPA - Horizontal Auto Scaler
=========
Short demo on the HPA function in K8s/OCP

Step 1 - The project and limitRange
------------
First, create a project.

`oc new-project hpa-demo`

Before we can start working with our auto-scaler we want to create ourselves a LimitRange to work with.

`oc apply -f limitrange.yaml -n hpa-demo`

A limit range is an object that can be used to restrict resource consumtion in projects/namespaces.

When set, it requires future resource requests, e.g. deployments and deploymentconfigs to evaluate against the limitRange in order to see if the request should be accepted or not.

For more information: https://docs.openshift.com/container-platform/4.7/nodes/clusters/nodes-cluster-limit-ranges.html

Step 2 - Creating the application
------------

Here we can now create our example application.
#TODO# Choose an application to use

`oc new-app --as-deployment-config <URL> --name=hpa-demo`

#TODO# Change into finished dc yaml

We will also expose our application in order to make it available for scraping at /metrics.

`oc expose svc hpa-demo` 



Step 3 - The Horizontal Auto Scaler
------------
The horizontal pod autoscaler works by querying configured metrics on the resource, often deployment or deploymentconfig, and scales it up or down according to its configuration.

More information can be found here: https://docs.openshift.com/container-platform/4.7/nodes/pods/nodes-pods-autoscaling.html

To create the HPA resource, run:

`oc apply -f hpa.yaml` 

NOTE: The yaml is set to dc name of hpa-demo. If you have used another name, either change the yaml or run:

`oc autoscale dc/<NAME> --min 1 --max 5 --cpu-percent=60`

instead.

Before the HPA takes effect, it needs to collect enough metrics in order to calculate a current status. Run:

`oc get hpa hpa-demo`

To see the current status. 

Until it is ready you will most likely end up seeing <unknown/50%> under TARGETS.

By running: 

`oc describe hpa hpa-demo` 

Any potential errors will be visible.

Redeploy the applciation in order to ensure that the HPA is taken into effect:

`oc rollout latest dc/hpa-demo`

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