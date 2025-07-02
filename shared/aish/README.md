# aish - AI Shell Integration for Tekton

This directory contains the aish (AI Shell) integration for the Tekton platform.

## Overview

aish provides a transparent shell enhancement that routes AI commands through the Tekton platform while passing all other commands to the underlying shell unchanged.

## Components

- `aish` - Main command for AI interaction
- `aish-proxy` - Transparent shell enhancement  
- `aish-history` - History management tool
- `src/` - Python implementation

## Usage

The aish command is automatically available when terminals are launched through Terma.

```bash
# Direct AI interaction
aish apollo "question"

# Piped input
echo "data" | aish athena

# Team chat
aish team-chat "message"

# Interactive shell (via aish-proxy)
./aish-proxy
```

## Integration with Terma

When launched via Terma, terminals automatically have aish available in the PATH and can use all AI routing capabilities through the Tekton platform.

## Environment Variables

- `RHETOR_ENDPOINT` - Override default Rhetor endpoint (default: http://localhost:8003)
- `AISH_ACTIVE` - Set by aish-proxy when active
- `AISH_DEBUG` - Enable debug output