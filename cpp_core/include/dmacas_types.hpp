#pragma once
/**
 * =============================================================================
 * DMACAS TYPES – GENESIS DUAL-SYSTEM V3.0.1
 * =============================================================================
 * Deterministic Multi-Agent Collision Avoidance System
 * Adapted for ORION Architekt-AT Safety-Critical Building Calculations
 *
 * Original: Fraunhofer IKS Proposal v1.0
 * Adaptation: ORION Building Physics & Structural Analysis
 * Standard: ISO 26262 ASIL-D principles → Applied to Building Safety
 * TRL: 5→6 (Validierung im relevanten Umfeld)
 *
 * Use Cases for ORION:
 * - Deterministic structural load calculations
 * - Multi-agent building element interactions
 * - Safety-critical fire/escape route simulations
 * - Energy flow optimization (thermal dynamics)
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

#ifndef DMACAS_TYPES_HPP
#define DMACAS_TYPES_HPP

#include <cstdint>
#include <cmath>
#include <array>
#include <vector>
#include <string>

namespace orion {
namespace safety {

// =============================================================================
// 2D STATE MODEL
// For ORION: Can represent building elements, load points, thermal nodes, etc.
// =============================================================================
struct AgentState2D {
    uint8_t id = 0;                  // Element ID (e.g., wall segment, floor slab)
    double x_m = 0.0;                // Position X in meters
    double y_m = 0.0;                // Position Y in meters
    double v_x_mps = 0.0;            // Velocity X (for dynamic loads, wind)
    double v_y_mps = 0.0;            // Velocity Y
    double a_x_mps2 = 0.0;           // Acceleration X (for seismic analysis)
    double a_y_mps2 = 0.0;           // Acceleration Y
    double mass_kg = 1500.0;         // Mass (for structural elements)
    double heading_rad = 0.0;        // Orientation in radians

    /**
     * Calculate speed magnitude
     * ORION Use: Wind speed, thermal flow velocity
     */
    double speed() const {
        return std::sqrt(v_x_mps * v_x_mps + v_y_mps * v_y_mps);
    }

    /**
     * Calculate kinetic energy
     * ORION Use: Impact forces, seismic energy
     */
    double kinetic_energy_joule() const {
        return 0.5 * mass_kg * speed() * speed();
    }

    /**
     * Calculate distance to another agent
     * ORION Use: Element spacing, thermal node distances
     */
    double distance_to(const AgentState2D& other) const {
        double dx = x_m - other.x_m;
        double dy = y_m - other.y_m;
        return std::sqrt(dx * dx + dy * dy);
    }

    /**
     * Check if collision course with another agent
     * ORION Use: Structural clash detection, thermal bridge detection
     */
    bool on_collision_course(const AgentState2D& other, double time_horizon_s) const {
        // Predict future positions
        double fx1 = x_m + v_x_mps * time_horizon_s;
        double fy1 = y_m + v_y_mps * time_horizon_s;
        double fx2 = other.x_m + other.v_x_mps * time_horizon_s;
        double fy2 = other.y_m + other.v_y_mps * time_horizon_s;

        double future_dist = std::sqrt((fx1-fx2)*(fx1-fx2) + (fy1-fy2)*(fy1-fy2));
        double current_dist = distance_to(other);

        return future_dist < current_dist; // Moving closer
    }
};

// =============================================================================
// 2D ACTION SPACE
// For ORION: Control actions for building systems, load adjustments
// =============================================================================
struct Action2D {
    double a_x_mps2 = 0.0;  // Acceleration X (force/mass)
    double a_y_mps2 = 0.0;  // Acceleration Y

    /**
     * Calculate action magnitude
     * ORION Use: Total force magnitude, load adjustment magnitude
     */
    double magnitude() const {
        return std::sqrt(a_x_mps2 * a_x_mps2 + a_y_mps2 * a_y_mps2);
    }

    /**
     * Normalize action to unit vector
     * ORION Use: Directional analysis
     */
    Action2D normalized() const {
        double mag = magnitude();
        if (mag < 1e-9) return {0.0, 0.0};
        return {a_x_mps2 / mag, a_y_mps2 / mag};
    }

    /**
     * Scale action by factor
     * ORION Use: Safety factor application, load case scaling
     */
    Action2D scaled(double factor) const {
        return {a_x_mps2 * factor, a_y_mps2 * factor};
    }
};

// =============================================================================
// 2D TRAJECTORY
// For ORION: Load paths, thermal flow paths, escape routes
// =============================================================================
struct Trajectory2D {
    static constexpr size_t MAX_TRAJECTORY_POINTS = 100;

