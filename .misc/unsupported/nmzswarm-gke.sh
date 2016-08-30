#!/bin/sh
# Usage:
#  $ docker build -t etcd-nmzswarm ./example/etcd
#  $ gcloud container clusters get-credentials <CLUSTER> \
#    --zone <ZONE> --project <PROJECT_ID>
#  $ PARALLEL=50 <THIS_SCRIPT> etcd-nmzswarm
set -e # exit on an error

: ${PROJECT:=$(gcloud config list --format='value(core.project)')}
: ${GCR:=asia.gcr.io}
IMAGE=$1
: ${TAG:=$(date +%s)}
: ${PARALLEL=10}
: ${LOGS=/tmp/logs}
: ${NMZSWARM=nmzswarm}

set -x
docker tag $1 $GCR/$PROJECT/$IMAGE:$TAG
time gcloud docker --server $GCR -- push $GCR/$PROJECT/$IMAGE:$TAG
time $NMZSWARM --driver=k8s run --ui simple --parallel $PARALLEL --logs $LOGS $GCR/$PROJECT/$IMAGE:$TAG
set +x
