FROM java:8
RUN apt-get update && apt-get install -y ant

# May 26, 2017
ARG ZK_CHECKOUT=5bfcc13fd6820c212d67c39fede4dc4a50d84d83
RUN git clone https://github.com/apache/zookeeper.git && \
 cd zookeeper && \
 git checkout $ZK_CHECKOUT
WORKDIR zookeeper

RUN ant && ant test-init

ADD master.sh /
ADD worker.sh /
RUN chmod +x /master.sh /worker.sh
LABEL net.osrg.namazu-swarm.v0.master.script="/master.sh" \
      net.osrg.namazu-swarm.v0.worker.script="/worker.sh"

# Execute the whole test when running without nmzswarm.
# This ENTRYPOINT will be overridden when running with nmzswarm.
ENTRYPOINT ["ant", "test-core-java"]
