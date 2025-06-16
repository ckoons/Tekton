"""
Latent Memory Space State Definitions

Defines the states that a thought can be in within a latent memory space.
This enhanced model provides more nuanced states for better reasoning workflows.
"""

class ThoughtState:
    """
    Enhanced enum for thought states in the latent space.
    
    This expanded state model allows for more sophisticated reasoning flows,
    particularly for reconsidering previously abandoned or rejected thoughts.
    """
    INITIAL = "initial"                # Just created, first formulation
    REFINING = "refining"              # Actively being improved through iterations
    FINALIZED = "finalized"            # Completed and accepted as valid
    PAUSED = "paused"                  # Temporarily stopped work, may resume
    ABANDONED = "abandoned"            # No longer actively pursued, but not invalid
    REJECTED = "rejected"              # Explicitly determined to be invalid/incorrect
    RECONSIDERING = "reconsidering"    # Re-examining previously finalized/abandoned/rejected
    SUPERSEDED = "superseded"          # Replaced by a newer, better thought
    MERGED = "merged"                  # Combined with another thought

    @classmethod
    def get_active_states(cls) -> list:
        """States where a thought is being actively worked on."""
        return [cls.INITIAL, cls.REFINING, cls.RECONSIDERING]
    
    @classmethod
    def get_terminal_states(cls) -> list:
        """States that generally represent completion of the thought process."""
        return [cls.FINALIZED, cls.REJECTED, cls.SUPERSEDED, cls.MERGED]
    
    @classmethod
    def get_inactive_states(cls) -> list:
        """States where a thought is not being actively worked on but could be resumed."""
        return [cls.PAUSED, cls.ABANDONED]
    
    @classmethod
    def can_transition(cls, from_state: str, to_state: str) -> bool:
        """
        Check if a state transition is valid.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            Whether the transition is permitted
        """
        # Define allowed transitions
        transitions = {
            cls.INITIAL: [cls.REFINING, cls.FINALIZED, cls.PAUSED, cls.ABANDONED, cls.REJECTED],
            cls.REFINING: [cls.REFINING, cls.FINALIZED, cls.PAUSED, cls.ABANDONED, cls.REJECTED, cls.MERGED],
            cls.FINALIZED: [cls.RECONSIDERING, cls.SUPERSEDED],
            cls.PAUSED: [cls.REFINING, cls.RECONSIDERING, cls.ABANDONED, cls.REJECTED],
            cls.ABANDONED: [cls.RECONSIDERING, cls.SUPERSEDED],
            cls.REJECTED: [cls.RECONSIDERING],
            cls.RECONSIDERING: [cls.REFINING, cls.FINALIZED, cls.PAUSED, cls.ABANDONED, cls.REJECTED],
            cls.SUPERSEDED: [],  # Terminal state
            cls.MERGED: []       # Terminal state
        }
        
        return to_state in transitions.get(from_state, [])