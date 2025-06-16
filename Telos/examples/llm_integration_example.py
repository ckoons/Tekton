#!/usr/bin/env python3
"""
Example of using the Telos LLM integration capabilities.

This example demonstrates how to use Telos client to access LLM-powered 
requirements management features.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any

# Add the parent directory to the path so we can import telos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from telos.client import TelosClient, get_telos_client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("telos_llm_example")

async def analyze_requirement_example():
    """Example of using LLM to analyze a requirement."""
    # Create a Telos client
    client = await get_telos_client()
    
    # Example requirement text
    requirement_text = """
    Requirement ID: SEC-001
    Title: Secure User Authentication
    Description: The system shall authenticate users through a username and password, 
    and must require strong passwords of at least 8 characters.
    Type: Security
    Priority: High
    """
    
    # Project context
    context = """
    This is a financial application that manages sensitive customer data and transactions.
    It needs to comply with industry security standards.
    """
    
    # Call the LLM analysis capability
    print("Analyzing requirement...")
    result = await client.llm_analyze_requirement(
        requirement_text=requirement_text,
        context=context
    )
    
    print("\n=== Requirement Analysis Results ===")
    print(f"Success: {result.get('success', False)}")
    
    if result.get('success'):
        print("\nScores:")
        scores = result.get('analysis', {}).get('scores', {})
        for category, score in scores.items():
            print(f"- {category.capitalize()}: {score}/5")
        
        print("\nIssues:")
        for issue in result.get('analysis', {}).get('issues', []):
            print(f"- {issue}")
        
        print("\nSuggestions:")
        for suggestion in result.get('analysis', {}).get('suggestions', []):
            print(f"- {suggestion}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

async def generate_traces_example():
    """Example of using LLM to generate traceability links."""
    # Create a Telos client
    client = await get_telos_client()
    
    # Example requirements
    requirements = """
    Requirement ID: SEC-001
    Title: Secure User Authentication
    Description: The system shall authenticate users through a username and password, 
    and must require strong passwords of at least 8 characters.
    
    Requirement ID: SEC-002
    Title: Password Encryption
    Description: User passwords must be stored in an encrypted format using industry-standard
    encryption algorithms.
    """
    
    # Example implementation artifacts
    artifacts = """
    File: auth_service.py
    Description: Implements user authentication and password validation.
    Key functions:
    - authenticate_user(username, password) -> Validates user login credentials
    - validate_password_strength(password) -> Checks if password meets strength requirements
    
    File: user_repository.py
    Description: Manages user data storage operations.
    Key functions:
    - encrypt_password(password) -> Encrypts user password using bcrypt
    - save_user(user_data) -> Saves user data to the database
    
    File: password_policy.py
    Description: Defines password policies and validation rules.
    Key constants:
    - MIN_PASSWORD_LENGTH = 8
    - REQUIRE_SPECIAL_CHARS = True
    """
    
    # Call the trace generation capability
    print("Generating traceability links...")
    result = await client.llm_generate_traces(
        requirements=requirements,
        artifacts=artifacts
    )
    
    print("\n=== Traceability Results ===")
    if result.get('success'):
        print(result.get('traces', 'No traces generated'))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

async def initialize_project_example():
    """Example of using LLM to initialize a new requirements project."""
    # Create a Telos client
    client = await get_telos_client()
    
    # Project details
    project_name = "Mobile Banking App"
    project_description = """
    A secure mobile banking application that allows users to manage accounts,
    transfer funds, deposit checks via mobile capture, and pay bills.
    """
    project_domain = "Financial Services"
    stakeholders = """
    - Bank IT Department
    - Security Compliance Team
    - Mobile App Development Team
    - Customer Support
    - Bank Customers
    """
    constraints = """
    - Must comply with banking security regulations
    - Must be available on iOS and Android platforms
    - Development timeline: 8 months
    - Budget constraints require using existing infrastructure where possible
    """
    
    # Call the project initialization capability
    print("Initializing project with LLM recommendations...")
    result = await client.llm_initialize_project(
        project_name=project_name,
        project_description=project_description,
        project_domain=project_domain,
        stakeholders=stakeholders,
        constraints=constraints
    )
    
    print("\n=== Project Initialization Results ===")
    if result.get('success'):
        print(result.get('recommendations', 'No recommendations generated'))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

async def main():
    """Run the examples."""
    try:
        await analyze_requirement_example()
        print("\n" + "="*50 + "\n")
        
        await generate_traces_example()
        print("\n" + "="*50 + "\n")
        
        await initialize_project_example()
        
    except Exception as e:
        logger.error(f"Example failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())