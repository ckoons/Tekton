# aish Help System - Implementation Plan

## Overview

This document details the implementation steps for the aish help system sprint.

## Implementation Steps

### Step 1: Create Documentation Directory Structure

Create all directories for AI Training and User Guides:

```bash
# Base directories
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides

# Component directories for AI Training
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/aish
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/numa
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/tekton
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/prometheus
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/telos
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/metis
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/harmonia
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/synthesis
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/athena
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/sophia
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/noesis
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/engram
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/apollo
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/rhetor
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/penia
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/hermes
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/ergon
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/terma

# Component directories for User Guides
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/aish
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/numa
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/tekton
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/prometheus
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/telos
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/metis
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/harmonia
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/synthesis
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/athena
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/sophia
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/noesis
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/engram
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/apollo
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/rhetor
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/penia
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/hermes
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/ergon
mkdir -p /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/terma
```

### Step 2: Create README Files

Create placeholder README.md files in each directory:

```bash
# AI Training READMEs
echo "# AI Training Documentation\n\nThis directory contains training materials for Companion Intelligences." > /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/README.md

# User Guides READMEs  
echo "# User Guide Documentation\n\nThis directory contains guides for human users." > /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/README.md

# Component-specific placeholders will be created with appropriate content
```

### Step 3: Modify aish Command

Add help handling to `/Users/cskoons/projects/github/Tekton/shared/aish/aish`:

```python
# After line 91 (args = parser.parse_args())

    # Handle help command
    if args.ai_or_script == "help":
        # General aish help
        print("Usage: aish [options] [ai] [message]")
        print("AI Training: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/aish/")
        print("User Guides: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/aish/")
        return
    
    # Check if requesting component help
    if args.ai_or_script in ai_names and args.message and args.message[0] == "help":
        component = args.ai_or_script
        print(f"Usage: aish {component} [message]")
        print(f"AI Training: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/AITraining/{component}/")
        print(f"User Guides: /Users/cskoons/projects/github/Tekton/MetaData/TektonDocumentation/UserGuides/{component}/")
        return
```

### Step 4: Test Implementation

Test all help commands:
```bash
aish help
aish terma help
aish apollo help
# ... test each component
```

### Step 5: Document Results

Update sprint documentation with implementation results.