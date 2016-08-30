FROM golang:latest

RUN apt-get update && apt-get install -y libpcap-dev

# Aug 29, 2016
ARG ETCD_CHECKOUT=e53b99588a05d1f4ef172c178d4ed8e8106b8be4
RUN mkdir -p $GOPATH/src/github.com/coreos && \
 cd $GOPATH/src/github.com/coreos && \
 git clone https://github.com/coreos/etcd.git && \
 cd etcd && \
 git checkout $ETCD_CHECKOUT
WORKDIR $GOPATH/src/github.com/coreos/etcd
RUN ./build && cp -r bin gopath

ADD NamazuSwarmfile /
RUN chmod +x /NamazuSwarmfile

CMD echo "hack for keeping the container running" && tail -f /dev/null
