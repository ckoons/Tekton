#!/usr/bin/env python3
"""
Example of using the LLM adapter in Harmonia.

This example demonstrates how to use the tekton-llm-client based adapter
for workflow creation, expression evaluation, and state transitions.
"""

import os
import sys
import asyncio
import logging
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from harmonia.core.llm.adapter import LLMAdapter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_adapter_example")

async def workflow_creation_example():
    """Example of using the LLM adapter for workflow creation."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a goal for the workflow
    goal = """
    Create a document approval workflow for legal contract review that involves 
    multiple stakeholders including legal team, finance department, and executive sign-off.
    """
    
    # Available components
    components = """
    1. DocumentProcessor - Handles document parsing, metadata extraction, and format conversion
       - Inputs: document_url, document_type
       - Outputs: metadata, content, format_info
    
    2. ReviewAssignment - Assigns reviewers based on document type and content
       - Inputs: document_metadata, document_content, organization_structure
       - Outputs: reviewer_list, assignment_priority, deadline
    
    3. NotificationSender - Sends notifications to stakeholders
       - Inputs: recipient_list, message_template, priority
       - Outputs: notification_status, delivery_confirmation
    
    4. ReviewCollector - Collects and aggregates review feedback
       - Inputs: document_id, reviewer_list
       - Outputs: review_status, feedback_summary, approval_status
    
    5. ApprovalGate - Enforces approval requirements based on document type
       - Inputs: document_metadata, approval_list, review_status
       - Outputs: gate_status, next_steps, escalation_needed
    
    6. DocumentVersioner - Creates new versions of documents with tracked changes
       - Inputs: original_document, feedback_list
       - Outputs: new_document_version, change_summary
    
    7. FinalApproval - Collects final executive approval and signatures
       - Inputs: document_final_version, approver_list
       - Outputs: approval_status, signature_status, completion_time
    """
    
    # Constraints for the workflow
    constraints = """
    - The workflow must include at least one approval gate for legal compliance
    - Finance department must review all contracts with values over $10,000
    - Executive approval is required for all contracts regardless of value
    - The workflow must include notification of all stakeholders at each major step
    - Timeouts must be implemented for reviews to prevent bottlenecks
    - All feedback must be collected and integrated before final approval
    """
    
    # Create the workflow
    print("Creating workflow...")
    result = await adapter.create_workflow(
        goal=goal,
        components=components,
        constraints=constraints
    )
    
    print("\n=== Workflow Creation Result ===")
    print(result)

async def expression_evaluation_example():
    """Example of using the LLM adapter for expression evaluation."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define an expression to evaluate
    expression = "${document.value > 10000 && reviewStatus.legal == 'approved'}"
    
    # Current state
    state = """
    {
      "document": {
        "id": "DOC-2025-042",
        "title": "Supply Agreement - TechCorp",
        "type": "contract",
        "value": 15000,
        "currency": "USD",
        "created": "2025-03-15T14:22:00Z"
      },
      "reviewStatus": {
        "legal": "approved",
        "finance": "pending",
        "executive": "not_started"
      },
      "approvals": {
        "required": ["legal", "finance", "executive"],
        "completed": ["legal"],
        "pending": ["finance", "executive"]
      },
      "workflow": {
        "currentStep": "finance_review",
        "nextSteps": ["executive_review", "final_approval"],
        "completedSteps": ["document_processing", "legal_review"]
      }
    }
    """
    
    # Evaluate the expression
    print("Evaluating expression...")
    result = await adapter.evaluate_expression(
        expression=expression,
        state=state
    )
    
    print("\n=== Expression Evaluation Result ===")
    print(result)

