"""
Budget CLI

Command-line interface for the Budget component.
"""

import os
import sys
import json
import click
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from tabulate import tabulate
from shared.env import TektonEnviron
from shared.urls import budget_url

# Add the parent directory to sys.path to ensure package imports work correctly
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Try to import debug_utils from shared if available
try:
    from shared.debug.debug_utils import debug_log, log_function
except ImportError:
    # Create a simple fallback if shared module is not available
    class DebugLog:
        def __getattr__(self, name):
            def dummy_log(*args, **kwargs):
                pass
            return dummy_log
    debug_log = DebugLog()
    
    def log_function(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

# Import budget models
from budget.data.models import (
    BudgetTier, BudgetPeriod, BudgetPolicyType, 
    TaskPriority, PriceType
)

# Default API URL
DEFAULT_API_URL = budget_url()

@click.group()
@click.option('--debug/--no-debug', default=False, help='Enable debug output')
@click.pass_context
def cli(ctx, debug):
    """
    Budget component command-line interface.
    
    Manage LLM token budgets and cost tracking for Tekton components.
    """
    ctx.ensure_object(dict)
    
    if debug:
        os.environ["TEKTON_DEBUG"] = "true"
        os.environ["TEKTON_LOG_LEVEL"] = "DEBUG"
        
    ctx.obj['DEBUG'] = debug
    debug_log.info("budget_cli", "CLI initialized")

@cli.command()
@click.pass_context
def start(ctx):
    """Start the Budget API server."""
    debug_log.info("budget_cli", "Starting Budget API server")
    from budget.api.app import main as start_api
    start_api()

@cli.command()
@click.option('--period', type=click.Choice(['hourly', 'daily', 'weekly', 'monthly']), default='daily', help='Budget period')
@click.option('--tier', type=click.Choice(['local_lightweight', 'local_midweight', 'remote_heavyweight']), help='Budget tier')
@click.option('--provider', help='Provider name')
@click.option('--component', help='Component name')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def status(ctx, period, tier, provider, component, format, api_url):
    """Show the current budget status."""
    debug_log.info("budget_cli", "Getting budget status")
    
    # Build query parameters
    params = {
        'period': period
    }
    if tier:
        params['tier'] = tier
    if provider:
        params['provider'] = provider
    if component:
        params['component'] = component
    
    try:
        # Get budget summary
        response = requests.get(f"{api_url}/api/usage/summary", params=params)
        response.raise_for_status()
        summary = response.json()
        
        if format == 'json':
            click.echo(json.dumps(summary, indent=2))
        else:
            # Format as table
            table_data = []
            for item in summary:
                row = {
                    'Period': item.get('period'),
                    'Provider': item.get('provider', 'All'),
                    'Tier': item.get('tier', 'All'),
                    'Component': item.get('component', 'All'),
                    'Tokens Used': item.get('total_tokens_used', 0),
                    'Token Limit': item.get('token_limit', 'No limit'),
                    'Cost': f"${item.get('total_cost', 0):.2f}",
                    'Cost Limit': f"${item.get('cost_limit', 0):.2f}" if item.get('cost_limit') else 'No limit',
                    'Usage %': f"{item.get('cost_usage_percentage', 0) * 100:.1f}%" if item.get('cost_usage_percentage') else 'N/A'
                }
                table_data.append(row)
            
            if not table_data:
                click.echo("No budget data found for the specified criteria.")
            else:
                click.echo(tabulate(table_data, headers='keys', tablefmt='pretty'))
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not retrieve budget status. {str(e)}")
        debug_log.error("budget_cli", f"Error retrieving budget status: {str(e)}")

@cli.command()
@click.argument('period', type=click.Choice(['hourly', 'daily', 'weekly', 'monthly']))
@click.option('--provider', help='Filter by provider')
@click.option('--model', help='Filter by model')
@click.option('--component', help='Filter by component')
@click.option('--days', type=int, default=7, help='Number of days to look back')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def get_usage(ctx, period, provider, model, component, days, format, api_url):
    """
    Get usage data for a specific period.
    
    PERIOD can be one of: hourly, daily, weekly, monthly
    """
    debug_log.info("budget_cli", f"Getting usage for period: {period}")
    
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Build query parameters
    params = {
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat()
    }
    if provider:
        params['provider'] = provider
    if model:
        params['model'] = model
    if component:
        params['component'] = component
    
    try:
        # Get usage analytics
        response = requests.get(f"{api_url}/api/usage/analytics", params=params)
        response.raise_for_status()
        usage_data = response.json()
        
        if format == 'json':
            click.echo(json.dumps(usage_data, indent=2))
        else:
            # Format as table
            table_data = []
            for item in usage_data:
                row = {
                    'Date': item.get('date'),
                    'Provider': item.get('provider', 'All'),
                    'Model': item.get('model', 'All'),
                    'Component': item.get('component', 'All'),
                    'Requests': item.get('request_count', 0),
                    'Input Tokens': item.get('input_tokens', 0),
                    'Output Tokens': item.get('output_tokens', 0),
                    'Total Cost': f"${item.get('total_cost', 0):.4f}"
                }
                table_data.append(row)
            
            if not table_data:
                click.echo("No usage data found for the specified criteria.")
            else:
                click.echo(tabulate(table_data, headers='keys', tablefmt='pretty'))
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not retrieve usage data. {str(e)}")
        debug_log.error("budget_cli", f"Error retrieving usage data: {str(e)}")

@cli.command()
@click.argument('period', type=click.Choice(['hourly', 'daily', 'weekly', 'monthly']))
@click.argument('limit', type=float)
@click.option('--budget-id', help='Budget ID to update')
@click.option('--provider', help='Provider to set limit for')
@click.option('--tier', type=click.Choice(['local_lightweight', 'local_midweight', 'remote_heavyweight']), help='Tier to set limit for')
@click.option('--component', help='Component to set limit for')
@click.option('--policy-type', type=click.Choice(['ignore', 'warn', 'soft_limit', 'hard_limit']), default='warn', help='Policy enforcement type')
@click.option('--warning-threshold', type=float, default=0.8, help='Warning threshold (0.0-1.0)')
@click.option('--action-threshold', type=float, default=0.95, help='Action threshold (0.0-1.0)')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def set_limit(ctx, period, limit, budget_id, provider, tier, component, policy_type, warning_threshold, action_threshold, api_url):
    """
    Set a budget limit for a period.
    
    PERIOD can be one of: hourly, daily, weekly, monthly
    LIMIT is the budget amount in USD
    """
    debug_log.info("budget_cli", 
                   f"Setting {period} limit to ${limit} for provider {provider}")
    
    # If no budget_id is provided, get or create the default budget
    if not budget_id:
        try:
            # Try to get the default budget
            response = requests.get(f"{api_url}/api/budgets", params={'name': 'Default Budget'})
            response.raise_for_status()
            budgets = response.json()
            
            if budgets:
                budget_id = budgets[0]['budget_id']
                click.echo(f"Using existing budget: {budget_id}")
            else:
                # Create a default budget
                budget_data = {
                    'name': 'Default Budget',
                    'description': 'Default budget created by CLI',
                    'owner': TektonEnviron.get('USER', 'cli_user')
                }
                response = requests.post(f"{api_url}/api/budgets", json=budget_data)
                response.raise_for_status()
                budget = response.json()
                budget_id = budget['budget_id']
                click.echo(f"Created new default budget: {budget_id}")
        except requests.exceptions.RequestException as e:
            click.echo(f"Error: Could not get or create budget. {str(e)}")
            debug_log.error("budget_cli", f"Error with budget: {str(e)}")
            return
    
    # Create the policy data
    policy_data = {
        'type': policy_type,
        'period': period,
        'cost_limit': limit,
        'warning_threshold': warning_threshold,
        'action_threshold': action_threshold,
        'enabled': True
    }
    
    # Add optional parameters if provided
    if provider:
        policy_data['provider'] = provider
    if tier:
        policy_data['tier'] = tier
    if component:
        policy_data['component'] = component
    
    try:
        # Create the policy
        response = requests.post(f"{api_url}/api/policies", json=policy_data)
        response.raise_for_status()
        policy = response.json()
        
        # Associate the policy with the budget
        budget_update = {
            'policies': [policy['policy_id']]
        }
        response = requests.put(f"{api_url}/api/budgets/{budget_id}/policies", json=budget_update)
        response.raise_for_status()
        
        click.echo(f"Budget limit for {period} set to ${limit}")
        click.echo(f"Policy created with ID: {policy['policy_id']}")
        click.echo(f"Policy added to budget: {budget_id}")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not set budget limit. {str(e)}")
        debug_log.error("budget_cli", f"Error setting budget limit: {str(e)}")

@cli.group()
def allocate():
    """Manage budget allocations."""
    pass

@allocate.command('create')
@click.option('--context-id', required=True, help='Context ID for the allocation')
@click.option('--component', required=True, help='Component name')
@click.option('--provider', help='Provider name')
@click.option('--model', help='Model name')
@click.option('--tier', type=click.Choice(['local_lightweight', 'local_midweight', 'remote_heavyweight']), help='Model tier')
@click.option('--tokens', type=int, required=True, help='Number of tokens to allocate')
@click.option('--task-type', default='default', help='Task type')
@click.option('--priority', type=int, default=5, help='Priority (1-10)')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def create_allocation(ctx, context_id, component, provider, model, tier, tokens, task_type, priority, api_url):
    """Create a new budget allocation."""
    debug_log.info("budget_cli", f"Creating allocation for {context_id} with {tokens} tokens")
    
    # Create allocation data
    allocation_data = {
        'context_id': context_id,
        'component': component,
        'tokens_allocated': tokens,
        'task_type': task_type,
        'priority': priority
    }
    
    # Add optional fields
    if provider:
        allocation_data['provider'] = provider
    if model:
        allocation_data['model'] = model
    if tier:
        allocation_data['tier'] = tier
    
    try:
        # Create the allocation
        response = requests.post(f"{api_url}/api/allocations", json=allocation_data)
        response.raise_for_status()
        allocation = response.json()
        
        click.echo(f"Allocation created with ID: {allocation['allocation_id']}")
        click.echo(f"Tokens allocated: {allocation['tokens_allocated']}")
        click.echo(f"Estimated cost: ${allocation.get('estimated_cost', 0):.4f}")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not create allocation. {str(e)}")
        debug_log.error("budget_cli", f"Error creating allocation: {str(e)}")

@allocate.command('list')
@click.option('--context-id', help='Filter by context ID')
@click.option('--component', help='Filter by component')
@click.option('--active-only/--all', default=True, help='Show only active allocations')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def list_allocations(ctx, context_id, component, active_only, format, api_url):
    """List budget allocations."""
    debug_log.info("budget_cli", "Listing allocations")
    
    # Build query parameters
    params = {}
    if context_id:
        params['context_id'] = context_id
    if component:
        params['component'] = component
    if active_only:
        params['is_active'] = 'true'
    
    try:
        # Get allocations
        response = requests.get(f"{api_url}/api/allocations", params=params)
        response.raise_for_status()
        allocations = response.json()
        
        if format == 'json':
            click.echo(json.dumps(allocations, indent=2))
        else:
            # Format as table
            table_data = []
            for item in allocations:
                row = {
                    'ID': item.get('allocation_id', '')[:8] + '...',  # Show abbreviated ID
                    'Context': item.get('context_id', '')[:8] + '...',
                    'Component': item.get('component', ''),
                    'Provider': item.get('provider', 'N/A'),
                    'Model': item.get('model', 'N/A'),
                    'Tokens Alloc': item.get('tokens_allocated', 0),
                    'Tokens Used': item.get('tokens_used', 0),
                    'Remaining': item.get('tokens_allocated', 0) - item.get('tokens_used', 0),
                    'Est. Cost': f"${item.get('estimated_cost', 0):.4f}",
                    'Active': '\u2713' if item.get('is_active', False) else '\u2717'
                }
                table_data.append(row)
            
            if not table_data:
                click.echo("No allocations found for the specified criteria.")
            else:
                click.echo(tabulate(table_data, headers='keys', tablefmt='pretty'))
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not list allocations. {str(e)}")
        debug_log.error("budget_cli", f"Error listing allocations: {str(e)}")

@allocate.command('release')
@click.argument('allocation_id')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def release_allocation(ctx, allocation_id, api_url):
    """Release an allocation, freeing up the unused tokens."""
    debug_log.info("budget_cli", f"Releasing allocation {allocation_id}")
    
    try:
        # Release the allocation
        response = requests.post(f"{api_url}/api/allocations/{allocation_id}/release")
        response.raise_for_status()
        result = response.json()
        
        click.echo(f"Allocation {allocation_id} released")
        click.echo(f"Tokens released: {result.get('tokens_released', 0)}")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not release allocation. {str(e)}")
        debug_log.error("budget_cli", f"Error releasing allocation: {str(e)}")

@cli.group()
def prices():
    """Manage and view price information."""
    pass

@prices.command('list')
@click.option('--provider', help='Filter by provider')
@click.option('--model', help='Filter by model')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def list_prices(ctx, provider, model, format, api_url):
    """List current prices for models."""
    debug_log.info("budget_cli", "Listing prices")
    
    # Build query parameters
    params = {}
    if provider:
        params['provider'] = provider
    if model:
        params['model'] = model
    
    try:
        # Get prices
        response = requests.get(f"{api_url}/api/prices", params=params)
        response.raise_for_status()
        prices = response.json()
        
        if format == 'json':
            click.echo(json.dumps(prices, indent=2))
        else:
            # Format as table
            table_data = []
            for item in prices:
                row = {
                    'Provider': item.get('provider', ''),
                    'Model': item.get('model', ''),
                    'Input $ / 1K': f"${item.get('input_cost_per_token', 0) * 1000:.4f}",
                    'Output $ / 1K': f"${item.get('output_cost_per_token', 0) * 1000:.4f}",
                    'Type': item.get('price_type', ''),
                    'Source': item.get('source', ''),
                    'Verified': '\u2713' if item.get('verified', False) else '\u2717'
                }
                table_data.append(row)
            
            if not table_data:
                click.echo("No prices found for the specified criteria.")
            else:
                click.echo(tabulate(table_data, headers='keys', tablefmt='pretty'))
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not list prices. {str(e)}")
        debug_log.error("budget_cli", f"Error listing prices: {str(e)}")

@prices.command('update')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def update_prices(ctx, api_url):
    """Update prices from all configured sources."""
    debug_log.info("budget_cli", "Updating prices")
    
    try:
        # Trigger price update
        response = requests.post(f"{api_url}/api/prices/update")
        response.raise_for_status()
        result = response.json()
        
        click.echo(f"Price update initiated")
        click.echo(f"Updates started: {result.get('updates_started', 0)}")
        click.echo(f"Sources: {', '.join(result.get('sources', []))}")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not update prices. {str(e)}")
        debug_log.error("budget_cli", f"Error updating prices: {str(e)}")

@cli.command()
@click.option('--task-type', help='Task type')
@click.option('--context-size', type=int, help='Context size in tokens')
@click.option('--output-size', type=int, help='Expected output size in tokens')
@click.option('--prefer-provider', help='Preferred provider')
@click.option('--max-cost', type=float, help='Maximum cost in USD')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def recommend(ctx, task_type, context_size, output_size, prefer_provider, max_cost, api_url):
    """Get model recommendations based on your requirements."""
    debug_log.info("budget_cli", "Getting model recommendations")
    
    # Build recommendation request
    request_data = {}
    if task_type:
        request_data['task_type'] = task_type
    if context_size:
        request_data['context_size'] = context_size
    if output_size:
        request_data['output_size'] = output_size
    if prefer_provider:
        request_data['prefer_provider'] = prefer_provider
    if max_cost:
        request_data['max_cost'] = max_cost
    
    try:
        # Get recommendations
        response = requests.post(f"{api_url}/api/prices/recommendations", json=request_data)
        response.raise_for_status()
        recommendations = response.json()
        
        # Display results
        click.echo("\nModel Recommendations:")
        click.echo("--------------------")
        
        # Display best match
        if recommendations.get('best_match'):
            best = recommendations['best_match']
            click.echo(f"Best Match: {best.get('provider', '')} - {best.get('model', '')}")
            click.echo(f"  Estimated cost: ${best.get('estimated_cost', 0):.4f}")
            click.echo(f"  Reason: {best.get('reason', '')}")
            click.echo("")
        
        # Display alternatives
        if recommendations.get('alternatives'):
            click.echo("Alternatives:")
            table_data = []
            for item in recommendations['alternatives']:
                row = {
                    'Provider': item.get('provider', ''),
                    'Model': item.get('model', ''),
                    'Est. Cost': f"${item.get('estimated_cost', 0):.4f}",
                    'Notes': item.get('reason', '')
                }
                table_data.append(row)
            
            click.echo(tabulate(table_data, headers='keys', tablefmt='simple'))
        
        # Display optimization tips
        if recommendations.get('optimization_tips'):
            click.echo("\nOptimization Tips:")
            for tip in recommendations['optimization_tips']:
                click.echo(f"- {tip}")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not get recommendations. {str(e)}")
        debug_log.error("budget_cli", f"Error getting recommendations: {str(e)}")

@cli.group()
def alerts():
    """Manage budget alerts."""
    pass

@alerts.command('list')
@click.option('--budget-id', help='Filter by budget ID')
@click.option('--severity', type=click.Choice(['info', 'warning', 'error']), help='Filter by severity')
@click.option('--acknowledged/--unacknowledged', default=None, help='Filter by acknowledgement status')
@click.option('--format', type=click.Choice(['table', 'json']), default='table', help='Output format')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def list_alerts(ctx, budget_id, severity, acknowledged, format, api_url):
    """List budget alerts."""
    debug_log.info("budget_cli", "Listing alerts")
    
    # Build query parameters
    params = {}
    if budget_id:
        params['budget_id'] = budget_id
    if severity:
        params['severity'] = severity
    if acknowledged is not None:
        params['acknowledged'] = 'true' if acknowledged else 'false'
    
    try:
        # Get alerts
        response = requests.get(f"{api_url}/api/alerts", params=params)
        response.raise_for_status()
        alerts = response.json()
        
        if format == 'json':
            click.echo(json.dumps(alerts, indent=2))
        else:
            # Format as table
            table_data = []
            for item in alerts:
                row = {
                    'ID': item.get('alert_id', '')[:8] + '...',
                    'Severity': item.get('severity', '').upper(),
                    'Type': item.get('type', ''),
                    'Message': item.get('message', ''),
                    'Timestamp': item.get('timestamp', ''),
                    'Acknowledged': '\u2713' if item.get('acknowledged', False) else '\u2717'
                }
                table_data.append(row)
            
            if not table_data:
                click.echo("No alerts found for the specified criteria.")
            else:
                click.echo(tabulate(table_data, headers='keys', tablefmt='pretty'))
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not list alerts. {str(e)}")
        debug_log.error("budget_cli", f"Error listing alerts: {str(e)}")

@alerts.command('acknowledge')
@click.argument('alert_id')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def acknowledge_alert(ctx, alert_id, api_url):
    """Acknowledge an alert."""
    debug_log.info("budget_cli", f"Acknowledging alert {alert_id}")
    
    try:
        # Acknowledge the alert
        response = requests.post(f"{api_url}/api/alerts/{alert_id}/acknowledge")
        response.raise_for_status()
        
        click.echo(f"Alert {alert_id} acknowledged")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not acknowledge alert. {str(e)}")
        debug_log.error("budget_cli", f"Error acknowledging alert: {str(e)}")

@cli.command()
@click.option('--provider', required=True, help='Provider name')
@click.option('--model', required=True, help='Model name')
@click.option('--input-tokens', type=int, required=True, help='Number of input tokens')
@click.option('--output-tokens', type=int, help='Number of output tokens')
@click.option('--api-url', default=DEFAULT_API_URL, help='Budget API URL')
@click.pass_context
def calc_cost(ctx, provider, model, input_tokens, output_tokens, api_url):
    """Calculate cost for a specific model and token count."""
    debug_log.info("budget_cli", f"Calculating cost for {provider}/{model}")
    
    # Build cost calculation request
    request_data = {
        'provider': provider,
        'model': model,
        'input_tokens': input_tokens
    }
    if output_tokens:
        request_data['output_tokens'] = output_tokens
    
    try:
        # Calculate cost
        response = requests.post(f"{api_url}/api/prices/calculate", json=request_data)
        response.raise_for_status()
        result = response.json()
        
        # Display results
        click.echo("\nCost Calculation:")
        click.echo(f"Provider: {provider}")
        click.echo(f"Model: {model}")
        click.echo(f"Input tokens: {input_tokens}")
        click.echo(f"Output tokens: {output_tokens or 0}")
        click.echo(f"Input cost: ${result.get('input_cost', 0):.4f}")
        click.echo(f"Output cost: ${result.get('output_cost', 0):.4f}")
        click.echo(f"Total cost: ${result.get('total_cost', 0):.4f}")
    
    except requests.exceptions.RequestException as e:
        click.echo(f"Error: Could not calculate cost. {str(e)}")
        debug_log.error("budget_cli", f"Error calculating cost: {str(e)}")

def main():
    """
    Main entry point for the budget CLI.
    """
    try:
        import pkg_resources
        version = pkg_resources.get_distribution("budget").version
        click.echo(f"Budget CLI v{version}")
    except Exception:
        pass
        
    cli(obj={})

if __name__ == '__main__':
    main()