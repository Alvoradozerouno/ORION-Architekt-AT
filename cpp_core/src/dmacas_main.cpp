/**
 * =============================================================================
 * DMACAS V3.0.1 – MAIN ENTRY POINT
 * =============================================================================
 * Deterministic Multi-Agent Collision Avoidance System
 * Adapted for ORION Architekt-AT Building Safety Applications
 *
 * Example: Structural load path analysis with audit trail
 *
 * Version: 3.0.1 (Integrated with ORION 2026-04-06)
 *
 * Copyright (c) 2024-2026 Elisabeth Steurer & Gerhard Hirschmann
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 *
 * Created: 2026-04-06
 * Location: Almdorf 9, St. Johann in Tirol, Austria
 * Part of: GENESIS DUAL-SYSTEM (DMACAS + BSH-Träger EC5-AT)
 * =============================================================================
 */

#include "dmacas_types.hpp"
#include "dmacas_audit.hpp"
#include <iostream>
#include <iomanip>

using namespace orion::safety;

/**
 * Print safety metrics
 */
void print_safety_metrics(const SafetyMetrics& metrics) {
    std::cout << "\n=== Safety Metrics ===\n";
    std::cout << "Min Distance: " << metrics.min_distance_m << " m\n";
    std::cout << "Collision Count: " << metrics.collision_count << "\n";
    std::cout << "Collision Probability: " << (metrics.collision_probability * 100.0) << "%\n";
    std::cout << "Safety Score: " << metrics.safety_score() << "/100\n";
    std::cout << "Is Safe: " << (metrics.is_safe() ? "YES" : "NO") << "\n";
}

/**
 * Print multi-agent decision
 */
void print_decision(const MultiAgentDecision& decision) {
    std::cout << "\n=== Decision ===\n";
    std::cout << "Decision ID: " << decision.decision_id << "\n";
    std::cout << "Safety Class: ";
    switch (decision.worst_safety_class) {
        case SafetyClass::SAFE: std::cout << "SAFE"; break;
        case SafetyClass::WARNING: std::cout << "WARNING"; break;
        case SafetyClass::CAUTION: std::cout << "CAUTION"; break;
        case SafetyClass::CRITICAL: std::cout << "CRITICAL"; break;
        case SafetyClass::UNSAFE: std::cout << "UNSAFE"; break;
    }
    std::cout << "\n";

    std::cout << "Operation Mode: ";
    switch (decision.mode) {
        case OperationMode::NORMAL: std::cout << "NORMAL"; break;
        case OperationMode::DEGRADED: std::cout << "DEGRADED"; break;
        case OperationMode::EMERGENCY: std::cout << "EMERGENCY"; break;
        case OperationMode::SAFE_STOP: std::cout << "SAFE_STOP"; break;
    }
    std::cout << "\n";

    std::cout << "Confidence: " << (decision.confidence_score * 100.0) << "%\n";
    std::cout << "Safety Rating: " << decision.get_safety_rating() << "/100\n";
    std::cout << "Safe to Execute: " << (decision.is_safe_to_execute() ? "YES" : "NO") << "\n";
    std::cout << "Rationale: " << decision.rationale << "\n";
}

/**
 * Example 1: Simple structural load path analysis
 */
void example_load_path_analysis() {
    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════════╗\n";
    std::cout << "║   EXAMPLE 1: Structural Load Path Analysis                ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════╝\n";

    // Create building elements (roof -> column -> foundation)
    std::vector<AgentState2D> elements;

    // Roof slab
    AgentState2D roof;
    roof.id = 1;
    roof.x_m = 10.0;
    roof.y_m = 20.0;  // 20m height
    roof.mass_kg = 5000.0;  // 5 tons
    elements.push_back(roof);

    // Column
    AgentState2D column;
    column.id = 2;
    column.x_m = 10.0;
    column.y_m = 10.0;
    column.mass_kg = 3000.0;
    elements.push_back(column);

    // Foundation
    AgentState2D foundation;
    foundation.id = 3;
    foundation.x_m = 10.0;
    foundation.y_m = 0.0;
    foundation.mass_kg = 10000.0;
    elements.push_back(foundation);

    // Create trajectory
    Trajectory2D load_path;
    for (const auto& elem : elements) {
        load_path.add_state(elem);
    }

    std::cout << "Load Path Length: " << load_path.total_length_m() << " m\n";
    std::cout << "Total Mass: " << (roof.mass_kg + column.mass_kg + foundation.mass_kg) / 1000.0 << " tons\n";

    // Analyze with DMACAS
    DMACASCoordinator coordinator;
    MultiAgentDecision decision = coordinator.optimize_multi_agent(elements);

    print_decision(decision);

    // Create audit entry
    coordinator.create_audit_entry(elements, decision);

    std::cout << "\n✓ Audit entry created\n";
}

