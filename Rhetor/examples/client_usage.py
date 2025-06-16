#!/usr/bin/env python3
"""
Example Usage of the Rhetor Client

This script demonstrates how to use the RhetorPromptClient and RhetorCommunicationClient
to interact with the Rhetor prompt engineering and communication components.
"""

import asyncio
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rhetor_example")

# Try to import from the rhetor package
try:
    from rhetor.client import (
        RhetorPromptClient,
        RhetorCommunicationClient,
        get_rhetor_prompt_client,
        get_rhetor_communication_client
    )
except ImportError:
    import sys
    import os
    
    # Add the parent directory to sys.path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Try importing again
    from rhetor.client import (
        RhetorPromptClient,
        RhetorCommunicationClient,
        get_rhetor_prompt_client,
        get_rhetor_communication_client
    )


async def prompt_template_example():
    """Example of using the Rhetor prompt client for template management."""
    logger.info("=== Prompt Template Example ===")
    
    # Create a Rhetor prompt client
    client = await get_rhetor_prompt_client()
    
    try:
        # Create a prompt template
        template_name = "Technical Documentation"
        template_text = """
You are a technical writer creating documentation for {product_name}.

## Purpose
Create clear, concise technical documentation for {audience_type} that explains how to {task}.

## Requirements
- Use {tone} language
- Include {format} examples
- Cover the following topics: {topics}
- Documentation should be approximately {length} words

## Additional Information
{additional_info}
"""
        
        template_variables = [
            "product_name",
            "audience_type",
            "task",
            "tone",
            "format",
            "topics",
            "length",
            "additional_info"
        ]
        
        template_description = "Template for generating technical documentation prompts"
        template_tags = ["documentation", "technical", "writing"]
        
        logger.info(f"Creating prompt template: {template_name}")
        template = await client.create_prompt_template(
            name=template_name,
            template=template_text,
            variables=template_variables,
            description=template_description,
            tags=template_tags
        )
        
        template_id = template["template_id"]
        logger.info(f"Created template with ID: {template_id}")
        
        # Render a prompt using the template
        variables = {
            "product_name": "TektonOS",
            "audience_type": "software engineers",
            "task": "implement custom components",
            "tone": "professional",
            "format": "code",
            "topics": "installation, configuration, API reference, troubleshooting",
            "length": "2000",
            "additional_info": "Focus on best practices and common pitfalls to avoid."
        }
        
        logger.info(f"Rendering prompt with template {template_id}")
        rendered_prompt = await client.render_prompt(
            template_id=template_id,
            variables=variables
        )
        
        logger.info("Rendered prompt:")
        logger.info(rendered_prompt)
    
    except Exception as e:
        logger.error(f"Error in prompt template example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def personality_example():
    """Example of using the Rhetor prompt client for personality management."""
    logger.info("=== Personality Example ===")
    
    # Create a Rhetor prompt client
    client = await get_rhetor_prompt_client()
    
    try:
        # Create a personality
        personality_name = "Technical Expert"
        personality_traits = {
            "expertise": ["machine learning", "distributed systems", "cloud computing"],
            "communication_style": "precise",
            "knowledge_depth": "deep",
            "approach": "systematic",
            "formality": 0.8,  # 0.0 = informal, 1.0 = formal
            "detail_orientation": 0.9,  # 0.0 = high-level, 1.0 = very detailed
            "technical_jargon": 0.7  # 0.0 = simple language, 1.0 = heavy jargon
        }
        
        personality_description = "Expert in technical domains with precise communication style"
        personality_tone = "professional"
        
        personality_examples = [
            {
                "question": "How do distributed databases handle consistency?",
                "answer": "Distributed databases manage consistency through various strategies like strong consistency, eventual consistency, and consensus protocols. In strong consistency models (e.g., using two-phase commit), all nodes see the same data at the same time, but with performance costs. Eventual consistency (used in systems like Cassandra) allows temporary inconsistencies for better performance. Modern systems often implement consensus protocols like Paxos or Raft to achieve fault-tolerant consistency. The CAP theorem establishes that you can only have two of: Consistency, Availability, and Partition tolerance."
            },
            {
                "question": "What's the difference between CNN and RNN?",
                "answer": "CNNs (Convolutional Neural Networks) and RNNs (Recurrent Neural Networks) differ fundamentally in their architecture and applications. CNNs excel at spatial data like images by using convolutional layers to detect spatial patterns hierarchically. They're translation-invariant and parameter-efficient due to weight sharing. RNNs, conversely, process sequential data by maintaining an internal state that captures information from previous inputs. This makes them ideal for time-series data, text, and other sequences where temporal dependencies matter. While CNNs have fixed input sizes, RNNs can handle variable-length sequences, though they may struggle with long-term dependencies due to vanishing/exploding gradients, which variants like LSTMs and GRUs address."
            }
        ]
        
        logger.info(f"Creating personality: {personality_name}")
        personality = await client.create_personality(
            name=personality_name,
            traits=personality_traits,
            description=personality_description,
            tone=personality_tone,
            examples=personality_examples
        )
        
        personality_id = personality["personality_id"]
        logger.info(f"Created personality with ID: {personality_id}")
        
        # Generate a prompt using the personality
        task = "Explain the principles of database sharding and when it should be used"
        context = {
            "audience": "senior developers",
            "format": "technical blog post",
            "max_length": 500
        }
        
        logger.info(f"Generating prompt for task using personality {personality_id}")
        generated_prompt = await client.generate_prompt(
            task=task,
            context=context,
            personality_id=personality_id,
            format="instruction"
        )
        
        logger.info("Generated prompt:")
        logger.info(generated_prompt["prompt"])
        
        # Generate a prompt without a personality
        simple_task = "Write a poem about artificial intelligence"
        
        logger.info("Generating prompt without personality")
        simple_prompt = await client.generate_prompt(
            task=simple_task,
            format="chat"
        )
        
        logger.info("Generated simple prompt:")
        logger.info(simple_prompt["prompt"])
    
    except Exception as e:
        logger.error(f"Error in personality example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def conversation_example():
    """Example of using the Rhetor communication client for conversation management."""
    logger.info("=== Conversation Example ===")
    
    # Create a Rhetor communication client
    client = await get_rhetor_communication_client()
    
    try:
        # Create a conversation
        conversation_name = "Technical Support Session"
        conversation_metadata = {
            "customer_id": "C12345",
            "product": "TektonOS",
            "priority": "high",
            "category": "installation"
        }
        
        logger.info(f"Creating conversation: {conversation_name}")
        conversation = await client.create_conversation(
            name=conversation_name,
            metadata=conversation_metadata
        )
        
        conversation_id = conversation["conversation_id"]
        logger.info(f"Created conversation with ID: {conversation_id}")
        
        # Add messages to the conversation
        messages = [
            {"sender": "customer", "content": "I'm having trouble installing TektonOS on my custom hardware."},
            {"sender": "agent", "content": "I'd be happy to help you with the installation. Could you please share the specifications of your hardware?"},
            {"sender": "customer", "content": "It's a custom-built server with an ARM64 processor, 32GB RAM, and 1TB SSD."},
            {"sender": "agent", "content": "Thank you for providing those details. For ARM64 processors, you'll need to use our special installation package. Have you downloaded that specific version?"},
            {"sender": "customer", "content": "No, I was using the standard x86 version. Where can I find the ARM64 package?"},
            {"sender": "agent", "content": "You can download the ARM64 version from our website at downloads.tektonos.com/arm64. Let me know if you have any issues accessing it."}
        ]
        
        logger.info(f"Adding {len(messages)} messages to conversation {conversation_id}")
        for msg in messages:
            message = await client.add_message(
                conversation_id=conversation_id,
                sender=msg["sender"],
                message=msg["content"]
            )
            logger.info(f"Added message with ID: {message['message_id']}")
        
        # Get the conversation
        logger.info(f"Retrieving conversation {conversation_id}")
        retrieved_conversation = await client.get_conversation(conversation_id)
        
        logger.info(f"Retrieved conversation with {len(retrieved_conversation['messages'])} messages")
        
        # Analyze the conversation
        logger.info(f"Analyzing conversation {conversation_id}")
        analysis = await client.analyze_conversation(conversation_id)
        
        logger.info("Conversation analysis:")
        for key, value in analysis["analysis"].items():
            if isinstance(value, dict):
                logger.info(f"  {key}:")
                for subkey, subvalue in value.items():
                    logger.info(f"    {subkey}: {subvalue}")
            else:
                logger.info(f"  {key}: {value}")
        
        # Analyze the conversation with a specific analysis type
        logger.info(f"Performing sentiment analysis on conversation {conversation_id}")
        sentiment_analysis = await client.analyze_conversation(
            conversation_id=conversation_id,
            analysis_type="sentiment"
        )
        
        logger.info("Sentiment analysis:")
        for sender, sentiment in sentiment_analysis["analysis"].get("sentiment", {}).items():
            logger.info(f"  {sender}: {sentiment}")
    
    except Exception as e:
        logger.error(f"Error in conversation example: {e}")
    
    finally:
        # Close the client
        await client.close()


async def error_handling_example():
    """Example of handling errors with the Rhetor client."""
    logger.info("=== Error Handling Example ===")
    
    # Create a Rhetor prompt client with a non-existent component ID
    try:
        client = await get_rhetor_prompt_client(component_id="rhetor.nonexistent")
        # This should raise ComponentNotFoundError
        
    except Exception as e:
        logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    # Create a valid prompt client
    prompt_client = await get_rhetor_prompt_client()
    
    try:
        # Try to render a non-existent template
        try:
            await prompt_client.render_prompt(
                template_id="nonexistent-template-id",
                variables={}
            )
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    finally:
        # Close the client
        await prompt_client.close()
    
    # Create a valid communication client
    comm_client = await get_rhetor_communication_client()
    
    try:
        # Try to get a non-existent conversation
        try:
            await comm_client.get_conversation("nonexistent-conversation-id")
        except Exception as e:
            logger.info(f"Caught expected error: {type(e).__name__}: {e}")
    
    finally:
        # Close the client
        await comm_client.close()


async def main():
    """Run all examples."""
    try:
        await prompt_template_example()
        await personality_example()
        await conversation_example()
        await error_handling_example()
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())