#!/usr/bin/env python3

"""
Architecture Verification Script for OpenTalent

This script automates the verification of the architectural claims made in the
`gap_analysis_report.md` and `gap_analysis_verification.md` documents.

It inspects the codebase to ensure that the described patterns and gaps
are accurate representations of the current state of the system.
"""

import ast
from pathlib import Path

# ==============================================================================
# Helper Functions
# ==============================================================================


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return Path(path).is_file()


def class_defined_in_file(path: str, class_name: str) -> bool:
    """Check if a class is defined in a Python file."""
    if not file_exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return True
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  [Warning] Could not parse {path}: {e}")
        return False
    return False


def function_defined_in_file(path: str, func_name: str) -> bool:
    """Check if a function is defined in a Python file."""
    if not file_exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func_name:
                return True
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  [Warning] Could not parse {path}: {e}")
        return False
    return False


def variable_defined_in_file(path: str, var_name: str) -> bool:
    """Check if a variable is defined in a Python file."""
    if not file_exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=path)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        return True
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"  [Warning] Could not parse {path}: {e}")
        return False
    return False


def string_in_file(path: str, search_string: str) -> bool:
    """Check if a string exists in a file."""
    if not file_exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            return search_string in f.read()
    except UnicodeDecodeError as e:
        print(f"  [Warning] Could not read {path}: {e}")
        return False


# ==============================================================================
# Verification Checks
# ==============================================================================


class VerificationResult:
    """Holds the result of a verification check."""

    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message

    def __str__(self):
        return f"[{'✅' if self.success else '❌'}] {self.message}"


def check_scout_service_is_central_nervous_system() -> VerificationResult:
    """Verify the 'Central Nervous System' pattern of the scout-service."""
    path = "services/scout-service/main.py"
    registry_found = string_in_file(path, "get_agent_registry")
    router_found = class_defined_in_file("services/scout-service/agent_routes.py", "AgentRouter")

    success = registry_found and router_found
    message = "scout-service acts as a Central Nervous System (Registry & Router)."
    if not success:
        details = []
        if not registry_found:
            details.append("AgentRegistry not found")
        if not router_found:
            details.append("AgentRouter not found")
        message += f" Failed: {', '.join(details)}."

    return VerificationResult(success, message)


def check_scout_service_has_sourcing_logic() -> VerificationResult:
    """Verify that scout-service contains its own sourcing logic."""
    path = "services/scout-service/main.py"
    class_found = class_defined_in_file(path, "GitHubTalentScout")

    success = class_found
    message = "scout-service contains its own sourcing logic (`GitHubTalentScout`)."
    if not success:
        message += " Failed: Class `GitHubTalentScout` not found."

    return VerificationResult(success, message)


def check_scout_coordinator_is_orchestrator() -> VerificationResult:
    """Verify the 'Orchestrator' pattern of the scout-coordinator-agent."""
    path = "agents/scout-coordinator-agent/main.py"
    model_imported = string_in_file(path, "from shared import SourcingPipeline") or string_in_file(
        path, "SourcingPipeline,"
    )
    model_defined = class_defined_in_file("agents/shared/models.py", "SourcingPipeline")
    state_machine_found = function_defined_in_file(path, "transition_pipeline")

    success = (model_imported and model_defined) and state_machine_found
    message = "scout-coordinator-agent acts as an Orchestrator."
    if not success:
        details = []
        if not model_imported:
            details.append("`SourcingPipeline` model not imported in coordinator")
        if not model_defined:
            details.append("`SourcingPipeline` model not defined in shared/models.py")
        if not state_machine_found:
            details.append("`transition_pipeline` function not found")
        message += f" Failed: {', '.join(details)}."

    return VerificationResult(success, message)


def check_scout_coordinator_uses_message_bus() -> VerificationResult:
    """Verify that scout-coordinator-agent uses a message bus."""
    path = "agents/scout-coordinator-agent/main.py"
    string_found = string_in_file(path, "message_bus.publish_event")

    success = string_found
    message = "scout-coordinator-agent uses a message bus for communication."
    if not success:
        message += " Failed: `message_bus.publish_event` not found."

    return VerificationResult(success, message)


