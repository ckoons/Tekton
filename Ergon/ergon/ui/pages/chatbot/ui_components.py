"""
UI components for the Ergon chatbot.

Provides UI elements for feedback collection, plan reviews, and other interactive components.
"""

import streamlit as st
from typing import Dict, List, Any, Optional

def rate_feature_importance():
    """Display feature importance rating interface."""
    st.subheader("Rate Feature Importance")
    
    # Define features to rate
    features = [
        "Long-term Memory",
        "Agent Awareness",
        "Workflow Creation",
        "Plan Visualization",
        "Agent Creation via Chat",
        "Feedback Collection"
    ]
    
    # Display rating interface
    ratings = {}
    
    st.write("Please rate the importance of these features (1 = least important, 5 = most important):")
    
    cols = st.columns(2)
    
    for i, feature in enumerate(features):
        col_idx = i % 2
        with cols[col_idx]:
            ratings[feature] = st.slider(
                feature, 
                min_value=1, 
                max_value=5, 
                value=3,
                key=f"rating_{feature}"
            )
    
    # Submit button
    if st.button("Submit Ratings"):
        # Store in session state
        st.session_state.feature_ratings = ratings
        
        # Sort by importance
        sorted_features = sorted(
            ratings.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        st.success("Thank you for your feedback! Your priorities are:")
        
        for feature, rating in sorted_features:
            st.write(f"- {feature}: {rating}/5")
        
        # Store in memory if a nexus agent is selected
        if "selected_agent" in st.session_state and st.session_state.selected_agent:
            if st.session_state.selected_agent.get("type") == "nexus":
                # Store in future version
                st.info("Feature priorities stored in agent memory!")

def display_plan_review(plan):
    """Display a plan for review with feedback options."""
    st.subheader("Implementation Plan Review")
    
    st.write("Please review this implementation plan and provide feedback:")
    
    # Display each phase of the plan
    for i, phase in enumerate(plan):
        with st.expander(f"Phase {i+1}: {phase['name']}", expanded=True):
            st.write(phase['description'])
            
            # Display tasks
            for j, task in enumerate(phase['tasks']):
                task_key = f"task_{i}_{j}"
                
                # Store original approval state if not in session
                if f"{task_key}_approved" not in st.session_state:
                    st.session_state[f"{task_key}_approved"] = None
                
                cols = st.columns([1, 8, 3])
                
                # Task approval
                with cols[0]:
                    approved = st.checkbox("✓", key=f"{task_key}_checkbox", value=st.session_state[f"{task_key}_approved"])
                    st.session_state[f"{task_key}_approved"] = approved
                
                # Task description
                with cols[1]:
                    st.write(f"{j+1}. {task['description']}")
                
                # Priority
                with cols[2]:
                    priority = st.selectbox(
                        "Priority", 
                        ["High", "Medium", "Low"],
                        index=["High", "Medium", "Low"].index(task.get("priority", "Medium")),
                        key=f"{task_key}_priority"
                    )
                    
                    # Update task priority in the plan
                    plan[i]['tasks'][j]['priority'] = priority
            
            # Phase feedback
            st.text_area(
                "Feedback for this phase:", 
                key=f"phase_{i}_feedback"
            )
    
    # Overall feedback
    st.text_area(
        "Overall feedback on the plan:",
        key="overall_plan_feedback"
    )
    
    # Submit button
    if st.button("Submit Plan Feedback"):
        st.success("Thank you for your feedback! The plan will be updated accordingly.")
        
        # Collect all feedback
        feedback = {
            "overall": st.session_state.overall_plan_feedback,
            "phases": [
                {
                    "phase": i,
                    "feedback": st.session_state.get(f"phase_{i}_feedback", ""),
                    "tasks": [
                        {
                            "task": j,
                            "approved": st.session_state.get(f"task_{i}_{j}_approved", False),
                            "priority": st.session_state.get(f"task_{i}_{j}_priority", "Medium")
                        }
                        for j in range(len(phase['tasks']))
                    ]
                }
                for i, phase in enumerate(plan)
            ]
        }
        
        # Store feedback in session state
        st.session_state.plan_feedback = feedback
        
        # Update session state plan with the feedback
        st.session_state.current_plan = plan
        
        return feedback
    
    return None

def build_agent_recommendation(matching_agents: List[Dict[str, Any]]) -> str:
    """Build a recommendation message based on matching agents."""
    if matching_agents:
        response = f"I found {len(matching_agents)} agent(s) that might help with your request:\n\n"
        
        for i, agent in enumerate(matching_agents, 1):
            agent_type = agent["type"] or "standard"
            agent_score = agent.get("score", 0)
            
            # Start with the agent name and type
            response += f"{i}. **{agent['name']}** (Type: {agent_type}"
            
            # Add match score for transparency
            if agent_score > 20:
                response += ", Excellent match)"
            elif agent_score > 10:
                response += ", Good match)"
            else:
                response += ")"
            
            response += "\n"
            
            # Add the agent's description if available
            if agent["description"]:
                response += f"   {agent['description']}\n"
            else:
                # Use the type description if no specific description
                response += f"   {agent.get('type_description', '')}\n"
            
            # Add capabilities
            if "capabilities" in agent:
                response += "   **Capabilities**: " + ", ".join(agent["capabilities"]) + "\n"
            
            response += "\n"
        
        response += "Please select one of these agents from the sidebar dropdown to continue our conversation."
    else:
        response = "I don't see any agents that match your request. You can select any agent from the sidebar to continue our conversation, or create a new Nexus agent using the 'Create New Nexus Agent' button."
    
    return response