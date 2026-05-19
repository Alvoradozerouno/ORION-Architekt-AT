"""
Deterministic Executor fuer Baumeister-Tool-Austria
Deterministische Ausfuehrung von Bau-Berechnungen mit epistemischen States.

Jede Berechnung wird deterministisch ausgefueht mit:
- Gleicher Input = Gleicher Output (immer)
- Epistemischer State fuer jede Entscheidung
- SHA-256 Hash fuer Integritaet
- ABSTAIN bei Unsicherheit (Safety-First)
"""

from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import time
from .epistemic_states import EpistemicState, EpistemicDecision, StateTransition


@dataclass
class ExecutionResult:
    """Ergebnis einer deterministischen Ausfuehrung."""
    calculation_id: str
    calculation_type: str
    result: Optional[Dict[str, Any]]
    epistemic_state: EpistemicState
    confidence: float
    execution_time_ms: float
    input_hash: str
    output_hash: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    error: Optional[str] = None

    @property
    def is_verified(self) -> bool:
        return self.epistemic_state == EpistemicState.VERIFIED

    @property
    def requires_human(self) -> bool:
        return self.epistemic_state.requires_human

    def to_dict(self) -> Dict:
        return {
            "calculation_id": self.calculation_id,
            "calculation_type": self.calculation_type,
            "result": self.result,
            "epistemic_state": self.epistemic_state.value,
            "confidence": self.confidence,
            "execution_time_ms": self.execution_time_ms,
            "input_hash": self.input_hash,
            "output_hash": self.output_hash,
            "timestamp": self.timestamp.isoformat(),
            "error": self.error,
            "is_verified": self.is_verified,
            "requires_human": self.requires_human,
        }


class DeterministicExecutor:
    """
    Deterministischer Executor fuer Bau-Berechnungen.

    Garantiert:
    - Gleicher Input => Gleicher Output (deterministisch)
    - Keine versteckten Seiteneffekte
    - Epistemische States fuer jede Entscheidung
    - ABSTAIN bei Unsicherheit
    """

    def __init__(self):
        self._registered_calculations: Dict[str, Callable] = {}
        self._execution_log: List[ExecutionResult] = []
        self._execution_count = 0

    def register_calculation(self, name: str, func: Callable):
        """Registriert eine Berechnungsfunktion."""
        self._registered_calculations[name] = func

    def _compute_hash(self, data: Any) -> str:
        """Berechnet SHA-256 Hash fuer Daten."""
        if isinstance(data, (dict, list)):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _assess_epistemic_state(
        self,
        calculation_type: str,
        result: Optional[Dict],
        input_data: Dict,
        execution_time_ms: float
    ) -> tuple:
        """
        Bestimmt den epistemischen State einer Berechnung.

        Returns: (EpistemicState, confidence)
        """
        # Keine Daten => UNKNOWN
        if result is None:
            return EpistemicState.UNKNOWN, 0.0

        # Fehler => ABSTAIN
        if "error" in result:
            return EpistemicState.ABSTAIN, 0.0

        # Kritische Berechnungen mit fehlenden Parametern => ABSTAIN
        critical_calculations = ["schneelast", "windlast", "erdbeben", "tragwerk"]
        if calculation_type in critical_calculations:
            required_params = {
                "schneelast": ["standort", "hoehe"],
                "windlast": ["standort", "hoehe", "gelaende"],
                "erdbeben": ["standort", "bodenklasse"],
                "tragwerk": ["material", "geometrie"],
            }
            missing = [p for p in required_params.get(calculation_type, []) if p not in input_data]
            if missing:
                return EpistemicState.ABSTAIN, 0.0

        # Grenzwert-Checks => INSTABIL
        if "value" in result:
            value = result.get("value", 0)
            limit = result.get("limit", float("inf"))
            if limit != float("inf") and value > limit * 0.9:
                return EpistemicState.INSTABIL, 0.7

        # Alles OK => VERIFIED
        return EpistemicState.VERIFIED, 0.95

    def execute(
        self,
        calculation_type: str,
        input_data: Dict[str, Any],
        calculation_id: Optional[str] = None
    ) -> ExecutionResult:
        """
        Fuehrt eine Berechnung deterministisch aus.

        Args:
            calculation_type: Typ der Berechnung (z.B. "schneelast")
            input_data: Eingabedaten fuer die Berechnung
            calculation_id: Optionale ID (wird generiert wenn None)

        Returns:
            ExecutionResult mit epistemischem State
        """
        start_time = time.monotonic()
        self._execution_count += 1

        if calculation_id is None:
            calculation_id = f"calc_{self._execution_count:06d}"

        # Input-Hash fuer Reproduzierbarkeit
        input_hash = self._compute_hash(input_data)

        # Berechnung ausfuehren
        result = None
        error = None

        if calculation_type in self._registered_calculations:
            try:
                func = self._registered_calculations[calculation_type]
                result = func(input_data)
            except Exception as e:
                error = str(e)
                result = {"error": error}
        else:
            error = f"Unbekannte Berechnung: {calculation_type}"
            result = {"error": error}

        execution_time_ms = (time.monotonic() - start_time) * 1000

        # Epistemischen State bestimmen
        epistemic_state, confidence = self._assess_epistemic_state(
            calculation_type, result, input_data, execution_time_ms
        )

        # Output-Hash
        output_hash = self._compute_hash(result)

        # Ergebnis erstellen
        exec_result = ExecutionResult(
            calculation_id=calculation_id,
            calculation_type=calculation_type,
            result=result,
            epistemic_state=epistemic_state,
            confidence=confidence,
            execution_time_ms=execution_time_ms,
            input_hash=input_hash,
            output_hash=output_hash,
            error=error,
        )

        # Loggen
        self._execution_log.append(exec_result)

        return exec_result

    def get_execution_log(self) -> List[ExecutionResult]:
        """Gibt das Ausfuehrungs-Log zurueck."""
        return self._execution_log.copy()

    def get_statistics(self) -> Dict:
        """Gibt Statistiken ueber Ausfuehrungen zurueck."""
        if not self._execution_log:
            return {"total": 0}

        states = {}
        for r in self._execution_log:
            states[r.epistemic_state.value] = states.get(r.epistemic_state.value, 0) + 1

        return {
            "total": len(self._execution_log),
            "by_state": states,
            "avg_execution_time_ms": sum(r.execution_time_ms for r in self._execution_log) / len(self._execution_log),
            "verified_count": states.get("VERIFIED", 0),
            "abstain_count": states.get("ABSTAIN", 0),
        }