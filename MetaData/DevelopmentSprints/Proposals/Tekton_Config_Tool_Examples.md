# Tekton Config Tool - Examples

## Example JSON Structures

### 1. Shared Configuration (federation_menu.json)
```json
{
  "version": "2024.12.20-v3.2.1",
  "updated": "2024-12-20T12:00:00Z",
  "object_types": {
    "site": {
      "properties": ["name", "region", "components", "federation_status"]
    },
    "container": {
      "properties": ["name", "version", "image", "dependencies"]
    },
    "stage": {
      "properties": ["name", "type", "containers"]
    },
    "service": {
      "properties": ["name", "port", "protocol", "health_check"]
    }
  },
  "available_components": {
    "aish": {
      "version": "1.2.0",
      "container": "aish-v1.2.0",
      "requirements": ["python3.10+"]
    },
    "numa": {
      "version": "0.9.5",
      "container": "numa-v0.9.5",
      "requirements": ["aish"]
    },
    "engram": {
      "version": "2.1.0",
      "container": "engram-v2.1.0",
      "requirements": ["lancedb"]
    },
    "tekton-full": {
      "version": "3.2.1",
      "container": "tekton-v3.2.1",
      "requirements": ["all-components"]
    }
  },
  "federation_stats": {
    "total_sites": 1847,
    "components_in_use": {
      "aish": 1623,
      "numa": 892,
      "engram": 234,
      "tekton-full": 45
    }
  }
}
```

### 2. Local Private Configuration (local_private.json)
```json
{
  "site": {
    "name": "casey-home",
    "federation_id": "site-0042",
    "trust_level": "full",
    "hermes_endpoint": "https://casey-home.local:8001"
  },
  "deployment": {
    "stages": {
      "production": {
        "hosts": ["10.0.1.10", "10.0.1.11"],
        "state": "DEPLOY",
        "containers": ["aish-v1.2.0", "numa-v0.9.5"]
      },
      "development": {
        "hosts": ["10.0.2.10"],
        "state": "HOLD",
        "hold_info": {
          "who": "casey",
          "when": "2024-12-15T10:00:00Z",
          "why": "Testing new Engram features",
          "until": "2024-12-22T00:00:00Z"
        },
        "containers": ["tekton-v3.2.1"]
      }
    }
  },
  "schedule": [
    {
      "command": "production HOLD on",
      "datetime": "2024-12-23T18:00:00Z",
      "user": "casey",
      "authorization": "holiday-freeze"
    },
    {
      "command": "production HOLD off",
      "datetime": "2024-12-26T06:00:00Z",
      "user": "casey",
      "authorization": "post-holiday"
    }
  ],
  "credentials": {
    "type": "vault",
    "path": "vault://tekton/prod"
  }
}
```

### 3. Status Report (sent to federation)
```json
{
  "site_id": "site-0042",
  "timestamp": "2024-12-20T14:30:00Z",
  "menu_version": "2024.12.20-v3.2.1",
  "components_active": ["aish", "numa"],
  "health": "operational",
  "holds": 1,
  "public_info": {
    "use_case": "Personal CI development environment",
    "feedback": "Engram memory improvements working well"
  }
}
```

## Example Commands

### Installation
```bash
# Download and compile
git clone https://github.com/tekton/config-tool
cd config-tool
make
sudo make install

# Initialize (solo mode)
tekton-config init --mode solo

# Initialize (federation member)
tekton-config init --mode federation --site-name "my-startup"
```

### Daily Operations
```bash
# Check status
tekton-config status

# View holds
tekton-config holds

# Set a hold
tekton-config hold production on --reason "quarterly-review"

# Schedule a deployment
tekton-config schedule "staging HOLD off" "2024-12-21T02:00:00Z"

# View federation status
tekton systems status

# Query remote site (if permission granted)
tekton --system amazon-us-east status
```

### Meeting Commands
```bash
# Review all holds (for standup meeting)
$ tekton-config holds --verbose

CURRENT HOLDS:
1. production - 3 weeks
   Who: casey
   Why: holiday-freeze
   Remove? [y/N]

2. payment-service - 5 days  
   Who: alice
   Why: debugging-issue-325
   Remove? [y/N]

3. europe-stage - 2 months
   Who: bob (no longer with company)
   Why: compliance-review
   Remove? [y/N] y
   > Hold removed, will deploy on next sync
```

## Example C Code Structure (simplified)

```c
// config_tool.c - main structure
typedef struct {
    char* name;
    char* state;  // "DEPLOY" or "HOLD"
    char* version;
    json_t* config;
    hold_info_t* hold;
} deployment_object_t;

typedef struct {
    char* who;
    time_t when;
    char* why;
    char* hold_version;
} hold_info_t;

int main(int argc, char** argv) {
    // Load configurations
    json_t* shared = load_json("federation_menu.json");
    json_t* private = load_json("local_private.json");
    
    // Merge configurations
    config_t* config = merge_configs(shared, private);
    
    // Check each object
    for (object in config->objects) {
        if (object->state == "DEPLOY") {
            deploy(object);
        } else {
            log_hold(object->hold);
        }
    }
    
    // Report status if federation member
    if (config->federation_id) {
        report_status(config);
    }
    
    return 0;
}
```

## Federation Trust Levels

### Anonymous
```json
{"federation_status": "anonymous"}
```
- Downloads menu
- Counted in stats
- No reporting back

### Named
```json
{
  "federation_status": "named",
  "site_name": "startup-423"
}
```
- Visible in federation list
- Basic stats shared

### Hermes-Registered
```json
{
  "federation_status": "hermes",
  "site_name": "acme-corp",
  "hermes_endpoint": "https://acme.com:8001"
}
```
- Can receive broadcasts
- Participates in federation events

### Read Access
```json
{
  "federation_status": "read",
  "site_name": "trusted-partner",
  "hermes_endpoint": "https://partner.com:8001",
  "read_token": "abc123..."
}
```
- Remote status queries allowed
- Federation can check health

### Full Access
```json
{
  "federation_status": "full",
  "site_name": "casey-home",
  "hermes_endpoint": "https://casey-home.local:8001",
  "admin_token": "xyz789..."
}
```
- Remote start/stop permitted
- Full federation privileges

## The Beauty of Simplicity

1. **One JSON file** - Complete truth
2. **One C program** - No dependencies  
3. **One command** - Deploy or hold
4. **One schedule** - When to act
5. **One federation** - Optional membership

No YAML sprawl, no template languages, no operators, no service mesh. Just objects, states, and time.

---

*"Infrastructure as code, the way it was meant to be - simple, visible, and under your control."*