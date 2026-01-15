"""
OpenAPI Schema Validator

Validates OpenAPI schemas for compliance with OpenAPI 3.0+ specification.
Can be used standalone or imported by test suites.

Usage:
    # Validate all services
    python tools/openapi_schema_validator.py --all

    # Validate specific service
    python tools/openapi_schema_validator.py --service notification

    # Validate with detailed output
    python tools/openapi_schema_validator.py --all --verbose

    # Output to file
    python tools/openapi_schema_validator.py --all --output report.json
"""

import argparse
import asyncio
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime

import httpx

# ============================================================================
# OPENAPI VALIDATION RULES
# ============================================================================


@dataclass
class ValidationError:
    """Represents a validation error"""

    level: str  # "error", "warning", "info"
    path: str  # JSON path to error (e.g., "paths./api/v1/users")
    message: str
    suggestion: str | None = None


@dataclass
class ValidationResult:
    """Validation result for a schema"""

    service_name: str
    service_port: int
    is_valid: bool
    openapi_version: str
    title: str
    version: str
    endpoints_count: int
    has_components: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    info: list[ValidationError] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    @property
    def info_count(self) -> int:
        return len(self.info)


# ============================================================================
# OPENAPI VALIDATOR
# ============================================================================


class OpenAPIValidator:
    """Validates OpenAPI schemas"""

    REQUIRED_TOP_LEVEL_FIELDS = ["openapi", "info", "paths"]
    REQUIRED_INFO_FIELDS = ["title", "version"]
    OPENAPI_3_VERSIONS = ["3.0.0", "3.0.1", "3.0.2", "3.0.3", "3.1.0"]

    def __init__(self, service_name: str, service_port: int, schema: dict):
        self.service_name = service_name
        self.service_port = service_port
        self.schema = schema
        self.result = ValidationResult(
            service_name=service_name,
            service_port=service_port,
            is_valid=True,
            openapi_version="",
            title="",
            version="",
            endpoints_count=0,
            has_components=False,
        )

    def validate(self) -> ValidationResult:
        """Run all validations"""
        self._validate_top_level()
        self._validate_info()
        self._validate_paths()
        self._validate_components()
        self._validate_endpoints()

        # Schema is valid only if no errors
        self.result.is_valid = self.result.error_count == 0

        return self.result

    def _validate_top_level(self):
        """Validate top-level fields"""
        # Check required fields exist
        for field in self.REQUIRED_TOP_LEVEL_FIELDS:
            if field not in self.schema:
                self.result.errors.append(
                    ValidationError(
                        level="error",
                        path="$",
                        message=f"Missing required field: '{field}'",
                        suggestion=f"Add '{field}' to the root of your OpenAPI schema",
                    )
                )

        # Validate OpenAPI version
        openapi_version = self.schema.get("openapi", "")
        self.result.openapi_version = openapi_version

        if openapi_version not in self.OPENAPI_3_VERSIONS:
            if openapi_version.startswith("3."):
                self.result.warnings.append(
                    ValidationError(
                        level="warning",
                        path="$.openapi",
                        message=f"OpenAPI version '{openapi_version}' may not be officially supported",
                        suggestion=f"Consider using one of: {', '.join(self.OPENAPI_3_VERSIONS)}",
                    )
                )
            else:
                self.result.errors.append(
                    ValidationError(
                        level="error",
                        path="$.openapi",
                        message=f"Invalid OpenAPI version: '{openapi_version}'",
                        suggestion="Use OpenAPI 3.x (e.g., '3.0.0' or '3.1.0')",
                    )
                )

    def _validate_info(self):
        """Validate info object"""
        info = self.schema.get("info", {})

        # Check required info fields
        for field in self.REQUIRED_INFO_FIELDS:
            if field not in info:
                self.result.errors.append(
                    ValidationError(
                        level="error",
                        path="$.info",
                        message=f"Missing required info field: '{field}'",
                        suggestion=f"Add 'info.{field}' to your schema",
                    )
                )
            else:
                value = info[field]
                if field == "title":
                    self.result.title = value
                elif field == "version":
                    self.result.version = value

        # Warn if description is missing
        if "description" not in info:
            self.result.warnings.append(
                ValidationError(
                    level="warning",
                    path="$.info",
                    message="Missing 'info.description'",
                    suggestion="Add a description of your API to help users understand it",
                )
            )

        # Warn if contact info is missing
        if "contact" not in info:
            self.result.info.append(
                ValidationError(
                    level="info",
                    path="$.info",
                    message="Missing 'info.contact'",
                    suggestion="Consider adding contact information for support",
                )
            )

        # Warn if license is missing
        if "license" not in info:
            self.result.info.append(
                ValidationError(
                    level="info",
                    path="$.info",
                    message="Missing 'info.license'",
                    suggestion="Consider adding license information",
                )
            )

    def _validate_paths(self):
        """Validate paths object"""
        paths = self.schema.get("paths", {})

        if not isinstance(paths, dict):
            self.result.errors.append(
                ValidationError(
                    level="error",
                    path="$.paths",
                    message="'paths' must be an object/dict",
                )
            )
            return

        self.result.endpoints_count = len(paths)

        if len(paths) == 0:
            self.result.warnings.append(
                ValidationError(
                    level="warning",
                    path="$.paths",
                    message="No paths defined",
                    suggestion="Add at least one API endpoint to your schema",
                )
            )

        # Validate each path
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                self.result.errors.append(
                    ValidationError(
                        level="error",
                        path=f"$.paths.{path}",
                        message="Path item must be an object/dict",
                    )
                )
                continue

            # Check for methods
            methods = [
                m
                for m in path_item.keys()
                if m.lower()
                in ["get", "post", "put", "delete", "patch", "options", "head", "trace"]
            ]

            if len(methods) == 0:
                self.result.warnings.append(
                    ValidationError(
                        level="warning",
                        path=f"$.paths.{path}",
                        message=f"No HTTP methods defined for path '{path}'",
                        suggestion="Add at least one HTTP method (get, post, etc.)",
                    )
                )

            # Validate each method
            for method in methods:
                method_item = path_item[method]
                if not isinstance(method_item, dict):
                    continue

                # Check for operation ID
                if "operationId" not in method_item:
                    self.result.info.append(
                        ValidationError(
                            level="info",
                            path=f"$.paths.{path}.{method}",
                            message="Missing 'operationId'",
                            suggestion="Add 'operationId' for better documentation",
                        )
                    )

                # Check for summary/description
                if "summary" not in method_item and "description" not in method_item:
                    self.result.warnings.append(
                        ValidationError(
                            level="warning",
                            path=f"$.paths.{path}.{method}",
                            message="Missing 'summary' or 'description'",
                            suggestion="Add a description of what this endpoint does",
                        )
                    )

    def _validate_components(self):
        """Validate components object"""
        components = self.schema.get("components")
        self.result.has_components = components is not None

        if components:
            if not isinstance(components, dict):
                self.result.errors.append(
                    ValidationError(
                        level="error",
                        path="$.components",
                        message="'components' must be an object/dict",
                    )
                )

    def _validate_endpoints(self):
        """Validate endpoint consistency"""
        paths = self.schema.get("paths", {})

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method in path_item.keys():
                if method.lower() not in [
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "options",
                    "head",
                    "trace",
                ]:
                    continue

                method_item = path_item[method]
                if not isinstance(method_item, dict):
                    continue

                # Check for responses
                if "responses" not in method_item:
                    self.result.errors.append(
                        ValidationError(
                            level="error",
                            path=f"$.paths.{path}.{method}",
                            message="Missing 'responses' field",
                            suggestion="Define at least one response (e.g., 200 for success)",
                        )
                    )
                else:
                    responses = method_item["responses"]
                    if not isinstance(responses, dict) or len(responses) == 0:
                        self.result.errors.append(
                            ValidationError(
                                level="error",
                                path=f"$.paths.{path}.{method}.responses",
                                message="'responses' must contain at least one response code",
                                suggestion="Add at least a 200 response",
                            )
                        )


