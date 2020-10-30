#!/bin/bash

HELP() {


  echo "This script will grant users access to chosen namespaces."
  echo 
  echo "To use, run: 'sh onboarding.sh [-u, -n]"
  echo 
  echo "For more information about the access that is being assigned, run 'oc describe clusterrole edit'"
  echo 
  echo "options:"
  echo "-u      This is the name of your user as identified through AD. Run 'oc get users' to view existing users in the cluster."
  echo "-n      Choose a namespace that you want to give the user access to."
  echo "-h      Run this help section."
  exit 1
}

which oc > /dev/null

if [ $? == 1 ]
then
  echo "oc client was not found. Please install and place it in your path."
  exit 1
fi

while getopts ":u:n:h" opt; do
  case ${opt} in
    u )
      username=${OPTARG}
      ;;
    n )
      namespace=${OPTARG}
      ;;
    h )
      HELP
      exit 0
      ;;
    \? )
      echo "Invalid option: '$OPTARG' run -h for more information." 1>&2
      exit 1
      ;;
    : )
      echo "Invalid option: '$OPTARG' requires an argument. Run -h for more information." 1>&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

oc adm policy add-role-to-user edit ${username} -n ${namespace}
echo "The user ${username} has now been granted access to the project '${namespace}'."
