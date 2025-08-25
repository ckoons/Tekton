"""
Chat Route Endpoint Implementation for Rhetor

This file contains the implementation of the /chat/route endpoint
that needs to be added to Rhetor's app.py to support the new
Hephaestus UI chat routing functionality.

Add this code to /Rhetor/rhetor/api/app.py after the existing endpoints.
"""

from .RouteRequest import RouteRequest, RouteResponse


@app.post("/chat/route")
async def route_chat_message(request: RouteRequest) -> RouteResponse:
    """
    Route chat messages to component CIs or team chat.
    
    This endpoint handles the routing logic for the Hephaestus UI chat widget,
    directing messages to the appropriate CI specialist based on the component
    or orchestrating team chat when requested.
    """
    
    if not ai_specialist_manager:
        raise HTTPException(status_code=503, detail="CI Specialist Manager not initialized")
    
    try:
        # Handle team chat
        if request.component == "team":
            # Use existing CI messaging integration for team chat
            if not ai_messaging_integration:
                raise HTTPException(
                    status_code=503, 
                    detail="CI messaging integration not available for team chat"
                )
            
            # Get all active specialists for team chat
            active_specialists = await ai_specialist_manager.list_active_specialists()
            
            # Create a team chat orchestration request
            # Rhetor acts as the moderator
            messages = await ai_messaging_integration.orchestrate_team_chat(
                topic=request.message,
                specialists=active_specialists,
                initial_prompt=request.message,
                context_id=request.context_id
            )
            
            # Extract the primary response
            if messages and len(messages) > 0:
                primary_message = messages[0]
                return RouteResponse(
                    success=True,
                    component="team",
                    speaker=primary_message.get("sender", "Rhetor"),
                    message=primary_message.get("content", ""),
                    participants=[msg.get("sender") for msg in messages]
                )
            else:
                # Fallback to Rhetor's direct response
                system_prompt = "You are Rhetor, moderating a team discussion. Provide a thoughtful response that considers multiple perspectives."
                response = await model_router.route_request(
                    message=request.message,
                    context_id=request.context_id,
                    task_type="team_moderation",
                    component="rhetor",
                    system_prompt=system_prompt,
                    streaming=False
                )
                
                return RouteResponse(
                    success=True,
                    component="team",
                    speaker="Rhetor",
                    message=response.get("message", ""),
                    model=response.get("model"),
                    provider=response.get("provider"),
                    participants=["Rhetor"]
                )
        
        else:
            # Route to specific component AI
            specialist_id = f"{request.component}-assistant"
            
            # Check if specialist exists, create if needed
            specialist_exists = False
            active_specialists = await ai_specialist_manager.list_active_specialists()
            for spec in active_specialists:
                if spec.get("id") == specialist_id:
                    specialist_exists = True
                    break
            
            if not specialist_exists:
                # Create specialist for this component
                logger.info(f"Creating new specialist for component: {request.component}")
                
                # Define specialist configuration based on component
                specialist_config = {
                    "id": specialist_id,
                    "name": f"{request.component.capitalize()} Assistant",
                    "description": f"CI assistant for the {request.component.capitalize()} component",
                    "model_preferences": {
                        "primary": "claude-3-5-haiku-20241022",  # Fast for component chats
                        "fallback": "llama3.3"  # Local fallback
                    },
                    "personality_traits": [
                        f"Expert in {request.component} functionality",
                        "Helpful and concise",
                        "Context-aware"
                    ],
                    "system_prompt": f"You are the CI assistant for the {request.component.capitalize()} component in Tekton. Help users understand and use {request.component} effectively."
                }
                
                # Create the specialist
                await ai_specialist_manager.create_specialist(specialist_config)
            
            # Use existing send_to_specialist method for routing
            response_data = await ai_specialist_manager.send_to_specialist(
                specialist_id=specialist_id,
                message=request.message,
                context_id=request.context_id,
                streaming=False
            )
            
            # If send_to_specialist returns a dict, use it directly
            if isinstance(response_data, dict):
                return RouteResponse(
                    success=True,
                    component=request.component,
                    message=response_data.get("message", ""),
                    model=response_data.get("model"),
                    provider=response_data.get("provider")
                )
            else:
                # Handle other response formats
                return RouteResponse(
                    success=True,
                    component=request.component,
                    message=str(response_data)
                )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error routing chat message: {e}")
        # Fallback to basic Rhetor response
        try:
            system_prompt = prompt_engine.get_system_prompt(component=request.component)
            response = await model_router.route_request(
                message=request.message,
                context_id=request.context_id,
                task_type="chat",
                component=request.component,
                system_prompt=system_prompt,
                streaming=False
            )
            
            return RouteResponse(
                success=True,
                component=request.component,
                message=response.get("message", ""),
                model=response.get("model"),
                provider=response.get("provider")
            )
        except Exception as fallback_error:
            logger.error(f"Fallback routing also failed: {fallback_error}")
            raise HTTPException(status_code=500, detail=str(e))