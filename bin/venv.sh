#!/bin/bash

if [ ! -d "./.venv" ]; then
  echo "Creating virtual environment."
  python3 -m venv .venv;
fi

source .venv/bin/activate


