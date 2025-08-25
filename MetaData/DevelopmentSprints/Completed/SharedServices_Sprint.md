# Shared Services Infrastructure Sprint

## Overview
Build a comprehensive shared services infrastructure for Tekton to manage cross-cutting concerns like operational data lifecycle, health monitoring, and system-wide utilities.

## Background
Currently, operational data (landmarks, registrations, messages, etc.) grows unbounded. We need intelligent lifecycle management with deduplication, archival, and configurable retention policies.

## Sprint Goals

### Phase 1: Core Infrastructure
1. **Create `shared/services/` structure**
   - Establish service patterns
   - Define base service class
   - Setup configuration management

2. **Operational Data Service**
   - Smart deduplication for landmarks
   - Configurable retention policies per data type
   - Archival before deletion
   - Compression for old data
   - Health metrics and monitoring

3. **Integration Framework**
   - Seamless integration with StandardComponentBase
   - Optional standalone usage
   - Background service capabilities
   - Thread-safe singleton patterns

### Phase 2: Advanced Features
1. **Intelligent Cleanup Strategies**
   - Category-based retention (permanent vs temporary landmarks)
   - Usage-based cleanup (LRU for caches)
   - Component-specific policies
   - Peak load awareness

2. **Monitoring & Metrics**
   - Disk usage tracking
   - Cleanup performance metrics
   - Data growth trends
   - Alert thresholds

3. **Data Archival System**
   - Compressed archives
   - Searchable metadata
   - Restore capabilities
   - S3/cloud storage option

4. **CI Config Sync Service**
   - Run `shared/services/ai_config_sync.py` periodically
   - Syncs CI Registry state to `config/tekton_ai_config.json`
   - Monitors registry update flag set by Rhetor
   - Ensures config reflects runtime CI roster changes

5. **Unified CI Platform Integration** (✅ Completed June 2025)
   - Replaced old internal CI specialist system with unified CI Registry
   - All CI specialists now auto-register with `shared/ai/registry_client.py`
   - Rhetor acts as hiring manager via `/api/ai/specialists` endpoints
   - MCP tools integration updated to use CI Registry
   - Discovery service provides `aish` and other clients with CI discovery

## Running Services

### CI Config Sync Service
```bash
# Run the CI config sync service
cd $TEKTON_ROOT
python3 shared/services/ai_config_sync.py

# Or run in background
nohup python3 shared/services/ai_config_sync.py > ~/.tekton/logs/ai_config_sync.log 2>&1 &
```

This service:
- Checks every 30 seconds for registry updates
- Syncs changes from CI Registry to config file
- Maintains config/tekton_ai_config.json as source of truth

## Technical Design

### Architecture
```
shared/
  services/
    __init__.py
    base_service.py              # Base class for all services
    
    operational_data/
      __init__.py
      manager.py                 # Core OperationalDataManager
      config.py                  # Configuration handling
      
      strategies/
        __init__.py
        base_strategy.py         # Abstract strategy
        landmark_cleaner.py      # Landmark-specific logic
        registration_cleaner.py  # Registration cleanup
        message_cleaner.py       # Message cleanup
        memory_cleaner.py        # CI memory cleanup
        
      deduplication/
        __init__.py
        landmark_dedup.py        # Smart landmark deduplication
        hash_manager.py          # Content hashing
        
      archival/
        __init__.py
        archiver.py              # Archive manager
        compressor.py            # Compression utilities
        
      monitors/
        __init__.py
        disk_monitor.py          # Disk usage tracking
        performance_monitor.py   # Cleanup performance
```

### Key Components

#### 1. OperationalDataManager
```python
class OperationalDataManager(BaseService):
    """
    Manages lifecycle of all operational data in Tekton.
    
    Features:
    - Configurable retention policies
    - Smart deduplication
    - Background cleanup
    - Health monitoring
    - Archival support
    """
    
    def __init__(self):
        super().__init__("operational_data")
        self.strategies = self._load_strategies()
        self.deduplicator = LandmarkDeduplicator()
        self.archiver = DataArchiver()
        self.monitor = DiskMonitor()
```

