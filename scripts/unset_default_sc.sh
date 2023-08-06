# Get all storage classes
#!/bin/bash
storageclasses=$(kubectl get sc -o json | jq -r '.items[].metadata.name')

# Loop through storage classes and unset defaults
for sc in $storageclasses; do
      kubectl patch storageclass $sc -p '{"metadata": {"annotations":{"storageclass.kubernetes.io/is-default-class":"false"}}}'
done