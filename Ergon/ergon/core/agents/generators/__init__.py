"""
Code generator modules for Ergon agent creation.
"""

from .code_generator import (
    generate_main_file,
    generate_tools_file,
    generate_prompts_file,
    generate_requirements_file,
    generate_env_file,
    generate_readme_file
)

from .fallbacks import (
    generate_fallback_main_file,
    generate_fallback_tools_file,
    generate_fallback_prompts_file,
    generate_fallback_requirements_file,
    generate_fallback_readme_file,
    generate_fallback_env_file
)

from .github_generator import (
    generate_github_tools_file,
    generate_github_agent_file
)

__all__ = [
    'generate_main_file',
    'generate_tools_file',
    'generate_prompts_file',
    'generate_requirements_file',
    'generate_env_file',
    'generate_readme_file',
    'generate_fallback_main_file',
    'generate_fallback_tools_file',
    'generate_fallback_prompts_file',
    'generate_fallback_requirements_file',
    'generate_fallback_readme_file',
    'generate_fallback_env_file',
    'generate_github_tools_file',
    'generate_github_agent_file'
]