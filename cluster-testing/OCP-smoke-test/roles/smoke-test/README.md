Role Name
=========

A simple "smoke-test" role. Currently does:
- Creates a smoke-test namespace
- Checks if it can pull an image from an external registry
- Checks if wanted storage is provisioned
- Prints the cluster version together with the client version


WIP (Work in progress)

Setting Environment for logging in.

Testing potential networkpolicies?

Checking node status?

Removing everything (oc delete project {{ smoke_test_ns }}

Requirements
------------

Role is using K8s module. Requirements for this module are: openshift >= 0.6 python module, PyYAML >= 3.11 and python >=2.7

Currently the user who runs this playbook needs to be logged in to the cluster before running. (WIP)

Role Variables
--------------

Default variables are set in defaults/main.yml

Variables in use currently are:

* smoke_test_ns: Name of namespace being created
* smoke_test_pod: Name of the test pod
* smoke_test_image: URL to the image being pulled
* smoke_test_pvc: Name of the pvc being created
* smoke_test_pvc2: Name of the second pvc being created

Dependencies
------------


Example Playbook
----------------

---
- name: smoke-test
  hosts: localhost
  become: yes
  vars:
    smoke_test_ns: smoke-testing
  roles:
  - ocp-smoke-test


License
-------

BSD

Author Information
------------------

Oscar Lindholm 

olindhol@redhat.com