    std::array<AgentState2D, MAX_TRAJECTORY_POINTS> states;
    size_t num_points = 0;
    double time_step_s = 0.1;  // Simulation time step

    /**
     * Add state to trajectory
     */
    bool add_state(const AgentState2D& state) {
        if (num_points >= MAX_TRAJECTORY_POINTS) {
            return false;  // Trajectory full
        }
        states[num_points++] = state;
        return true;
    }

    /**
     * Get state at specific index
     */
    const AgentState2D* get_state(size_t index) const {
        if (index >= num_points) return nullptr;
        return &states[index];
    }

    /**
     * Calculate total trajectory length
     * ORION Use: Total escape route length, load path length
     */
    double total_length_m() const {
        if (num_points < 2) return 0.0;

        double length = 0.0;
        for (size_t i = 1; i < num_points; ++i) {
            length += states[i].distance_to(states[i-1]);
        }
        return length;
    }

    /**
     * Calculate maximum speed along trajectory
     * ORION Use: Peak wind speed, maximum thermal flow rate
     */
    double max_speed_mps() const {
        double max_spd = 0.0;
        for (size_t i = 0; i < num_points; ++i) {
            max_spd = std::max(max_spd, states[i].speed());
        }
        return max_spd;
    }

    /**
     * Calculate total energy along trajectory
     * ORION Use: Cumulative energy dissipation, heat transfer
     */
    double total_energy_joule() const {
        double total = 0.0;
        for (size_t i = 0; i < num_points; ++i) {
            total += states[i].kinetic_energy_joule();
        }
        return total;
    }

    /**
     * Check if trajectory intersects with another
     * ORION Use: Escape route conflict detection, load path interference
     */
    bool intersects_with(const Trajectory2D& other, double tolerance_m = 0.5) const {
        for (size_t i = 0; i < num_points; ++i) {
            for (size_t j = 0; j < other.num_points; ++j) {
                if (states[i].distance_to(other.states[j]) < tolerance_m) {
                    return true;
                }
            }
        }
        return false;
    }

    /**
     * Clear trajectory
     */
    void clear() {
        num_points = 0;
    }
};

// =============================================================================
// COLLISION EVENT
// For ORION: Structural failures, thermal bridges, code violations
// =============================================================================
struct CollisionEvent {
    uint8_t agent1_id = 0;
    uint8_t agent2_id = 0;
    double time_s = 0.0;
    double distance_m = 0.0;
    double relative_speed_mps = 0.0;
    double impact_energy_joule = 0.0;
    std::string event_type = "unknown";  // "contact", "collision", "near_miss"

    /**
     * Calculate severity score (0-10)
     * ORION Use: Compliance violation severity, structural risk level
     */
    double severity_score() const {
        // Higher energy and speed = higher severity
        double energy_score = std::min(impact_energy_joule / 100000.0, 5.0);
        double speed_score = std::min(relative_speed_mps / 10.0, 5.0);
        return energy_score + speed_score;
    }

    /**
     * Check if critical event
     * ORION Use: Determine if building code violation is critical
     */
    bool is_critical() const {
        return severity_score() > 7.0 || impact_energy_joule > 500000.0;
    }
};

// =============================================================================
// SAFETY METRICS
// For ORION: Building safety indicators, compliance metrics
// =============================================================================
struct SafetyMetrics {
    double min_distance_m = 0.0;           // Minimum separation
    double time_to_collision_s = 0.0;      // TTC
    double collision_probability = 0.0;    // Risk probability
    size_t collision_count = 0;            // Number of collisions
    double avg_safety_margin_m = 0.0;      // Average safety buffer

    /**
     * Check if metrics pass safety threshold
     * ORION Use: Check OIB-RL compliance thresholds
     */
    bool is_safe(double min_distance_threshold_m = 2.0) const {
        return min_distance_m >= min_distance_threshold_m &&
               collision_count == 0 &&
               collision_probability < 0.1;
    }

    /**
     * Calculate overall safety score (0-100)
     * ORION Use: Building safety rating, compliance score
     */
    double safety_score() const {
        double score = 100.0;

        // Penalize low distances
        if (min_distance_m < 2.0) score -= 30.0;
        else if (min_distance_m < 5.0) score -= 15.0;

        // Penalize collisions
        score -= collision_count * 20.0;

        // Penalize high collision probability
        score -= collision_probability * 50.0;

        return std::max(0.0, std::min(100.0, score));
    }
};

} // namespace safety
} // namespace orion

#endif // DMACAS_TYPES_HPP
