FROM busybox
ADD tests.txt /
LABEL net.osrg.namazu-swarm.v0.master.script="cat /tests.txt" \
      net.osrg.namazu-swarm.v0.worker.script="sh -e -x"
