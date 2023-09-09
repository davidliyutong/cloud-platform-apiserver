#!/bin/bash

NS=clpl
SA=clpl-admin


# 解析命令行参数
while [[ "$#" -gt 0 ]]; do
    case "$1" in
    -n | --namespace)
        NS="$2"
        shift
        ;;
    -s | --serviceaccount)
        SA="$2"
        shift
        ;;
    *)
        echo "illegal option: $1" >&2
        exit 1
        ;;
    esac
    shift
done

mkdir -p creds

# Download the credentials for the service account
kubectl -n $NS get secret $SA-secret -o jsonpath='{.data.ca\.crt}' | base64 --decode > ./creds/ca.crt
kubectl -n $NS get secret $SA-secret -o jsonpath='{.data.token}' | base64 --decode > ./creds/token