#### 2. Landmark Deduplication
```python
class LandmarkDeduplicator:
    """
    Prevents duplicate landmarks from being created.
    
    - Content-based hashing
    - Parameter normalization
    - Update tracking
    - Access patterns
    """
    
    def should_create_new(self, landmark_data: dict) -> bool:
        """Check if landmark already exists"""
        
    def update_existing(self, landmark_id: str, access_info: dict):
        """Update access patterns for existing landmark"""
```

#### 3. Cleanup Strategies
```python
class CleanupStrategy(ABC):
    """Base class for cleanup strategies"""
    
    @abstractmethod
    def should_delete(self, file_path: str, metadata: dict) -> bool:
        """Determine if file should be deleted"""
        
    @abstractmethod
    def pre_delete_action(self, file_path: str) -> Optional[str]:
        """Action before deletion (e.g., archive)"""

class LandmarkCleanupStrategy(CleanupStrategy):
    """
    Landmark-specific cleanup logic:
    - Keep architectural decisions forever
    - Delete runtime discoveries after 2 days
    - Archive before deletion
    """
```

### Configuration Schema
```env
# Shared Services Configuration
TEKTON_SERVICES_ENABLED=true
TEKTON_SERVICES_LOG_LEVEL=INFO

# Operational Data Management
TEKTON_DATA_RETENTION_DAYS=2
TEKTON_DATA_SCAN_INTERVAL_HOURS=6
TEKTON_DATA_MAX_FILES_PER_DIR=10000
TEKTON_DATA_ENABLE_ARCHIVAL=true
TEKTON_DATA_ARCHIVE_PATH=${TEKTON_ROOT}/.tekton/archives
TEKTON_DATA_COMPRESSION_LEVEL=6

# Component-Specific Retention
TEKTON_LANDMARK_RETENTION_DAYS=2
TEKTON_LANDMARK_PERMANENT_TYPES=architecture_decision,api_contract
TEKTON_REGISTRATION_RETENTION_DAYS=1
TEKTON_MESSAGE_RETENTION_DAYS=3
TEKTON_CI_MEMORY_RETENTION_DAYS=7

# Deduplication Settings
TEKTON_LANDMARK_DEDUP_ENABLED=true
TEKTON_LANDMARK_DEDUP_HASH_ALGO=sha256
TEKTON_LANDMARK_UPDATE_THRESHOLD=100  # Update instead of create after N duplicates

# Monitoring Thresholds
TEKTON_DATA_DISK_WARNING_GB=10
TEKTON_DATA_DISK_CRITICAL_GB=5
TEKTON_DATA_FILE_COUNT_WARNING=50000
```

### Integration Points

#### 1. Landmark Registry Enhancement
```python
# landmarks/core/registry.py
class LandmarkRegistry:
    def __init__(self):
        # Get deduplication service
        from shared.services.operational_data import get_deduplicator
        self.deduplicator = get_deduplicator()
    
    def register_landmark(self, landmark):
        # Check for duplicates first
        if self.deduplicator.is_duplicate(landmark):
            return self.deduplicator.update_existing(landmark)
        # Continue with creation...
```

#### 2. StandardComponentBase Integration
```python
# shared/utils/standard_component.py
class StandardComponentBase:
    async def _component_specific_init(self):
        # Initialize operational data management
        if self.config.get('enable_data_management', True):
            from shared.services.operational_data import OperationalDataManager
            self._data_manager = OperationalDataManager.get_instance()
            await self._data_manager.register_component(self.component_name)
```

## Implementation Plan

### Week 1: Core Infrastructure
- [ ] Create shared/services structure
- [ ] Implement BaseService class
- [ ] Build OperationalDataManager core
- [ ] Create configuration system

