#!/bin/bash


origin=$1

clang -emit-llvm -S "$origin" -o ${origin/.c/.ll}
#opt -fsanitize=undefined -mem2reg -S "$fname".ll -O3 -o "$fname"-opt.ll
