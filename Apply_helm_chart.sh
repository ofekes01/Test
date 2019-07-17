#!/bin/bash
id

cd /home/kessler/paas-labs/ofer-cd

export KUBECONFIG=$PWD/kubeconfig

kubectl cluster-info

source /home/kessler/v0.19.2/bin/activate 

splatt kubectl -n gocd get all

helm list