async def state_transition_example():
    """Example of using the LLM adapter for state transitions."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Current state
    current_state = """
    {
      "document": {
        "id": "DOC-2025-042",
        "title": "Supply Agreement - TechCorp",
        "type": "contract",
        "value": 15000,
        "currency": "USD",
        "version": 1
      },
      "reviewStatus": {
        "legal": "approved",
        "finance": "in_progress",
        "executive": "not_started"
      },
      "approvals": {
        "required": ["legal", "finance", "executive"],
        "completed": ["legal"],
        "pending": ["finance", "executive"]
      },
      "workflow": {
        "currentStep": "finance_review",
        "nextSteps": ["executive_review", "final_approval"],
        "completedSteps": ["document_processing", "legal_review"]
      }
    }
    """
    
    # Step that completed
    completed_step = """
    {
      "id": "finance_review",
      "status": "completed",
      "assignee": "finance_department",
      "startTime": "2025-03-16T09:30:00Z",
      "completionTime": "2025-03-17T14:45:00Z"
    }
    """
    
    # Step output
    step_output = """
    {
      "approval": "approved_with_changes",
      "changes_required": [
        {
          "section": "Payment Terms",
          "current": "Net 60",
          "suggested": "Net 45",
          "reason": "Company policy restricts terms beyond 45 days"
        },
        {
          "section": "Early Payment Discount",
          "current": "None",
          "suggested": "1% for payment within 10 days",
          "reason": "Align with cash flow optimization strategy"
        }
      ],
      "comments": "Approved with minor changes to payment terms. Please update and return for final sign-off.",
      "risk_assessment": "Low financial risk after suggested changes",
      "next_action": "Document revision required before executive review"
    }
    """
    
    # Potential next steps
    next_steps = """
    {
      "document_revision": {
        "id": "document_revision",
        "description": "Update document with required changes",
        "component": "DocumentVersioner",
        "inputs": ["document", "changes_required"]
      },
      "executive_review": {
        "id": "executive_review",
        "description": "Submit for executive approval",
        "component": "ReviewAssignment",
        "inputs": ["document", "previous_approvals"]
      },
      "legal_revalidation": {
        "id": "legal_revalidation",
        "description": "Request legal to validate changes",
        "component": "ReviewAssignment",
        "inputs": ["document", "changes_made"]
      }
    }
    """
    
    # Determine state transition
    print("Determining state transition...")
    result = await adapter.determine_state_transition(
        current_state=current_state,
        completed_step=completed_step,
        step_output=step_output,
        next_steps=next_steps
    )
    
    print("\n=== State Transition Result ===")
    print(result)

async def template_expansion_example():
    """Example of using the LLM adapter for template expansion."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a template to expand
    template = """
    Dear ${approver.name},
    
    This is a request for your review and approval of ${document.title} (ID: ${document.id}).
    
    Document Details:
    - Type: ${document.type}
    - Value: ${formatCurrency(document.value, document.currency)}
    - Created: ${formatDate(document.created, "MM/DD/YYYY")}
    - Version: ${document.version}
    
    ${if(previousApprovals.length > 0, "Previous approvals have been received from: " + previousApprovals.join(", "), "This is the first approval being requested.")}
    
    Please review the document and provide your ${approvalType} by ${deadline}.
    ${if(isUrgent, "This review is marked as URGENT and requires your immediate attention.", "")}
    
    Thank you,
    ${sender.name}
    ${sender.title}
    """
    
    # Current state
    state = """
    {
      "approver": {
        "name": "Sarah Johnson",
        "title": "Chief Financial Officer",
        "email": "sjohnson@example.com",
        "department": "Finance"
      },
      "document": {
        "id": "DOC-2025-042",
        "title": "Supply Agreement - TechCorp",
        "type": "contract",
        "value": 15000,
        "currency": "USD",
        "created": "2025-03-15T14:22:00Z",
        "version": 2
      },
      "previousApprovals": ["Legal Team", "Procurement Department"],
      "approvalType": "financial approval",
      "deadline": "2025-03-20",
      "isUrgent": true,
      "sender": {
        "name": "David Chen",
        "title": "Contract Management System",
        "email": "system@example.com"
      }
    }
    """
    
    # Available functions
    functions = """
    - formatCurrency(value, currency): Formats a number as currency
      Example: formatCurrency(1000, "USD") -> "$1,000.00"
    
    - formatDate(dateString, format): Formats a date string
      Example: formatDate("2025-03-15T14:22:00Z", "MM/DD/YYYY") -> "03/15/2025"
    
    - if(condition, trueValue, falseValue): Conditional expression
      Example: if(true, "Yes", "No") -> "Yes"
    """
    
    # Expand the template
    print("Expanding template...")
    result = await adapter.expand_template(
        template=template,
        state=state,
        functions=functions
    )
    
    print("\n=== Template Expansion Result ===")
    print(result)

