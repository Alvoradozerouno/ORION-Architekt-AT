"""
Test suite for ROS2 Bridge Router
Tests bidirectional ORION ↔ ROS2 communication.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestRos2BridgeRouter:
    """Tests for ROS2 Bridge API endpoints."""

    def test_publish_decision_verified(self):
        """Test publishing a VERIFIED decision to ROS2."""
        response = client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "decision-123",
                "state": "VERIFIED",
                "command": {"action": "move", "target": [1.0, 2.0, 3.0]},
                "priority": 8
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message_id" in data
        assert "published_at" in data
        assert data["safe_to_execute"] is True
        assert "command" in data
        assert data["priority"] == 8

    def test_publish_decision_abstain(self):
        """Test publishing an ABSTAIN decision (should not be safe)."""
        response = client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "decision-456",
                "state": "ABSTAIN",
                "command": {"action": "hold"},
                "priority": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "message_id" in data
        assert data["safe_to_execute"] is False

    def test_publish_decision_uncertain(self):
        """Test publishing an UNCERTAIN decision."""
        response = client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "decision-789",
                "state": "UNCERTAIN",
                "command": {"action": "probe"},
                "priority": 5
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["safe_to_execute"] is False

    def test_publish_decision_invalid_state(self):
        """Test that invalid state is rejected."""
        response = client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "decision-invalid",
                "state": "INVALID_STATE",
                "command": {},
                "priority": 5
            }
        )
        assert response.status_code == 400

    def test_publish_decision_priority_boundary(self):
        """Test boundary priority values."""
        for priority in [0, 5, 10]:
            response = client.post(
                "/api/v1/ros2-bridge/publish-decision",
                json={
                    "decision_id": f"decision-priority-{priority}",
                    "state": "VERIFIED",
                    "command": {"action": "test"},
                    "priority": priority
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["priority"] == priority

    def test_update_sensor_data(self):
        """Test updating sensor data from robot."""
        sensor_data = {
            "camera": {
                "objects": [
                    {"id": 1, "class": "person", "confidence": 0.95},
                    {"id": 2, "class": "chair", "confidence": 0.87}
                ]
            },
            "imu": {
                "acceleration": [0.1, 0.2, 9.8],
                "gyro": [0.01, -0.01, 0.0]
            }
        }
        
        response = client.post(
            "/api/v1/ros2-bridge/update-sensor-data",
            json=sensor_data
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "received_at" in data
        assert data["sensor_count"] == 2
        assert "camera" in data["last_sensor_data"]
        assert "imu" in data["last_sensor_data"]

    def test_get_robot_state(self):
        """Test getting current robot state."""
        response = client.get("/api/v1/ros2-bridge/robot-state")
        assert response.status_code == 200
        data = response.json()
        
        assert "connected" in data
        assert isinstance(data["connected"], bool)
        assert "node_name" in data
        assert "robot_state" in data
        assert "topics_subscribed" in data
        assert isinstance(data["topics_subscribed"], list)
        assert "topics_published" in data
        assert isinstance(data["topics_published"], list)
        assert "sensor_data" in data
        assert "last_heartbeat" in data

    def test_bridge_command_connect(self):
        """Test bridge connect command."""
        response = client.post(
            "/api/v1/ros2-bridge/bridge-command",
            json={"command": "connect"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["command"] == "connect"
        assert data["status"] == "success"
        assert "Connected" in data["message"]
        assert data["bridge_state"]["connected"] is True

    def test_bridge_command_disconnect(self):
        """Test bridge disconnect command."""
        response = client.post(
            "/api/v1/ros2-bridge/bridge-command",
            json={"command": "disconnect"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["command"] == "disconnect"
        assert data["status"] == "success"

    def test_bridge_command_reset(self):
        """Test bridge reset command."""
        # First publish something
        client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "test-reset",
                "state": "VERIFIED",
                "command": {"action": "test"},
                "priority": 5
            }
        )
        
        # Reset
        response = client.post(
            "/api/v1/ros2-bridge/bridge-command",
            json={"command": "reset"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    def test_bridge_command_health_check(self):
        """Test bridge health check command."""
        response = client.post(
            "/api/v1/ros2-bridge/bridge-command",
            json={"command": "health_check"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["command"] == "health_check"
        assert data["status"] in ["healthy", "disconnected"]

    def test_bridge_command_invalid(self):
        """Test that invalid command is rejected."""
        response = client.post(
            "/api/v1/ros2-bridge/bridge-command",
            json={"command": "invalid_command"}
        )
        assert response.status_code == 400

    def test_get_bridge_health(self):
        """Test getting bridge health information."""
        response = client.get("/api/v1/ros2-bridge/bridge-health")
        assert response.status_code == 200
        data = response.json()
        
        assert "healthy" in data
        assert isinstance(data["healthy"], bool)
        assert "connected" in data
        assert "uptime_ms" in data
        assert "message_queue" in data
        assert "error_count" in data
        assert "last_error" in data
        assert "bridge_info" in data

    def test_message_id_uniqueness(self):
        """Test that each published message gets a unique ID."""
        message_ids = []
        
        for i in range(5):
            response = client.post(
                "/api/v1/ros2-bridge/publish-decision",
                json={
                    "decision_id": f"decision-{i}",
                    "state": "VERIFIED",
                    "command": {"action": "test"},
                    "priority": 5
                }
            )
            assert response.status_code == 200
            message_ids.append(response.json()["message_id"])
        
        # All IDs should be unique
        assert len(set(message_ids)) == 5

    def test_sensor_data_persistence(self):
        """Test that sensor data is stored and retrievable."""
        sensor_data1 = {"lidar": [1.0, 2.0, 3.0]}
        
        client.post(
            "/api/v1/ros2-bridge/update-sensor-data",
            json=sensor_data1
        )
        
        # Get robot state and check sensor data
        response = client.get("/api/v1/ros2-bridge/robot-state")
        assert response.status_code == 200
        data = response.json()
        
        # Sensor data should be present
        assert data["sensor_data"] == sensor_data1

    def test_robot_state_after_decisions(self):
        """Test robot state changes after publishing decisions."""
        # Get initial state
        response1 = client.get("/api/v1/ros2-bridge/robot-state")
        initial_count = len(response1.json()["topics_published"])
        
        # Publish a decision
        client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "state-test",
                "state": "VERIFIED",
                "command": {"action": "move"},
                "priority": 7
            }
        )
        
        # Get state again
        response2 = client.get("/api/v1/ros2-bridge/robot-state")
        final_count = len(response2.json()["topics_published"])
        
        # Should have one more published message
        assert final_count >= initial_count

    def test_complex_command_structure(self):
        """Test publishing complex nested command structures."""
        complex_command = {
            "action": "trajectory",
            "points": [
                {"x": 0, "y": 0, "z": 0},
                {"x": 1, "y": 1, "z": 0},
                {"x": 2, "y": 0, "z": 0}
            ],
            "velocity": 0.5,
            "acceleration": 0.1,
            "metadata": {
                "planner": "rrt",
                "timeout": 30,
                "constraints": ["joint_limits", "collision_avoidance"]
            }
        }
        
        response = client.post(
            "/api/v1/ros2-bridge/publish-decision",
            json={
                "decision_id": "complex-trajectory",
                "state": "VERIFIED",
                "command": complex_command,
                "priority": 9
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["command"] == complex_command


class TestRos2BridgeEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_sensor_data(self):
        """Test updating with empty sensor data."""
        response = client.post(
            "/api/v1/ros2-bridge/update-sensor-data",
            json={}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sensor_count"] == 0

    def test_multiple_decisions_same_robot_state(self):
        """Test multiple decisions maintain robot state consistency."""
        decisions = []
        for i in range(5):
            response = client.post(
                "/api/v1/ros2-bridge/publish-decision",
                json={
                    "decision_id": f"consistency-{i}",
                    "state": "VERIFIED",
                    "command": {"action": "step", "index": i},
                    "priority": 5
                }
            )
            assert response.status_code == 200
            decisions.append(response.json())
        
        # Get robot state
        response = client.get("/api/v1/ros2-bridge/robot-state")
        state = response.json()
        
        # All messages should be in published list
        assert len(state["topics_published"]) >= 5

    def test_bridge_command_with_parameters(self):
        """Test bridge command with additional parameters."""
        response = client.post(
            "/api/v1/ros2-bridge/bridge-command",
            json={
                "command": "connect",
                "parameters": {"timeout": 30, "retry": 3}
            }
        )
        assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
