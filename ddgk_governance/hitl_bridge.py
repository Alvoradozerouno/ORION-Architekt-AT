"""
HITL Bridge (Human-in-the-Loop) fuer Baumeister-Tool-Austria
Menschliche Freigabe fuer kritische Bau-Berechnungen.

Workflow:
1. Kritische Berechnung wird erstellt
2. HITL-Bridge erstellt Approval-Request
3. Menschlicher Experte prueft und genehmigt/lehnt ab
4. Berechnung wird freigegeben oder blockiert
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from enum import Enum
import hashlib


class ApprovalStatus(Enum):
    """Status einer Freigabe-Anfrage."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


@dataclass
class ApprovalRequest:
    """Anfrage fuer menschliche Freigabe."""
    request_id: str
    calculation_id: str
    calculation_type: str
    risk_level: str
    summary: str
    details: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approval_comment: str = ""
    request_hash: str = ""

    def __post_init__(self):
        if not self.request_hash:
            data = f"{self.request_id}:{self.calculation_id}:{self.calculation_type}:{self.created_at.isoformat()}"
            self.request_hash = hashlib.sha256(data.encode()).hexdigest()[:16]

    @property
    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    @property
    def is_approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    @property
    def is_rejected(self) -> bool:
        return self.status == ApprovalStatus.REJECTED

    def approve(self, approver: str, comment: str = "") -> bool:
        """Genehmigt die Anfrage."""
        if not self.is_pending:
            return False
        self.status = ApprovalStatus.APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = approver
        self.approval_comment = comment
        return True

    def reject(self, approver: str, comment: str = "") -> bool:
        """Lehnt die Anfrage ab."""
        if not self.is_pending:
            return False
        self.status = ApprovalStatus.REJECTED
        self.approved_at = datetime.utcnow()
        self.approved_by = approver
        self.approval_comment = comment
        return True

    def to_dict(self) -> Dict:
        return {
            "request_id": self.request_id,
            "calculation_id": self.calculation_id,
            "calculation_type": self.calculation_type,
            "risk_level": self.risk_level,
            "summary": self.summary,
            "details": self.details,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "approved_by": self.approved_by,
            "approval_comment": self.approval_comment,
            "request_hash": self.request_hash,
        }


class HITLBridge:
    """
    Human-in-the-Loop Bridge fuer Bau-Berechnungen.

    Verwaltung von Freigabe-Anfragen fuer kritische Berechnungen.
    """

    def __init__(self, approval_callback: Optional[Callable] = None):
        self._requests: Dict[str, ApprovalRequest] = {}
        self._approval_callback = approval_callback
        self._request_counter = 0

    def create_request(
        self,
        calculation_id: str,
        calculation_type: str,
        risk_level: str,
        summary: str,
        details: Dict[str, Any],
    ) -> ApprovalRequest:
        """Erstellt eine neue Freigabe-Anfrage."""
        self._request_counter += 1
        request_id = f"hitl_{self._request_counter:06d}"

        request = ApprovalRequest(
            request_id=request_id,
            calculation_id=calculation_id,
            calculation_type=calculation_type,
            risk_level=risk_level,
            summary=summary,
            details=details,
        )

        self._requests[request_id] = request

        # Callback wenn registriert
        if self._approval_callback:
            self._approval_callback(request)

        return request

    def approve_request(self, request_id: str, approver: str, comment: str = "") -> bool:
        """Genehmigt eine Freigabe-Anfrage."""
        if request_id not in self._requests:
            return False
        return self._requests[request_id].approve(approver, comment)

    def reject_request(self, request_id: str, approver: str, comment: str = "") -> bool:
        """Lehnt eine Freigabe-Anfrage ab."""
        if request_id not in self._requests:
            return False
        return self._requests[request_id].reject(approver, comment)

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        return self._requests.get(request_id)

    def get_pending_requests(self) -> List[ApprovalRequest]:
        """Gibt alle ausstehenden Anfragen zurueck."""
        return [r for r in self._requests.values() if r.is_pending]

    def get_statistics(self) -> Dict:
        """Gibt Statistiken ueber HITL-Anfragen zurueck."""
        by_status: Dict[str, int] = {}
        for r in self._requests.values():
            by_status[r.status.value] = by_status.get(r.status.value, 0) + 1

        return {
            "total_requests": len(self._requests),
            "by_status": by_status,
            "pending_count": by_status.get("PENDING", 0),
            "approved_count": by_status.get("APPROVED", 0),
            "rejected_count": by_status.get("REJECTED", 0),
        }