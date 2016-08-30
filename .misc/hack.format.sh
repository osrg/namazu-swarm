#!/bin/sh
set -x
set -e

# requires yapf (`pip3 install yapf`)
yapf --recursive --in-place .
