#!/bin/bash
# Run the Ergon LLM adapter example

# Export necessary environment variables
export RHETOR_PORT=8003
export LLM_ADAPTER_URL="http://localhost:${RHETOR_PORT}"
export LLM_PROVIDER="anthropic"
export LLM_MODEL="claude-3-haiku-20240307"

# Check if Rhetor is running
if ! curl -s "$LLM_ADAPTER_URL/health" > /dev/null; then
  echo "Warning: Rhetor LLM adapter does not appear to be running at $LLM_ADAPTER_URL"
  echo "The example will still run but may not be able to connect to the LLM service."
  echo "Consider starting Rhetor with: cd ../Rhetor && python -m rhetor.api.app"
  echo ""
fi

# Run the example
python examples/llm_adapter_example.py