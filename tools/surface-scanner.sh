#!/bin/bash
# Oscar Lindholm olindhol@redhat.com

## Script to get a general health overview of your cluster
#
# Pre-req testing - OC client exists and a user is logged in
which oc > /dev/null

if [ $? == 1 ]; then
  echo "oc client was not found. Please install and place it in your path."
  exit 1
fi

oc whoami > /dev/null
if [ $? == 1 ]; then
  echo "Please login to the cluster before use."
  exit 1
fi

# Variables
REPORT=/tmp/ClusterReport.txt
OCVER=$(oc version | grep oc)
OCAPI=$(oc whoami --show-server)
RESOURCES=pods,cronjobs,jobs,deployments,deploymentconfigs,daemonsets,statefulsets,builds,buildconfigs,replicasets,replicationcontrollers
# Colors
DARK_RED="\e[0;31m"
RED="\e[1;31m"
BLUE="\e[1;34m"
NO_COL="\e[0m"
GREEN="\e[1;32m"


# Main function
function main() {
case $1 in 

        -s) fullScan
        ;;
        -h) helpmsg
        ;;
        *) helpmsg
        ;;
esac
}

function helpmsg() {
echo "   _____             __                  _____                                 ";
echo "  / ____|           / _|                / ____|                                ";
echo " | (___  _   _ _ __| |_ __ _  ___ ___  | (___   ___ __ _ _ __  _ __   ___ _ __ ";
echo "  \___ \| | | | '__|  _/ _\` |/ __/ _ \  \___ \ / __/ _\` | '_ \| '_ \ / _ \ '__|";
echo "  ____) | |_| | |  | || (_| | (_|  __/  ____) | (_| (_| | | | | | | |  __/ |   ";
echo " |_____/ \__,_|_|  |_| \__,_|\___\___| |_____/ \___\__,_|_| |_|_| |_|\___|_|   ";
echo "                                                                               ";
echo "                                                                               ";
echo -e "${DARK_RED} Detected OpenShift version: ${OCVER}${NO_COL}"
echo
echo "Usage: $0 [options]"
echo
echo "Options:"
echo "    -s          Performs a surface scan of the cluster - reports the results and sends it to ${REPORT}"
echo "    -h		Prints this messages and exits."

exit
}
#################################################################
# Does a simple curl check to the API endpoints
#
# Reports the results to the report file
#################################################################
function apiCheck() {
         echo "--------------------------------------------------"
         echo -e "${BLUE} Testing API endpoints${NO_COL}"
         echo ""
         printf "\nAPI ENDPOINT TESTS\n" >> ${REPORT}
	 curl -s -k ${OCAPI}/healthz?verbose >> ${REPORT}
	 if grep -q 'healthz check passed' ${REPORT}; then
     		echo -e "${GREEN} Endpoint check passed.${NO_COL}"
         else
     		echo -e "${RED} Something failed.${NO_COL}"
 	 fi
}
#################################################################
# Checks the compute usage of the nodes
#
# Prints a warning or pass and reports to the report file
#################################################################
function nodeCheck() {
         echo "--------------------------------------------------"
         echo -e "${BLUE} Checking node resource usage...${NO_COL}"
         printf "\nNODE RESOURCE USAGE:\n" >> ${REPORT}
         oc adm top node >> ${REPORT}
         oc adm top node | awk '{print $3}' > tmp-node-cpu.txt
         oc adm top node | awk '{print $5}' > tmp-node-mem.txt
         # Removing all but the numbers we need
         sed -i 's/%//g' tmp-node-cpu.txt tmp-node-mem.txt
         sed -i '1d' tmp-node-cpu.txt tmp-node-mem.txt
         # Scan the files for a eq or gt value
         if ! awk '{exit $1 >= 85}' tmp-node-cpu.txt; then
             echo -e "${RED} CPU usage of over 85% detected! - More information in ${REPORT}${NO_COL}"
             NODE_RESULT="FAILED"
         else 
             echo ""
             echo -e "${BLUE} CPU usage under 85%.${NO_COL}"
         fi
         if ! awk -v x=85 '{exit $1 >= x}' tmp-node-mem.txt; then
             echo -e "${RED} Memory usage of over 85% detected! - More information in ${REPORT}${NO_COL}"
             NODE_RESULT="FAILED"
         else
             echo ""
             echo -e "${BLUE} Memory usage under 85%.${NO_COL}" 
         fi
         echo ""
         if [[ $NODE_RESULT == "FAILED" ]]; then
            echo -e "${RED} FAILED - Node usage is over 85%${NO_COL}"
         else
            echo -e "${GREEN} PASS - Node usage is under 85%${NO_COL}"
         fi
         # Removing temporary node-files
         rm -f tmp-node-*
}
#################################################################
# Looks for namespaces that holds no workload
#
# Compares the list of NS:es with the RESOURCE variable
# Prints the results and sends it to the report file
#################################################################
function nsCheck() {
         echo "--------------------------------------------------"
         echo -e "${BLUE} Scanning for namespaces without current running workload...${NO_COL}"
         printf "\nNO RUNNING WORKLOADS FOUND IN NAMESPACES:\n" >> ${REPORT}
         oc get ns --no-headers -o=custom-columns=NAME:.metadata.name > tmp-namespaces.txt
         oc get ${RESOURCES} --no-headers --all-namespaces -o=custom-columns=NAMESPACE:.metadata.namespace | sort -u > tmp-resources.txt
         echo ""
         echo -e "${GREEN} List of namespaces found without a workload: ${NO_COL}" 
         grep -vf tmp-resources.txt tmp-namespaces.txt | tee -a ${REPORT}

         # Removing temporary files
         rm -f tmp-resources.txt tmp-namespaces.txt
}
#################################################################
# Checks the status code of all routes
#
# Compares the list of NS:es with the RESOURCE variable
# Prints the results and sends it to the report file
#################################################################
function routeCheck() {

# first create a variable containing all hosts

HOSTS=$(oc get route --all-namespaces -o jsonpath='{.items[*].spec.host}')

# Prepare the section in the report

         echo ""
         echo "--------------------------------------------------"
         echo -e "${DARK_RED} HTTP return code of routes: ${NO_COL}"
         echo "" 

         for HOST in $HOSTS ; do
           curl https://$HOST -k -I -w "%{url_effective} %{http_code}\n" -o /dev/null -s | tee -a tmp-route-check.txt
         done

         ERROR_ROUTES=$(awk '{print $2}' tmp-route-check.txt | grep -v '^2' | wc -l)
         NR_OF_ROUTES=$(wc -l < tmp-route-check.txt)
         echo ""
         echo -e "${BLUE} Number of routes found: ${NR_OF_ROUTES} ${NO_COL}"
         echo -e "${RED} Number of routes with non 200 status codes: ${ERROR_ROUTES} ${NO_COL}"
         printf "\nROUTES AND STATUS CODES: \n" >> ${REPORT}
         cat tmp-route-check.txt >> ${REPORT}
      
         # Removing temp file
         rm -f tmp-route-check.txt

}
#################################################################
# Looks for pods stuck in CrashLoop, Failed or Pending statuses
# 
# 
# Prints results and sends it to the report file
#################################################################
function podCheck() {
         
         echo ""
         echo "--------------------------------------------------"
         echo -e "${BLUE} Checking for faulty pods.${NO_COL}"
         echo ""
         printf "\nPENDING AND CRASHLOOP PODS: \n" >> ${REPORT}
         # Gather the namespaces, pods and pod statuses
         oc get pods --all-namespaces -o=custom-columns=NAMESPACE:.metadata.namespace,POD:.metadata.name,STATUS:.status.phase \
         | grep -v -e 'Running' -e 'Succeeded' | tee -a tmp-pod-status.txt ${REPORT}

# Saving count of Failed and crashing pods
PENDING_PODS=$(grep -c Pending tmp-pod-status.txt)
CRASH_PODS=$(grep -c CrashLoop tmp-pod-status.txt)
FAILED_PODS=$(grep -c Failed tmp-pod-status.txt)

         echo ""
         if [[ ${PENDING_PODS} -ge 1 ]]; then
           echo -e "${RED} Pending pod number: ${PENDING_PODS} ${NO_COL}"
         else
           echo -e "${GREEN} No Pending pods. ${NO_COL}"
         fi
         if [[ ${CRASH_PODS} -ge 1 ]]; then
           echo -e "${RED} Pods stuck in CrashLoop: ${CRASH_PODS} ${NO_COL}"
         else
           echo -e "${GREEN} No pods in CrashLoop. ${NO_COL}"
         fi
         if [[ ${FAILED_PODS} -ge 1 ]]; then
           echo -e "${RED} Number of failed pods: ${FAILED_PODS} ${NO_COL}"
         else
           echo -e "${GREEN} No failed pods. ${NO_COL}"
         fi

# Cleaning up
         rm -f tmp-pod-status.txt
}
#################################################################
# Looks for workload older than 9 days
# 
# 
# Prints results and sends it to the report file
#################################################################
function workloadAge() {
         
         echo ""
         echo "--------------------------------------------------"
         echo -e "${BLUE} Checking for long running pods.${NO_COL}"
         echo ""
         printf "\nPODS & RUNTIME: \n" >> ${REPORT}

# First set the date variables
         C_DATE=$(date -d "-9days $(date +%F) day" +%s)
         CU_DATE=$(date +%s)
         CUT_DATE=$((CU_DATE-$C_DATE))
# Get age of pods
         POD_DATE=$(oc get pods --all-namespaces -o=custom-columns=NAMESPACE:.metadata.namespace,POD:metadata.name,AGE:.metadata.creationTimestamp | awk '{ print $3 }' | sed 's/\T.*$//' | sed 's/AGE//')

         for pod in $POD_DATE; do
           date -d $pod +%s >> tmp-pod-date.txt
         done

LONG_PODS=0

         for line in $(cat tmp-pod-date.txt); do
           if [ $((line+$CUT_DATE)) -lt ${C_DATE} ]; then
             LONG_PODS=$((LONG_PODS+1))
             echo $(date -d @$line +%F) >> tmp-test.txt
           fi
         done

         if [ ${LONG_PODS} -gt 1 ]; then
           echo "Amount of long running pods: ${LONG_PODS}"
         else
           echo -e "${GREEN} Found no long running pods in the cluster.${NO_COL}"
         fi

         # Print data for manipulation
         oc get pods --all-namespaces -o=custom-columns=NAMESPACE:.metadata.namespace,POD:metadata.name,AGE:.metadata.creationTimestamp >> pod-date.txt

         # Create a new column with the AGE of the pods
         awk -v OFS='\t' 'BEGIN { printf "%s\n", "AGE"} {print $1}' tmp-test.txt > tmp-test2.txt
         # Replace the third column in the pod-date file with the newly created column
         # Warning - messy formatting
         awk  'FNR==NR{a[NR]=$1;next}{$3=a[FNR]}1' tmp-test2.txt pod-date.txt >> ${REPORT}
         # Removing the temp file
         rm -f tmp-pod-date.txt pod-date.txt tmp-test.txt tmp-test2.txt

         # Removing the temp file
         rm -f tmp-pod-date.txt                
}
#################################################################
# Calls all functions to perform a scan
#
# Creates a report file. If the file already exists,
# backs up the old one first.
#################################################################
function fullScan() {

echo "   _____             __                  _____                                 ";
echo "  / ____|           / _|                / ____|                                ";
echo " | (___  _   _ _ __| |_ __ _  ___ ___  | (___   ___ __ _ _ __  _ __   ___ _ __ ";
echo "  \___ \| | | | '__|  _/ _\` |/ __/ _ \  \___ \ / __/ _\` | '_ \| '_ \ / _ \ '__|";
echo "  ____) | |_| | |  | || (_| | (_|  __/  ____) | (_| (_| | | | | | | |  __/ |   ";
echo " |_____/ \__,_|_|  |_| \__,_|\___\___| |_____/ \___\__,_|_| |_|_| |_|\___|_|   ";
echo "                                                                               ";
echo "                                                                               ";
         echo "--------------------------------------------------"
         echo -e "${BLUE} Starting a surface scan of the cluster.${NO_COL}"
         echo ""
         echo ""
         if [[ -f ${REPORT} ]]; then
         OLD_REPORT=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 9 |head -n 1)
             echo " A previous report already exist. Moving it to ${REPORT}.${OLD_REPORT}"
             mv ${REPORT} ${REPORT}.${OLD_REPORT}
         fi
         echo " After completion the full report can be found at ${REPORT}"
         echo ""
         echo -e "${DARK_RED} OpenShift version is: ${OCVER}${NO_COL}" 
         echo "Scan started at $(date): " >> ${REPORT}

apiCheck

nodeCheck

nsCheck

routeCheck

podCheck

workloadAge
echo ""
echo -e "${GREEN} Scan completed. For details, read ${REPORT}${NO_COL}"
}


main $1
