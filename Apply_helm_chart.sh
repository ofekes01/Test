#!/bin/bash
id

wget -q https://storage.googleapis.com/kubernetes-helm/helm-v2.14.1-linux-amd64.tar.gz -O - | tar -xzO linux-amd64/helm > /usr/local/sbin/helm \
chmod +x /usr/local/sbin/helm

 wget -q https://storage.googleapis.com/kubernetes-release/release/v1.15.0/bin/linux/amd64/kubectl /usr/local/sbin/kubectl -O /usr/local/sbin/kubectl
 chmod +x /usr/local/sbin/kubectl
 
 /usr/local/sbin/kubectl
 /usr/local/sbin/helm
 
