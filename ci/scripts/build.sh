#!/bin/bash -eux

pushd dp-nlp-berlin-api
  make build-bin
popd

cwd=$(pwd)

pushd dp-nlp-category-api
  make build-bin
  mv dist/ $cwd/build
  mv data/ $cwd/build
  cp Dockerfile.concourse $cwd/build
popd
