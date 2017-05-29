#!/bin/sh
find src/java/test -name '*Test.java' -printf '%f\n' | sed -e 's/\.java$//g' | sort
