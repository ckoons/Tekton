# Tekton Shared Services

Background services that support the entire Tekton platform.

## Services

### 1. Orphan Process Cleanup Service
Automatically detects and cleans up orphaned Tekton CI processes.

**Features:**
- Runs every 6 hours (configurable)
- Only removes processes older than 2 hours
- Cross-references with CI registry
- Safe termination (SIGTERM before SIGKILL)
- Comprehensive logging

**Configuration:**
- `--orphan-interval`: Hours between cleanup runs (default: 6.0, min: 1.0)
- `--orphan-min-age`: Minimum age before considering process orphaned (default: 2.0)
- `--dry-run`: Only log what would be cleaned

### 2. CI Config Sync Service
Synchronizes CI configuration between config file and registry.

**Features:**
- Monitors for update flags from Rhetor
- Syncs registry state to configuration
- Runs every 30 seconds

## Running Services

### Quick Start
```bash
# Start with defaults (6 hour cleanup interval)
./start_shared_services.sh

# Custom interval (e.g., every 12 hours)
./start_shared_services.sh --orphan-interval 12.0

# Dry run mode (no actual cleanup)
./start_shared_services.sh --dry-run
```

### Standalone Orphan Cleanup
```bash
# Run orphan cleanup once
python3 ../aish/cleanup_orphan_processes.py

# Dry run to see what would be cleaned
python3 ../aish/cleanup_orphan_processes.py --dry-run

# With custom age threshold
python3 ../aish/cleanup_orphan_processes.py --min-age 4.0
```

### Python API
```python
from shared.services.orphan_cleanup_service import OrphanCleanupService

# Create service
service = OrphanCleanupService(
    check_interval=21600,  # 6 hours in seconds
    min_age_hours=2.0,
    dry_run=False
)

# Run in async context
await service.start()

# Check status
status = service.status()
print(f"Next cleanup: {status['next_cleanup']}")

# Stop service
await service.stop()
```

## Installation

### Systemd (Linux)
```bash
# Copy service file
sudo cp tekton-shared-services.service /etc/systemd/system/

# Edit to set correct user and paths
sudo systemctl edit tekton-shared-services.service

# Enable and start
sudo systemctl enable tekton-shared-services
sudo systemctl start tekton-shared-services

# Check status
sudo systemctl status tekton-shared-services
```

### Launchd (macOS)
Create `~/Library/LaunchAgents/com.tekton.shared-services.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tekton.shared-services</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/cskoons/projects/github/Tekton/shared/services/start_shared_services.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/cskoons/.tekton/logs/shared-services.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/cskoons/.tekton/logs/shared-services-error.log</string>
</dict>
</plist>
```

Then:
```bash
launchctl load ~/Library/LaunchAgents/com.tekton.shared-services.plist
launchctl start com.tekton.shared-services
```

## Monitoring

### Check Service Status
```bash
# If running via script
ps aux | grep run_shared_services.py

# Check logs
tail -f ~/.tekton/logs/orphan_cleanup.log
```

### Manual Cleanup Check
```bash
# See what orphans exist
python3 ../aish/cleanup_orphan_processes.py --dry-run --verbose
```

## Architecture

The shared services follow Tekton's distributed service pattern:
- Each service runs in its own async loop
- Services are component-agnostic
- Minimal dependencies
- Fail-safe operation (errors don't crash the service)
- Comprehensive logging for debugging

## Safety Features

1. **Minimum Age Threshold**: Processes must be at least 2 hours old
2. **Registry Verification**: Only removes unregistered processes
3. **Graceful Termination**: Tries SIGTERM before SIGKILL
4. **Dry Run Mode**: Test without making changes
5. **Interval Limiting**: Minimum 1 hour between runs
6. **Comprehensive Logging**: All actions logged for audit

## Troubleshooting

### Service Won't Start
- Check Python path: `which python3`
- Verify imports: `python3 -c "import psutil"`
- Check permissions on log directory

### Not Finding Orphans
- Orphans must be > 2 hours old
- Check if processes are in registry
- Run with `--verbose` flag

### Too Aggressive Cleanup
- Increase `--orphan-min-age`
- Check registry is up to date
- Review process patterns in cleanup script