def check_specialized_worker_pattern() -> VerificationResult:
    """Verify the 'Specialized Worker' pattern for multiple agents."""
    checks = {
        "boolean-mastery-agent": function_defined_in_file(
            "agents/boolean-mastery-agent/main.py", "handle_query_request"
        ),
        "data-enrichment-agent": function_defined_in_file(
            "agents/data-enrichment-agent/main.py", "handle_enrichment_request"
        ),
        "interviewer-agent": function_defined_in_file(
            "agents/interviewer-agent/main.py", "handle_candidate_event"
        ),
    }

    failed_agents = [agent for agent, result in checks.items() if not result]

    success = not failed_agents
    message = "Agents exhibit the 'Specialized Worker' pattern."
    if not success:
        message += f" Failed for: {', '.join(failed_agents)}."

    return VerificationResult(success, message)


def check_redundant_functionality() -> VerificationResult:
    """Verify the redundant functionality gap."""
    scout_service_has_sourcing = class_defined_in_file(
        "services/scout-service/main.py", "GitHubTalentScout"
    )
    proactive_agent_exists = file_exists("agents/proactive-scanning-agent/main.py")
    boolean_agent_exists = file_exists("agents/boolean-mastery-agent/main.py")

    success = scout_service_has_sourcing and proactive_agent_exists and boolean_agent_exists
    message = (
        "Gap confirmed: Redundant functionality exists between scout-service and other agents."
    )
    if not success:
        message = "Gap not confirmed: Redundant functionality check inconclusive."

    return VerificationResult(success, message)


def check_static_service_discovery() -> VerificationResult:
    """Verify the static service discovery gap."""
    path = "services/scout-service/agent_registry.py"
    variable_found = variable_defined_in_file(path, "AGENT_CONFIG")

    success = variable_found
    message = "Gap confirmed: Service discovery is static (hardcoded `AGENT_CONFIG`)."
    if not success:
        message = "Gap not confirmed: `AGENT_CONFIG` not found."

    return VerificationResult(success, message)


def check_communication_strategy_gap() -> VerificationResult:
    """Verify the communication strategy gap."""
    message_bus_usage = string_in_file("agents/scout-coordinator-agent/main.py", "MessageBus")
    http_routing = class_defined_in_file("services/scout-service/agent_routes.py", "AgentRouter")

    success = message_bus_usage and http_routing
    message = "Gap confirmed: Both message bus and direct HTTP routing are used."
    if not success:
        message = "Gap not confirmed: Communication strategy check inconclusive."

    return VerificationResult(success, message)


def check_decentralized_configuration() -> VerificationResult:
    """Verify the decentralized configuration gap."""
    files_to_check = [
        "agents/data-enrichment-agent/.env.example",
        "agents/scout-coordinator-agent/.env.example",
        "services/scout-service/.env.example",
    ]

    found_files = [f for f in files_to_check if file_exists(f)]

    success = len(found_files) > 0
    message = f"Gap confirmed: Decentralized configuration found in {len(found_files)} locations."
    if not success:
        message = "Gap not confirmed: No `.env.example` files found in checked locations."

    return VerificationResult(success, message)


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """Run all verification checks and print the results."""
    print("=" * 70)
    print(" Verifying Architectural Claims from gap_analysis_report.md")
    print("=" * 70)

    checks = [
        check_scout_service_is_central_nervous_system,
        check_scout_service_has_sourcing_logic,
        check_scout_coordinator_is_orchestrator,
        check_scout_coordinator_uses_message_bus,
        check_specialized_worker_pattern,
    ]

    print("\n--- Verifying Architectural Patterns ---\\n")
    pattern_results = [check() for check in checks]
    for result in pattern_results:
        print(result)

    print("\n--- Verifying Architectural Gaps ---\\n")

    gap_checks = [
        check_redundant_functionality,
        check_static_service_discovery,
        check_communication_strategy_gap,
        check_decentralized_configuration,
    ]

    gap_results = [check() for check in gap_checks]
    for result in gap_results:
        print(result)

    all_results = pattern_results + gap_results
    total_checks = len(all_results)
    successful_checks = sum(1 for r in all_results if r.success)

    print("\n" + "=" * 70)
    print(" Verification Summary")
    print("-" * 70)
    print(f"  Total Checks: {total_checks}")
    print(f"  Successful:   {successful_checks}")
    print(f"  Failed:       {total_checks - successful_checks}")
    print("=" * 70)

    if successful_checks != total_checks:
        print("\nVerification failed for one or more checks.")
        exit(1)
    else:
        print("\nAll architectural claims successfully verified against the codebase.")
        exit(0)


if __name__ == "__main__":
    main()
