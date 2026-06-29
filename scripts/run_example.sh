#!/usr/bin/env bash
set -euo pipefail
python -m nb_auto.cli submit-yaml configs/example_job.yaml --download
