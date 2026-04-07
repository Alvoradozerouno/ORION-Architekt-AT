"""
Custom Exceptions for ORION Architekt-AT

Provides structured error handling for Austrian building regulations,
compliance checks, and validation errors.
"""


class OrionArchitektError(Exception):
    """Base exception for all ORION Architekt-AT errors"""
    pass


# === Validation Errors ===

class ValidationError(OrionArchitektError):
    """Base class for validation errors"""
    pass


class StandardVersionError(ValidationError):
    """Raised when a standard version is invalid or outdated"""
    def __init__(self, standard_name, message="Standard version error"):
        self.standard_name = standard_name
        super().__init__(f"{message}: {standard_name}")


class DataFreshnessError(ValidationError):
    """Raised when data is too old and needs updating"""
    def __init__(self, age_days, threshold_days=180):
        self.age_days = age_days
        self.threshold_days = threshold_days
        super().__init__(
            f"Data is {age_days} days old (threshold: {threshold_days} days)"
        )


# === Compliance Errors ===

class ComplianceError(OrionArchitektError):
    """Base class for compliance-related errors"""
    pass


class OIBComplianceError(ComplianceError):
    """Raised when OIB-RL compliance check fails"""
    def __init__(self, richtlinie, message):
        self.richtlinie = richtlinie
        super().__init__(f"OIB-RL {richtlinie}: {message}")


class ONORMComplianceError(ComplianceError):
    """Raised when ÖNORM compliance check fails"""
    def __init__(self, norm, message):
        self.norm = norm
        super().__init__(f"ÖNORM {norm}: {message}")


class BarrierefreiheitError(ComplianceError):
    """Raised when accessibility requirements are not met"""
    def __init__(self, mangel_list):
        self.mangel_list = mangel_list
        super().__init__(
            f"Barrierefreiheit nicht erfüllt: {', '.join(mangel_list)}"
        )


class FluchwegError(ComplianceError):
    """Raised when emergency exit requirements are not met"""
    def __init__(self, mangel_list):
        self.mangel_list = mangel_list
        super().__init__(
            f"Fluchtweg-Anforderungen nicht erfüllt: {', '.join(mangel_list)}"
        )


# === Calculation Errors ===

class CalculationError(OrionArchitektError):
    """Base class for calculation errors"""
    pass


class UWertError(CalculationError):
    """Raised when U-value calculation fails"""
    def __init__(self, message="U-Wert Berechnung fehlgeschlagen"):
        super().__init__(message)


class FlaechenberechnungError(CalculationError):
    """Raised when area calculation fails (ÖNORM B 1800)"""
    def __init__(self, message="Flächenberechnung fehlgeschlagen"):
        super().__init__(message)


# === Bundesland Errors ===

class BundeslandError(OrionArchitektError):
    """Raised when Bundesland-specific data or logic fails"""
    def __init__(self, bundesland, message="Bundesland error"):
        self.bundesland = bundesland
        super().__init__(f"{message} für Bundesland: {bundesland}")


class InvalidBundeslandError(BundeslandError):
    """Raised when an invalid Bundesland is specified"""
    def __init__(self, bundesland):
        super().__init__(
            bundesland,
            f"Ungültiges Bundesland: '{bundesland}'. "
            "Gültige Werte: burgenland, kaernten, niederoesterreich, "
            "oberoesterreich, salzburg, steiermark, tirol, vorarlberg, wien"
        )


# === Data Errors ===

class DataError(OrionArchitektError):
    """Base class for data-related errors"""
    pass


class MissingDataError(DataError):
    """Raised when required data is missing"""
    def __init__(self, field_name):
        self.field_name = field_name
        super().__init__(f"Erforderliche Daten fehlen: {field_name}")


class InvalidDataError(DataError):
    """Raised when data is invalid or malformed"""
    def __init__(self, field_name, value, expected_type=None):
        self.field_name = field_name
        self.value = value
        self.expected_type = expected_type
        msg = f"Ungültige Daten für {field_name}: {value}"
        if expected_type:
            msg += f" (erwartet: {expected_type})"
        super().__init__(msg)


# === API/Integration Errors ===

class IntegrationError(OrionArchitektError):
    """Base class for external integration errors"""
    pass


class RISAPIError(IntegrationError):
    """Raised when RIS Austria API call fails"""
    def __init__(self, message="RIS API call failed"):
        super().__init__(message)


class HoraAPIError(IntegrationError):
    """Raised when hora.gv.at API call fails"""
    def __init__(self, message="hora.gv.at API call failed"):
        super().__init__(message)


class OIBAPIError(IntegrationError):
    """Raised when OIB API call fails"""
    def __init__(self, message="OIB API call failed"):
        super().__init__(message)


# === Configuration Errors ===

class ConfigurationError(OrionArchitektError):
    """Raised when configuration is invalid or missing"""
    def __init__(self, config_key, message=None):
        self.config_key = config_key
        msg = f"Konfigurationsfehler: {config_key}"
        if message:
            msg += f" - {message}"
        super().__init__(msg)


# === Cache Errors ===

class CacheError(OrionArchitektError):
    """Raised when cache operations fail"""
    pass


class CacheInvalidationError(CacheError):
    """Raised when cache invalidation fails"""
    def __init__(self, cache_key):
        self.cache_key = cache_key
        super().__init__(f"Cache invalidation failed for key: {cache_key}")


# Convenience functions for error handling

def validate_bundesland(bundesland):
    """
    Validate that bundesland is one of the 9 Austrian Bundesländer.

    Args:
        bundesland: Bundesland name (lowercase)

    Raises:
        InvalidBundeslandError: If bundesland is invalid

    Returns:
        str: The validated bundesland name
    """
    valid_bundeslaender = [
        "burgenland", "kaernten", "niederoesterreich",
        "oberoesterreich", "salzburg", "steiermark",
        "tirol", "vorarlberg", "wien"
    ]

    if bundesland.lower() not in valid_bundeslaender:
        raise InvalidBundeslandError(bundesland)

    return bundesland.lower()


def require_field(data, field_name, expected_type=None):
    """
    Validate that a required field exists in data.

    Args:
        data: Dictionary containing the data
        field_name: Name of required field
        expected_type: Optional type to check against

    Raises:
        MissingDataError: If field is missing
        InvalidDataError: If field has wrong type

    Returns:
        The value of the field
    """
    if field_name not in data:
        raise MissingDataError(field_name)

    value = data[field_name]

    if expected_type and not isinstance(value, expected_type):
        raise InvalidDataError(
            field_name,
            value,
            expected_type=expected_type.__name__
        )

    return value


# Error context manager for better error messages

class ErrorContext:
    """Context manager for adding context to errors"""

    def __init__(self, context_message):
        self.context_message = context_message

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val and isinstance(exc_val, OrionArchitektError):
            # Add context to the error message
            exc_val.args = (f"{self.context_message}: {exc_val}",)
        return False  # Don't suppress the exception
