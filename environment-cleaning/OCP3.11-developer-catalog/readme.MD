Developer Catalog
=========
The developer catalog in OCP 3.11 gets populated by the installed ClusterServiceBrokers. These in turn pulls down ClusterServiceClasses which is then selectable/usable by users in /console/catalog.

The cluster normally comes with two brokers, the template-service-broker and the ansible-service-broker.

To remove an item from this catalog we simply remove the corresponding ClusterServiceClass. However this will only work until the next sync from the Broker. 

For the template-service-broker we can stop this synchronization of content by also removing the corresponding template in the **openshift** namespace.

> NOTE: If you are using an instance that you are planning on removing you should be aware that you might encounter certain issues after the fact.

I've created a script for a quick and easy way of clearing the service catalog. Simple edit it and add the templates you want to keep.

> IMPORTANT: it will delete everything not from the template-service-broker.