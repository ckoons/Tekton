#!/usr/bin/env python3
"""
Apollo CLI.

Command-line interface for interacting with the Apollo component.
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

import httpx
import tabulate
import rich
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.tree import Tree
from rich.syntax import Syntax
from rich.pretty import Pretty

# Use Tekton's environment management for port configuration
try:
    from shared.env import TektonEnviron
    def get_apollo_port() -> int:
        return int(TektonEnviron.get("APOLLO_PORT", "8112"))
except ImportError:
    # Fallback if shared module not available
    def get_apollo_port() -> int:
        return int(os.environ.get("APOLLO_PORT", "8112"))
from apollo.models.context import ContextHealth

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("apollo.cli")

# Create rich console
console = Console()


class ApolloClient:
    """Client for interacting with the Apollo API."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0):
        """
        Initialize the Apollo client.
        
        Args:
            base_url: Base URL for Apollo API, defaults to localhost with configured port
            timeout: Timeout for HTTP requests in seconds
        """
        port = get_apollo_port()
        self.base_url = base_url or f"http://localhost:{port}"
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def get_health(self) -> Dict[str, Any]:
        """
        Get health information from Apollo.
        
        Returns:
            Health information
        """
        url = f"{self.base_url}/health"
        response = await self.client.get(url)
        return response.json()
    
    async def get_contexts(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all contexts from Apollo.
        
        Args:
            status: Optional status filter
            
        Returns:
            API response with contexts
        """
        url = f"{self.base_url}/api/contexts"
        if status:
            url += f"?status={status}"
        response = await self.client.get(url)
        return response.json()
    
    async def get_context(
        self, 
        context_id: str, 
        include_history: bool = False,
        history_limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get a specific context from Apollo.
        
        Args:
            context_id: Context identifier
            include_history: Whether to include history
            history_limit: Maximum history records to return
            
        Returns:
            API response with context details
        """
        url = f"{self.base_url}/api/contexts/{context_id}"
        params = {}
        if include_history:
            params["include_history"] = "true"
            params["history_limit"] = str(history_limit)
        response = await self.client.get(url, params=params)
        return response.json()
    
    async def get_context_dashboard(self, context_id: str) -> Dict[str, Any]:
        """
        Get dashboard data for a context from Apollo.
        
        Args:
            context_id: Context identifier
            
        Returns:
            API response with context dashboard
        """
        url = f"{self.base_url}/api/contexts/{context_id}/dashboard"
        response = await self.client.get(url)
        return response.json()
    
    async def get_predictions(self, health: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all predictions from Apollo.
        
        Args:
            health: Optional health filter
            
        Returns:
            API response with predictions
        """
        url = f"{self.base_url}/api/predictions"
        if health:
            url += f"?health={health}"
        response = await self.client.get(url)
        return response.json()
    
    async def get_prediction(self, context_id: str) -> Dict[str, Any]:
        """
        Get a prediction for a specific context from Apollo.
        
        Args:
            context_id: Context identifier
            
        Returns:
            API response with prediction
        """
        url = f"{self.base_url}/api/predictions/{context_id}"
        response = await self.client.get(url)
        return response.json()
    
    async def get_actions(
        self, 
        critical_only: bool = False,
        actionable_now: bool = False
    ) -> Dict[str, Any]:
        """
        Get all actions from Apollo.
        
        Args:
            critical_only: Whether to only return critical actions
            actionable_now: Whether to only return actions that should be taken now
            
        Returns:
            API response with actions
        """
        url = f"{self.base_url}/api/actions"
        params = {}
        if critical_only:
            params["critical_only"] = "true"
        if actionable_now:
            params["actionable_now"] = "true"
        response = await self.client.get(url, params=params)
        return response.json()
    
    async def get_actions_for_context(
        self, 
        context_id: str,
        highest_priority_only: bool = False
    ) -> Dict[str, Any]:
        """
        Get actions for a specific context from Apollo.
        
        Args:
            context_id: Context identifier
            highest_priority_only: Whether to only return the highest priority action
            
        Returns:
            API response with actions
        """
        url = f"{self.base_url}/api/actions/{context_id}"
        params = {}
        if highest_priority_only:
            params["highest_priority_only"] = "true"
        response = await self.client.get(url, params=params)
        return response.json()
    
    async def mark_action_applied(self, action_id: str) -> Dict[str, Any]:
        """
        Mark an action as applied.
        
        Args:
            action_id: Action identifier
            
        Returns:
            API response
        """
        url = f"{self.base_url}/api/actions/{action_id}/applied"
        response = await self.client.post(url)
        return response.json()
    
    async def get_protocols(
        self,
        type: Optional[str] = None,
        scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all protocols from Apollo.
        
        Args:
            type: Optional type filter
            scope: Optional scope filter
            
        Returns:
            API response with protocols
        """
        url = f"{self.base_url}/api/protocols"
        params = {}
        if type:
            params["type"] = type
        if scope:
            params["scope"] = scope
        response = await self.client.get(url, params=params)
        return response.json()
    
    async def get_protocol(self, protocol_id: str) -> Dict[str, Any]:
        """
        Get a specific protocol from Apollo.
        
        Args:
            protocol_id: Protocol identifier
            
        Returns:
            API response with protocol details
        """
        url = f"{self.base_url}/api/protocols/{protocol_id}"
        response = await self.client.get(url)
        return response.json()
    
    async def get_protocol_violations(
        self,
        component: Optional[str] = None,
        protocol_id: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get protocol violations from Apollo.
        
        Args:
            component: Optional component filter
            protocol_id: Optional protocol ID filter
            severity: Optional severity filter
            limit: Maximum violations to return
            
        Returns:
            API response with violations
        """
        url = f"{self.base_url}/api/protocols/violations"
        params = {}
        if component:
            params["component"] = component
        if protocol_id:
            params["protocol_id"] = protocol_id
        if severity:
            params["severity"] = severity
        params["limit"] = str(limit)
        response = await self.client.get(url, params=params)
        return response.json()
    
    async def get_system_status(self) -> Dict[str, Any]:
        """
        Get system status from Apollo.
        
        Returns:
            API response with system status
        """
        url = f"{self.base_url}/api/status"
        response = await self.client.get(url)
        return response.json()
    
    async def get_health_metrics(self) -> Dict[str, Any]:
        """
        Get health metrics from Apollo.
        
        Returns:
            API response with health metrics
        """
        url = f"{self.base_url}/metrics/health"
        response = await self.client.get(url)
        return response.json()
    
    async def get_prediction_metrics(self) -> Dict[str, Any]:
        """
        Get prediction metrics from Apollo.
        
        Returns:
            API response with prediction metrics
        """
        url = f"{self.base_url}/metrics/predictions"
        response = await self.client.get(url)
        return response.json()
    
    async def get_action_metrics(self) -> Dict[str, Any]:
        """
        Get action metrics from Apollo.
        
        Returns:
            API response with action metrics
        """
        url = f"{self.base_url}/metrics/actions"
        response = await self.client.get(url)
        return response.json()
    
    async def get_protocol_metrics(self) -> Dict[str, Any]:
        """
        Get protocol metrics from Apollo.
        
        Returns:
            API response with protocol metrics
        """
        url = f"{self.base_url}/metrics/protocols"
        response = await self.client.get(url)
        return response.json()
    
    async def get_message_metrics(self) -> Dict[str, Any]:
        """
        Get message metrics from Apollo.
        
        Returns:
            API response with message metrics
        """
        url = f"{self.base_url}/metrics/messages"
        response = await self.client.get(url)
        return response.json()


# Command handlers

async def handle_status(args):
    """Handle status command."""
    client = ApolloClient()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Fetching Apollo status..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            health = await client.get_health()
            system_status = await client.get_system_status()
        
        # Extract relevant info
        status_data = system_status.get("data", {})
        components_status = status_data.get("components_status", {})
        
        # Create table
        table = Table(title="Apollo Status", show_header=True)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")
        
        # Add system row
        health_status = health.get("status", "unknown")
        status_style = {
            "healthy": "green",
            "degraded": "yellow",
            "error": "red"
        }.get(health_status, "white")
        
        table.add_row(
            "Apollo System", 
            f"[{status_style}]{health_status.upper()}[/{status_style}]"
        )
        
        # Add component rows
        for component, is_running in components_status.items():
            status_text = "RUNNING" if is_running else "STOPPED"
            status_style = "green" if is_running else "red"
            table.add_row(
                component, 
                f"[{status_style}]{status_text}[/{status_style}]"
            )
        
        # Display table
        console.print(table)
        
        # Display additional status information
        if "active_contexts" in status_data:
            console.print(Panel(
                f"Active Contexts: {status_data['active_contexts']}\n"
                f"Critical Contexts: {status_data.get('critical_contexts', 0)}\n"
                f"Critical Predictions: {status_data.get('critical_predictions', 0)}\n"
                f"Pending Actions: {status_data.get('pending_actions', 0)}\n"
                f"Critical Actions: {status_data.get('critical_actions', 0)}\n"
                f"Actionable Now: {status_data.get('actionable_now', 0)}",
                title="Status Summary",
                expand=False
            ))
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


async def handle_contexts(args):
    """Handle contexts command."""
    client = ApolloClient()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Fetching contexts..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            result = await client.get_contexts(status=args.status)
        
        # Extract data
        if result.get("status") != "success":
            errors = result.get("errors", ["Unknown error"])
            console.print(f"[bold red]Error: {', '.join(errors)}[/bold red]")
            return
            
        contexts = result.get("data", [])
        
        if not contexts:
            console.print("[yellow]No contexts found[/yellow]")
            return
            
        # Create table
        table = Table(title=f"Apollo Contexts ({len(contexts)} total)", show_header=True)
        table.add_column("ID", style="cyan", no_wrap=True, max_width=36)
        table.add_column("Component", style="blue")
        table.add_column("Model", style="magenta")
        table.add_column("Health", style="green")
        table.add_column("Tokens", style="yellow")
        table.add_column("Updated", style="dim")
        
        # Add rows
        for context in contexts:
            # Extract data
            context_id = context.get("context_id", "unknown")
            component = context.get("component_id", "unknown")
            model = context.get("model", "unknown")
            health = context.get("health", "unknown")
            
            # Get metrics
            metrics = context.get("metrics", {})
            token_utilization = metrics.get("token_utilization", 0) * 100
            total_tokens = metrics.get("total_tokens", 0)
            max_tokens = metrics.get("max_tokens", 0)
            
            # Format last updated
            last_updated = context.get("last_updated")
            if last_updated:
                try:
                    dt = datetime.fromisoformat(last_updated.replace("Z", "+00:00"))
                    updated_str = dt.strftime("%H:%M:%S")
                except:
                    updated_str = last_updated
            else:
                updated_str = "unknown"
                
            # Set health color
            health_style = {
                "excellent": "bright_green",
                "good": "green",
                "fair": "yellow",
                "poor": "orange3",
                "critical": "red"
            }.get(health, "white")
            
            # Format token usage
            token_style = "green"
            if token_utilization > 90:
                token_style = "red"
            elif token_utilization > 75:
                token_style = "yellow"
                
            tokens_text = f"[{token_style}]{total_tokens}/{max_tokens} ({token_utilization:.1f}%)[/{token_style}]"
            
            # Add row
            table.add_row(
                context_id,
                component,
                model,
                f"[{health_style}]{health.upper()}[/{health_style}]",
                tokens_text,
                updated_str
            )
        
        # Display table
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


async def handle_context(args):
    """Handle context command."""
    client = ApolloClient()
    
    try:
        context_id = args.context_id
        
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]Fetching context {context_id}..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            if args.dashboard:
                result = await client.get_context_dashboard(context_id)
            else:
                result = await client.get_context(
                    context_id,
                    include_history=args.history,
                    history_limit=args.history_limit
                )
        
        # Extract data
        if result.get("status") != "success":
            errors = result.get("errors", ["Unknown error"])
            console.print(f"[bold red]Error: {', '.join(errors)}[/bold red]")
            return
            
        context_data = result.get("data", {})
        
        if not context_data:
            console.print(f"[yellow]Context {context_id} not found[/yellow]")
            return
            
        # Display context information
        if args.dashboard:
            # Display dashboard summary
            summary = context_data.get("summary", {})
            
            health = summary.get("health", "unknown")
            health_score = summary.get("health_score", 0)
            token_utilization = summary.get("token_utilization", 0) * 100
            repetition_score = summary.get("repetition_score", 0) * 100
            age_minutes = summary.get("age_minutes", 0)
            
            health_style = {
                "excellent": "bright_green",
                "good": "green",
                "fair": "yellow",
                "poor": "orange3",
                "critical": "red"
            }.get(health, "white")
            
            console.print(Panel(
                f"Health: [{health_style}]{health.upper()}[/{health_style}] ({health_score:.2f})\n"
                f"Token Utilization: {token_utilization:.1f}%\n"
                f"Repetition Score: {repetition_score:.1f}%\n"
                f"Age: {age_minutes:.1f} minutes\n"
                f"Health Trend: {context_data.get('health_trend', 'stable')}",
                title=f"Context Dashboard: {context_id}",
                expand=False
            ))
            
            # Display state, prediction, and actions if available
            if "state" in context_data:
                state = context_data["state"]
                console.print(Panel(
                    Pretty(state),
                    title="Current State",
                    expand=False
                ))
                
            if "prediction" in context_data:
                prediction = context_data["prediction"]
                console.print(Panel(
                    Pretty(prediction),
                    title="Prediction",
                    expand=False
                ))
                
            if "actions" in context_data and context_data["actions"]:
                actions = context_data["actions"]
                action_table = Table(title=f"Recommended Actions ({len(actions)})", show_header=True)
                action_table.add_column("ID", style="cyan", no_wrap=True)
                action_table.add_column("Type", style="blue")
                action_table.add_column("Priority", style="green")
                action_table.add_column("Reason", style="yellow")
                
                for action in actions:
                    action_id = action.get("action_id", "unknown")
                    action_type = action.get("action_type", "unknown")
                    priority = action.get("priority", 0)
                    reason = action.get("reason", "")
                    
                    # Set priority color
                    priority_style = "green"
                    if priority >= 8:
                        priority_style = "red"
                    elif priority >= 5:
                        priority_style = "yellow"
                        
                    action_table.add_row(
                        action_id,
                        action_type,
                        f"[{priority_style}]{priority}[/{priority_style}]",
                        reason
                    )
                    
                console.print(action_table)
        else:
            # Format basic context info
            console.print(Panel(
                Pretty(context_data),
                title=f"Context: {context_id}",
                expand=False
            ))
            
            # Show history if included
            if "history" in context_data and context_data["history"]:
                history = context_data["history"]
                
                history_table = Table(title=f"Context History ({len(history)} records)", show_header=True)
                history_table.add_column("Time", style="dim")
                history_table.add_column("Health", style="green")
                history_table.add_column("Score", style="yellow")
                history_table.add_column("Tokens", style="blue")
                history_table.add_column("Repetition", style="magenta")
                
                for record in history:
                    # Extract data
                    timestamp = record.get("timestamp")
                    health = record.get("health", "unknown")
                    health_score = record.get("health_score", 0)
                    
                    # Get metrics
                    metrics = record.get("metrics", {})
                    token_utilization = metrics.get("token_utilization", 0) * 100
                    repetition_score = metrics.get("repetition_score", 0) * 100
                    
                    # Format timestamp
                    if timestamp:
                        try:
                            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                            time_str = dt.strftime("%H:%M:%S")
                        except:
                            time_str = timestamp
                    else:
                        time_str = "unknown"
                        
                    # Set health color
                    health_style = {
                        "excellent": "bright_green",
                        "good": "green",
                        "fair": "yellow",
                        "poor": "orange3",
                        "critical": "red"
                    }.get(health, "white")
                    
                    # Add row
                    history_table.add_row(
                        time_str,
                        f"[{health_style}]{health.upper()}[/{health_style}]",
                        f"{health_score:.2f}",
                        f"{token_utilization:.1f}%",
                        f"{repetition_score:.1f}%"
                    )
                    
                console.print(history_table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


async def handle_predictions(args):
    """Handle predictions command."""
    client = ApolloClient()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Fetching predictions..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            
            # Get single prediction if context_id provided
            if args.context_id:
                result = await client.get_prediction(args.context_id)
            else:
                # Otherwise get all predictions with optional filter
                result = await client.get_predictions(health=args.health)
        
        # Extract data
        if result.get("status") != "success":
            errors = result.get("errors", ["Unknown error"])
            console.print(f"[bold red]Error: {', '.join(errors)}[/bold red]")
            return
            
        # Handle single prediction
        if args.context_id:
            prediction = result.get("data", {})
            
            if not prediction:
                console.print(f"[yellow]No prediction found for context {args.context_id}[/yellow]")
                return
                
            console.print(Panel(
                Pretty(prediction),
                title=f"Prediction for Context: {args.context_id}",
                expand=False
            ))
        else:
            # Handle multiple predictions
            predictions = result.get("data", [])
            
            if not predictions:
                console.print("[yellow]No predictions found[/yellow]")
                return
                
            # Create table
            table = Table(title=f"Apollo Predictions ({len(predictions)} total)", show_header=True)
            table.add_column("Context ID", style="cyan", no_wrap=True, max_width=36)
            table.add_column("Predicted Health", style="green")
            table.add_column("Confidence", style="yellow")
            table.add_column("Horizon", style="blue")
            table.add_column("Basis", style="magenta")
            
            # Add rows
            for pred in predictions:
                # Extract data
                context_id = pred.get("context_id", "unknown")
                predicted_health = pred.get("predicted_health", "unknown")
                predicted_score = pred.get("predicted_health_score", 0)
                confidence = pred.get("confidence", 0) * 100
                horizon = pred.get("prediction_horizon", 0)
                basis = pred.get("basis", "unknown")
                
                # Set health color
                health_style = {
                    "excellent": "bright_green",
                    "good": "green",
                    "fair": "yellow",
                    "poor": "orange3",
                    "critical": "red"
                }.get(predicted_health, "white")
                
                # Format health text
                health_text = f"[{health_style}]{predicted_health.upper()}[/{health_style}] ({predicted_score:.2f})"
                
                # Format confidence
                conf_style = "green" if confidence > 80 else "yellow" if confidence > 60 else "red"
                conf_text = f"[{conf_style}]{confidence:.1f}%[/{conf_style}]"
                
                # Add row
                table.add_row(
                    context_id,
                    health_text,
                    conf_text,
                    f"{horizon} sec",
                    basis
                )
            
            # Display table
            console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


async def handle_actions(args):
    """Handle actions command."""
    client = ApolloClient()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Fetching actions..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            
            # Get actions for specific context
            if args.context_id:
                result = await client.get_actions_for_context(
                    args.context_id,
                    highest_priority_only=args.highest_priority
                )
            else:
                # Get all actions with filters
                result = await client.get_actions(
                    critical_only=args.critical,
                    actionable_now=args.actionable
                )
                
            # Handle apply action
            if args.apply:
                apply_result = await client.mark_action_applied(args.apply)
                if apply_result.get("status") == "success":
                    console.print(f"[green]Action {args.apply} marked as applied[/green]")
                else:
                    errors = apply_result.get("errors", ["Unknown error"])
                    console.print(f"[bold red]Error applying action: {', '.join(errors)}[/bold red]")
        
        # Extract data
        if result.get("status") != "success":
            errors = result.get("errors", ["Unknown error"])
            console.print(f"[bold red]Error: {', '.join(errors)}[/bold red]")
            return
            
        actions = result.get("data", [])
        
        if not actions:
            console.print("[yellow]No actions found[/yellow]")
            return
            
        # Create table
        title = "Apollo Actions"
        if args.context_id:
            title += f" for Context {args.context_id}"
        elif args.critical:
            title += " (Critical Only)"
        elif args.actionable:
            title += " (Actionable Now)"
            
        table = Table(title=f"{title} ({len(actions)} total)", show_header=True)
        table.add_column("ID", style="cyan", no_wrap=True, max_width=36)
        table.add_column("Context ID", style="blue", max_width=36)
        table.add_column("Type", style="magenta")
        table.add_column("Priority", style="yellow")
        table.add_column("Reason", style="green", max_width=50)
        
        # Add rows
        for action in actions:
            # Extract data
            action_id = action.get("action_id", "unknown")
            context_id = action.get("context_id", "unknown")
            action_type = action.get("action_type", "unknown")
            priority = action.get("priority", 0)
            reason = action.get("reason", "")
            
            # Set priority color
            priority_style = "green"
            if priority >= 8:
                priority_style = "red"
            elif priority >= 5:
                priority_style = "yellow"
                
            # Add row
            table.add_row(
                action_id,
                context_id,
                action_type,
                f"[{priority_style}]{priority}[/{priority_style}]",
                reason
            )
        
        # Display table
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


async def handle_protocols(args):
    """Handle protocols command."""
    client = ApolloClient()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Fetching protocols..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            
            # Get single protocol
            if args.protocol_id:
                result = await client.get_protocol(args.protocol_id)
            # Get violations
            elif args.violations:
                result = await client.get_protocol_violations(
                    component=args.component,
                    protocol_id=args.violations if args.violations != "all" else None,
                    severity=args.severity,
                    limit=args.limit
                )
            # Get all protocols
            else:
                result = await client.get_protocols(
                    type=args.type,
                    scope=args.scope
                )
        
        # Extract data
        if result.get("status") != "success":
            errors = result.get("errors", ["Unknown error"])
            console.print(f"[bold red]Error: {', '.join(errors)}[/bold red]")
            return
            
        # Handle single protocol
        if args.protocol_id:
            protocol = result.get("data", {})
            
            if not protocol:
                console.print(f"[yellow]Protocol {args.protocol_id} not found[/yellow]")
                return
                
            console.print(Panel(
                Pretty(protocol),
                title=f"Protocol: {args.protocol_id}",
                expand=False
            ))
        
        # Handle violations
        elif args.violations:
            violations = result.get("data", [])
            
            if not violations:
                console.print("[yellow]No violations found[/yellow]")
                return
                
            # Create table
            table = Table(title=f"Protocol Violations ({len(violations)} total)", show_header=True)
            table.add_column("ID", style="cyan", no_wrap=True, max_width=36)
            table.add_column("Protocol ID", style="blue", max_width=40)
            table.add_column("Component", style="magenta")
            table.add_column("Severity", style="yellow")
            table.add_column("Message", style="green", max_width=50)
            
            # Add rows
            for violation in violations:
                # Extract data
                violation_id = violation.get("violation_id", "unknown")
                protocol_id = violation.get("protocol_id", "unknown")
                component = violation.get("component", "unknown")
                severity = violation.get("severity", "unknown")
                message = violation.get("message", "")
                
                # Set severity color
                severity_style = {
                    "info": "blue",
                    "warning": "yellow",
                    "error": "red",
                    "critical": "red bold"
                }.get(severity, "white")
                
                # Add row
                table.add_row(
                    violation_id,
                    protocol_id,
                    component,
                    f"[{severity_style}]{severity.upper()}[/{severity_style}]",
                    message
                )
            
            # Display table
            console.print(table)
        
        # Handle all protocols
        else:
            protocols = result.get("data", [])
            
            if not protocols:
                console.print("[yellow]No protocols found[/yellow]")
                return
                
            # Create table
            filter_text = ""
            if args.type:
                filter_text += f" (Type: {args.type})"
            if args.scope:
                filter_text += f" (Scope: {args.scope})"
                
            table = Table(title=f"Apollo Protocols{filter_text} ({len(protocols)} total)", show_header=True)
            table.add_column("ID", style="cyan", no_wrap=True, max_width=40)
            table.add_column("Name", style="blue")
            table.add_column("Type", style="magenta")
            table.add_column("Scope", style="yellow")
            table.add_column("Mode", style="green")
            table.add_column("Enabled", style="dim")
            
            # Add rows
            for protocol in protocols:
                # Extract data
                protocol_id = protocol.get("protocol_id", "unknown")
                name = protocol.get("name", "unknown")
                type_value = protocol.get("type", "unknown")
                scope = protocol.get("scope", "unknown")
                mode = protocol.get("enforcement_mode", "unknown")
                enabled = protocol.get("enabled", False)
                
                # Add row
                table.add_row(
                    protocol_id,
                    name,
                    type_value,
                    scope,
                    mode,
                    "[green]Yes[/green]" if enabled else "[red]No[/red]"
                )
            
            # Display table
            console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


async def handle_metrics(args):
    """Handle metrics command."""
    client = ApolloClient()
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]Fetching {args.type} metrics..."),
            transient=True
        ) as progress:
            progress.add_task("fetch", total=None)
            
            # Get metrics based on type
            if args.type == "health":
                result = await client.get_health_metrics()
            elif args.type == "predictions":
                result = await client.get_prediction_metrics()
            elif args.type == "actions":
                result = await client.get_action_metrics()
            elif args.type == "protocols":
                result = await client.get_protocol_metrics()
            elif args.type == "messages":
                result = await client.get_message_metrics()
            else:
                # Get all metrics
                health_result = await client.get_health_metrics()
                predictions_result = await client.get_prediction_metrics()
                actions_result = await client.get_action_metrics()
                protocols_result = await client.get_protocol_metrics()
                messages_result = await client.get_message_metrics()
                
                # Combine results
                result = {
                    "status": "success",
                    "data": {
                        "health": health_result.get("data", {}),
                        "predictions": predictions_result.get("data", {}),
                        "actions": actions_result.get("data", {}),
                        "protocols": protocols_result.get("data", {}),
                        "messages": messages_result.get("data", {})
                    }
                }
        
        # Extract data
        if result.get("status") != "success":
            errors = result.get("errors", ["Unknown error"])
            console.print(f"[bold red]Error: {', '.join(errors)}[/bold red]")
            return
            
        metrics_data = result.get("data", {})
        
        if not metrics_data:
            console.print("[yellow]No metrics found[/yellow]")
            return
            
        # Display metrics based on type
        if args.type == "health" or args.type == "all":
            if "health" in metrics_data:
                health_data = metrics_data["health"]
            else:
                health_data = metrics_data
                
            # Get health distribution
            health_distribution = health_data.get("health_distribution", {})
            health_percentages = health_data.get("health_percentages", {})
            
            # Create health table
            health_table = Table(title="Context Health Distribution", show_header=True)
            health_table.add_column("Health Status", style="blue")
            health_table.add_column("Count", style="cyan", justify="right")
            health_table.add_column("Percentage", style="green", justify="right")
            
            # Add rows
            for status, count in health_distribution.items():
                percentage = health_percentages.get(status, 0)
                
                # Set health color
                health_style = {
                    "excellent": "bright_green",
                    "good": "green",
                    "fair": "yellow",
                    "poor": "orange3",
                    "critical": "red"
                }.get(status, "white")
                
                health_table.add_row(
                    f"[{health_style}]{status.upper()}[/{health_style}]",
                    str(count),
                    f"{percentage}%"
                )
                
            console.print(health_table)
            
            # Display summary
            console.print(Panel(
                f"Total Contexts: {health_data.get('total_contexts', 0)}\n"
                f"Critical Contexts: {health_data.get('critical_contexts', 0)}",
                title="Health Metrics Summary",
                expand=False
            ))
            
        if args.type == "predictions" or args.type == "all":
            if "predictions" in metrics_data:
                pred_data = metrics_data["predictions"]
            else:
                pred_data = metrics_data
                
            # Get prediction accuracy
            accuracy = pred_data.get("prediction_accuracy", {})
            
            # Create accuracy table
            accuracy_table = Table(title="Prediction Accuracy by Rule", show_header=True)
            accuracy_table.add_column("Rule", style="blue")
            accuracy_table.add_column("Accuracy", style="green", justify="right")
            
            # Add rows
            for rule, acc in accuracy.items():
                # Set accuracy color
                acc_style = "green" if acc > 0.8 else "yellow" if acc > 0.6 else "red"
                
                accuracy_table.add_row(
                    rule,
                    f"[{acc_style}]{acc:.2%}[/{acc_style}]"
                )
                
            console.print(accuracy_table)
            
            # Display summary
            console.print(Panel(
                f"Total Predictions: {pred_data.get('total_predictions', 0)}\n"
                f"Critical Predictions: {pred_data.get('critical_predictions', 0)}",
                title="Prediction Metrics Summary",
                expand=False
            ))
            
        if args.type == "actions" or args.type == "all":
            if "actions" in metrics_data:
                action_data = metrics_data["actions"]
            else:
                action_data = metrics_data
                
            # Get action distribution
            type_distribution = action_data.get("type_distribution", {})
            priority_distribution = action_data.get("priority_distribution", {})
            
            # Create type distribution table
            type_table = Table(title="Actions by Type", show_header=True)
            type_table.add_column("Action Type", style="blue")
            type_table.add_column("Count", style="green", justify="right")
            
            # Add rows
            for action_type, count in type_distribution.items():
                type_table.add_row(
                    action_type,
                    str(count)
                )
                
            console.print(type_table)
            
            # Create priority distribution table
            priority_table = Table(title="Actions by Priority", show_header=True)
            priority_table.add_column("Priority", style="blue")
            priority_table.add_column("Count", style="green", justify="right")
            
            # Add rows
            for priority, count in sorted(priority_distribution.items(), key=lambda x: int(x[0]), reverse=True):
                # Set priority color
                priority_val = int(priority)
                priority_style = "green"
                if priority_val >= 8:
                    priority_style = "red"
                elif priority_val >= 5:
                    priority_style = "yellow"
                    
                priority_table.add_row(
                    f"[{priority_style}]{priority}[/{priority_style}]",
                    str(count)
                )
                
            console.print(priority_table)
            
            # Display summary
            console.print(Panel(
                f"Total Actions: {action_data.get('total_actions', 0)}\n"
                f"Critical Actions: {action_data.get('critical_actions', 0)}\n"
                f"Actionable Now: {action_data.get('actionable_now', 0)}",
                title="Action Metrics Summary",
                expand=False
            ))
            
        if args.type == "protocols" or args.type == "all":
            if "protocols" in metrics_data:
                protocol_data = metrics_data["protocols"]
            else:
                protocol_data = metrics_data
                
            # Get violation summary
            violation_summary = protocol_data.get("violation_summary", {})
            
            # Create violation summary table
            violation_table = Table(title="Protocol Violations by Severity", show_header=True)
            violation_table.add_column("Severity", style="blue")
            violation_table.add_column("Count", style="green", justify="right")
            
            # Add rows
            for severity, count in violation_summary.items():
                # Set severity color
                severity_style = {
                    "info": "blue",
                    "warning": "yellow",
                    "error": "red",
                    "critical": "red bold"
                }.get(severity, "white")
                
                violation_table.add_row(
                    f"[{severity_style}]{severity.upper()}[/{severity_style}]",
                    str(count)
                )
                
            console.print(violation_table)
            
            # Display summary
            total_evaluations = protocol_data.get("total_evaluations", 0)
            total_violations = protocol_data.get("total_violations", 0)
            violation_rate = protocol_data.get("violation_rate", 0)
            
            console.print(Panel(
                f"Total Protocols: {protocol_data.get('total_protocols', 0)}\n"
                f"Total Evaluations: {total_evaluations}\n"
                f"Total Violations: {total_violations}\n"
                f"Violation Rate: {violation_rate}%",
                title="Protocol Metrics Summary",
                expand=False
            ))
            
        if args.type == "messages" or args.type == "all":
            if "messages" in metrics_data:
                message_data = metrics_data["messages"]
            else:
                message_data = metrics_data
                
            # Get queue stats
            queue_stats = message_data.get("queue_stats", {})
            delivery_stats = message_data.get("delivery_stats", {})
            
            # Display summary
            console.print(Panel(
                f"Outbound Queue: {queue_stats.get('outbound_queue_size', 0)}/{queue_stats.get('outbound_queue_max_size', 0)}\n"
                f"Inbound Queue: {queue_stats.get('inbound_queue_size', 0)}/{queue_stats.get('inbound_queue_max_size', 0)}\n"
                f"Current Batch: {queue_stats.get('current_batch_size', 0)}/{queue_stats.get('batch_size_limit', 0)}\n"
                f"Delivery Records: {queue_stats.get('delivery_records_count', 0)}\n"
                f"Local Subscriptions: {queue_stats.get('local_subscriptions_count', 0)}\n"
                f"Remote Subscriptions: {queue_stats.get('remote_subscriptions_count', 0)}",
                title="Message Queue Stats",
                expand=False
            ))
            
            # Create delivery stats table
            delivery_table = Table(title="Message Delivery Stats", show_header=True)
            delivery_table.add_column("Status", style="blue")
            delivery_table.add_column("Count", style="green", justify="right")
            
            # Add rows
            for status, count in delivery_stats.items():
                # Set status color
                status_style = {
                    "pending": "yellow",
                    "delivered": "green",
                    "failed": "red",
                    "expired": "red dim"
                }.get(status, "white")
                
                delivery_table.add_row(
                    f"[{status_style}]{status.upper()}[/{status_style}]",
                    str(count)
                )
                
            console.print(delivery_table)
        
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
    finally:
        await client.close()


def create_parser():
    """Create command-line parser."""
    parser = argparse.ArgumentParser(
        description="Apollo CLI - Command-line interface for Apollo executive coordinator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Show Apollo status")
    
    # Contexts command
    contexts_parser = subparsers.add_parser("contexts", help="List contexts")
    contexts_parser.add_argument(
        "--status", "-s",
        choices=["excellent", "good", "fair", "poor", "critical"],
        help="Filter by context health status"
    )
    
    # Context command
    context_parser = subparsers.add_parser("context", help="Show context details")
    context_parser.add_argument(
        "context_id",
        help="Context identifier"
    )
    context_parser.add_argument(
        "--history", "-H",
        action="store_true",
        help="Include context history"
    )
    context_parser.add_argument(
        "--history-limit",
        type=int,
        default=10,
        help="Maximum history records to include"
    )
    context_parser.add_argument(
        "--dashboard", "-d",
        action="store_true",
        help="Show context dashboard"
    )
    
    # Predictions command
    predictions_parser = subparsers.add_parser("predictions", help="Show predictions")
    predictions_parser.add_argument(
        "--context-id", "-c",
        help="Show prediction for specific context"
    )
    predictions_parser.add_argument(
        "--health", "-s",
        choices=["excellent", "good", "fair", "poor", "critical"],
        help="Filter by predicted health status"
    )
    
    # Actions command
    actions_parser = subparsers.add_parser("actions", help="Show actions")
    actions_parser.add_argument(
        "--context-id", "-c",
        help="Show actions for specific context"
    )
    actions_parser.add_argument(
        "--critical",
        action="store_true",
        help="Show only critical actions"
    )
    actions_parser.add_argument(
        "--actionable",
        action="store_true",
        help="Show only actionable now actions"
    )
    actions_parser.add_argument(
        "--highest-priority",
        action="store_true",
        help="Show only highest priority action for context"
    )
    actions_parser.add_argument(
        "--apply", "-a",
        help="Mark action as applied"
    )
    
    # Protocols command
    protocols_parser = subparsers.add_parser("protocols", help="Show protocols")
    protocols_parser.add_argument(
        "--protocol-id", "-p",
        help="Show specific protocol"
    )
    protocols_parser.add_argument(
        "--type", "-t",
        choices=[
            "message_format", "request_flow", "response_format", 
            "authentication", "rate_limiting", "data_validation", 
            "error_handling", "event_sequencing"
        ],
        help="Filter by protocol type"
    )
    protocols_parser.add_argument(
        "--scope", "-s",
        choices=["global", "component", "endpoint", "message_type"],
        help="Filter by protocol scope"
    )
    protocols_parser.add_argument(
        "--violations", "-v",
        nargs="?",
        const="all",
        help="Show protocol violations (optionally for specific protocol)"
    )
    protocols_parser.add_argument(
        "--component", "-c",
        help="Filter violations by component"
    )
    protocols_parser.add_argument(
        "--severity",
        choices=["info", "warning", "error", "critical"],
        help="Filter violations by severity"
    )
    protocols_parser.add_argument(
        "--limit", "-l",
        type=int,
        default=100,
        help="Maximum violations to show"
    )
    
    # Metrics command
    metrics_parser = subparsers.add_parser("metrics", help="Show metrics")
    metrics_parser.add_argument(
        "type",
        choices=["health", "predictions", "actions", "protocols", "messages", "all"],
        default="all",
        nargs="?",
        help="Type of metrics to show"
    )
    
    return parser


async def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    # Execute command
    if args.command == "status":
        await handle_status(args)
    elif args.command == "contexts":
        await handle_contexts(args)
    elif args.command == "context":
        await handle_context(args)
    elif args.command == "predictions":
        await handle_predictions(args)
    elif args.command == "actions":
        await handle_actions(args)
    elif args.command == "protocols":
        await handle_protocols(args)
    elif args.command == "metrics":
        await handle_metrics(args)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("[yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)