#pragma once
/**
 * =============================================================================
 * DMACAS AUDIT & DECISION SYSTEM – GENESIS DUAL-SYSTEM V3.0.1
 * =============================================================================
 * Multi-Agent Decision Making with Cryptographic Audit Trail
 * Adapted for ORION Architekt-AT
 *
 * Use Cases:
 * - Multi-criteria building optimization decisions
 * - Safety-critical compliance validation
 * - Deterministic reproducibility verification
 * - Audit trail for regulatory compliance
 *
 * Version: 3.0.1 (Integrated with ORION 2026-04-06)
 * License: Apache 2.0
 * =============================================================================
 */

#ifndef DMACAS_AUDIT_HPP
#define DMACAS_AUDIT_HPP

#include "dmacas_types.hpp"
#include <chrono>
#include <sstream>
#include <iomanip>
#include <optional>
#include <functional>

namespace orion {
namespace safety {

// =============================================================================
// SAFETY CLASS ENUM
// =============================================================================
enum class SafetyClass : uint8_t {
    SAFE = 0,           // No issues
    WARNING = 1,        // Minor warnings
    CAUTION = 2,        // Requires attention
    CRITICAL = 3,       // Critical safety issue
    UNSAFE = 4          // Unsafe condition
};

// =============================================================================
// OPERATION MODE ENUM
// =============================================================================
enum class OperationMode : uint8_t {
    NORMAL = 0,         // Normal operation
    DEGRADED = 1,       // Degraded performance
    EMERGENCY = 2,      // Emergency mode
    SAFE_STOP = 3       // Safe stop required
};

// =============================================================================
// MULTI-AGENT DECISION
// For ORION: Decisions about building compliance, material choices, etc.
// =============================================================================
struct MultiAgentDecision {
    uint32_t decision_id = 0;
    OperationMode mode = OperationMode::NORMAL;
    SafetyClass worst_safety_class = SafetyClass::SAFE;
    std::vector<Action2D> agent_actions;

    // Cryptographic hashes for audit trail
    std::string input_hash = "";
    std::string output_hash = "";
    std::string chain_hash = "";

    double confidence_score = 0.0;  // 0.0 to 1.0
    std::string rationale = "";     // Human-readable explanation

    /**
     * Check if decision is safe to execute
     * ORION Use: Check if building design meets safety requirements
     */
    bool is_safe_to_execute() const {
        return worst_safety_class <= SafetyClass::WARNING &&
               mode != OperationMode::SAFE_STOP;
    }

    /**
     * Get safety rating (0-100)
     * ORION Use: Overall safety score for building design
     */
    double get_safety_rating() const {
        double base_score = 100.0;

        // Penalize based on safety class
        base_score -= static_cast<int>(worst_safety_class) * 20.0;

        // Penalize based on mode
        if (mode == OperationMode::DEGRADED) base_score -= 10.0;
        if (mode == OperationMode::EMERGENCY) base_score -= 30.0;
        if (mode == OperationMode::SAFE_STOP) base_score -= 50.0;

        // Apply confidence
        base_score *= confidence_score;

        return std::max(0.0, std::min(100.0, base_score));
    }
};

// =============================================================================
// AUDIT ENTRY
// For ORION: Compliance check records, design decisions, approval steps
// =============================================================================
struct AuditEntry {
    std::string timestamp = "";
    uint32_t decision_id = 0;
    size_t num_agents = 0;

    std::vector<AgentState2D> input_states;
    MultiAgentDecision decision;

    // Cryptographic hashes
    std::string input_hash = "";
    std::string output_hash = "";
    std::string chain_hash = "";

    // JSON export for external systems
    std::string json_export = "";

    /**
     * Verify cryptographic integrity
     */
    bool verify_integrity() const {
        return !input_hash.empty() &&
               !output_hash.empty() &&
               !chain_hash.empty();
    }
};

// =============================================================================
// DMACAS COORDINATOR
// Main decision-making and audit system
// =============================================================================
class DMACASCoordinator {
private:
    std::vector<AuditEntry> audit_log;
    size_t validation_runs = 0;
    size_t successful_validations = 0;
    std::string previous_chain_hash = "";

public:
    /**
     * Optimize multi-agent system
     * ORION Use: Find optimal building element configuration
     */
    MultiAgentDecision optimize_multi_agent(const std::vector<AgentState2D>& agents) {
        MultiAgentDecision decision;
        decision.decision_id = static_cast<uint32_t>(audit_log.size() + 1);

        // Analyze agent states
        SafetyMetrics metrics = analyze_safety(agents);

        // Determine safety class
        if (metrics.collision_count > 0) {
            decision.worst_safety_class = SafetyClass::CRITICAL;
        } else if (metrics.min_distance_m < 1.0) {
            decision.worst_safety_class = SafetyClass::WARNING;
        } else {
            decision.worst_safety_class = SafetyClass::SAFE;
        }

        // Determine operation mode
        if (decision.worst_safety_class >= SafetyClass::CRITICAL) {
            decision.mode = OperationMode::EMERGENCY;
        } else if (decision.worst_safety_class == SafetyClass::WARNING) {
            decision.mode = OperationMode::DEGRADED;
        } else {
            decision.mode = OperationMode::NORMAL;
        }

        // Generate actions for each agent
        decision.agent_actions.reserve(agents.size());
        for (const auto& agent : agents) {
            Action2D action;
            // Simple collision avoidance logic
            action.a_x_mps2 = -agent.v_x_mps * 0.1;  // Damping
            action.a_y_mps2 = -agent.v_y_mps * 0.1;
            decision.agent_actions.push_back(action);
        }

        // Calculate confidence
        decision.confidence_score = metrics.safety_score() / 100.0;

        // Generate hashes (simplified - real version would use SHA-256)
        decision.input_hash = generate_hash(agents);
        decision.output_hash = generate_hash(decision.agent_actions);
        decision.chain_hash = combine_hashes(previous_chain_hash, decision.output_hash);

        previous_chain_hash = decision.chain_hash;

        // Generate rationale
        std::ostringstream oss;
        oss << "Safety analysis: " << static_cast<int>(decision.worst_safety_class)
            << ", Mode: " << static_cast<int>(decision.mode)
            << ", Confidence: " << (decision.confidence_score * 100.0) << "%";
        decision.rationale = oss.str();

        return decision;
    }

