# Rhetor CI Communication Protocol

## Overview

AIs are just sockets. They read input, write output. Nothing more.

## Core Operations

### Create
```python
socket_id = rhetor.create(model="claude-3", prompt="Be helpful", context={})
```
Creates new CI instance, returns socket identifier.

### Read
```python
messages = rhetor.read("apollo-123")      # Read from specific AI
messages = rhetor.read("team-chat-all")   # Read from all CIs
```
Reads automatically add source headers: `[team-chat-from-apollo-123] message`

### Write
```python
rhetor.write("apollo-123", "Analyze this")     # Write to specific AI
rhetor.write("team-chat-all", "Status report") # Write to all CIs
```
Writes automatically add destination headers: `[team-chat-to-apollo-123] message`

### Delete
```python
rhetor.delete("apollo-123")  # Terminate AI, clean up socket
```

### Reset
```python
rhetor.reset("apollo-123")   # Clear context, keep socket alive
```

## Socket Registry

All sockets registered in Rhetor's central registry:
```python
registry = {
    "rhetor": socket_0,          # Rhetor's own listening socket
    "apollo-123": socket_1,      # CI instances
    "athena-456": socket_2,
    "team-chat-all": broadcast,  # Special broadcast socket
}
```

## Header Format

Messages wrapped with headers for routing:
- `[team-chat-from-X]` - Source identification (added by Read)
- `[team-chat-to-Y]` - Destination routing (added by Write)
- `[urgent]` - Priority handling
- `[debug-context]` - Debug stream
- `[audio-in]`, `[video-in]` - Media type markers

## Pipeline Notation

Express CI communication flows using Unix pipes:

### Simple Flows
```bash
# Basic query
user_input | rhetor | response

# Team consultation
question | rhetor | tee apollo athena | rhetor | answer

# Multi-modal
audio.stream | whisper | rhetor | claude | tts | speaker.stream
```

### Complex Topologies
```bash
# Parallel processing
input | rhetor | tee >(apollo > pred.tmp) >(athena > know.tmp) | wait
cat *.tmp | rhetor[synthesize] | output

# Context injection
problem | athena > knowledge.ctx
knowledge.ctx | prometheus > plan.ctx
cat *.ctx | rhetor | solution
```

## Everything is a File

- Text AI: stdin → ai-socket → stdout
- Audio AI: audio.stream → ai-socket → audio.out
- Vision AI: video.stream → ai-socket → analysis.out
- Multi-modal: all.streams → ai-socket → unified.out

## Usage Examples

### Team Chat Message Flow
```python
# User asks question
rhetor.write("team-chat-all", "How to optimize the system?")

# Each CI reads from their socket
apollo_msg = rhetor.read("apollo")     # "[team-chat-to-apollo-123] How to optimize?"
athena_msg = rhetor.read("athena")     # "[team-chat-to-athena-456] How to optimize?"

# CIs respond
apollo_socket.write("Prediction: 30% improvement possible")
athena_socket.write("Knowledge: See optimization patterns...")

# Rhetor reads responses
msgs = rhetor.read("rhetor")  # Gets all responses with source headers
```

### Creating Specialized Pipeline
```bash
# Define topology
echo "user question" | 
rhetor |
tee >(grep -i "technical" | apollo > tech.analysis) \
    >(grep -i "business" | hermes > biz.analysis) |
rhetor[wait-and-merge] |
synthesis > final.answer
```

## Implementation Notes

1. **Sockets are just file descriptors** - Can be files, pipes, network sockets
2. **Headers are transparent** - CIs only see message content, not headers
3. **Registry is the source of truth** - All socket lookups go through registry
4. **No magic** - Just read, write, and process streams

## Error Handling

- Socket not found: Returns empty read, logs error
- Write to closed socket: Message dropped, error logged
- Malformed header: Treated as plain message
- Registry conflict: Last registration wins

---

Simple. Works. Hard to screw up.

## Future Direction: aish - The CI Shell

Rhetor is evolving into `aish`, a full command-line shell for multi-CI distributed computing.

### Vision

Just as `bash` orchestrates processes, `aish` will orchestrate CIs:

```bash
$ aish
aish> apollo | athena | sophia > analysis.txt
aish> team-chat << EOF
Design a distributed cache
EOF
aish> for ai in apollo athena; do
>   echo "status" | $ai | grep ready
> done
```

### Features

**Interactive Shell**
```bash
aish> echo "question" | apollo     # Simple pipeline
aish> jobs                         # List running CI pipelines  
aish> fg 1                         # Bring CI pipeline to foreground
aish> history | grep "optimize"    # Search command history
```

**Script Execution**
```bash
#!/usr/bin/aish
# analyze.ai - executable CI script
input=$1
$input | athena > knowledge.tmp &
$input | apollo > prediction.tmp &
wait
cat *.tmp | rhetor[synthesize]
```

**Distributed CI Computing**
```bash
# Remote CI execution
aish> echo "analyze" | ssh node1 apollo

# Parallel distributed processing
aish> scatter "big_problem.txt" | parallel --host nodes.txt apollo | gather

# CI cluster management  
aish> ps -ai                      # List all CI instances
aish> kill -RESET apollo-123      # Reset specific AI
aish> nice -ai 10 sophia          # Lower CI priority
```

**Shell Integration**
```bash
# .aishrc configuration
alias think="apollo | athena | rhetor[merge]"
alias review="tee apollo athena hermes | rhetor[vote]"
export AIPATH=/usr/local/ai:/home/user/ai

# Mix with Unix tools
aish> cat data.csv | awk '{print $2}' | apollo | sort -n
aish> find . -name "*.py" | xargs -I {} sh -c 'echo {} | athena review'
```

### Why This Matters

1. **Universal CI Interface** - Every Unix tool works with CIs
2. **Distributed by Design** - CIs can run anywhere, like Unix processes
3. **Composable** - Build complex CI systems from simple pipelines  
4. **Familiar** - 50 years of Unix knowledge applies immediately

The command line that conquered computing will now orchestrate intelligence.