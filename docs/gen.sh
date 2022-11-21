#!/bin/bash

cd `dirname $0`/..
lazydocs \
	--output-path="./docs" \
	--overview-file="readme.md" \
	--src-base-url="https://github.com/ronny-rentner/ultraimport/blob/main/" \
	--no-watermark \
	--no-remove-package-prefix \
	--ignored-modules="setup" \
	.

# Postprocess: Remove duplicate emtpy lines
sed -i -z 's/\n\n\n\+/\n\n/g' docs/readme.md
sed -i -z 's/\n\n\n\+/\n\n/g' docs/ultraimport.md
