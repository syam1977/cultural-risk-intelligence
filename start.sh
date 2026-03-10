#!/bin/bash
export GOOGLE_CLOUD_PROJECT=avex-corp-elearning
export GOOGLE_CLOUD_LOCATION=global
export GOOGLE_CLOUD_LIVE_LOCATION=us-central1
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --loop asyncio