# ============================================================================
# SCHEMA FETCHER
# ============================================================================


async def fetch_openapi_schema(service_port: int, timeout: int = 5) -> dict | None:
    """Fetch OpenAPI schema from service"""
    base_url = f"http://localhost:{service_port}"

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(f"{base_url}/openapi.json")
            if response.status_code == 200:
                return response.json()
    except Exception as e:
        print(f"Failed to fetch schema from port {service_port}: {e}")

    return None


# ============================================================================
# SERVICE DEFINITIONS
# ============================================================================

SERVICES = {
    "notification": 8011,
    "desktop_integration": 8009,
    "security": 8010,
    "ai_auditing": 8012,
    "explainability": 8013,
    "granite_interview": 8005,
    "interview": 8006,
    "user": 8007,
    "candidate": 8008,
    "scout": 8010,
    "conversation": 8014,
    "voice": 8015,
    "avatar": 8016,
    "analytics": 8017,
}


# ============================================================================
# REPORTING
# ============================================================================


def print_result(result: ValidationResult, verbose: bool = False):
    """Print validation result"""
    status = "✅ VALID" if result.is_valid else "❌ INVALID"

    print(f"\n{status} {result.service_name} (Port {result.service_port})")
    print(f"  OpenAPI: {result.openapi_version}")
    print(f"  Title: {result.title}")
    print(f"  Version: {result.version}")
    print(f"  Endpoints: {result.endpoints_count}")
    print(f"  Components: {'Yes' if result.has_components else 'No'}")

    if result.errors:
        print(f"\n  ❌ Errors ({result.error_count}):")
        for error in result.errors:
            print(f"    - {error.message}")
            if verbose and error.suggestion:
                print(f"      💡 {error.suggestion}")

    if result.warnings:
        print(f"\n  ⚠️  Warnings ({result.warning_count}):")
        for warning in result.warnings:
            print(f"    - {warning.message}")
            if verbose and warning.suggestion:
                print(f"      💡 {warning.suggestion}")

    if verbose and result.info:
        print(f"\n  ℹ️  Info ({result.info_count}):")
        for info in result.info:
            print(f"    - {info.message}")
            if info.suggestion:
                print(f"      💡 {info.suggestion}")


