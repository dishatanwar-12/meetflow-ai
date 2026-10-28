from typing import Optional, List, Dict, Any, Tuple
from backend.app.models.task import OwnerStatus

class IdentityResolver:
    @staticmethod
    def resolve_task_owner(
        raw_owner_name: Optional[str],
        attendees: List[Dict[str, Any]],
        project_members: List[Dict[str, Any]]
    ) -> Tuple[Optional[str], Optional[str], OwnerStatus, Optional[str]]:
        """
        Resolves task owner identity with strict uncertainty preservation.
        
        Returns:
            (owner_display_name, matched_user_id, owner_status, confirmation_reason)
        """
        # If no owner stated in source
        if not raw_owner_name or raw_owner_name.strip().lower() in ["", "none", "not stated", "unknown", "tbd", "unassigned", "team"]:
            return None, None, OwnerStatus.NOT_STATED, "No individual owner was specified in the meeting source."

        clean_name = raw_owner_name.strip()
        lower_name = clean_name.lower()

        # Combine potential identity candidates
        # Candidates can have: id (user_id if registered member), name, email
        all_candidates = []
        for att in attendees:
            all_candidates.append({
                "name": att.get("name", ""),
                "email": att.get("email"),
                "user_id": att.get("user_id"),
                "source": "attendee"
            })

        for pm in project_members:
            # Avoid duplicate entries if user is both attendee and PM
            if not any(c.get("user_id") == pm.get("user_id") for c in all_candidates if c.get("user_id")):
                all_candidates.append({
                    "name": pm.get("name", ""),
                    "email": pm.get("email"),
                    "user_id": pm.get("user_id"),
                    "source": "project_member"
                })

        # Check for multiple matches with the same first name (Scenario F: Ambiguous identity)
        exact_matches = []
        first_name_matches = []

        for candidate in all_candidates:
            cand_name = candidate["name"].strip()
            cand_lower = cand_name.lower()

            if cand_lower == lower_name:
                exact_matches.append(candidate)
            elif cand_lower.startswith(lower_name + " ") or lower_name.startswith(cand_lower + " "):
                first_name_matches.append(candidate)

        if len(exact_matches) > 1:
            return clean_name, None, OwnerStatus.AMBIGUOUS, f"Multiple candidates match '{clean_name}'. Please confirm the intended person."

        if len(exact_matches) == 1:
            match = exact_matches[0]
            return match["name"], match.get("user_id"), OwnerStatus.EXPLICIT, None

        if len(first_name_matches) > 1:
            matching_names = ", ".join([c["name"] for c in first_name_matches])
            return clean_name, None, OwnerStatus.AMBIGUOUS, f"Ambiguous name '{clean_name}': multiple candidates identified ({matching_names}). Human confirmation required."

        if len(first_name_matches) == 1:
            # Single candidate matches the first name
            match = first_name_matches[0]
            return match["name"], match.get("user_id"), OwnerStatus.EXPLICIT, None

        # The name was explicitly named in the meeting, but not in our workspace database yet
        return clean_name, None, OwnerStatus.EXPLICIT, "Owner explicitly stated in transcript, but not yet linked to a registered workspace user."

