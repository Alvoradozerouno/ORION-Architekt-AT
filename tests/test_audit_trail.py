"""
ORION Safety Core - Test Suite for Audit Trail

Tests the cryptographic audit trail system adapted from GENESIS DUAL-SYSTEM.

Run with: pytest api/safety/tests/test_audit_trail.py -v
"""

import pytest
import json
import hashlib
from pathlib import Path
from datetime import datetime
from api.safety.audit_trail import (
    AuditEntry,
    AuditTrail,
    create_compliance_trail,
    create_calculation_trail,
    create_bim_trail,
)


class TestAuditEntry:
    """Test individual audit entry functionality"""

    def test_create_entry(self):
        """Test creating an audit entry"""
        entry = AuditEntry.create(
            event_type="test_event",
            actor="test_user",
            action="test_action",
            resource="test_resource",
            result="success",
            details={"key": "value"},
        )

        assert entry.event_type == "test_event"
        assert entry.actor == "test_user"
        assert entry.result == "success"
        assert entry.details["key"] == "value"
        assert len(entry.entry_hash) == 64  # SHA-256 hash
        assert entry.previous_hash == "0" * 64  # Genesis hash

    def test_entry_verification(self):
        """Test that entry hash verification works"""
        entry = AuditEntry.create(
            event_type="test",
            actor="user",
            action="action",
            resource="resource",
            result="success",
            details={},
        )

        # Should verify correctly
        assert entry.verify() is True

        # Tampering should break verification
        entry.details["tampered"] = "data"
        assert entry.verify() is False

    def test_entry_hash_calculation(self):
        """Test hash calculation is deterministic"""
        # Use same timestamp for both entries to ensure identical hashes
        fixed_timestamp = "2026-04-07T12:00:00.000000Z"

        entry1 = AuditEntry.create(
            event_type="test",
            actor="user",
            action="action",
            resource="res",
            result="success",
            details={"a": 1, "b": 2},
            timestamp=fixed_timestamp,
        )

        entry2 = AuditEntry.create(
            event_type="test",
            actor="user",
            action="action",
            resource="res",
            result="success",
            details={"b": 2, "a": 1},  # Different order
            timestamp=fixed_timestamp,
        )

        # Should produce same hash (JSON sorted)
        assert entry1.entry_hash == entry2.entry_hash


class TestAuditTrail:
    """Test audit trail chain functionality"""

    def test_create_trail(self, tmp_path):
        """Test creating a new audit trail"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        assert trail.name == "test_trail"
        assert len(trail.entries) == 0
        assert trail.verify_chain() is True  # Empty chain is valid

    def test_add_entry(self, tmp_path):
        """Test adding entries to trail"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        entry = trail.add_entry(
            event_type="compliance_check",
            actor="user1",
            action="oib_rl_check",
            resource="project1",
            result="success",
            details={"compliant": True},
        )

        assert len(trail.entries) == 1
        assert entry.previous_hash == "0" * 64  # First entry

    def test_chain_linkage(self, tmp_path):
        """Test that entries are correctly linked"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        entry1 = trail.add_entry("event1", "user1", "action1", "res1", "success", {})
        entry2 = trail.add_entry("event2", "user2", "action2", "res2", "success", {})
        entry3 = trail.add_entry("event3", "user3", "action3", "res3", "success", {})

        # Check linkage
        assert entry2.previous_hash == entry1.entry_hash
        assert entry3.previous_hash == entry2.entry_hash

        # Chain should be valid
        assert trail.verify_chain() is True

    def test_chain_tampering_detection(self, tmp_path):
        """Test that tampering is detected"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        trail.add_entry("e1", "u1", "a1", "r1", "success", {})
        trail.add_entry("e2", "u2", "a2", "r2", "success", {})
        trail.add_entry("e3", "u3", "a3", "r3", "success", {})

        # Tamper with middle entry
        trail.entries[1].details["tampered"] = "data"

        # Chain should be invalid
        assert trail.verify_chain() is False

    def test_persistence(self, tmp_path):
        """Test that trail persists to disk"""
        storage_path = tmp_path / "test.jsonl"
        trail = AuditTrail("test_trail", storage_path=storage_path)

        trail.add_entry("e1", "u1", "a1", "r1", "success", {"data": 1})
        trail.add_entry("e2", "u2", "a2", "r2", "success", {"data": 2})

        # File should exist
        assert storage_path.exists()

        # Load in new trail instance
        trail2 = AuditTrail("test_trail", storage_path=storage_path)

        assert len(trail2.entries) == 2
        assert trail2.verify_chain() is True
        assert trail2.entries[0].details["data"] == 1
        assert trail2.entries[1].details["data"] == 2

    def test_get_entries_by_type(self, tmp_path):
        """Test filtering by event type"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        trail.add_entry("compliance", "u1", "a1", "r1", "success", {})
        trail.add_entry("calculation", "u2", "a2", "r2", "success", {})
        trail.add_entry("compliance", "u3", "a3", "r3", "success", {})

        compliance_entries = trail.get_entries_by_type("compliance")
        assert len(compliance_entries) == 2

        calculation_entries = trail.get_entries_by_type("calculation")
        assert len(calculation_entries) == 1

    def test_get_entries_by_actor(self, tmp_path):
        """Test filtering by actor"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        trail.add_entry("e1", "user_arch", "a1", "r1", "success", {})
        trail.add_entry("e2", "user_eng", "a2", "r2", "success", {})
        trail.add_entry("e3", "user_arch", "a3", "r3", "success", {})

        arch_entries = trail.get_entries_by_actor("user_arch")
        assert len(arch_entries) == 2

        eng_entries = trail.get_entries_by_actor("user_eng")
        assert len(eng_entries) == 1

    def test_export_json(self, tmp_path):
        """Test JSON export"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        trail.add_entry("e1", "u1", "a1", "r1", "success", {})
        trail.add_entry("e2", "u2", "a2", "r2", "success", {})

        export_path = tmp_path / "export.json"
        trail.export_report(export_path, format="json")

        assert export_path.exists()

        with open(export_path) as f:
            data = json.load(f)

        assert data["trail_name"] == "test_trail"
        assert data["total_entries"] == 2
        assert data["chain_verified"] is True
        assert len(data["entries"]) == 2

    def test_export_csv(self, tmp_path):
        """Test CSV export"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        trail.add_entry("e1", "u1", "a1", "r1", "success", {"k": "v"})

        export_path = tmp_path / "export.csv"
        trail.export_report(export_path, format="csv")

        assert export_path.exists()

        with open(export_path) as f:
            content = f.read()

        assert "timestamp" in content
        assert "event_type" in content
        assert "actor" in content

    def test_statistics(self, tmp_path):
        """Test statistics generation"""
        trail = AuditTrail("test_trail", storage_path=tmp_path / "test.jsonl")

        trail.add_entry("compliance", "user1", "a1", "r1", "success", {})
        trail.add_entry("compliance", "user1", "a2", "r2", "failure", {})
        trail.add_entry("calculation", "user2", "a3", "r3", "success", {})

        stats = trail.get_statistics()

        assert stats["total_entries"] == 3
        assert stats["chain_valid"] is True
        assert stats["event_types"]["compliance"] == 2
        assert stats["event_types"]["calculation"] == 1
        assert stats["actors"]["user1"] == 2
        assert stats["actors"]["user2"] == 1
        assert stats["success_rate"] == pytest.approx(66.67, rel=0.1)


