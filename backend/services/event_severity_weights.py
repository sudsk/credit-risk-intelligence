"""
Event Severity Weights
Maps event types to risk score adjustments based on business impact
"""

EVENT_SEVERITY_WEIGHTS = {
    # C-Level Departures (Highest Impact)
    "ceo_departure": -12,
    "cfo_departure": -12,
    "cto_departure": -10,
    
    # Executive Departures
    "executive_departure": -8,
    "vp_departure": -6,
    
    # Operational Events
    "payment_delay": -5,
    "client_churn": -6,
    "supplier_issues": -4,
    
    # Regulatory
    "regulation_critical": -15,
    "regulation_warning": -8,
    "compliance_issue": -10,
    
    # Market/Reputation
    "negative_news": -4,
    "litigation": -9,
    "reputation_damage": -7,
    
    # Positive Events (Risk Reduction)
    "contract_win": +3,
    "funding_round": +5,
    "expansion": +2,
    
    # Personal/Irrelevant (Zero Impact)
    "ceo_personal_press": 0,
    "employee_personal": 0,
}

def get_event_severity(event_type: str) -> int:
    """
    Get severity weight for event type
    
    Returns:
        Negative = increases risk, Positive = decreases risk, 0 = no impact
    """
    return EVENT_SEVERITY_WEIGHTS.get(event_type, 0)

def adjust_risk_score(current_score: int, event_type: str) -> int:
    """
    Adjust risk score based on event
    
    Args:
        current_score: Current risk score (0-100)
        event_type: Type of event detected
        
    Returns:
        Adjusted risk score (constrained 0-100)
    """
    severity = get_event_severity(event_type)
    new_score = current_score - severity  # Note: negative severity increases score
    return max(0, min(100, new_score))