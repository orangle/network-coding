#!/bin/bash
if [[ $GOPATH =~ .*$PWD.* ]]
then
    echo "currnet dir is already in GOPATH"
else
    export GOPATH=$GOPATH:$PWD
    echo "fininsh setting $PWD in GOPATH"
fi