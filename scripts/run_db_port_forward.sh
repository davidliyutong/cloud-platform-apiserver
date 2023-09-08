$NS=clpl
$DB_SERVICE_NAME=mongodb

kubectl -n $NS port-forward service/$DB_SERVICE_NAME 27017
