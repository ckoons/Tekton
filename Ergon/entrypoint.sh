#!/bin/bash
if [[ "$1" == "ui" ]]; then
    shift
    ergon ui "$@"
elif [[ "$1" == "api" ]]; then
    shift
    uvicorn ergon.api.app:app --host 0.0.0.0 --port 8000
elif [[ "$1" == "init" ]]; then
    shift
    ergon init "$@"
elif [[ "$1" == "preload-docs" ]]; then
    shift
    python -m ergon.cli.main preload-docs "$@"
else
    ergon "$@"
fi