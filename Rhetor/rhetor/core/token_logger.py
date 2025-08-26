#!/usr/bin/env python3
"""
Token Usage Logger
Tracks and logs token usage, sundown events, and threshold warnings
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

# Import landmarks with fallback
try:
    from landmarks import (
        monitoring_point,
        audit_trail
    )
except ImportError:
    def monitoring_point(**kwargs):
        def decorator(func): return func
        return decorator
    def audit_trail(**kwargs):
        def decorator(func): return func
        return decorator


class TokenLogger:
    """Centralized logging for token management system."""
    
    def __init__(self, log_dir: Optional[Path] = None):
        """Initialize token logger."""
        if log_dir is None:
            from shared.env import TektonEnviron
            tekton_root = Path(TektonEnviron.get('TEKTON_ROOT', '.'))
            log_dir = tekton_root / '.tekton' / 'logs' / 'tokens'
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up file logger
        self.log_file = self.log_dir / f"token_usage_{datetime.now():%Y%m%d}.log"
        
        # Configure logging
        self.logger = logging.getLogger('TokenManager')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.log_file)
        fh.setLevel(logging.INFO)
        
        # Console handler for warnings
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    @monitoring_point(
        name="Token Usage Log",
        description="Log token usage for analysis",
        metrics=["usage_percentage", "total_tokens", "threshold_level"]
    )
    def log_usage(self, ci_name: str, usage_data: Dict[str, Any]):
        """Log token usage snapshot."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ci_name': ci_name,
            'event': 'usage_check',
            **usage_data
        }
        
        self.logger.info(f"Token usage for {ci_name}: {json.dumps(log_entry)}")
        
        # Also append to JSON log for analysis
        json_log = self.log_dir / f"{ci_name}_usage.jsonl"
        with open(json_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    @audit_trail(
        name="Sundown Event",
        description="Log sundown triggers and outcomes",
        compliance="Track CI state transitions"
    )
    def log_sundown(self, ci_name: str, reason: str, triggered_by: str = 'automatic'):
        """Log sundown event."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ci_name': ci_name,
            'event': 'sundown',
            'reason': reason,
            'triggered_by': triggered_by
        }
        
        self.logger.warning(f"SUNDOWN triggered for {ci_name}: {reason}")
        
        # Append to events log
        events_log = self.log_dir / 'sundown_events.jsonl'
        with open(events_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_sunrise(self, ci_name: str, context_restored: bool):
        """Log sunrise event."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ci_name': ci_name,
            'event': 'sunrise',
            'context_restored': context_restored
        }
        
        self.logger.info(f"SUNRISE for {ci_name}: context_restored={context_restored}")
        
        # Append to events log
        events_log = self.log_dir / 'sundown_events.jsonl'
        with open(events_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def log_threshold_warning(self, ci_name: str, percentage: float, level: str):
        """Log threshold warning."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'ci_name': ci_name,
            'event': 'threshold_warning',
            'percentage': percentage,
            'level': level
        }
        
        if level in ['auto', 'critical']:
            self.logger.warning(f"THRESHOLD {level.upper()} for {ci_name}: {percentage:.1f}%")
        else:
            self.logger.info(f"Threshold {level} for {ci_name}: {percentage:.1f}%")
        
        # Track thresholds
        threshold_log = self.log_dir / 'threshold_events.jsonl'
        with open(threshold_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def get_ci_history(self, ci_name: str, limit: int = 100) -> list:
        """Get recent history for a CI."""
        history = []
        json_log = self.log_dir / f"{ci_name}_usage.jsonl"
        
        if json_log.exists():
            with open(json_log) as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        history.append(json.loads(line))
                    except:
                        pass
        
        return history
    
    def analyze_usage_patterns(self, ci_name: str) -> Dict[str, Any]:
        """Analyze usage patterns for optimization."""
        history = self.get_ci_history(ci_name)
        
        if not history:
            return {'status': 'no_data'}
        
        # Calculate statistics
        percentages = [h.get('usage_percentage', 0) for h in history]
        
        return {
            'ci_name': ci_name,
            'samples': len(history),
            'avg_usage': sum(percentages) / len(percentages),
            'max_usage': max(percentages),
            'trend': 'increasing' if percentages[-1] > percentages[0] else 'stable',
            'last_check': history[-1].get('timestamp')
        }


# Global logger instance
_token_logger = None

def get_token_logger() -> TokenLogger:
    """Get or create global token logger."""
    global _token_logger
    if _token_logger is None:
        _token_logger = TokenLogger()
    return _token_logger