async def workflow_troubleshooting_example():
    """Example of using the LLM adapter for workflow troubleshooting."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Workflow definition
    workflow = """
    {
      "name": "ContractApprovalWorkflow",
      "description": "Process for reviewing and approving legal contracts",
      "steps": [
        {
          "id": "document_processing",
          "name": "Document Processing",
          "component": "DocumentProcessor",
          "inputs": {
            "document_url": "${inputs.document_url}",
            "document_type": "${inputs.document_type}"
          },
          "outputs": {
            "metadata": "document.metadata",
            "content": "document.content",
            "format_info": "document.format"
          }
        },
        {
          "id": "legal_review",
          "name": "Legal Review",
          "component": "ReviewAssignment",
          "inputs": {
            "document_metadata": "${document.metadata}",
            "document_content": "${document.content}",
            "organization_structure": "${inputs.org_structure}"
          },
          "outputs": {
            "reviewer_list": "legal.reviewers",
            "assignment_priority": "legal.priority",
            "deadline": "legal.deadline"
          },
          "conditions": {
            "document_ready": "${document.metadata != null && document.content != null}"
          }
        },
        {
          "id": "finance_review",
          "name": "Finance Review",
          "component": "ReviewAssignment",
          "inputs": {
            "document_metadata": "${document.metadata}",
            "document_content": "${document.content}",
            "organization_structure": "${inputs.org_structure}"
          },
          "outputs": {
            "reviewer_list": "finance.reviewers",
            "assignment_priority": "finance.priority",
            "deadline": "finance.deadline"
          },
          "conditions": {
            "needs_financial_review": "${document.metadata.value > 10000}",
            "legal_approved": "${legal.status == 'approved'}"
          }
        }
      ]
    }
    """
    
    # Current state
    state = """
    {
      "inputs": {
        "document_url": "https://storage.example.com/docs/contract-techcorp.pdf",
        "document_type": "contract",
        "org_structure": {
          "legal": ["john.doe@example.com", "jane.smith@example.com"],
          "finance": ["sarah.jones@example.com"],
          "executive": ["ceo@example.com"]
        }
      },
      "document": {
        "metadata": {
          "id": "DOC-2025-042",
          "title": "Supply Agreement - TechCorp",
          "type": "contract",
          "value": 8500,
          "currency": "USD"
        },
        "content": "<document content data>",
        "format": "PDF"
      },
      "legal": {
        "reviewers": ["john.doe@example.com"],
        "priority": "normal",
        "deadline": "2025-03-20",
        "status": "approved"
      },
      "workflow": {
        "current_step": "finance_review",
        "status": "error"
      }
    }
    """
    
    # Error details
    error = """
    Error: Failed to execute step 'finance_review'
    Error occurred in condition evaluation: Cannot read property 'value' of null at path 'document.metadata.value'
    Step ID: finance_review
    Timestamp: 2025-03-17T15:22:34Z
    """
    
    # Execution history
    execution_history = """
    [
      {
        "timestamp": "2025-03-17T15:20:12Z",
        "step": "document_processing",
        "status": "success",
        "duration_ms": 3450
      },
      {
        "timestamp": "2025-03-17T15:21:05Z",
        "step": "legal_review",
        "status": "success",
        "duration_ms": 12340
      },
      {
        "timestamp": "2025-03-17T15:22:34Z",
        "step": "finance_review",
        "status": "error",
        "error_message": "Cannot read property 'value' of null at path 'document.metadata.value'",
        "duration_ms": 520
      }
    ]
    """
    
    # Troubleshoot the workflow
    print("Troubleshooting workflow...")
    result = await adapter.troubleshoot_workflow(
        workflow=workflow,
        state=state,
        error=error,
        execution_history=execution_history
    )
    
    print("\n=== Workflow Troubleshooting Result ===")
    print(result)

async def json_workflow_example():
    """Example of using the LLM adapter to generate JSON workflow."""
    # Initialize the LLM adapter
    adapter = LLMAdapter()
    
    # Define a goal for the workflow
    goal = """
    Create a content publishing workflow that includes content creation, editorial review,
    compliance check, and multi-channel publishing with analytics tracking.
    """
    
    # Available components
    components = """
    1. ContentCreator - Handles content creation and initial metadata
       - Inputs: content_request, author_id, template_id
       - Outputs: draft_content, initial_metadata
    
    2. EditorialReviewer - Performs editorial review and suggestion
       - Inputs: content_draft, style_guide, review_criteria
       - Outputs: review_comments, approval_status
    
    3. ComplianceChecker - Verifies content meets compliance requirements
       - Inputs: content, compliance_rules, industry_regulations
       - Outputs: compliance_status, issues_found, recommendations
    
    4. ContentFormatter - Formats content for different channels
       - Inputs: approved_content, target_channels, format_templates
       - Outputs: formatted_content_map
    
    5. Publisher - Publishes content to specified channels
       - Inputs: content_package, publishing_schedule, channel_credentials
       - Outputs: publishing_status, published_urls
    
    6. AnalyticsCollector - Sets up analytics tracking for published content
       - Inputs: published_content_map, tracking_parameters
       - Outputs: tracking_codes, dashboard_config
    """
    
    # Generate JSON workflow
    print("Generating JSON workflow...")
    result = await adapter.generate_json_workflow(
        goal=goal,
        components=components
    )
    
    print("\n=== JSON Workflow Generation Result ===")
    import json
    print(json.dumps(result, indent=2))

async def main():
    """Run all examples."""
    try:
        await workflow_creation_example()
        print("\n" + "="*60 + "\n")
        
        await expression_evaluation_example()
        print("\n" + "="*60 + "\n")
        
        await state_transition_example()
        print("\n" + "="*60 + "\n")
        
        await template_expansion_example()
        print("\n" + "="*60 + "\n")
        
        await workflow_troubleshooting_example()
        print("\n" + "="*60 + "\n")
        
        await json_workflow_example()
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")

if __name__ == "__main__":
    asyncio.run(main())