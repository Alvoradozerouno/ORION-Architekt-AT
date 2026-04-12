"""
ORION Architekt-AT - Load Testing with Locust
==============================================

Performance and load testing scenarios for production validation.

Author: ORION Engineering Team
Date: 2026-04-12
Status: PRODUCTION TESTING
"""

from locust import HttpUser, task, between, events
import json
import random
import time
from typing import Dict, Any


# ============================================================================
# Test Data
# ============================================================================

BUNDESLAENDER = ["wien", "tirol", "salzburg", "vorarlberg", "steiermark",
                 "oberoesterreich", "niederoesterreich", "kaernten", "burgenland"]

BUILDING_TYPES = ["einfamilienhaus", "mehrfamilienhaus", "wohngebaeude",
                  "buerogebaeude", "gewerbe", "industrie"]

MATERIALS = [
    ("Außenputz", 10, 0.7),
    ("Dämmung EPS", 160, 0.035),
    ("Beton", 200, 2.1),
    ("Innendämmung", 40, 0.04),
    ("Gipskarton", 12, 0.21),
]


# ============================================================================
# Test Scenarios
# ============================================================================

class BaseORIONUser(HttpUser):
    """Base user with common functionality"""

    host = "http://localhost"
    wait_time = between(1, 3)

    def on_start(self):
        """Called when user starts"""
        # Check if API is healthy
        response = self.client.get("/health")
        if response.status_code != 200:
            events.test_stop()
            raise Exception("API is not healthy")


class AnonymousUser(BaseORIONUser):
    """
    Anonymous user browsing documentation
    Weight: 50% of users
    """

    weight = 5

    @task(5)
    def view_health(self):
        """Health check endpoint"""
        self.client.get("/health", name="/health")

    @task(3)
    def view_docs(self):
        """View API documentation"""
        self.client.get("/docs", name="/docs")

    @task(2)
    def view_openapi(self):
        """View OpenAPI spec"""
        self.client.get("/openapi.json", name="/openapi.json")


