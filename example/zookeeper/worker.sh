#!/bin/bash
status=0

tests=()
# we need to read all the stdin lines at once for some reason.
# (maybe ant steals our stdin?)
while read r; do
    tests+=( $r )
done
echo "Loaded ${#tests[@]} tests"

executed=0
for t in ${tests[@]}; do
    echo "=== Test $t ==="
    set -x
    ant -Dtestcase=$t test-core-java
    status=$?
    set +x
    echo "=== Test $t done (status: $status) ==="
    let executed++
done
echo "Executed $executed tests, status $status"
exit $status
