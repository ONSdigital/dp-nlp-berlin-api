#!/bin/bash -eux

pushd dp-nlp-berlin-api
  make test-component
popd
