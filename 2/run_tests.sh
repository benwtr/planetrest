#!/bin/bash
set -e
set -x

python 2/planetrestless.py &
sleep 4
python 2/planetrestless_tests.py
kill %1
