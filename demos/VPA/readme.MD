VPA - Vertical Pod Autoscaler
=========
Short demo of the VPA in OCP

The lesser known alternative for auto-scaling workload in OCP. The more commonly known autoscaler, the HPA - horizontal pod autoscaler resolves around scaling pods up and down in order to ensure efficient resource consumption regards to application load. The VPA instead tries to set the most correct resource requests and limits based on over time usage data.

In short:
* HPA - Autoscaling on pod replicas to ensure optimal ratio between pods/workload
* VPA - Autoscaling on the compute request/limits directly on the containers to minimize occurences of resources being reserved and not used by too large requests. At the same time will also adjust too low set limits to avoid pod OOM events and CPU throttling.

More information can be found here: https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler#vertical-pod-autoscaler

Step 1 - Installing VPA
------------
For us to use the vertical pod autoscaler, we need to install it. We do this by installing a number of CRD:s.

>- **NOTE:** These steps are taken from the github url pasted above. We can also use the VPA operator that is in Tech Preview (as of 4.7).

Clone the repo:

`git clone https://github.com/kubernetes/autoscaler.git`

Change to the correct directory:

`cd autoscaler/vertical-pod-autoscaler`

Run the setup script:

`./hack/vpa-up.sh`

Now that we have the necessary CRD:s, lets create a namespace to work in.

Create the namespace:

`oc new-project vpa-demo`

Step 2 - Creating our application and VPA
------------
To test the VPA, we need an application to work with.
An example application taken from the OpenShift documentation is used here as  *example-app.yaml*

https://docs.openshift.com/container-platform/4.7/monitoring/managing-metrics.html#deploying-a-sample-service_managing-metrics

`oc apply -f example-app.yaml`

This will gives us a example application that we can use.

The next step is to create our VPA resource. 

Lets take a look at the resource definition:

```YAML
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: demo-vpa
spec:
  targetRef:                    # This is the selector - where we choose what to scale
    apiVersion: "apps/v1"
    kind: Deployment
    name: prometheus-example-app
  updatePolicy:                 # How the "autoscaling" should be done - updates to requests/limits 
    updateMode:  Recreate       # This option will recreate the application
    containerPolicies:
      - containerName: '*'
        minAllowed:
          cpu: 0m
          memory: 0Mi
        maxAllowed:
          cpu: 200m
          memory: 200Mi
        controlledResources: ["cpu", "memory"]
        controlledValues: RequestsAndLimits        # What we aim to control. Requests, limits or both
```        
I've highlighted the parts that I believe deserves some extra attention.

To expand on the **updateMode** option. There are 4 different values possible for this setting. They are:

* **Recreate** The VPA will assign the initial resource requests and also update them on already existing pods. This by evicting the pod when there is a large enough difference in the current request compared to the latest recommendation.
* **Initial** With this setting, the VPA will only assign requests on pod creation. It wont change them later.
* **Off** When the VPA updateMode is set to Off, it will only calculate recommendations (can be viewed in the VPA). It wont set or change anything.
* **Auto** Currently works the same way as the **Recreate** method. It may take advantage of restart free updates once that is available.

Now that we know what we are trying to deploy, lets go ahead and create our VPA:

`oc apply -f vpa.yaml`

Step 3 - Understanding the VPA
------------
After the VPA have been running for a while it will have collected enough metrics to give us a recommendation of resources. It can look like this:

```YAML
  Recommendation:
    Container Recommendations:
      Container Name:  prometheus-example-app
      Lower Bound:
        Cpu:     25m
        Memory:  262144k
      Target:
        Cpu:     25m
        Memory:  262144k
      Uncapped Target:
        Cpu:     25m
        Memory:  262144k
      Upper Bound:
        Cpu:     98m
        Memory:  262144k
```
Here we can see four different estimations:

* Lower Bound - Lowest estimated resources required
* Target - Used for setting the requests
* Uncapped Target - Target if no min/maxAllowed restrictions exist
* Upper Bound - Highest estimation of resources required

The VPA uses the Lower and Upper Bound when deciding to do an eviction. If a resource is lower than the lower bound or higher than the upper bound, the eviction could be triggered.

After an eviction have taken place, the VPA will add an annotation to the pod with the information.

```YAML
apiVersion: v1
kind: Pod
metadata:
  annotations:
    openshift.io/scc: restricted
    vpaObservedContainers: prometheus-example-app
    vpaUpdates: 'Pod resources updated by demo-vpa: container 0: cpu request, memory request'
```

Limitations and additional information
------------
Some of the limitations include: 
* The VPA is not supposed to be run together with an HPA that is using CPU or Memory.
* Recommendations generated by the VPA does not take cluster resources in account. This means that pods could end up in a "**Pending**" state due to limited cluster resources.
* Currently not possible to update running pods. This means that when set to automatically adjust requests/limits on pods it will do so by evicting the current ones. This might not be ideal for certain workload but can be circumvented by using the VPA to **Initial** or **Off**.

The Vertical Pod Autoscaler has three components.
1. The **Recommender** which uses current and past resource consumption as data in order to provide recommended values.
2. **Updater** which checks if the pods have correct resources set. If not it evicts them and let them be recreated with the correct resources.
3. **Admission Plugin** This is the component that actually sets the updated resource request on the pod.


References and further reading
------------
[Vertical Pod Autoscaling GitHub](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)

[Autopilot: Workload Autoscaling at Google Scale](https://research.google/pubs/pub49174/)

[VPA Operator - OpenShift Docs](https://docs.openshift.com/container-platform/4.7/nodes/pods/nodes-pods-vertical-autoscaler.html)

[Vertical Pod Autoscaling: The Definitive Guide](https://povilasv.me/vertical-pod-autoscaling-the-definitive-guide/)