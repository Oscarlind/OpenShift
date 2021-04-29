Sealed Secrets
=========

With K8s secrets being base64 encoded they are also easily decoded once access to them have been given. This creates a problem when you are trying to work in a GitOps manner.

**Sealed Secrets** are a solution to not being able to store K8s secrets in git. They allow users to encrypt their secrets before adding them to their git repository. Once applied in the cluster a controller will decrypt (unseal) them.

More reading can be done here:

https://github.com/bitnami-labs/sealed-secrets

This demo is meant to showcase how they can be used.

Step 1 - Installing Sealed Secrets
------------
First we will install our controller. This is the entity carrying a private key (master key) that can decrypt sealed-secrets for us.

`oc apply -k sealed-secrets`

And our binary. We will need it to encrypt our secrets.

`wget https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.15.0/kubeseal-linux-amd64 -O kubeseal `

`sudo install -m 755 kubeseal /usr/local/bin/kubeseal`

Step 2 - Creating a secret
------------
Now that we have our controller installed, we can start of by creating a secret to encrypt.

We will be using the demo-file, which contains

**password: secret**



`oc create secret generic demo-secret --dry-run=client --from-file=demo-file -n demo-namespace -o yaml> demo-secret.yaml `

This will create a normal K8s secret. The next step is to encrypt it.

`kubeseal -o yaml <demo-secret.yaml > sealed-demo-secret.yaml`

> Info: The kubeseal command talks with the controller to fetch the certificate. This means that you need to be logged in to the cluster or save the certificate locally.

Now we have a SealedSecret object that can be added to a git repository without worry of it's content being readable.

Example Sealed Secret:
```yaml
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  creationTimestamp: null
  name: demo-secret
  namespace: demo-namespace
spec:
  encryptedData:
    demo-file: AgBmPJGmXRt+o9ndCX+9ec47h+RhXYNE3eCHfnhevN+DNH09tog0oCFEX7bep7QuxQJPaLrcRstQFs1sBpl1gF/IRlKvwDtN09phFV9JZttd4Z0fXnOvgKIqbgWPoJUBnq9XUqlad4+aSb+XBRuR+niFc7107Fca1x4hTEBBagJ4WWoPH1L80HaoJ3p9HcJaTJpZaf3DFv/ojaVH0UUCqZcz4b2ZYW5WW9bQt3qowqqeqByAj2RzyDYW/x9izyPq7UECbERDv+DLgtcJ5xrORxOTP9iyyZBDKQDGyq0JeALH/l7rTwGq8qxaTre/RaR8maoH7MkEHGhFYpWePod5rlTxUMI6QEQu9wIDQoJpIacS6iJjgOXe9wpkgKOjnCay0yNeE6nF/3YxHo3ZRi1oC/AL7qoHYzUvNjxw7MAyWl2Qf4IgoSQMmM3lV3Vr1ObqdR46icNgZfbo68mUHwIPuDYQQ3MRQHHJnxZdy2sKxzZRgnPeZt1QtrhmqCrbCmXrm3+bGi5/Q2Pv6MevY9ckb5FmVNv+tDjpbWvNx/gYjuX95ZchZ/NjcwrABNSIOJX1BFWIzPRTx8gzQ8R6Zj7hsmnQ+eug+KjgB6GX9VlKmTV4PYZnw5r6bwEYfp1pvOiLwpE87wA9SDzyB4/BVOaXqYJeOcOp9xAhVXWTzDsBE0GtGBPpmG6YoW4W4KGFuRNrb6x7YOfsJSlGOBJopJpXrmOe
  template:
    metadata:
      creationTimestamp: null
      name: demo-secret
      namespace: demo-namespace
```



Step 3 - Applying the secret
------------
Now that we have created our sealed secret we can look what happens to it once we apply it to our cluster.

`oc apply -f sealed-demo-secret.yaml`

Once the secret has been added to the cluster we can go ahead and take a look at the logs coming from the controller.

`oc logs $(oc get pods -n kube-system | grep sealed-secrets | awk '{print $1}') -n kube-system`

You should see something like this:

**'Unsealed' SealedSecret unsealed successfully**

As implied it means that the controller have now decrypted the sealed-secret and the secret is now available in the cluster.

Lets have a look:

`oc get secret -n demo-namespace`

will show:

