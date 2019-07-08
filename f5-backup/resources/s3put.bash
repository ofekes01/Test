#!/bin/bash
# Upload Files to an Amazon S3 Bucket
# Ofer Kessler
# v1.0.0, 21/04/2019

trap "echo; echo 'Exiting...'; exit" SIGINT

if (( $# < 2 )); then
        echo; echo "Usage: ./s3put {BUCKET_NAME}[/PATH/] {FILE_TO_UPLOAD} [REGION]"; echo
        exit
fi
export AWS_HOME=/opt/aws/awscli-1.10.26
export AWS_DEFAULT_REGION="$3"
export PATH=$PATH:${AWS_HOME}/bin
export PYTHONPATH=${AWS_HOME}/lib/python2.6/site-packages:/opt/aws/awscli-1.10.26//lib64/python2.6/site-packages

FILE_TO_UPLOAD="$2"
BUCKET=$(echo "$1" | cut -d'/' -f1)

if [[ $(aws s3 cp ${FILE_TO_UPLOAD} s3://${BUCKET}/) ]]; then
    echo 204
else
    echo 400
   fi