### Week 2: Cleanup Strategies
- [ ] Implement base strategy pattern
- [ ] Create component-specific strategies
- [ ] Add archival system
- [ ] Build monitoring framework

### Week 3: Deduplication System
- [ ] Design landmark hashing algorithm
- [ ] Implement deduplication logic
- [ ] Update landmark registry
- [ ] Add metrics tracking

### Week 4: Integration & Testing
- [ ] Integrate with all components
- [ ] Performance testing
- [ ] Documentation
- [ ] Migration from simple cleanup

## Success Metrics
1. **Data Growth Control**: < 10MB/day operational data growth
2. **Deduplication Rate**: > 90% duplicate prevention
3. **Performance Impact**: < 1% CPU overhead
4. **Disk Usage**: Maintain under configured thresholds
5. **Zero Data Loss**: All important data archived before deletion

## Migration Plan
1. Deploy simple DeleteOldOperationalRecords first
2. Run SharedServices in parallel (monitoring only)
3. Verify behavior matches expectations
4. Switch over component by component
5. Deprecate simple solution

## CI Platform Integration Details

### API Changes
The old Rhetor specialist endpoints have been replaced with unified CI Registry endpoints:

**Old Endpoints (Removed):**
- `GET /api/v1/specialists` - List specialists
- `POST /api/v1/specialists/{id}/start` - Start specialist
- `POST /api/v1/specialists/{id}/stop` - Stop specialist

**New Unified Endpoints:**
- `GET /api/ai/specialists` - List all CIs from registry
- `POST /api/ai/specialists/{id}/hire` - Hire an CI (add to roster)
- `POST /api/ai/specialists/{id}/fire` - Fire an CI (remove from roster)
- `GET /api/ai/roster` - Get Rhetor's current hired roster
- `POST /api/ai/specialists/{id}/reassign` - Reassign CI to new role

### Key Components
1. **CI Registry** (`shared/ai/registry_client.py`)
   - Thread-safe registry with file locking
   - Unified discovery for both CI types
   - Role-based CI selection
   - Socket info for Greek Chorus CIs

2. **CI Discovery Service** (`shared/ai/ai_discovery_service.py`)
   - List CIs by role (both types)
   - Find best CI for a task
   - Get CI connection info with socket details

3. **Dual Communication Architecture**:
   - **Greek Chorus**: Direct TCP socket (JSON protocol)
   - **Rhetor Specialists**: HTTP API endpoints
   - **aish**: Smart routing based on CI type

4. **Unified Endpoints** (`Rhetor/rhetor/api/ai_specialist_endpoints_unified.py`)
   - Rhetor as hiring manager (for managed specialists)
   - Roster management
   - Config sync triggers

### CI Architecture - Two Types of CIs

**1. Greek Chorus CIs** (Independent)
- Run on dedicated socket ports (45000-50000)
- Direct TCP socket communication
- Auto-register with CI Registry for discovery
- Examples: apollo-ai, athena-ai, prometheus-ai

**2. Rhetor Specialists** (Managed)
- Managed through Rhetor's API endpoints
- Communication via HTTP API calls
- Rhetor acts as hiring manager
- Examples: rhetor-orchestrator, planning-specialist

### Testing with aish
```bash
# List available CIs (discovers both types)
aish -l

# Find CIs by role
ai-discover --json list --role planning

# Use Greek Chorus CI (direct socket)
echo "Analyze this code" | aish --ai apollo

# Use Rhetor specialist (via API)
echo "Plan a feature" | rhetor

# Pipeline mixing both types
echo "Complex task" | apollo | rhetor | athena
```

**Note**: aish automatically detects CI type and uses appropriate communication method.

## Future Enhancements
1. **Cloud Storage Integration**: S3/GCS for archives
2. **Data Analytics**: Insights from operational data patterns
3. **Predictive Cleanup**: ML-based retention optimization
4. **Cross-Component Dedup**: Detect duplicates across components
5. **Real-time Monitoring**: Grafana dashboards for data health