/**
 * Example 2: Clash detection
 */
void example_clash_detection() {
    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════════╗\n";
    std::cout << "║   EXAMPLE 2: BIM Clash Detection                          ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════╝\n";

    std::vector<AgentState2D> elements;

    // Wall
    AgentState2D wall;
    wall.id = 10;
    wall.x_m = 5.0;
    wall.y_m = 3.0;
    wall.mass_kg = 2000.0;
    elements.push_back(wall);

    // Duct (too close - clash!)
    AgentState2D duct;
    duct.id = 11;
    duct.x_m = 5.2;  // Only 20cm away
    duct.y_m = 3.1;
    duct.mass_kg = 50.0;
    elements.push_back(duct);

    // Check distance
    double distance = wall.distance_to(duct);
    std::cout << "Distance between wall and duct: " << distance << " m\n";

    if (distance < 0.5) {
        std::cout << "⚠️  WARNING: Clash detected! (< 0.5m clearance)\n";
    }

    // Analyze with DMACAS
    DMACASCoordinator coordinator;
    MultiAgentDecision decision = coordinator.optimize_multi_agent(elements);

    print_decision(decision);

    coordinator.create_audit_entry(elements, decision);
}

/**
 * Example 3: Determinism verification
 */
void example_determinism_verification() {
    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════════╗\n";
    std::cout << "║   EXAMPLE 3: Determinism Verification                     ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════╝\n";

    std::vector<AgentState2D> elements;

    for (int i = 0; i < 5; ++i) {
        AgentState2D elem;
        elem.id = i;
        elem.x_m = i * 2.0;
        elem.y_m = 5.0;
        elem.mass_kg = 1000.0;
        elements.push_back(elem);
    }

    DMACASCoordinator coordinator;

    std::cout << "Running 20 determinism verification tests...\n";
    bool is_deterministic = coordinator.verify_determinism(elements, 20);

    std::cout << "Result: " << (is_deterministic ? "✓ DETERMINISTIC" : "✗ NON-DETERMINISTIC") << "\n";
    std::cout << "Validation Runs: " << coordinator.get_validation_runs() << "\n";
    std::cout << "Successful: " << coordinator.get_successful_validations() << "\n";
}

/**
 * Example 4: Audit log export
 */
void example_audit_export() {
    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════════╗\n";
    std::cout << "║   EXAMPLE 4: Audit Log Export                             ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════╝\n";

    DMACASCoordinator coordinator;

    // Create some decisions
    for (int run = 0; run < 3; ++run) {
        std::vector<AgentState2D> elements;

        for (int i = 0; i < 3; ++i) {
            AgentState2D elem;
            elem.id = i;
            elem.x_m = i * 3.0 + run;
            elem.y_m = 5.0;
            elements.push_back(elem);
        }

        MultiAgentDecision decision = coordinator.optimize_multi_agent(elements);
        coordinator.create_audit_entry(elements, decision);
    }

    std::cout << "Total audit entries: " << coordinator.get_audit_log().size() << "\n";

    // Export to JSON
    std::string json = coordinator.export_audit_log_json();
    std::cout << "\nAudit Log JSON:\n" << json << "\n";

    std::cout << "\n✓ Audit log exported (ready for RIS Austria, building authorities, etc.)\n";
}

/**
 * Main entry point
 */
int main(int argc, char* argv[]) {
    std::cout << "\n";
    std::cout << "╔════════════════════════════════════════════════════════════╗\n";
    std::cout << "║   ORION DMACAS V3.0.1 – Safety-Critical Building Analysis  ║\n";
    std::cout << "║   Adapted from GENESIS DUAL-SYSTEM (Fraunhofer IKS)       ║\n";
    std::cout << "║   TRL: 5→6 (Production-Ready)                              ║\n";
    std::cout << "╚════════════════════════════════════════════════════════════╝\n";

    try {
        // Run examples
        example_load_path_analysis();
        example_clash_detection();
        example_determinism_verification();
        example_audit_export();

        std::cout << "\n";
        std::cout << "╔════════════════════════════════════════════════════════════╗\n";
        std::cout << "║   All examples completed successfully! ✓                   ║\n";
        std::cout << "╚════════════════════════════════════════════════════════════╝\n";
        std::cout << "\n";

        return 0;

    } catch (const std::exception& e) {
        std::cerr << "\n✗ ERROR: " << e.what() << "\n";
        return 1;
    }
}
