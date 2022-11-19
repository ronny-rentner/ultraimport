#!/bin/bash

cd `dirname $0`/..
lazydocs --output-path="./docs" --overview-file="readme.md" --src-base-url="https://github.com/ronny-rentner/ultraimport/blob/main/" --no-watermark --ignored-modules="setup" .
