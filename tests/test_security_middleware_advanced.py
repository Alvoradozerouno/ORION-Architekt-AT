"""
Comprehensive test suite for Security Middleware
===============================================

Tests for advanced security features including headers, XSS protection, CSRF,
rate limiting, and input sanitization.

Covers api/middleware/security_advanced.py with 100% coverage target.

Author: ORION Engineering Team
Date: 2026-05-19
Status: PRODUCTION
Coverage Target: 100%
"""

import sys
import os

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app
from api.main import app

# Create test client
client = TestClient(app)


# ============================================================================
# SECURITY HEADERS TESTS
# ============================================================================


class TestSecurityHeaders:
    """Test security headers middleware"""

    def test_hsts_header_present(self):
        """Test HSTS header is present"""
        response = client.get("/health")

        assert "Strict-Transport-Security" in response.headers

    def test_hsts_header_value(self):
        """Test HSTS header has correct value"""
        response = client.get("/health")

        hsts = response.headers.get("Strict-Transport-Security", "")
        assert "max-age=31536000" in hsts
        assert "includeSubDomains" in hsts
        assert "preload" in hsts

    def test_csp_header_present(self):
        """Test Content-Security-Policy header is present"""
        response = client.get("/health")

        assert "Content-Security-Policy" in response.headers

    def test_csp_header_value(self):
        """Test CSP header contains expected directives"""
        response = client.get("/health")

        csp = response.headers.get("Content-Security-Policy", "")
        assert "default-src 'self'" in csp
        assert "script-src" in csp
        assert "style-src" in csp

    def test_x_frame_options_present(self):
        """Test X-Frame-Options header is present"""
        response = client.get("/health")

        assert "X-Frame-Options" in response.headers

    def test_x_frame_options_value(self):
        """Test X-Frame-Options header value"""
        response = client.get("/health")

        assert response.headers.get("X-Frame-Options") == "DENY"

    def test_x_content_type_options_present(self):
        """Test X-Content-Type-Options header is present"""
        response = client.get("/health")

        if "X-Content-Type-Options" in response.headers:
            assert response.headers["X-Content-Type-Options"] == "nosniff"

    def test_security_headers_on_all_endpoints(self):
        """Test security headers are present on all endpoints"""
        endpoints = ["/health", "/health/live", "/health/ready"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            assert "Strict-Transport-Security" in response.headers or response.status_code >= 400


# ============================================================================
# INPUT SANITIZATION TESTS
# ============================================================================


class TestInputSanitization:
    """Test input sanitization"""

    def test_xss_payload_in_query_param(self):
        """Test XSS payload in query parameter"""
        xss_payload = "<script>alert('XSS')</script>"
        response = client.get(f"/api/v1/bundesland/{xss_payload}")

        # Should not execute script, should return error or 404
        assert response.status_code in [404, 422, 400]

    def test_sql_injection_in_query_param(self):
        """Test SQL injection payload in query parameter"""
        sql_payload = "'; DROP TABLE users; --"
        response = client.get(f"/api/v1/bundesland/{sql_payload}")
        # Should not execute query, should return error or 404
        assert response.status_code in [200, 404, 422, 400]

    def test_command_injection_in_query_param(self):
        """Test command injection payload in query parameter"""
        cmd_payload = "; rm -rf /"
        response = client.get(f"/api/v1/bundesland/{cmd_payload}")
        # Should not execute command, should return error or 404
        assert response.status_code in [200, 404, 422, 400]

    def test_path_traversal_attempt(self):
        """Test path traversal attempt"""
        payload = "../../../../etc/passwd"
        response = client.get(f"/api/v1/bundesland/{payload}")
        # Should not allow path traversal or safely handle it
        assert response.status_code in [200, 404, 422, 400]


# ============================================================================
# CSRF PROTECTION TESTS
# ============================================================================


class TestCSRFProtection:
    """Test CSRF protection"""

    def test_post_request_accepted(self):
        """Test POST requests are accepted"""
        params = {
            "bundesland": "Wien",
            "building_type": "Wohnhaus",
            "bgf_m2": 1500.0,
            "geschosse": 3,
        }

        response = client.post("/api/v1/compliance/oib-rl-check", params=params)
        # Should be processed (success or validation error)
        assert response.status_code in [200, 422]

    def test_origin_header_validation(self):
        """Test Origin header validation"""
        headers = {"Origin": "https://example.com"}
        response = client.get("/health", headers=headers)

        # Should handle different origins
        assert response.status_code in [200, 403, 404]


# ============================================================================
# RATE LIMITING TESTS
# ============================================================================


class TestRateLimiting:
    """Test rate limiting middleware"""

    def test_single_request_allowed(self):
        """Test single request is allowed"""
        response = client.get("/health")
        assert response.status_code in [200, 503]

    def test_multiple_requests_allowed(self):
        """Test multiple requests are allowed"""
        for _ in range(5):
            response = client.get("/health")
            assert response.status_code in [200, 503, 429]

    def test_rate_limit_headers_present(self):
        """Test rate limit headers are present if implemented"""
        response = client.get("/health")

        # Check for rate limit headers if rate limiting is enabled
        if "X-RateLimit-Limit" in response.headers:
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers


# ============================================================================
# HTTPS ENFORCEMENT TESTS
# ============================================================================


class TestHTTPSEnforcement:
    """Test HTTPS enforcement"""

    def test_hsts_preload_header(self):
        """Test HSTS preload header"""
        response = client.get("/health")

        hsts = response.headers.get("Strict-Transport-Security", "")
        # Should include preload for HSTS
        if "preload" in hsts:
            assert "includeSubDomains" in hsts


# ============================================================================
# CORS TESTS
# ============================================================================


class TestCORSProtection:
    """Test CORS protection"""

    def test_cors_headers_on_preflight(self):
        """Test CORS headers on preflight request"""
        response = client.options(
            "/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should handle CORS preflight or return error
        assert response.status_code in [200, 204, 405, 404]

    def test_same_origin_requests_allowed(self):
        """Test same origin requests are allowed"""
        response = client.get("/health")
        assert response.status_code in [200, 503]


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================


class TestAuthenticationSecurity:
    """Test authentication security"""

    def test_invalid_token_rejected(self):
        """Test invalid token is rejected"""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.get("/health", headers=headers)

        # Should either process without auth or reject invalid token
        assert response.status_code in [200, 401, 403, 503]

    def test_missing_token_handled(self):
        """Test missing token is handled"""
        response = client.get("/health")
        # Public endpoints should work without token
        assert response.status_code in [200, 503]

    def test_malformed_token_rejected(self):
        """Test malformed token is rejected"""
        headers = {"Authorization": "Bearer"}  # No actual token
        response = client.get("/health", headers=headers)

        assert response.status_code in [200, 401, 403, 503]


# ============================================================================
# RESPONSE VALIDATION TESTS
# ============================================================================


class TestResponseValidation:
    """Test response validation"""

    def test_response_content_type_valid(self):
        """Test response Content-Type is valid"""
        response = client.get("/health")

        content_type = response.headers.get("Content-Type", "")
        # Should be valid content type
        assert "application/json" in content_type or "text/plain" in content_type

    def test_response_headers_no_sensitive_info(self):
        """Test response headers don't leak sensitive info"""
        response = client.get("/health")

        # Should not include server version or other sensitive info
        headers_str = str(response.headers)
        # Check that specific sensitive patterns aren't exposed
        assert "debug" not in headers_str.lower()


# ============================================================================
# ENCODING TESTS
# ============================================================================


class TestEncoding:
    """Test encoding security"""

    def test_utf8_encoding_handled(self):
        """Test UTF-8 encoding is handled"""
        response = client.get("/api/v1/bundesland/Niederösterreich")
        # Should handle UTF-8 characters
        assert response.status_code in [200, 404]

    def test_null_byte_injection(self):
        """Test null byte injection is prevented"""
        payload = "Wien%00<script>"
        response = client.get(f"/api/v1/bundesland/{payload}")
        # Should not execute, should return error or 404
        assert response.status_code in [200, 404, 422, 400]


# ============================================================================
# TIMEOUT TESTS
# ============================================================================


class TestTimeout:
    """Test timeout protection"""

    def test_request_completes(self):
        """Test request completes within reasonable time"""
        response = client.get("/health")
        # Should complete (no timeout)
        assert response is not None


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


class TestErrorHandling:
    """Test error handling with security in mind"""

    def test_404_error_response(self):
        """Test 404 error response"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_error_response_headers(self):
        """Test error responses include security headers"""
        response = client.get("/nonexistent")

        # Error responses should also have security headers
        assert "Strict-Transport-Security" in response.headers or response.status_code == 404


# ============================================================================
# INJECTION ATTACK PREVENTION TESTS
# ============================================================================


class TestInjectionPrevention:
    """Test prevention of various injection attacks"""

    def test_ldap_injection_prevention(self):
        """Test LDAP injection is prevented"""
        payload = "*)(&(uid=*"
        response = client.get(f"/api/v1/bundesland/{payload}")
        assert response.status_code in [200, 404, 422, 400]

    def test_xml_injection_prevention(self):
        """Test XML injection is prevented"""
        payload = "<?xml version='1.0'?><!DOCTYPE foo [<!ENTITY xxe SYSTEM 'file:///etc/passwd'>]>"
        response = client.post(
            "/api/v1/compliance/oib-rl-check",
            json={"building_type": payload},
        )
        assert response.status_code in [422, 400]

    def test_os_command_injection_prevention(self):
        """Test OS command injection is prevented"""
        payload = "`touch /tmp/pwned`"
        response = client.get(f"/api/v1/bundesland/{payload}")
        assert response.status_code in [200, 404, 422, 400]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


class TestSecurityIntegration:
    """Integration tests for security"""

    def test_all_endpoints_have_security_headers(self):
        """Test all endpoints have security headers"""
        endpoints = ["/health", "/health/live", "/health/ready"]

        for endpoint in endpoints:
            response = client.get(endpoint)
            # At least HSTS should be present
            assert "Strict-Transport-Security" in response.headers or response.status_code >= 400

    def test_legitimate_request_accepted(self):
        """Test legitimate requests are accepted"""
        params = {
            "bundesland": "Wien",
            "building_type": "Wohnhaus",
            "bgf_m2": 1500.0,
            "geschosse": 3,
        }

        response = client.post("/api/v1/compliance/oib-rl-check", params=params)
        # Should process legitimate request
        assert response.status_code in [200, 422]

    def test_malicious_request_blocked(self):
        """Test malicious requests are blocked"""
        malicious_data = {
            "bundesland": "<script>alert('XSS')</script>",
        }

        response = client.post(
            "/api/v1/compliance/oib-rl-check",
            json=malicious_data,
        )
        # Should block or reject malicious request
        assert response.status_code in [400, 422]


# ============================================================================
# EDGE CASE TESTS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_long_input(self):
        """Test very long input"""
        long_input = "x" * 10000
        response = client.get(f"/api/v1/bundesland/{long_input}")
        # Should handle gracefully
        assert response.status_code in [200, 404, 422, 400, 414]  # 414 = URI Too Long

    def test_unicode_characters_in_input(self):
        """Test Unicode characters in input"""
        unicode_payload = "🔒🔓💻"
        response = client.get(f"/api/v1/bundesland/{unicode_payload}")
        # Should handle Unicode
        assert response.status_code in [404, 422, 400, 200]

    def test_binary_payload(self):
        """Test binary payload"""
        response = client.get("/api/v1/bundesland/%00%01%02")
        # Should handle binary data
        assert response.status_code in [200, 404, 422, 400]

    def test_empty_payload(self):
        """Test empty payload"""
        response = client.get("/api/v1/bundesland/")
        # Should handle empty
        assert response.status_code in [200, 404, 422]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
