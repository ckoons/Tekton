# Single Port Architecture Issue Tracker

## Issues Fixed

1. ✅ **Rhetor Port Mismatch** (8003 vs 8300)
   - Rhetor was using port 8300 instead of the standard 8003
   - Fixed in `__main__.py` and `app.py` by implementing standardized port configuration
   - Created `port_config.py` utility module for Rhetor

2. ✅ **Hard-coded Hermes URL in Terma**
   - Terma was using a hard-coded URL for Hermes (defaulting to port 8000)
   - Updated to use the standardized port configuration (port 8001)
   - Created `get_hermes_api_url()` helper function

3. ✅ **Inconsistent Environment Variable Names**
   - Created consistent environment variable naming (`COMPONENT_PORT`)
   - Added comprehensive mappings in each `port_config.py` module

4. ✅ **Component Directory Variable Issue**
   - Created `component_launcher.py` script to handle component directory path resolution
   - Fixed improper string interpolation in shell scripts
   - Ensured proper Python argument handling

5. ✅ **Missing async Methods in Hermes MessageBus**
   - Added async implementations for `create_channel()`, `subscribe()` and `publish()`
   - Fixed critical errors preventing Hermes from starting

## Pending Issues

1. ⏳ **Hermes Database MCP Port Configuration**
   - Database MCP and Ergon both use port 8002
   - Need to reconsider this configuration for environments where both are running

2. ⏳ **WebSocket Port Standardization for Terma**
   - Terma still uses the legacy WebSocket port 8767
   - Future sprints should consolidate to a single port using path-based routing

3. ⏳ **Duplicate Port Configuration Code**
   - Each component has its own copy of the port configuration utilities
   - Should be consolidated into a shared library

4. ⏳ **Remaining Components to Update**
   - Prometheus (8006)
   - Harmonia (8007)
   - Telos (8008)
   - Synthesis (8009)
   - Tekton Core (8010)

5. ⏳ **Launch Script Updates**
   - `tekton-launch` script needs updating to use the standardized ports consistently
   - Should detect and report port conflicts

## Discovered Issues (For Further Investigation)

1. ❓ **LLM Adapter Port Standardization**
   - LLM Adapter is using port 8300 instead of following the Single Port Architecture
   - Should it be moved to a standard port in the 8000-8010 range?

2. ❓ **Rhetor Launch Timing Issues**
   - Rhetor reports timeouts when waiting for initialization, despite successful startup
   - Further investigation needed for race conditions in health check

3. ❓ **Component Registration with Hermes**
   - Components need to handle both direct registration and URL construction
   - Registration process should be standardized

## Progress Update

- 4 components have been successfully updated with the standardized port configuration
- All components tested are now using their correct standard ports
- Next component to update: Prometheus (8006)
- Estimated completion: 6 more components need to be updated