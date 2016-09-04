FROM java:7

ENV JAVA_TOOL_OPTIONS -Dfile.encoding=UTF8
RUN apt-get update && apt-get install -y ant

# Aug 25, 2016
ARG ZK_CHECKOUT=c1b496442130b8b5c3795c7efcb9020de58dd698
RUN git clone https://github.com/apache/zookeeper.git && \
 cd zookeeper && \
 git checkout $ZK_CHECKOUT
WORKDIR zookeeper

RUN ant && ant test-init

ADD commands.jsonl /
ADD NamazuSwarmfile /
RUN chmod +x /NamazuSwarmfile

CMD echo "hack for keeping the container running" && tail -f /dev/null
