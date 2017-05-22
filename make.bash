#!/bin/bash
set -e
[ $(uname -s) = "Linux" ] || { echo "Unsupported OS: $(uname -s)"; exit 1; }
pkg=github.com/osrg/namazu-swarm

echo "$pkg/cmd/nmzswarm"
go build -o bin/nmzswarm $pkg/cmd/nmzswarm
for f in cmd/nmzswarm-agent*;do
    echo "$pkg/$f (static)"
    bin=bin/$(basename $f)
    go build -ldflags "-linkmode external -extldflags -static" -o $bin $pkg/$f
    file $bin | grep "statically linked, for GNU/Linux" > /dev/null || { echo "failed to build ${bin} as a statically-linked binary"; exit 1; }
done
