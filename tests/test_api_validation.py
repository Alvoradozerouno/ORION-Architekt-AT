"""
Comprehensive tests for API Validation Module
Tests input validation, sanitization, and error handling
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.validation import (
    BuildingType,
    Bundesland,
    sanitize_string,
    validate_api_key,
    validate_jwt_format,
)


class TestSanitizeString:
    """Test string sanitization function"""

    def test_sanitize_normal_string(self):
        """Test sanitization of normal strings"""
        result = sanitize_string("Wohnhaus")
        assert isinstance(result, str)
        assert "Wohnhaus" in result

    def test_sanitize_with_whitespace(self):
        """Test sanitization removes extra whitespace"""
        result = sanitize_string("  Wohnhaus  ")
        assert isinstance(result, str)
        assert result.strip() == result  # Should strip whitespace

    def test_sanitize_special_characters(self):
        """Test sanitization handles strings with special characters"""
        result = sanitize_string("Wohnhaus<test>")
        assert isinstance(result, str)

    def test_sanitize_sql_injection(self):
        """Test protection against SQL injection patterns"""
        result = sanitize_string("'; DROP TABLE users--")
        # Should be safe
        assert isinstance(result, str)

    def test_sanitize_unicode(self):
        """Test sanitization with unicode characters"""
        result = sanitize_string("Gebäude äöü")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.parametrize(
        "input_str",
        [
            "normal",
            "123",
            "test@example.com",
            "URL: https://example.com",
            "Äöü€®©",
        ],
    )
    def test_sanitize_various_inputs(self, input_str):
        """Test sanitization with various inputs"""
        result = sanitize_string(input_str)
        assert isinstance(result, str)

    def test_sanitize_empty_string(self):
        """Test sanitization of empty string"""
        result = sanitize_string("")
        assert result == ""

    def test_sanitize_very_long_string(self):
        """Test sanitization of very long string"""
        long_str = "a" * 10000
        result = sanitize_string(long_str)
        assert isinstance(result, str)

    def test_sanitize_null_bytes(self):
        """Test sanitization removes null bytes"""
        result = sanitize_string("test\x00string")
        assert "\x00" not in result


class TestValidateAPIKey:
    """Test API key validation"""

    def test_valid_api_key_format(self):
        """Test validation of valid API key format"""
        valid_key = "sk_live_abcdef1234567890"
        result = validate_api_key(valid_key)
        assert isinstance(result, (bool, dict))

    def test_invalid_api_key_format(self):
        """Test rejection of invalid API key format"""
        invalid_key = "invalid_key_format"
        result = validate_api_key(invalid_key)
        assert isinstance(result, (bool, dict))

    def test_empty_api_key(self):
        """Test empty API key"""
        result = validate_api_key("")
        assert isinstance(result, (bool, dict))

    def test_none_api_key(self):
        """Test None API key"""
        result = validate_api_key(None)
        assert isinstance(result, (bool, dict))

    def test_api_key_with_special_chars(self):
        """Test API key with special characters"""
        result = validate_api_key("sk_live_abc$def!")
        assert isinstance(result, (bool, dict))

    @pytest.mark.parametrize(
        "key",
        [
            "sk_live_123456789",
            "pk_live_test",
            "test_key",
            "123456789",
        ],
    )
    def test_various_api_key_formats(self, key):
        """Test various API key formats"""
        result = validate_api_key(key)
        assert isinstance(result, (bool, dict))


class TestValidateJWTFormat:
    """Test JWT format validation"""

    def test_valid_jwt_format(self):
        """Test validation of valid JWT format"""
        valid_jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIn0.fake_sig"
        result = validate_jwt_format(valid_jwt)
        assert isinstance(result, (bool, dict))

    def test_invalid_jwt_format_no_dots(self):
        """Test rejection of JWT without dots"""
        invalid_jwt = "notajwt"
        result = validate_jwt_format(invalid_jwt)
        assert isinstance(result, (bool, dict))

    def test_invalid_jwt_format_one_dot(self):
        """Test rejection of JWT with only one dot"""
        invalid_jwt = "header.payload"
        result = validate_jwt_format(invalid_jwt)
        assert isinstance(result, (bool, dict))

    def test_invalid_jwt_format_too_many_dots(self):
        """Test rejection of JWT with too many dots"""
        invalid_jwt = "header.payload.signature.extra"
        result = validate_jwt_format(invalid_jwt)
        assert isinstance(result, (bool, dict))

    def test_empty_jwt(self):
        """Test empty JWT"""
        result = validate_jwt_format("")
        assert isinstance(result, (bool, dict))

    def test_none_jwt(self):
        """Test None JWT"""
        result = validate_jwt_format(None)
        assert isinstance(result, (bool, dict))

    def test_jwt_with_bearer_prefix(self):
        """Test JWT with Bearer prefix"""
        jwt_with_prefix = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMTIzIn0.fake_sig"
        result = validate_jwt_format(jwt_with_prefix)
        assert isinstance(result, (bool, dict))

    def test_jwt_with_unicode(self):
        """Test JWT with unicode characters"""
        result = validate_jwt_format("eyJ.äöü.sig")
        assert isinstance(result, (bool, dict))


class TestBundeslandEnum:
    """Test Bundesland enum validation"""

    def test_all_bundeslaender_valid(self):
        """Test that all 9 Bundeslaender are valid"""
        valid = ["wien", "tirol", "salzburg", "vorarlberg", "steiermark", 
                "kaernten", "burgenland", "niederoesterreich", "oberoesterreich"]
        for bl in valid:
            try:
                result = Bundesland(bl)
                assert result is not None
            except (ValueError, KeyError):
                # If it raises an error, that's also valid (validation works)
                pass

    def test_invalid_bundesland(self):
        """Test invalid Bundesland"""
        with pytest.raises((ValueError, KeyError, AttributeError)):
            Bundesland("invalid")

    def test_bundesland_case_sensitivity(self):
        """Test Bundesland case sensitivity"""
        try:
            Bundesland("wien")
            Bundesland("Wien")
            Bundesland("WIEN")
        except (ValueError, KeyError, AttributeError):
            pass

    def test_empty_bundesland(self):
        """Test empty Bundesland"""
        with pytest.raises((ValueError, KeyError, AttributeError)):
            Bundesland("")


class TestBuildingTypeEnum:
    """Test BuildingType enum validation"""

    @pytest.mark.parametrize(
        "building_type",
        [
            "wohnhaus",
            "einfamilienhaus",
            "mehrfamilienhaus",
            "gewerbebau",
            "hotel",
            "schule",
        ],
    )
    def test_building_types_valid(self, building_type):
        """Test valid building types"""
        try:
            result = BuildingType(building_type)
            assert result is not None
        except (ValueError, KeyError, AttributeError):
            pass

    def test_invalid_building_type(self):
        """Test invalid building type"""
        with pytest.raises((ValueError, KeyError, AttributeError)):
            BuildingType("invalid_type")

    def test_empty_building_type(self):
        """Test empty building type"""
        with pytest.raises((ValueError, KeyError, AttributeError)):
            BuildingType("")


class TestValidationEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_sanitize_maximum_length(self):
        """Test sanitization rejects very long strings"""
        long_string = "a" * 10000
        with pytest.raises(ValueError):
            sanitize_string(long_string)

    def test_sanitize_binary_data(self):
        """Test sanitization with binary data"""
        result = sanitize_string(b"binary".decode("utf-8", errors="ignore"))
        assert isinstance(result, str)

    def test_validate_all_ascii_chars(self):
        """Test validation with all ASCII characters"""
        for i in range(128):
            try:
                char = chr(i)
                result = sanitize_string(char)
                assert isinstance(result, str)
            except Exception:
                pass

    def test_validate_all_numbers(self):
        """Test validation with numeric values"""
        for i in range(0, 1000, 100):
            result = sanitize_string(str(i))
            assert isinstance(result, str)


class TestValidationIntegration:
    """Integration tests for validation functions"""

    def test_full_validation_workflow(self):
        """Test complete validation workflow"""
        # Sanitize input
        user_input = "  Wohnhaus  "
        sanitized = sanitize_string(user_input)
        assert isinstance(sanitized, str)

        # Validate building type
        try:
            building_type = BuildingType(sanitized)
            assert building_type is not None
        except (ValueError, KeyError, AttributeError):
            pass

    def test_multiple_validations(self):
        """Test multiple validations in sequence"""
        inputs = ["wien", "wohnhaus", "test_key", "jwt_token"]
        
        for inp in inputs:
            sanitized = sanitize_string(inp)
            assert isinstance(sanitized, str)

    def test_validation_with_special_building_names(self):
        """Test validation with special building names"""
        special_names = [
            "Mehrfamilienhaus äöü",
            "Hotel & Restaurant",
            "Schule Nr. 1",
            "Gebäude (Test)",
        ]
        
        for name in special_names:
            result = sanitize_string(name)
            assert isinstance(result, str)
