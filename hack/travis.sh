#!/bin/sh
set -e
echo "========== BUILD =========="
set -x
./make.bash
export PATH=$(pwd)/bin:$PATH
set +x

echo "========== Test: dummy =========="
set -x
docker build -t dummy ./example/dummy
nmzswarm -docker-stack dummy \
         -source dummy \
         -replicas 10
set +x

echo "========== Test: dummy-fail =========="
set -x
docker build -t dummy-fail ./example/dummy-fail
nmzswarm -docker-stack dummy-fail \
         -source dummy-fail \
         -replicas 10 && { echo should fail; false; }
set +x
