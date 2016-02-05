#!/bin/bash
set -e
set -x

python planetrestless.py &
sleep 4
python planetrestless_tests.py
kill %1