<pre>
NAME                       TYPE                                  DATA   AGE
builder-dockercfg-z7d9p    kubernetes.io/dockercfg               1      21m
builder-token-7wpl7        kubernetes.io/service-account-token   4      21m
builder-token-8x2jd        kubernetes.io/service-account-token   4      21m
default-dockercfg-bdfr6    kubernetes.io/dockercfg               1      21m
default-token-57brf        kubernetes.io/service-account-token   4      21m
default-token-gvpbb        kubernetes.io/service-account-token   4      21m
<b>demo-secret                Opaque                                1      14m</b>
deployer-dockercfg-x2mxf   kubernetes.io/dockercfg               1      21m
deployer-token-gx5tv       kubernetes.io/service-account-token   4      21m
deployer-token-jdzmf       kubernetes.io/service-account-token   4      21m
</pre>

Lets have a look at the secret:
`oc get secret demo-secret -n demo-namespace -o yaml`

```yaml
apiVersion: v1
data:
  demo-file: cGFzc3dvcmQ6IHNlY3JldA==
kind: Secret
metadata:
  creationTimestamp: "2021-04-23T14:09:22Z"
    manager: controller
    operation: Update
    time: "2021-04-23T14:09:22Z"
  name: demo-secret
  namespace: demo-namespace
  ownerReferences:
  - apiVersion: bitnami.com/v1alpha1
    controller: true
    kind: SealedSecret
    name: demo-secret
    uid: 06f70c30-8c0d-4e4f-b11c-9c34fc4bbee0
  resourceVersion: "721363"
  selfLink: /api/v1/namespaces/demo-namespace/secrets/demo-secret
  uid: bacfedaf-487a-4e4c-95e7-85001d54d8c4
type: Opaque
```

Here we can see two interesting things. First of we can see that the secret has its data in a base64 encoded format, which we can easily decode:

`printf cGFzc3dvcmQ6IHNlY3JldA== | base64 -d`

**password: secret** 

The second is that we can see **ownerReferences** in the yaml definition, telling us that the secret is owned by a sealed-secret called demo-secret.

Step 4 - [OPTIONAL] Installing Sealed-Secrets in a custom namespace
------------

To avoid installing the controller in the **kube-system** namespace and instead doing it in a dedicated namespace, we can use **Kustomize** to ensure the controller gets deployed where we want it to.

This change in namespace do affect how we will create our sealed-secrets.
With the controller deployed in another namespace than kube-system, kubeseal wont find the certififcate unless we specify the path to the controller, in other words, the namespace where we decided to deploy it to. This means that the command we used earlier: 

`kubeseal -o yaml <demo-secret.yaml > sealed-demo-secret.yaml` 

will fail with.

```
error: cannot fetch certificate: services "sealed-secrets-controller" not found
``` 

I'll address this point later on. First, lets get rid of the previous deployment.

`oc delete -k sealed-secrets`

and install it in our dedicated namespace, sealed-secrets.

`oc apply -k sealed-secrets/overlays/isolation`

> NOTE: This solution was originally found here: https://github.com/redhat-cop/rhel-edge-automation-arch/tree/main/openshift/gitops/manifests/configs/sealed-secrets

What this does is:

1. Creates the **sealed-secrets** namespace
2. Deploys the controller and the other resources in that namespace

As mentioned when trying to encrypt (seal) a secret using kubeseal, we will now be getting an error. This is because we now have to specify the path to the controller in order to fetch the certificate.

> NOTE: We can also fetch locally and tell **Kubeseal** to point at a file.

In this example we have deployed the controller in the *sealed-secrets* namespace and to create a sealed-secret we would specify:

`kubeseal --controller-namespace=sealed-secrets -o yaml <demo-secret.yaml > sealed-demo-secret.yaml`

Now that we specify where to go and fetch the certificate, the command will run without errors and produce our sealed-secret.

Step 5 - [OPTIONAL] Simplifying the process
------------
Now that we have seen how Sealed-Secrets are deployed and used, we can start to look at how we can simplify the process from a user PoV.

Once the controller is deployed and a user wants to make use of it, he or she needs to:

1. Create a secret definition. For example by doing a dry-run and include the namespace, content for the secret
2. Encrypt (Seal) the secret using kubeseal and define the location for the controller and the secret definition we created in the previous step 

This is perhaps not the most user-friendly way of working, and is also error-prone due to typos. A suggested way of working with this is to automate the process of creating both the secret and the sealed-secret.

For this reason I created this script: https://github.com/Oscarlind/OpenShift/tree/main/tools/sealed-secrets/sealed-secrets.sh

It's usage is simple. Just run it with `sh sealed-secrets.sh [OPTIONS]`

Options available are:

```
-s     Name of the secret, will be converted to lowercase
-n     The namespace to apply the secret to
-f     The file containing the secret data
-h     Print this message and exit 
```

In our example, we can run it like this:

```bash
[olindhol ~]$ sh sealed-secrets.sh -s test-SECRET -n demo-namespace -f demo-file

Sealed-Secret: test-secret.yml has now been created. You can add it to git

```
