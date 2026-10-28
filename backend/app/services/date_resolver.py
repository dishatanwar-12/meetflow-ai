import re
from datetime import datetime, date, timedelta
from typing import Optional, Tuple
import calendar
from backend.app.models.task import DueDateStatus

class DateResolver:
    WEEKDAYS = {
        "monday": 0, "mon": 0,
        "tuesday": 1, "tue": 1,
        "wednesday": 2, "wed": 2,
        "thursday": 3, "thu": 3,
        "friday": 4, "fri": 4,
        "saturday": 5, "sat": 5,
        "sunday": 6, "sun": 6,
    }

    MONTHS = {
        "january": 1, "jan": 1, "february": 2, "feb": 2, "march": 3, "mar": 3,
        "april": 4, "apr": 4, "may": 5, "june": 6, "jun": 6, "july": 7, "jul": 7,
        "august": 8, "aug": 8, "september": 9, "sep": 9, "october": 10, "oct": 10,
        "november": 11, "nov": 11, "december": 12, "dec": 12
    }

    @classmethod
    def resolve_deadline(
        cls,
        date_expression: Optional[str],
        meeting_datetime: Optional[datetime],
        explicit_date_str: Optional[str] = None
    ) -> Tuple[Optional[date], DueDateStatus, Optional[str]]:
        """
        Resolves a deadline while preserving uncertainty.
        Returns: (resolved_date, due_date_status, explanation_or_warning)
        """
        # If there's no expression and no explicit date:
        if not date_expression and not explicit_date_str:
            return None, DueDateStatus.NOT_STATED, "No deadline mentioned in the meeting source."

        # If an explicit date string is provided in ISO or clear format (e.g., '2026-11-15')
        if explicit_date_str:
            clean_str = explicit_date_str.strip()
            # Try YYYY-MM-DD
            try:
                dt = datetime.strptime(clean_str, "%Y-%m-%d").date()
                return dt, DueDateStatus.EXPLICIT, "Explicit calendar date stated in source."
            except ValueError:
                pass

        if not date_expression:
            return None, DueDateStatus.NOT_STATED, None

        raw_expr = date_expression.strip().lower()

        # If meeting date is NOT known, we CANNOT resolve relative dates!
        if not meeting_datetime:
            return None, DueDateStatus.NOT_STATED, f"Meeting date is unknown; relative deadline '{date_expression}' cannot be resolved."

        base_date = meeting_datetime.date() if isinstance(meeting_datetime, datetime) else meeting_datetime

        # 1. "today"
        if raw_expr in ["today", "by today", "end of day today"]:
            return base_date, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved from meeting date: {base_date}"

        # 2. "tomorrow"
        if raw_expr in ["tomorrow", "by tomorrow", "tomorrow morning", "tomorrow afternoon"]:
            resolved = base_date + timedelta(days=1)
            return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved from meeting date + 1 day: {resolved}"

        # 3. "in X days" / "X days from now"
        days_match = re.search(r"in\s+(\d+)\s+days?", raw_expr)
        if days_match:
            days = int(days_match.group(1))
            resolved = base_date + timedelta(days=days)
            return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved from meeting date + {days} days: {resolved}"

        # 4. "in X weeks" / "in a week"
        if "in a week" in raw_expr or "in one week" in raw_expr:
            resolved = base_date + timedelta(days=7)
            return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved from meeting date + 7 days: {resolved}"

        weeks_match = re.search(r"in\s+(\d+)\s+weeks?", raw_expr)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            resolved = base_date + timedelta(weeks=weeks)
            return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved from meeting date + {weeks} weeks: {resolved}"

        # 5. "next [weekday]" or "this [weekday]" or "by [weekday]"
        for day_name, day_num in cls.WEEKDAYS.items():
            if re.search(rf"\b(next|this|by|on)?\s*{day_name}\b", raw_expr):
                # Calculate the day
                current_day = base_date.weekday()
                if "next " in raw_expr:
                    # Next week's occurrence
                    days_ahead = (day_num - current_day) % 7
                    if days_ahead == 0:
                        days_ahead = 7
                    else:
                        days_ahead += 7
                    resolved = base_date + timedelta(days=days_ahead)
                    return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved '{date_expression}' relative to meeting date."
                else:
                    days_ahead = (day_num - current_day) % 7
                    if days_ahead == 0:
                        days_ahead = 7  # upcoming occurrence
                    resolved = base_date + timedelta(days=days_ahead)
                    return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved '{date_expression}' relative to meeting date."

        # 6. "end of the month" / "by month end"
        if "end of the month" in raw_expr or "end of month" in raw_expr or "month end" in raw_expr:
            _, last_day = calendar.monthrange(base_date.year, base_date.month)
            resolved = date(base_date.year, base_date.month, last_day)
            return resolved, DueDateStatus.RESOLVED_FROM_MEETING_DATE, f"Resolved to last day of meeting month: {resolved}"

        # 7. Ambiguous expressions (e.g. "in a couple weeks", "sometime soon", "before next sprint")
        return None, DueDateStatus.AMBIGUOUS, f"Relative expression '{date_expression}' is ambiguous and requires human confirmation."

