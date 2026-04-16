"""
ORION Safety Module - Audit Trail System
Adapted from GENESIS DUAL-SYSTEM V3.0.1

Provides cryptographically secure, immutable audit logs for building compliance.
Based on SHA-256 chaining similar to blockchain technology.

Use Cases:
- Unchangeable compliance verification records
- OIB-RL check audit trails
- Building authority submissions
- Legal documentation
- Multi-party approval workflows

Standards Compliance:
- EU AI Act Article 12 (High-Risk AI Systems Logging)
- ISO/IEC 27001 (Information Security)
- GDPR Article 30 (Records of Processing Activities)

Version: 1.0.0 (Integrated from GENESIS 2026-04-06)
License: Apache 2.0
"""

import hashlib
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """Single audit log entry with cryptographic linking"""

    timestamp: str
    event_type: str
    actor: str  # User/System performing action
    action: str
    resource: str  # What was affected
    result: str  # success/failure
    details: Dict[str, Any]
    previous_hash: str
    entry_hash: str

    @classmethod
    def create(
        cls,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        result: str,
        details: Dict[str, Any],
        previous_hash: str = "0" * 64,
        timestamp: Optional[str] = None,
    ) -> "AuditEntry":
        """Create new audit entry with calculated hash"""

        timestamp = timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Create data for hashing (excluding entry_hash itself)
        data_to_hash = {
            "timestamp": timestamp,
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "resource": resource,
            "result": result,
            "details": details,
            "previous_hash": previous_hash,
        }

        # Calculate SHA-256 hash
        entry_hash = cls._calculate_hash(data_to_hash)

        return cls(
            timestamp=timestamp,
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            details=details,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )

    @staticmethod
    def _calculate_hash(data: Dict[str, Any]) -> str:
        """Calculate SHA-256 hash of data"""
        json_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(json_str.encode("utf-8")).hexdigest()

    def verify(self) -> bool:
        """Verify this entry's hash is correct"""
        data_to_hash = {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "action": self.action,
            "resource": self.resource,
            "result": self.result,
            "details": self.details,
            "previous_hash": self.previous_hash,
        }
        calculated_hash = self._calculate_hash(data_to_hash)
        return calculated_hash == self.entry_hash

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class AuditTrail:
    """
    Immutable audit trail with cryptographic chain verification

    Similar to blockchain:
    - Each entry contains hash of previous entry
    - Tampering with any entry breaks the chain
    - Provides cryptographic proof of integrity
    """

    def __init__(self, name: str, storage_path: Optional[Path] = None):
        """
        Initialize audit trail

        Args:
            name: Trail name (e.g., "oib_rl_compliance", "bim_analysis")
            storage_path: Optional path to persist trail
        """
        self.name = name
        self.storage_path = storage_path or Path(f"./audit_trails/{name}.jsonl")
        self.entries: List[AuditEntry] = []
        self._load_existing()

    def _load_existing(self):
        """Load existing audit trail from storage"""
        if not self.storage_path.exists():
            logger.info(f"Creating new audit trail: {self.name}")
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            return

        logger.info(f"Loading existing audit trail: {self.name}")
        try:
            with open(self.storage_path, "r") as f:
                for line in f:
                    data = json.loads(line.strip())
                    entry = AuditEntry(**data)
                    self.entries.append(entry)

            logger.info(f"Loaded {len(self.entries)} entries")

            # Verify chain integrity
            if not self.verify_chain():
                logger.error("Audit trail chain verification FAILED!")
                raise ValueError("Audit trail has been tampered with!")

        except Exception as e:
            logger.error(f"Failed to load audit trail: {e}")
            raise

    def add_entry(
        self,
        event_type: str,
        actor: str,
        action: str,
        resource: str,
        result: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        Add new entry to audit trail

        Args:
            event_type: Category (e.g., "compliance_check", "calculation", "bim_upload")
            actor: Who performed action (user_id, system_name)
            action: What was done (e.g., "uwert_calculation", "oib_rl_check")
            resource: What was affected (project_id, file_name, etc.)
            result: "success" or "failure"
            details: Additional context data

        Returns:
            Created audit entry
        """
        details = details or {}

        # Get previous hash (or genesis hash for first entry)
        previous_hash = self.entries[-1].entry_hash if self.entries else "0" * 64

        # Create new entry
        entry = AuditEntry.create(
            event_type=event_type,
            actor=actor,
            action=action,
            resource=resource,
            result=result,
            details=details,
            previous_hash=previous_hash,
        )

        # Add to chain
        self.entries.append(entry)

        # Persist to disk
        self._persist_entry(entry)

        logger.info(f"Audit entry added: {event_type}/{action} by {actor} → {result}")

        return entry

    def _persist_entry(self, entry: AuditEntry):
        """Append entry to storage (JSONL format for append-only)"""
        try:
            with open(self.storage_path, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except Exception as e:
            logger.error(f"Failed to persist audit entry: {e}")
            # Don't raise - entry is still in memory

    def verify_chain(self) -> bool:
        """
        Verify complete audit trail integrity

        Returns:
            True if chain is valid, False if tampered
        """
        if not self.entries:
            return True  # Empty chain is valid

        # First entry should have genesis hash
        if self.entries[0].previous_hash != "0" * 64:
            logger.error("First entry doesn't have genesis hash")
            return False

        # Verify each entry
        for i, entry in enumerate(self.entries):
            # Verify entry's own hash
            if not entry.verify():
                logger.error(f"Entry {i} hash verification failed")
                return False

            # Verify linkage to previous entry
            if i > 0:
                expected_prev = self.entries[i - 1].entry_hash
                if entry.previous_hash != expected_prev:
                    logger.error(f"Entry {i} chain linkage broken")
                    return False

        logger.info(f"Audit trail verified: {len(self.entries)} entries valid")
        return True

    def get_entries_by_type(self, event_type: str) -> List[AuditEntry]:
        """Get all entries of specific type"""
        return [e for e in self.entries if e.event_type == event_type]

    def get_entries_by_actor(self, actor: str) -> List[AuditEntry]:
        """Get all entries by specific actor"""
        return [e for e in self.entries if e.actor == actor]

    def get_entries_by_resource(self, resource: str) -> List[AuditEntry]:
        """Get all entries for specific resource"""
        return [e for e in self.entries if e.resource == resource]

    def get_entries_in_timerange(self, start: datetime, end: datetime) -> List[AuditEntry]:
        """Get entries within time range"""
        return [e for e in self.entries if start.isoformat() <= e.timestamp <= end.isoformat()]

    def export_report(self, output_path: Path, format: str = "json"):
        """
        Export audit trail as report

        Args:
            output_path: Where to save report
            format: "json", "csv", or "pdf"
        """
        if format == "json":
            with open(output_path, "w") as f:
                json.dump(
                    {
                        "trail_name": self.name,
                        "total_entries": len(self.entries),
                        "chain_verified": self.verify_chain(),
                        "entries": [e.to_dict() for e in self.entries],
                    },
                    f,
                    indent=2,
                )
        elif format == "csv":
            import csv

            with open(output_path, "w", newline="") as f:
                if not self.entries:
                    return

                writer = csv.DictWriter(f, fieldnames=self.entries[0].to_dict().keys())
                writer.writeheader()
                for entry in self.entries:
                    row = entry.to_dict()
                    row["details"] = json.dumps(row["details"])  # Flatten details
                    writer.writerow(row)
        else:
            raise ValueError(f"Unsupported format: {format}")

        logger.info(f"Audit report exported to {output_path}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get audit trail statistics"""
        if not self.entries:
            return {
                "total_entries": 0,
                "chain_valid": True,
                "event_types": {},
                "actors": {},
                "success_rate": 0.0,
            }

        event_types = {}
        actors = {}
        success_count = 0

        for entry in self.entries:
            event_types[entry.event_type] = event_types.get(entry.event_type, 0) + 1
            actors[entry.actor] = actors.get(entry.actor, 0) + 1
            if entry.result == "success":
                success_count += 1

        return {
            "total_entries": len(self.entries),
            "chain_valid": self.verify_chain(),
            "event_types": event_types,
            "actors": actors,
            "success_rate": success_count / len(self.entries) * 100,
            "first_entry": self.entries[0].timestamp if self.entries else None,
            "last_entry": self.entries[-1].timestamp if self.entries else None,
        }


# =============================================================================
# CONVENIENCE FUNCTIONS FOR ORION API
# =============================================================================


def create_compliance_trail(project_id: str) -> AuditTrail:
    """Create audit trail for compliance checks"""
    return AuditTrail(
        name=f"compliance_{project_id}",
        storage_path=Path(f"./audit_trails/compliance/{project_id}.jsonl"),
    )


def create_calculation_trail(project_id: str) -> AuditTrail:
    """Create audit trail for calculations"""
    return AuditTrail(
        name=f"calculations_{project_id}",
        storage_path=Path(f"./audit_trails/calculations/{project_id}.jsonl"),
    )


def create_bim_trail(project_id: str) -> AuditTrail:
    """Create audit trail for BIM operations"""
    return AuditTrail(
        name=f"bim_{project_id}",
        storage_path=Path(f"./audit_trails/bim/{project_id}.jsonl"),
    )


# Example usage
if __name__ == "__main__":
    # Demo: Create audit trail for compliance checks
    trail = create_compliance_trail("PROJ_2026_001")

    # Add compliance check entry
    trail.add_entry(
        event_type="compliance_check",
        actor="user_arch_001",
        action="oib_rl_6_check",
        resource="building_energy_analysis",
        result="success",
        details={
            "uwert_exterior_wall": 0.16,
            "uwert_roof": 0.11,
            "uwert_windows": 0.70,
            "energy_class": "A+",
            "compliant": True,
        },
    )

    # Add calculation entry
    trail.add_entry(
        event_type="calculation",
        actor="system_api",
        action="uwert_calculation",
        resource="wall_construction_01",
        result="success",
        details={
            "layers": ["brick_250mm", "eps_200mm", "plaster_15mm"],
            "uwert_result": 0.16,
            "standard": "ÖNORM EN ISO 6946",
        },
    )

    # Verify chain
    print(f"Chain valid: {trail.verify_chain()}")

    # Get statistics
    stats = trail.get_statistics()
    print(f"Statistics: {json.dumps(stats, indent=2)}")

    # Export report
    trail.export_report(Path("./audit_report.json"), format="json")
