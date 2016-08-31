FROM golang:latest

RUN apt-get update && apt-get install -y time libpcap-dev

# Aug 29, 2016
ARG ETCD_CHECKOUT=e53b99588a05d1f4ef172c178d4ed8e8106b8be4
RUN mkdir -p $GOPATH/src/github.com/coreos && \
 cd $GOPATH/src/github.com/coreos && \
 git clone https://github.com/coreos/etcd.git && \
 cd etcd && \
 git checkout $ETCD_CHECKOUT
WORKDIR $GOPATH/src/github.com/coreos/etcd

# Pre-compile test binaries at once, using go-test-helper.sh
# NOTE: rafttest has been disabled by default (https://github.com/coreos/etcd/pull/5707)
RUN ./build && \
  go list -f '{{if len .TestGoFiles}}{{.ImportPath}}{{end}}' ./... | grep -v rafttest > /pkgs.txt
ADD go-test-helper.sh /
RUN GOPATH=$(pwd)/gopath time go test -p $(($(nproc)*2)) -cover -race -v -exec /go-test-helper.sh $(cat /pkgs.txt)

ADD NamazuSwarmfile /
RUN chmod +x /NamazuSwarmfile

CMD echo "hack for keeping the container running" && tail -f /dev/null
