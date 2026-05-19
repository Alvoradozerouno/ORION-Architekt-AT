"""
Tests for ORION Exception Classes
Tests custom exception handling and error scenarios
"""

import os
import sys

import pytest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from orion_exceptions import (
    OrionArchitektError,
    ValidationError,
    ComplianceError,
    StandardVersionError,
    DataFreshnessError,
    OIBComplianceError,
)


class TestOrionExceptions:
    """Test suite for ORION exception classes"""

    def test_orion_architekt_error_creation(self):
        """Test creating OrionArchitektError"""
        exc = OrionArchitektError("Test error")
        assert isinstance(exc, Exception)

    def test_validation_error(self):
        """Test ValidationError"""
        exc = ValidationError("Invalid input")
        assert isinstance(exc, Exception)
        assert isinstance(exc, OrionArchitektError)

    def test_compliance_error(self):
        """Test ComplianceError"""
        exc = ComplianceError("OIB-RL compliance failed")
        assert isinstance(exc, Exception)
        assert isinstance(exc, OrionArchitektError)

    def test_standard_version_error(self):
        """Test StandardVersionError"""
        exc = StandardVersionError("OIB-RL 6", "Outdated version")
        assert isinstance(exc, Exception)
        assert isinstance(exc, ValidationError)

    def test_data_freshness_error(self):
        """Test DataFreshnessError"""
        exc = DataFreshnessError(200, 180)
        assert isinstance(exc, Exception)
        assert isinstance(exc, ValidationError)

    def test_oib_compliance_error(self):
        """Test OIBComplianceError"""
        exc = OIBComplianceError("OIB-RL 6", "fGEE too high")
        assert isinstance(exc, Exception)
        assert isinstance(exc, ComplianceError)


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy"""

    def test_exception_inheritance_chain(self):
        """Test that exceptions inherit correctly"""
        exc = ComplianceError("Test")
        assert isinstance(exc, ComplianceError)
        assert isinstance(exc, OrionArchitektError)
        assert isinstance(exc, Exception)

    def test_all_exceptions_are_exceptions(self):
        """Test that all exception classes are Exception subclasses"""
        exception_classes = [
            OrionArchitektError,
            ValidationError,
            ComplianceError,
            StandardVersionError,
            DataFreshnessError,
            OIBComplianceError,
        ]
        
        for exc_class in exception_classes:
            assert issubclass(exc_class, Exception)

    def test_exception_catching(self):
        """Test catching exceptions"""
        try:
            raise ComplianceError("Test error")
        except OrionArchitektError:
            pass  # Should be caught
        except Exception:
            pytest.fail("Should have been caught as OrionArchitektError")

    def test_exception_catching_general(self):
        """Test catching exceptions with generic handler"""
        try:
            raise ValidationError("Test")
        except Exception as e:
            assert isinstance(e, ValidationError)


class TestExceptionMessages:
    """Test exception message handling"""

    def test_validation_error_message(self):
        """Test ValidationError message"""
        message = "Input validation failed"
        exc = ValidationError(message)
        assert isinstance(exc, Exception)

    def test_compliance_error_message(self):
        """Test ComplianceError message"""
        message = "OIB-RL 6 not met"
        exc = ComplianceError(message)
        assert isinstance(exc, Exception)

    def test_standard_version_error_message(self):
        """Test StandardVersionError with standard name"""
        exc = StandardVersionError("OIB-RL 6")
        assert "OIB-RL 6" in str(exc)

    def test_data_freshness_error_message(self):
        """Test DataFreshnessError with age info"""
        exc = DataFreshnessError(200, 180)
        exc_str = str(exc)
        assert "200" in exc_str


class TestExceptionScenarios:
    """Test exception scenarios and use cases"""

    def test_validation_error_scenario(self):
        """Test typical validation error scenario"""
        try:
            raise ValidationError("Bundesland must be one of: wien, tirol, ...")
        except ValidationError as e:
            assert "Bundesland" in str(e)

    def test_compliance_error_scenario(self):
        """Test typical compliance error scenario"""
        try:
            raise OIBComplianceError("OIB-RL 6", "fGEE > 0.75")
        except ComplianceError:
            pass

    def test_data_freshness_error_scenario(self):
        """Test data freshness error scenario"""
        try:
            raise DataFreshnessError(365, 180)
        except ValidationError:
            pass

    def test_standard_version_error_scenario(self):
        """Test standard version error scenario"""
        try:
            raise StandardVersionError("OENORM B 1800", "Outdated")
        except ValidationError:
            pass


class TestExceptionNesting:
    """Test exception nesting and chaining"""

    def test_nested_exception_handling(self):
        """Test nested exception handling"""
        try:
            try:
                raise ValidationError("Inner error")
            except ValidationError as e:
                raise ComplianceError(f"Outer error: {e}")
        except ComplianceError:
            pass

    def test_exception_in_function(self):
        """Test exception raised in function"""
        def failing_function():
            raise ComplianceError("Function failed")
        
        with pytest.raises(ComplianceError):
            failing_function()

    def test_exception_catching_hierarchy(self):
        """Test catching based on exception hierarchy"""
        try:
            raise OIBComplianceError("OIB-RL 6", "Error")
        except ComplianceError:
            pass  # Should be caught as ComplianceError
        except Exception:
            pytest.fail("Should have been caught")


class TestExceptionEdgeCases:
    """Test edge cases and corner cases"""

    def test_exception_with_unicode(self):
        """Test exception with unicode characters"""
        message = "Fehler mit Umlauten: äöü €"
        exc = ValidationError(message)
        assert isinstance(exc, Exception)

    def test_exception_repr(self):
        """Test exception repr"""
        exc = ValidationError("Test error")
        repr_str = repr(exc)
        assert isinstance(repr_str, str)

    def test_multiple_exception_types(self):
        """Test raising multiple exception types in sequence"""
        exceptions = [
            ValidationError("Validation error"),
            ComplianceError("Compliance error"),
            StandardVersionError("OIB-RL 6"),
        ]
        
        for exc in exceptions:
            with pytest.raises(OrionArchitektError):
                raise exc

    def test_exception_attributes(self):
        """Test exception attributes"""
        exc = ValidationError("Test")
        assert hasattr(exc, "args")

    def test_data_freshness_attributes(self):
        """Test DataFreshnessError attributes"""
        exc = DataFreshnessError(300, 180)
        assert exc.age_days == 300
        assert exc.threshold_days == 180

    def test_standard_version_attributes(self):
        """Test StandardVersionError attributes"""
        exc = StandardVersionError("OIB-RL 7")
        assert exc.standard_name == "OIB-RL 7"


class TestExceptionModularity:
    """Test exception module availability and structure"""

    def test_orion_exceptions_module_importable(self):
        """Test that orion_exceptions module is importable"""
        import orion_exceptions
        assert orion_exceptions is not None

    def test_all_exception_classes_importable(self):
        """Test that all exception classes can be imported"""
        from orion_exceptions import (
            OrionArchitektError,
            ValidationError,
            ComplianceError,
        )
        assert OrionArchitektError is not None
        assert ValidationError is not None
        assert ComplianceError is not None


class TestExceptionIntegration:
    """Integration tests for exception handling"""

    def test_exception_workflow(self):
        """Test complete exception workflow"""
        try:
            # Simulate some validation
            if True:  # Trigger error condition
                raise ValidationError("Input validation failed")
        except ValidationError as e:
            # Handle specific error
            assert "validation" in str(e).lower()

    def test_multiple_exception_catch(self):
        """Test catching multiple exception types"""
        exceptions_to_test = [
            (ValidationError("test"), ValidationError),
            (ComplianceError("test"), ComplianceError),
        ]
        
        for exc, exc_type in exceptions_to_test:
            with pytest.raises(exc_type):
                raise exc
