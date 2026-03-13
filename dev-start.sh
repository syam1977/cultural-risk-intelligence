#!/bin/bash
# dev-start.sh - Local development launcher with ADC check
# DO NOT use this on Cloud Run. Use start.sh directly.

echo "=== Checking Google Auth (ADC) ==="
python3 -c "
import google.auth
import google.auth.transport.requests
try:
    creds, proj = google.auth.default()
    req = google.auth.transport.requests.Request()
    if hasattr(creds, 'token') and creds.token:
        print(f'ADC OK (project: {proj})')
    else:
        creds.refresh(req)
        print(f'ADC OK after refresh (project: {proj})')
except Exception as e:
    print(f'ADC NG: {e}')
    exit(1)
" 2>/dev/null
AUTH_STATUS=$?

if [ $AUTH_STATUS -ne 0 ]; then
    echo ""
    echo "ADC not configured. Attempting fix..."
    gcloud auth application-default set-quota-project avex-corp-elearning
    if [ $? -ne 0 ]; then
        echo ""
        echo "Auto-fix failed. Please run manually:"
        echo "  gcloud config set auth/impersonate_service_account \"\""
        echo "  gcloud auth application-default set-quota-project avex-corp-elearning"
        exit 1
    fi
fi

echo ""
echo "=== Starting server ==="
./start.sh
