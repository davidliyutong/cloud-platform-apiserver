#!/bin/bash

NS=clpl

while [[ "$#" -gt 0 ]]; do
    case "$1" in
    -n | --namespace)
        NS="$2"
        shift
        ;;
    *)
        echo "illegal option: $1" >&2
        exit 1
        ;;
    esac
    shift
done

echo "Starting deletion process of Kubernetes objects."

# List of Kubernetes objects to delete
objects=("deployment" "services" "ingress"  "pvc" )

# Loop over the objects
for object_type in "${objects[@]}"; do
    echo "Deleting $object_type with label: k8s-app"

    # Fetch all the object_names with label "k8s-app"
    object_names=$(kubectl -n $NS get "$object_type" -l k8s-app -o jsonpath='{.items[*].metadata.name}')

    # Loop over each object name
    for name in $object_names; do
        echo "Deleting $object_type/$name"
        kubectl -n $NS delete "$object_type" "$name"
    done
done

echo "Deletion process completed."