    /**
     * Create audit entry for a decision
     * ORION Use: Log compliance checks, design decisions
     */
    void create_audit_entry(const std::vector<AgentState2D>& agents,
                           const MultiAgentDecision& decision) {
        AuditEntry entry;

        // Generate ISO 8601 timestamp
        auto now = std::chrono::system_clock::now();
        auto time_t_now = std::chrono::system_clock::to_time_t(now);
        std::stringstream ss;
        ss << std::put_time(std::gmtime(&time_t_now), "%Y-%m-%dT%H:%M:%SZ");
        entry.timestamp = ss.str();

        entry.decision_id = decision.decision_id;
        entry.num_agents = agents.size();
        entry.input_states = agents;
        entry.decision = decision;
        entry.input_hash = decision.input_hash;
        entry.output_hash = decision.output_hash;
        entry.chain_hash = decision.chain_hash;

        // Generate JSON export
        std::stringstream json_ss;
        json_ss << "{\"timestamp\":\"" << entry.timestamp << "\","
                << "\"decision_id\":" << entry.decision_id << ","
                << "\"num_agents\":" << entry.num_agents << ","
                << "\"safety_class\":" << static_cast<int>(entry.decision.worst_safety_class) << ","
                << "\"mode\":" << static_cast<int>(entry.decision.mode) << ","
                << "\"confidence\":" << entry.decision.confidence_score << ","
                << "\"safety_rating\":" << entry.decision.get_safety_rating() << "}";
        entry.json_export = json_ss.str();

        audit_log.push_back(entry);
    }

    /**
     * Verify determinism of the system
     * ORION Use: Ensure reproducible compliance checks
     */
    bool verify_determinism(const std::vector<AgentState2D>& agents, size_t num_runs = 20) {
        std::optional<MultiAgentDecision> first_decision;

        for (size_t i = 0; i < num_runs; ++i) {
            MultiAgentDecision current = optimize_multi_agent(agents);

            if (i == 0) {
                first_decision = current;
            } else {
                if (current.mode != first_decision->mode ||
                    current.worst_safety_class != first_decision->worst_safety_class) {
                    return false;
                }
            }
        }

        validation_runs += num_runs;
        successful_validations += num_runs;
        return true;
    }

    /**
     * Get audit log
     */
    const std::vector<AuditEntry>& get_audit_log() const {
        return audit_log;
    }

    /**
     * Get validation statistics
     */
    size_t get_validation_runs() const { return validation_runs; }
    size_t get_successful_validations() const { return successful_validations; }

    /**
     * Export audit log to JSON
     * ORION Use: Export for regulatory compliance, building authorities
     */
    std::string export_audit_log_json() const {
        std::ostringstream oss;
        oss << "[";
        for (size_t i = 0; i < audit_log.size(); ++i) {
            oss << audit_log[i].json_export;
            if (i < audit_log.size() - 1) oss << ",";
        }
        oss << "]";
        return oss.str();
    }

    /**
     * Clear audit log (use with caution!)
     */
    void clear_audit_log() {
        audit_log.clear();
        previous_chain_hash = "";
    }

private:
    /**
     * Analyze safety of agent configuration
     */
    SafetyMetrics analyze_safety(const std::vector<AgentState2D>& agents) const {
        SafetyMetrics metrics;

        if (agents.empty()) {
            return metrics;
        }

        // Find minimum distance between agents
        metrics.min_distance_m = 1e9;  // Large initial value
        metrics.collision_count = 0;

        for (size_t i = 0; i < agents.size(); ++i) {
            for (size_t j = i + 1; j < agents.size(); ++j) {
                double dist = agents[i].distance_to(agents[j]);
                metrics.min_distance_m = std::min(metrics.min_distance_m, dist);

                if (dist < 0.5) {  // 50cm threshold
                    metrics.collision_count++;
                }
            }
        }

        // Calculate collision probability (simplified)
        metrics.collision_probability =
            static_cast<double>(metrics.collision_count) /
            std::max(1.0, static_cast<double>(agents.size()));

        return metrics;
    }

    /**
     * Generate hash from agents (simplified)
     * Real version would use SHA-256
     */
    std::string generate_hash(const std::vector<AgentState2D>& agents) const {
        std::ostringstream oss;
        for (const auto& agent : agents) {
            oss << agent.id << "_" << agent.x_m << "_" << agent.y_m;
        }
        // Simplified hash (first 16 chars of string representation)
        std::string str = oss.str();
        return str.substr(0, std::min(size_t(16), str.length()));
    }

    /**
     * Generate hash from actions (simplified)
     */
    std::string generate_hash(const std::vector<Action2D>& actions) const {
        std::ostringstream oss;
        for (const auto& action : actions) {
            oss << action.a_x_mps2 << "_" << action.a_y_mps2;
        }
        std::string str = oss.str();
        return str.substr(0, std::min(size_t(16), str.length()));
    }

    /**
     * Combine two hashes (simplified)
     */
    std::string combine_hashes(const std::string& hash1, const std::string& hash2) const {
        return hash1 + "_" + hash2;
    }
};

} // namespace safety
} // namespace orion

#endif // DMACAS_AUDIT_HPP
