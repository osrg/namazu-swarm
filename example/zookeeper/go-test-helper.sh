#!/bin/sh
bin=$1
pkgdir=$(echo $(pwd) | sed -e s@$GOPATH/src@@g)
dstdir=/testbin$pkgdir
echo "Copying $bin to $dstdir (NOT executing!)"
mkdir -p $dstdir
cp $bin $dstdir
