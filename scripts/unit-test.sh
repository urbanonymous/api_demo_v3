#!/usr/bin/env bash
set -ex

# Start application
pytest tests/unit --asyncio-mode=auto
