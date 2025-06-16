# Budget Component

Budget is a centralized component for managing LLM token allocations and cost tracking within the Tekton ecosystem. It provides comprehensive budget management, monitoring, and optimization services for all Tekton components.

## Features

- **Unified Budget Management**: Combines token allocation and cost tracking in a single system
- **Automated Price Monitoring**: Automatically tracks and updates provider pricing information
- **Budget Enforcement**: Configurable budget policies with different enforcement levels
- **Detailed Reporting**: Comprehensive usage reporting and cost analysis
- **LLM-Assisted Optimization**: AI-powered budget optimization recommendations
- **Multiple Integration Methods**: Standardized API, CLI, and MCP protocol support

## Architecture

Budget follows a layered architecture:

1. **Core Layer**: Foundational budget tracking and enforcement
2. **Integration Layer**: Adapters for different components and LLM providers
3. **Service Layer**: API endpoints and event handlers
4. **Reporting Layer**: Analytics and visualization capabilities

## Installation

```bash
# Clone the repository (if not already part of Tekton)
git clone https://github.com/your-organization/budget.git

# Install dependencies
cd budget
pip install -r requirements.txt

# Install package
pip install -e .
```

## Usage

### Running the Component

```bash
# Start the Budget API server
./run_budget.sh
```

### CLI Usage

```bash
# Set a budget limit
budget set-limit daily 10.0

# Check current usage
budget get-usage daily

# View budget status
budget status
```

### API Usage

```python
from budget.client import BudgetClient

# Create client
client = BudgetClient()

# Check if a request is within budget
allowed, info = client.check_budget(
    provider="anthropic",
    model="claude-3-opus",
    input_text="Hello, world!",
    component="my-component"
)

# Record usage
client.record_completion(
    provider="anthropic",
    model="claude-3-opus",
    input_text="Hello, world!",
    output_text="Hi there! How can I assist you today?",
    component="my-component"
)
```

## Integration with Tekton

Budget integrates with the Tekton ecosystem through:

1. **Single Port Architecture**: Follows Tekton's standardized port and path conventions (port 8013)
2. **Hermes Integration**: Automatic registration with Hermes service registry on startup
3. **Client Libraries**: Language-specific client libraries for API access
4. **Component Adapters**: Dedicated adapters for Apollo and Rhetor
5. **Event Publishing**: Budget-related events for reactive components
6. **Shared Configuration**: Common configuration for budget settings
7. **MCP Protocol**: Standard protocol for component communication

See the [Integration Guide](/MetaData/ComponentDocumentation/Budget/INTEGRATION_GUIDE.md) for detailed instructions.

## Development

```bash
# Run tests
pytest tests/

# Run with debug output
TEKTON_DEBUG=true TEKTON_LOG_LEVEL=DEBUG python -m budget.api.app
```

## License

See the LICENSE file for details.