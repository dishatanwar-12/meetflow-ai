import React from 'react';
import { Badge } from '../ui/Badge';
import { OwnerStatus, DueDateStatus } from '../../types';
import { HelpCircle, AlertTriangle, CheckCircle2, UserCheck, Calendar } from 'lucide-react';

interface UncertaintyBadgeProps {
  type: 'owner' | 'due_date';
  status: OwnerStatus | DueDateStatus;
  dateExpression?: string;
  className?: string;
}

export const UncertaintyBadge: React.FC<UncertaintyBadgeProps> = ({
  type,
  status,
  dateExpression,
  className,
}) => {
  if (status === 'user_confirmed') {
    return (
      <Badge variant="success" className={className} title="Confirmed by team member">
        <UserCheck className="w-3 h-3 mr-1 inline" /> Confirmed
      </Badge>
    );
  }

  if (status === 'explicit') {
    return (
      <Badge variant="info" className={className} title="Explicitly stated in transcript">
        <CheckCircle2 className="w-3 h-3 mr-1 inline" /> Stated
      </Badge>
    );
  }

  if (status === 'resolved_from_meeting_date') {
    return (
      <Badge variant="teal" className={className} title={`Resolved relative expression: "${dateExpression}"`}>
        <Calendar className="w-3 h-3 mr-1 inline" /> Resolved
      </Badge>
    );
  }

  if (status === 'not_stated') {
    return (
      <Badge variant="amber" className={className} title={type === 'owner' ? "No owner stated in source" : "No deadline mentioned"}>
        <HelpCircle className="w-3 h-3 mr-1 inline" /> {type === 'owner' ? 'Owner Unknown' : 'No Deadline'}
      </Badge>
    );
  }

  if (status === 'ambiguous') {
    return (
      <Badge variant="warning" className={className} title="Ambiguous interpretation requires review">
        <AlertTriangle className="w-3 h-3 mr-1 inline" /> Ambiguous
      </Badge>
    );
  }

  if (status === 'conflicting') {
    return (
      <Badge variant="danger" className={className} title="Conflicting statements found in meeting">
        <AlertTriangle className="w-3 h-3 mr-1 inline" /> Conflicting
      </Badge>
    );
  }

  return (
    <Badge variant="neutral" className={className}>
      {status}
    </Badge>
  );
};

