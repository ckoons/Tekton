# Hermes Documentation Index

## Overview Documents
- [README.md](./README.md) - Component overview and key features
- [API_REFERENCE.md](./API_REFERENCE.md) - Complete API documentation
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) - Guide for integrating with Hermes

## Core Concepts

### Service Registry
- Component Registration - Process and requirements for registering components
- Service Discovery - Finding and connecting to other components
- Capability-based Discovery - Discovering components by capability
- Health Monitoring - Tracking component health and availability

### Messaging System
- Message Types - Different types of messages and their formats
- Routing Rules - How messages are routed between components
- Delivery Guarantees - Reliability and delivery confirmation mechanisms
- Correlation - Tracking related messages using correlation IDs

### Event System
- Event Broadcasting - Publishing events to interested components
- Subscription Management - Creating and managing event subscriptions
- Event Delivery - How events are delivered to subscribers
- Event Formats - Structure and content of different event types

### API Gateway
- Request Routing - Routing external requests to appropriate components
- Authentication - Securing access to component APIs
- Rate Limiting - Controlling API usage
- Request Transformation - Modifying requests before delivery

## API Documentation
- REST API - HTTP endpoints for registry, messaging, and events
- WebSocket API - Real-time communication interfaces
- Client Library - Programmatic access to Hermes functionality
- Authentication - Securing Hermes API access

## Integration Patterns
- Component Registration - Best practices for registering components
- Service Discovery - Patterns for discovering and using other components
- Message Exchange - Common message exchange patterns
- Event Handling - Patterns for working with events
- Fault Tolerance - Handling communication failures

## Development Resources
- Configuration - Settings and environment variables
- Deployment - Deployment options and scenarios
- Testing - Testing strategies for Hermes integration
- Monitoring - Tracking system performance and health

## Related Documents
- [Single Port Architecture](../../TektonDocumentation/Architecture/SinglePortArchitecture.md)
- [Component Integration Patterns](../../TektonDocumentation/Architecture/ComponentIntegrationPatterns.md)
- [Component Lifecycle](../../TektonDocumentation/Architecture/ComponentLifecycle.md)
- [Standardized Error Handling](../../TektonDocumentation/DeveloperGuides/StandardizedErrorHandling.md)