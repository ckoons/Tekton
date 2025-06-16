"""
Ergon Agent Module

This module provides agent creation and execution capabilities.
"""

# Export core components
from ergon.core.agents.generator import (
    generate_agent,
    generate_github_agent
)
from ergon.core.agents.runner import AgentRunner

# Export latent reasoning components if available
try:
    from ergon.core.agents.latent_reasoning import (
        generate_latent_agent,
        generate_latent_nexus_agent,
        generate_latent_github_agent,
        generate_latent_browser_agent,
        generate_latent_mail_agent,
        LatentReasoningAdapter
    )
    from ergon.core.agents.latent_runner import (
        create_latent_agent_runner,
        run_agent_with_latent_reasoning
    )
    
    HAS_LATENT_REASONING = True
except ImportError:
    HAS_LATENT_REASONING = False