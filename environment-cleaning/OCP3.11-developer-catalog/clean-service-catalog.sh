#!/bin/bash
# Cleanup of service catalog

# ADD ITEMS TO KEEP HERE #
list_to_keep=(s2i-fuse71-spring-boot-camel-amq s2i-fuse71-spring-boot-camel-config s2i-fuse71-spring-boot-camel-drools s2i-fuse71-spring-boot-camel-infinispan s2i-fuse71-spring-boot-camel-rest-sql s2i-fuse71-spring-boot-camel-teiid s2i-fuse71-spring-boot-camel s2i-fuse71-spring-boot-camel-xa s2i-fuse71-spring-boot-camel-xml s2i-fuse71-spring-boot-cxf-jaxrs s2i-fuse71-spring-boot-cxf-jaxws system)

# for overview
#s2i-fuse71-spring-boot-camel-amq
#s2i-fuse71-spring-boot-camel-config
#s2i-fuse71-spring-boot-camel-drools
#s2i-fuse71-spring-boot-camel-infinispan
#s2i-fuse71-spring-boot-camel-rest-sql
#s2i-fuse71-spring-boot-camel-teiid
#s2i-fuse71-spring-boot-camel
#s2i-fuse71-spring-boot-camel-xa
#s2i-fuse71-spring-boot-camel-xml
#s2i-fuse71-spring-boot-cxf-jaxrs
#s2i-fuse71-spring-boot-cxf-jaxws
#system


# making sure list does not already exist
rm -f templates.txt all-templates.txt clusterserviceclass.txt

oc get clusterserviceclass --no-headers > clusterserviceclass.txt
oc get templates -n openshift --no-headers | awk '{print $1}' > all-templates.txt

for i in ${list_to_keep[@]}; do
  oc get template --no-headers $i -n openshift | awk '{print $1}' >> templates.txt
done

oc delete clusterserviceclass $(grep -vf templates.txt clusterserviceclass.txt | awk '{print $1}')

oc delete template $(grep -vf templates.txt all-templates.txt) -n openshift

# cleanup
rm -f clusterserviceclass.txt templates.txt all-templates.txt