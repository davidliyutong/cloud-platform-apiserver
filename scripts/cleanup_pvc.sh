#!/bin/bash

#
#NS=clpl
## Get all PVCs in the specified namespace not in 'Bound' status and older than 1 week
#PVCs=$(kubectl get pvc -n $NS --no-headers=true | awk '{if ($2 != "Bound") print $1, $7}'| while read line; do name=$(echo $line | awk '{print $1}'); date=$(echo $line | awk '{print $2}'); if [[ "$(date -d "$date" +%s)" -lt "$(date -d "1 week ago" +%s)" ]]; then echo $name; fi; done)
#
## Iterate over selected PVCs and delete them
#for pvc in $PVCs
#do
#  echo "Deleting PVC: $pvc"
##  kubectl delete pvc $pvc -n $NS
#done
#
#echo "All released PVCs older than 1 week have been deleted"

# Get all released PVCs
NS=clpl

released_pvcs=$(kubectl -n $NS get pvc -o json | jq -r '.items[] | select(.status.phase=="Released") | .metadata.name')

for pvc in $released_pvcs
do
   # Get the creation timestamp of the PVC
   creation_timestamp=$(kubectl -n $NS get pvc $pvc -o json | jq -r '.metadata.creationTimestamp')

   # Convert the creation timestamp to Unix timestamp
   creation_seconds=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$creation_timestamp" +%s)

   # Get current timestamp in Unix format
   current_seconds=$(date -u +%s)

   # Compute the time difference in seconds
   time_difference=$((current_seconds-creation_seconds))

   # If the time difference is greater than or equal to 3600 seconds (1 hour), delete the PVC
   if [ $time_difference -ge 86400 ]; then
      echo "Deleting $pvc as it is older than 1 day."
      kubectl -n $NS delete pvc $pvc
   fi
done