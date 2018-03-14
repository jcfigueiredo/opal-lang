#!/bin/bash

fname=$1

clang -emit-llvm -S "$fname".c -o "$fname".ll
opt -mem2reg -S "$fname".ll -O3 -o "$fname"-opt.ll
