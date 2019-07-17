#!/bin/bash
id

cd /home/kessler/paas-labs/ofer-cd

export KUBECONFIG=$PWD/kubeconfig

kubectl cluster-info

splatt kubectl -n gocd get all

helm list
