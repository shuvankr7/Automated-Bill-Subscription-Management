from datetime import datetime, timedelta

def format_date(date_str):
    """Format a date string to a human-readable format."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%b %d, %Y")

def get_relative_time_string(date_str):
    """Get a relative time string (e.g., "3 days ago", "in 2 months")."""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    today = datetime.now().date()
    date_value = date_obj.date()
    
    diff = (date_value - today).days
    
    if diff == 0:
        return "Today"
    elif diff == 1:
        return "Tomorrow"
    elif diff == -1:
        return "Yesterday"
    elif diff < 0:
        if diff > -7:
            return f"{abs(diff)} days ago"
        elif diff > -30:
            weeks = abs(diff) // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif diff > -365:
            months = abs(diff) // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = abs(diff) // 365
            return f"{years} year{'s' if years > 1 else ''} ago"
    else:
        if diff < 7:
            return f"in {diff} day{'s' if diff > 1 else ''}"
        elif diff < 30:
            weeks = diff // 7
            return f"in {weeks} week{'s' if weeks > 1 else ''}"
        elif diff < 365:
            months = diff // 30
            return f"in {months} month{'s' if months > 1 else ''}"
        else:
            years = diff // 365
            return f"in {years} year{'s' if years > 1 else ''}"

def is_due_soon(due_date_str, days=7):
    """Check if a bill is due soon (within specified days)."""
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    
    return 0 <= (due_date - today).days <= days

def is_overdue(due_date_str):
    """Check if a bill is overdue."""
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    today = datetime.now().date()
    
    return due_date < today

def get_due_date_status(due_date_str):
    """Get the due date status label and color."""
    if is_overdue(due_date_str):
        return {
            "label": "Overdue",
            "color": "red",
            "severity": 3
        }
    elif is_due_soon(due_date_str, 3):
        return {
            "label": "Due Soon",
            "color": "orange",
            "severity": 2
        }
    elif is_due_soon(due_date_str, 7):
        return {
            "label": "Upcoming",
            "color": "green",
            "severity": 1
        }
    else:
        return {
            "label": "Scheduled",
            "color": "blue",
            "severity": 0
        }

def format_currency(amount):
    """Format currency amount."""
    return f"${amount:,.2f}"

def format_frequency(frequency):
    """Format a frequency (e.g., "monthly", "yearly") as a readable string."""
    if frequency == "monthly":
        return "Monthly"
    elif frequency == "yearly":
        return "Yearly"
    elif frequency == "quarterly":
        return "Quarterly"
    elif frequency == "weekly":
        return "Weekly"
    elif frequency == "biweekly":
        return "Bi-weekly"
    elif frequency == "daily":
        return "Daily"
    else:
        return frequency.capitalize()