async def validate_all_services(verbose: bool = False) -> list[ValidationResult]:
    """Validate all services"""
    results = []

    for service_name, port in SERVICES.items():
        schema = await fetch_openapi_schema(port)

        if schema is None:
            print(f"⚠️  Skipping {service_name} (not running on port {port})")
            continue

        validator = OpenAPIValidator(service_name, port, schema)
        result = validator.validate()
        results.append(result)

        print_result(result, verbose=verbose)

    return results


async def validate_service(service_name: str, verbose: bool = False) -> ValidationResult | None:
    """Validate specific service"""
    if service_name not in SERVICES:
        print(f"Unknown service: {service_name}")
        print(f"Available services: {', '.join(SERVICES.keys())}")
        return None

    port = SERVICES[service_name]
    schema = await fetch_openapi_schema(port)

    if schema is None:
        print(f"Failed to fetch OpenAPI schema from {service_name} (port {port})")
        return None

    validator = OpenAPIValidator(service_name, port, schema)
    result = validator.validate()

    print_result(result, verbose=verbose)

    return result


def export_results(results: list[ValidationResult], output_file: str):
    """Export results to JSON file"""
    export_data = {
        "timestamp": datetime.now().isoformat(),
        "total_services": len(results),
        "valid_services": sum(1 for r in results if r.is_valid),
        "invalid_services": sum(1 for r in results if not r.is_valid),
        "total_errors": sum(r.error_count for r in results),
        "total_warnings": sum(r.warning_count for r in results),
        "results": [
            {
                **asdict(r),
                "errors": [asdict(e) for e in r.errors],
                "warnings": [asdict(e) for e in r.warnings],
                "info": [asdict(e) for e in r.info],
            }
            for r in results
        ],
    }

    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"\n✅ Report exported to {output_file}")


# ============================================================================
# MAIN
# ============================================================================


async def main():
    parser = argparse.ArgumentParser(description="Validate OpenAPI schemas for all microservices")
    parser.add_argument("--all", action="store_true", help="Validate all services")
    parser.add_argument("--service", help="Validate specific service")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--output", "-o", help="Output file for results (JSON)")

    args = parser.parse_args()

    if not args.all and not args.service:
        parser.print_help()
        return

    print("\n" + "=" * 80)
    print("OpenAPI Schema Validator")
    print("=" * 80)

    results = []

    if args.all:
        results = await validate_all_services(verbose=args.verbose)
    elif args.service:
        result = await validate_service(args.service, verbose=args.verbose)
        if result:
            results = [result]

    # Print summary
    if results:
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        valid = sum(1 for r in results if r.is_valid)
        invalid = sum(1 for r in results if not r.is_valid)

        print(f"Valid Services: {valid}/{len(results)}")
        print(f"Invalid Services: {invalid}/{len(results)}")
        print(f"Total Errors: {sum(r.error_count for r in results)}")
        print(f"Total Warnings: {sum(r.warning_count for r in results)}")

        if args.output:
            export_results(results, args.output)

    print("\n")


if __name__ == "__main__":
    asyncio.run(main())
