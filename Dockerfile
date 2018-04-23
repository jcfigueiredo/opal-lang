FROM circleci/python:3.6.5

LABEL maintainer="jcfigueiredo@gmail.com"
LABEL repo="jcfigueiredo@gmail.com"

RUN wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
RUN sudo apt-get install -y software-properties-common
RUN sudo apt-add-repository "deb http://apt.llvm.org/jessie/ llvm-toolchain-jessie-5.0 main" && sudo apt-get update && sudo apt-get install -y llvm-5.0 clang-5.0 llvm-5.0-tools && sudo apt-get clean

RUN sudo ln -s $(which clang-5.0) /usr/local/bin/clang && sudo ln -s $(which lli-5.0) /usr/local/bin/lli
