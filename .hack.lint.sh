#!/bin/sh
set -x
set -e

mypy --silent-imports  -p nmzswarm

# C0103: invalid-name
# I0011: locally-disabled
# R0903: too-few-public-methods
# R0913: too-many-arguments
# W0511: fixme
pylint --msg-template='{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}' --disable C0103,I0011,R0903,R0913,W0511 nmzswarm