class TestConvenienceFunctions:
    """Test convenience functions"""

    def test_create_compliance_trail(self, tmp_path, monkeypatch):
        """Test compliance trail creation"""
        monkeypatch.chdir(tmp_path)

        trail = create_compliance_trail("PROJ001")

        assert "compliance_PROJ001" in trail.name
        assert trail.storage_path.parent.name == "compliance"

    def test_create_calculation_trail(self, tmp_path, monkeypatch):
        """Test calculation trail creation"""
        monkeypatch.chdir(tmp_path)

        trail = create_calculation_trail("PROJ002")

        assert "calculations_PROJ002" in trail.name
        assert trail.storage_path.parent.name == "calculations"

    def test_create_bim_trail(self, tmp_path, monkeypatch):
        """Test BIM trail creation"""
        monkeypatch.chdir(tmp_path)

        trail = create_bim_trail("PROJ003")

        assert "bim_PROJ003" in trail.name
        assert trail.storage_path.parent.name == "bim"


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""

    def test_compliance_workflow(self, tmp_path, monkeypatch):
        """Test complete compliance check workflow"""
        monkeypatch.chdir(tmp_path)

        # Create trail for project
        trail = create_compliance_trail("HOCHHAUS_WIEN_2026")

        # Architect checks OIB-RL 6
        trail.add_entry(
            event_type="compliance_check",
            actor="arch_mueller",
            action="oib_rl_6_energy",
            resource="building_energy_model",
            result="success",
            details={
                "uwert_wall": 0.16,
                "uwert_roof": 0.11,
                "energy_class": "A+",
                "compliant": True,
            },
        )

        # Engineer checks structure
        trail.add_entry(
            event_type="structural_check",
            actor="ing_schmidt",
            action="load_bearing_analysis",
            resource="structure_model",
            result="success",
            details={"safety_factor": 1.5, "eurocode_compliant": True},
        )

        # Authority approves
        trail.add_entry(
            event_type="official_approval",
            actor="magistrat_wien",
            action="building_permit_grant",
            resource="permit_2026_1234",
            result="success",
            details={"permit_valid_until": "2027-04-06"},
        )

        # Verify complete chain
        assert trail.verify_chain() is True
        assert len(trail.entries) == 3

        # Check statistics
        stats = trail.get_statistics()
        assert stats["success_rate"] == 100.0
        assert len(stats["actors"]) == 3

        # Export for authorities
        export_path = tmp_path / "bauabnahme.json"
        trail.export_report(export_path)
        assert export_path.exists()