class AuthenticatedFreeUser(BaseORIONUser):
    """
    Authenticated free tier user (100 req/min limit)
    Weight: 30% of users
    """

    weight = 3

    @task(10)
    def calculate_uwert(self):
        """U-value calculation (most common)"""
        schichten = []
        num_layers = random.randint(3, 6)

        for i in range(num_layers):
            material, dicke, lambda_val = random.choice(MATERIALS)
            schichten.append({
                "material": material,
                "dicke_mm": dicke + random.randint(-10, 10),
                "lambda_wert": lambda_val
            })

        payload = {
            "schichten": schichten,
            "innen_uebergang": 0.13,
            "aussen_uebergang": 0.04
        }

        with self.client.post(
            "/api/v1/berechnungen/uwert",
            json=payload,
            name="/api/v1/berechnungen/uwert",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                result = response.json()
                if "u_wert" in result:
                    response.success()
                else:
                    response.failure("Missing u_wert in response")
            elif response.status_code == 429:
                response.success()  # Rate limit is expected
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(5)
    def calculate_stellplaetze(self):
        """Parking space calculation"""
        payload = {
            "bundesland": random.choice(BUNDESLAENDER),
            "wohnungen": random.randint(10, 100),
            "building_type": random.choice(BUILDING_TYPES)
        }

        self.client.post(
            "/api/v1/berechnungen/stellplaetze",
            json=payload,
            name="/api/v1/berechnungen/stellplaetze"
        )

    @task(3)
    def check_barrierefreiheit(self):
        """Accessibility check"""
        payload = {
            "tuer_breite_cm": random.randint(80, 120),
            "rampe_vorhanden": random.choice([True, False]),
            "rampe_steigung_prozent": random.uniform(3, 6),
            "aufzug_vorhanden": random.choice([True, False]),
            "geschosse": random.randint(1, 8),
            "bundesland": random.choice(BUNDESLAENDER)
        }

        self.client.post(
            "/api/v1/checks/barrierefreiheit",
            json=payload,
            name="/api/v1/checks/barrierefreiheit"
        )

    @task(2)
    def calculate_heizlast(self):
        """Heating load calculation"""
        payload = {
            "bgf_m2": random.randint(100, 500),
            "uwert_wand": random.uniform(0.15, 0.35),
            "uwert_dach": random.uniform(0.12, 0.25),
            "uwert_fenster": random.uniform(0.8, 1.3),
            "bundesland": random.choice(BUNDESLAENDER)
        }

        self.client.post(
            "/api/v1/berechnungen/heizlast",
            json=payload,
            name="/api/v1/berechnungen/heizlast"
        )


class AuthenticatedPremiumUser(BaseORIONUser):
    """
    Authenticated premium user (1000 req/min limit)
    Weight: 15% of users
    Higher usage patterns
    """

    weight = 1.5

    @task(20)
    def calculate_uwert_bulk(self):
        """Multiple U-value calculations"""
        for _ in range(3):  # Premium users do batch operations
            schichten = []
            num_layers = random.randint(4, 8)

            for i in range(num_layers):
                material, dicke, lambda_val = random.choice(MATERIALS)
                schichten.append({
                    "material": material,
                    "dicke_mm": dicke + random.randint(-10, 10),
                    "lambda_wert": lambda_val
                })

            payload = {
                "schichten": schichten,
                "innen_uebergang": 0.13,
                "aussen_uebergang": 0.04
            }

            self.client.post(
                "/api/v1/berechnungen/uwert",
                json=payload,
                name="/api/v1/berechnungen/uwert"
            )

            time.sleep(0.1)  # Small delay between batch operations

    @task(10)
    def comprehensive_compliance_check(self):
        """Full OIB compliance check"""
        payload = {
            "bundesland": random.choice(BUNDESLAENDER),
            "building_type": random.choice(BUILDING_TYPES),
            "bgf_m2": random.randint(200, 2000),
            "geschosse": random.randint(2, 12),
            "wohnungen": random.randint(20, 200),
            "richtlinien": [1, 2, 3, 4, 5, 6]
        }

        self.client.post(
            "/api/v1/compliance/oib",
            json=payload,
            name="/api/v1/compliance/oib"
        )

    @task(5)
    def advanced_calculations(self):
        """Multiple calculation types in sequence"""
        # First calculate U-value
        uwert_payload = {
            "schichten": [
                {"material": "Beton", "dicke_mm": 200, "lambda_wert": 2.1},
                {"material": "Dämmung", "dicke_mm": 160, "lambda_wert": 0.035},
            ]
        }
        self.client.post("/api/v1/berechnungen/uwert", json=uwert_payload)

        # Then check accessibility
        barrierefreiheit_payload = {
            "tuer_breite_cm": 90,
            "rampe_vorhanden": True,
            "rampe_steigung_prozent": 6,
            "aufzug_vorhanden": True,
            "geschosse": 5,
            "bundesland": "wien"
        }
        self.client.post("/api/v1/checks/barrierefreiheit", json=barrierefreiheit_payload)


class EnterpriseUser(BaseORIONUser):
    """
    Enterprise user with highest limits (10000 req/min)
    Weight: 5% of users
    Heavy API usage
    """

    weight = 0.5

    @task(30)
    def batch_processing(self):
        """Enterprise batch processing"""
        # Simulate processing multiple projects
        for project_id in range(5):
            # Multiple calculations per project
            for _ in range(2):
                schichten = [
                    {"material": f"Material_{i}", "dicke_mm": random.randint(50, 200),
                     "lambda_wert": random.uniform(0.03, 2.0)}
                    for i in range(random.randint(4, 10))
                ]

                payload = {"schichten": schichten}
                self.client.post(
                    "/api/v1/berechnungen/uwert",
                    json=payload,
                    name="/api/v1/berechnungen/uwert [Enterprise]"
                )

            time.sleep(0.05)  # Minimal delay


# ============================================================================
# Stress Test User
# ============================================================================

class StressTestUser(BaseORIONUser):
    """
    Aggressive user for stress testing
    Only used in stress test scenarios
    """

    weight = 10  # Only active during stress tests

    wait_time = between(0.1, 0.5)  # Very short wait time

    @task
    def rapid_fire_requests(self):
        """Rapid fire requests to stress the system"""
        endpoints = [
            ("/api/v1/berechnungen/uwert", {
                "schichten": [{"material": "Test", "dicke_mm": 100, "lambda_wert": 1.0}]
            }),
            ("/api/v1/berechnungen/stellplaetze", {
                "bundesland": "wien", "wohnungen": 50, "building_type": "mehrfamilienhaus"
            }),
            ("/health", None)
        ]

        endpoint, payload = random.choice(endpoints)

        if payload:
            self.client.post(endpoint, json=payload, name=f"{endpoint} [STRESS]")
        else:
            self.client.get(endpoint, name=f"{endpoint} [STRESS]")


# ============================================================================
# Test Lifecycle Events
# ============================================================================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("=" * 80)
    print("ORION Load Test Starting")
    print("=" * 80)
    print(f"Target: {environment.host}")
    print(f"Users: {environment.runner.target_user_count if hasattr(environment.runner, 'target_user_count') else 'Unknown'}")
    print("=" * 80)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("=" * 80)
    print("ORION Load Test Completed")
    print("=" * 80)


# ============================================================================
# Custom Metrics
# ============================================================================

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track custom metrics"""
    if exception:
        print(f"Request failed: {name} - {exception}")

    # Track slow requests (>1s)
    if response_time > 1000:
        print(f"SLOW REQUEST: {name} took {response_time}ms")
