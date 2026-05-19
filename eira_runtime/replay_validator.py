"""
Replay Validator fuer Baumeister-Tool-Austria
Deterministische Reproduzierbarkeit von Bau-Berechnungen.

Jede Berechnung kann exakt reproduziert werden mit:
- Gleichem Input
- Gleichem Code
- Gleichem epistemischen State
"""

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from .epistemic_states import EpistemicState
from .deterministic_executor import ExecutionResult


@dataclass
class ReplayRecord:
    """Aufzeichnung einer Berechnung fuer Replay."""
    calculation_id: str
    calculation_type: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    expected_state: str
    expected_hash: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    replay_count: int = 0
    last_replay: Optional[datetime] = None
    replay_success: bool = True

    def to_dict(self) -> Dict:
        return {
            "calculation_id": self.calculation_id,
            "calculation_type": self.calculation_type,
            "input_data": self.input_data,
            "expected_output": self.expected_output,
            "expected_state": self.expected_state,
            "expected_hash": self.expected_hash,
            "timestamp": self.timestamp.isoformat(),
            "replay_count": self.replay_count,
            "last_replay": self.last_replay.isoformat() if self.last_replay else None,
            "replay_success": self.replay_success,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "ReplayRecord":
        return cls(
            calculation_id=data["calculation_id"],
            calculation_type=data["calculation_type"],
            input_data=data["input_data"],
            expected_output=data["expected_output"],
            expected_state=data["expected_state"],
            expected_hash=data["expected_hash"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            replay_count=data.get("replay_count", 0),
            last_replay=datetime.fromisoformat(data["last_replay"]) if data.get("last_replay") else None,
            replay_success=data.get("replay_success", True),
        )


@dataclass
class ReplayResult:
    """Ergebnis eines Replay-Vergleichs."""
    calculation_id: str
    matches: bool
    input_match: bool
    output_match: bool
    state_match: bool
    hash_match: bool
    replay_time_ms: float
    differences: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "calculation_id": self.calculation_id,
            "matches": self.matches,
            "input_match": self.input_match,
            "output_match": self.output_match,
            "state_match": self.state_match,
            "hash_match": self.hash_match,
            "replay_time_ms": self.replay_time_ms,
            "differences": self.differences,
        }


class ReplayValidator:
    """
    Validiert deterministische Reproduzierbarkeit von Bau-Berechnungen.

    Verwendung:
    1. record() - Berechnung aufzeichnen
    2. replay() - Berechnung reproduzieren und vergleichen
    3. verify_all() - Alle aufgezeichneten Berechnungen validieren
    """

    def __init__(self):
        self._records: Dict[str, ReplayRecord] = {}
        self._replay_log: List[ReplayResult] = []

    def record(self, result: ExecutionResult, input_data: Dict[str, Any]):
        """Zeichnet eine Berechnung fuer Replay auf."""
        record = ReplayRecord(
            calculation_id=result.calculation_id,
            calculation_type=result.calculation_type,
            input_data=input_data,
            expected_output=result.result or {},
            expected_state=result.epistemic_state.value,
            expected_hash=result.output_hash,
        )
        self._records[result.calculation_id] = record

    def replay(
        self,
        calculation_id: str,
        execute_func: Callable[[Dict[str, Any]], ExecutionResult]
    ) -> Optional[ReplayResult]:
        """
        Reproduziert eine aufgezeichnete Berechnung.

        Args:
            calculation_id: ID der aufzuzeichnenden Berechnung
            execute_func: Funktion die die Berechnung ausfuehrt

        Returns:
            ReplayResult oder None wenn nicht gefunden
        """
        if calculation_id not in self._records:
            return None

        record = self._records[calculation_id]
        import time
        start_time = time.monotonic()

        # Berechnung reproduzieren
        replay_result = execute_func(record.input_data)
        replay_time_ms = (time.monotonic() - start_time) * 1000

        # Vergleiche
        differences = []
        input_match = True  # Input ist per Definition gleich
        output_match = self._compare_outputs(record.expected_output, replay_result.result or {}, differences)
        state_match = record.expected_state == replay_result.epistemic_state.value
        hash_match = record.expected_hash == replay_result.output_hash

        matches = output_match and state_match and hash_match

        result = ReplayResult(
            calculation_id=calculation_id,
            matches=matches,
            input_match=input_match,
            output_match=output_match,
            state_match=state_match,
            hash_match=hash_match,
            replay_time_ms=replay_time_ms,
            differences=differences,
        )

        # Record aktualisieren
        record.replay_count += 1
        record.last_replay = datetime.utcnow()
        record.replay_success = matches

        self._replay_log.append(result)
        return result

    def verify_all(
        self,
        execute_func: Callable[[str, Dict[str, Any]], ExecutionResult]
    ) -> List[ReplayResult]:
        """
        Validiert alle aufgezeichneten Berechnungen.

        Args:
            execute_func: Funktion(calculation_type, input_data) -> ExecutionResult

        Returns:
            Liste aller Replay-Ergebnisse
        """
        results = []
        for calc_id in list(self._records.keys()):
            record = self._records[calc_id]

            def wrapper(input_data):
                return execute_func(record.calculation_type, input_data)

            result = self.replay(calc_id, wrapper)
            if result:
                results.append(result)

        return results

    def get_statistics(self) -> Dict:
        """Gibt Statistiken ueber Replay-Validierungen zurueck."""
        if not self._replay_log:
            return {
                "total_records": len(self._records),
                "total_replays": 0,
                "success_rate": 0.0,
            }

        success_count = sum(1 for r in self._replay_log if r.matches)
        total = len(self._replay_log)

        return {
            "total_records": len(self._records),
            "total_replays": total,
            "success_count": success_count,
            "failure_count": total - success_count,
            "success_rate": success_count / total if total > 0 else 0.0,
            "avg_replay_time_ms": sum(r.replay_time_ms for r in self._replay_log) / total,
        }

    def _compare_outputs(self, expected: Dict, actual: Dict, differences: List[str]) -> bool:
        """Vergleicht zwei Output-Dicts."""
        if set(expected.keys()) != set(actual.keys()):
            differences.append(f"Keys differ: {set(expected.keys())} vs {set(actual.keys())}")
            return False

        all_match = True
        for key in expected:
            exp_val = expected[key]
            act_val = actual[key]

            if isinstance(exp_val, float) and isinstance(act_val, float):
                if abs(exp_val - act_val) > 1e-10:
                    differences.append(f"{key}: {exp_val} != {act_val}")
                    all_match = False
            elif exp_val != act_val:
                differences.append(f"{key}: {exp_val} != {act_val}")
                all_match = False

        return all_match