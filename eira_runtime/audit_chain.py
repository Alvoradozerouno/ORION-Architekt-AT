"""
Audit Chain fuer Baumeister-Tool-Austria
SHA-256 verkettete Audit-Trail fuer alle Bau-Berechnungen.

Jede Berechnung wird in einer unveraenderlichen Kette gespeichert.
Manipulationen werden sofort erkannt (Hash-Kette bricht).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
import hashlib
import json
import os


@dataclass
class AuditEntry:
    """Ein einzelner Eintrag in der Audit-Kette."""
    entry_id: str
    timestamp: datetime
    calculation_type: str
    input_hash: str
    output_hash: str
    epistemic_state: str
    result_summary: str
    previous_hash: str = ""
    entry_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Berechne Hash fuer diesen Eintrag."""
        if not self.entry_hash:
            data = (
                f"{self.entry_id}:{self.timestamp.isoformat()}:"
                f"{self.calculation_type}:{self.input_hash}:{self.output_hash}:"
                f"{self.epistemic_state}:{self.previous_hash}"
            )
            self.entry_hash = hashlib.sha256(data.encode()).hexdigest()

    def to_dict(self) -> Dict:
        return {
            "entry_id": self.entry_id,
            "timestamp": self.timestamp.isoformat(),
            "calculation_type": self.calculation_type,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "epistemic_state": self.epistemic_state,
            "result_summary": self.result_summary,
            "previous_hash": self.previous_hash,
            "entry_hash": self.entry_hash,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AuditEntry":
        return cls(
            entry_id=data["entry_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            calculation_type=data["calculation_type"],
            input_hash=data["input_hash"],
            output_hash=data["output_hash"],
            epistemic_state=data["epistemic_state"],
            result_summary=data["result_summary"],
            previous_hash=data.get("previous_hash", ""),
            entry_hash=data.get("entry_hash", ""),
            metadata=data.get("metadata", {}),
        )


class AuditChain:
    """
    SHA-256 verkettete Audit-Kette fuer Bau-Berechnungen.

    Properties:
    - Unveraenderlich: Jeder Eintrag enthaelt Hash des vorherigen
    - Verifizierbar: Kette kann jederzeit geprueft werden
    - Persistent: Kann auf Festplatte gespeichert werden
    """

    GENESIS_HASH = "0" * 64  # Genesis-Hash fuer ersten Eintrag

    def __init__(self, storage_path: Optional[str] = None):
        self._chain: List[AuditEntry] = []
        self._storage_path = storage_path

        # Bestehende Kette laden wenn vorhanden
        if storage_path and os.path.exists(storage_path):
            self._load_from_file(storage_path)

    @property
    def length(self) -> int:
        return len(self._chain)

    @property
    def last_hash(self) -> str:
        if not self._chain:
            return self.GENESIS_HASH
        return self._chain[-1].entry_hash

    def add_entry(
        self,
        entry_id: str,
        calculation_type: str,
        input_hash: str,
        output_hash: str,
        epistemic_state: str,
        result_summary: str,
        metadata: Optional[Dict] = None,
    ) -> AuditEntry:
        """Fuegt einen neuen Eintrag zur Kette hinzu."""
        entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.utcnow(),
            calculation_type=calculation_type,
            input_hash=input_hash,
            output_hash=output_hash,
            epistemic_state=epistemic_state,
            result_summary=result_summary,
            previous_hash=self.last_hash,
            metadata=metadata or {},
        )
        self._chain.append(entry)

        # Optional: Auf Festplatte speichern
        if self._storage_path:
            self._save_to_file(self._storage_path)

        return entry

    def verify_chain(self) -> tuple:
        """
        Verifiziert die Integritaet der gesamten Kette.

        Returns: (is_valid, first_broken_index)
        """
        if not self._chain:
            return True, -1

        # Genesis-Entry pruefen
        if self._chain[0].previous_hash != self.GENESIS_HASH:
            return False, 0

        for i in range(1, len(self._chain)):
            if self._chain[i].previous_hash != self._chain[i-1].entry_hash:
                return False, i

            # Hash des Eintrags selbst pruefen
            entry = self._chain[i]
            data = (
                f"{entry.entry_id}:{entry.timestamp.isoformat()}:"
                f"{entry.calculation_type}:{entry.input_hash}:{entry.output_hash}:"
                f"{entry.epistemic_state}:{entry.previous_hash}"
            )
            expected_hash = hashlib.sha256(data.encode()).hexdigest()
            if entry.entry_hash != expected_hash:
                return False, i

        return True, -1

    def get_entries(self) -> List[AuditEntry]:
        return self._chain.copy()

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        for entry in self._chain:
            if entry.entry_id == entry_id:
                return entry
        return None

    def _save_to_file(self, path: str):
        """Speichert die Kette auf Festplatte."""
        data = [entry.to_dict() for entry in self._chain]
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def _load_from_file(self, path: str):
        """Laedt die Kette von Festplatte."""
        try:
            with open(path, "r") as f:
                data = json.load(f)
            self._chain = [AuditEntry.from_dict(d) for d in data]
        except (json.JSONDecodeError, KeyError):
            self._chain = []

    def get_statistics(self) -> Dict:
        """Gibt Statistiken ueber die Audit-Kette zurueck."""
        states = {}
        for entry in self._chain:
            states[entry.epistemic_state] = states.get(entry.epistemic_state, 0) + 1

        is_valid, broken_at = self.verify_chain()

        return {
            "total_entries": len(self._chain),
            "by_state": states,
            "chain_valid": is_valid,
            "broken_at_index": broken_at,
        }