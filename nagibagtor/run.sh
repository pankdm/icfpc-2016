#!/usr/bin/env bash

while [ 1 ]; do
    ./nagibator 2>err.$$ | tee >out.$$
    echo "restart..."
done
