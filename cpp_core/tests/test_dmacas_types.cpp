/**
 * =============================================================================
 * ORION Safety Core - Test Suite for DMACAS Types
 * =============================================================================
 * Tests the deterministic multi-agent system structures.
 *
 * Build & Run:
 *   cd cpp_core/build
 *   cmake ..
 *   make
 *   ctest
 * =============================================================================
 */

#include "dmacas_types.hpp"
#include <gtest/gtest.h>
#include <cmath>

using namespace orion::safety;

// =============================================================================
// AgentState2D Tests
// =============================================================================

TEST(AgentState2D, DefaultConstruction) {
    AgentState2D agent;

    EXPECT_EQ(agent.id, 0);
    EXPECT_DOUBLE_EQ(agent.x_m, 0.0);
    EXPECT_DOUBLE_EQ(agent.y_m, 0.0);
    EXPECT_DOUBLE_EQ(agent.mass_kg, 1500.0);
}

TEST(AgentState2D, SpeedCalculation) {
    AgentState2D agent;
    agent.v_x_mps = 3.0;
    agent.v_y_mps = 4.0;

    // 3-4-5 triangle
    EXPECT_DOUBLE_EQ(agent.speed(), 5.0);
}

TEST(AgentState2D, KineticEnergy) {
    AgentState2D agent;
    agent.mass_kg = 1000.0;  // 1 ton
    agent.v_x_mps = 10.0;    // 10 m/s
    agent.v_y_mps = 0.0;

    // E = 0.5 * m * v^2 = 0.5 * 1000 * 100 = 50000 J
    EXPECT_DOUBLE_EQ(agent.kinetic_energy_joule(), 50000.0);
}

TEST(AgentState2D, DistanceTo) {
    AgentState2D agent1;
    agent1.x_m = 0.0;
    agent1.y_m = 0.0;

    AgentState2D agent2;
    agent2.x_m = 3.0;
    agent2.y_m = 4.0;

    // 3-4-5 triangle
    EXPECT_DOUBLE_EQ(agent1.distance_to(agent2), 5.0);
}

TEST(AgentState2D, CollisionCourse) {
    AgentState2D agent1;
    agent1.x_m = 0.0;
    agent1.y_m = 0.0;
    agent1.v_x_mps = 1.0;  // Moving right
    agent1.v_y_mps = 0.0;

    AgentState2D agent2;
    agent2.x_m = 10.0;
    agent2.y_m = 0.0;
    agent2.v_x_mps = -1.0;  // Moving left (toward agent1)
    agent2.v_y_mps = 0.0;

    EXPECT_TRUE(agent1.on_collision_course(agent2, 5.0));
}

TEST(AgentState2D, NotOnCollisionCourse) {
    AgentState2D agent1;
    agent1.x_m = 0.0;
    agent1.y_m = 0.0;
    agent1.v_x_mps = 0.0;  // Stationary
    agent1.v_y_mps = 0.0;

    AgentState2D agent2;
    agent2.x_m = 10.0;
    agent2.y_m = 0.0;
    agent2.v_x_mps = 1.0;  // Moving away
    agent2.v_y_mps = 0.0;

    EXPECT_FALSE(agent1.on_collision_course(agent2, 5.0));
}

// =============================================================================
// Action2D Tests
// =============================================================================

TEST(Action2D, DefaultConstruction) {
    Action2D action;

    EXPECT_DOUBLE_EQ(action.a_x_mps2, 0.0);
    EXPECT_DOUBLE_EQ(action.a_y_mps2, 0.0);
}

TEST(Action2D, Magnitude) {
    Action2D action;
    action.a_x_mps2 = 3.0;
    action.a_y_mps2 = 4.0;

    EXPECT_DOUBLE_EQ(action.magnitude(), 5.0);
}

TEST(Action2D, Normalized) {
    Action2D action;
    action.a_x_mps2 = 10.0;
    action.a_y_mps2 = 0.0;

    Action2D norm = action.normalized();

    EXPECT_DOUBLE_EQ(norm.a_x_mps2, 1.0);
    EXPECT_DOUBLE_EQ(norm.a_y_mps2, 0.0);
}

TEST(Action2D, Scaled) {
    Action2D action;
    action.a_x_mps2 = 2.0;
    action.a_y_mps2 = 3.0;

    Action2D scaled = action.scaled(2.5);

    EXPECT_DOUBLE_EQ(scaled.a_x_mps2, 5.0);
    EXPECT_DOUBLE_EQ(scaled.a_y_mps2, 7.5);
}

// =============================================================================
// Trajectory2D Tests
// =============================================================================

TEST(Trajectory2D, DefaultConstruction) {
    Trajectory2D traj;

    EXPECT_EQ(traj.num_points, 0);
    EXPECT_DOUBLE_EQ(traj.time_step_s, 0.1);
}

TEST(Trajectory2D, AddState) {
    Trajectory2D traj;

    AgentState2D state1;
    state1.x_m = 0.0;
    state1.y_m = 0.0;

    EXPECT_TRUE(traj.add_state(state1));
    EXPECT_EQ(traj.num_points, 1);
}

TEST(Trajectory2D, GetState) {
    Trajectory2D traj;

    AgentState2D state1;
    state1.x_m = 1.0;
    state1.y_m = 2.0;

    traj.add_state(state1);

    const AgentState2D* retrieved = traj.get_state(0);
    ASSERT_NE(retrieved, nullptr);
    EXPECT_DOUBLE_EQ(retrieved->x_m, 1.0);
    EXPECT_DOUBLE_EQ(retrieved->y_m, 2.0);
}

TEST(Trajectory2D, TotalLength) {
    Trajectory2D traj;

    AgentState2D state1;
    state1.x_m = 0.0;
    state1.y_m = 0.0;

    AgentState2D state2;
    state2.x_m = 3.0;
    state2.y_m = 0.0;

    AgentState2D state3;
    state3.x_m = 3.0;
    state3.y_m = 4.0;

    traj.add_state(state1);
    traj.add_state(state2);
    traj.add_state(state3);

    // Total: 3m + 4m = 7m
    EXPECT_DOUBLE_EQ(traj.total_length_m(), 7.0);
}

TEST(Trajectory2D, MaxSpeed) {
    Trajectory2D traj;

    AgentState2D state1;
    state1.v_x_mps = 5.0;
    state1.v_y_mps = 0.0;

    AgentState2D state2;
    state2.v_x_mps = 3.0;
    state2.v_y_mps = 4.0;  // speed = 5

    AgentState2D state3;
    state3.v_x_mps = 6.0;
    state3.v_y_mps = 8.0;  // speed = 10 (max)

    traj.add_state(state1);
    traj.add_state(state2);
    traj.add_state(state3);

    EXPECT_DOUBLE_EQ(traj.max_speed_mps(), 10.0);
}

TEST(Trajectory2D, Intersection) {
    Trajectory2D traj1;

    AgentState2D s1;
    s1.x_m = 0.0;
    s1.y_m = 0.0;

    AgentState2D s2;
    s2.x_m = 10.0;
    s2.y_m = 0.0;

    traj1.add_state(s1);
    traj1.add_state(s2);

    // Intersecting trajectory
    Trajectory2D traj2;

    AgentState2D s3;
    s3.x_m = 5.0;
    s3.y_m = -5.0;

    AgentState2D s4;
    s4.x_m = 5.0;
    s4.y_m = 5.0;

    traj2.add_state(s3);
    traj2.add_state(s4);

    // Should intersect near (5, 0)
    EXPECT_TRUE(traj1.intersects_with(traj2, 1.0));
}

// =============================================================================
// CollisionEvent Tests
// =============================================================================

TEST(CollisionEvent, SeverityScore) {
    CollisionEvent event;
    event.impact_energy_joule = 100000.0;  // 100 kJ
    event.relative_speed_mps = 10.0;       // 10 m/s

    double score = event.severity_score();

    // (100000/100000)*5 + (10/10)*5 = 5 + 5 = 10
    EXPECT_DOUBLE_EQ(score, 10.0);
}

TEST(CollisionEvent, IsCritical) {
    CollisionEvent critical;
    critical.impact_energy_joule = 600000.0;  // > 500 kJ

    EXPECT_TRUE(critical.is_critical());

    CollisionEvent minor;
    minor.impact_energy_joule = 10000.0;  // 10 kJ

    EXPECT_FALSE(minor.is_critical());
}

// =============================================================================
// SafetyMetrics Tests
// =============================================================================

TEST(SafetyMetrics, IsSafe) {
    SafetyMetrics safe;
    safe.min_distance_m = 5.0;
    safe.collision_count = 0;
    safe.collision_probability = 0.05;

    EXPECT_TRUE(safe.is_safe(2.0));
}

TEST(SafetyMetrics, IsUnsafe) {
    SafetyMetrics unsafe;
    unsafe.min_distance_m = 1.0;  // Too close
    unsafe.collision_count = 0;
    unsafe.collision_probability = 0.05;

    EXPECT_FALSE(unsafe.is_safe(2.0));
}

TEST(SafetyMetrics, SafetyScore) {
    SafetyMetrics perfect;
    perfect.min_distance_m = 10.0;
    perfect.collision_count = 0;
    perfect.collision_probability = 0.0;

    EXPECT_DOUBLE_EQ(perfect.safety_score(), 100.0);

    SafetyMetrics poor;
    poor.min_distance_m = 1.0;  // -30
    poor.collision_count = 2;   // -40
    poor.collision_probability = 0.5;  // -25

    // 100 - 30 - 40 - 25 = 5
    EXPECT_DOUBLE_EQ(poor.safety_score(), 5.0);
}

// =============================================================================
// Integration Tests
// =============================================================================

TEST(Integration, SimulateLoadPath) {
    // Simulate structural load path through building

    Trajectory2D load_path;

    // Start at roof
    AgentState2D roof;
    roof.id = 1;
    roof.x_m = 10.0;
    roof.y_m = 20.0;  // 20m high
    roof.mass_kg = 5000.0;  // 5 ton roof slab

    // Column
    AgentState2D column;
    column.id = 2;
    column.x_m = 10.0;
    column.y_m = 10.0;
    column.mass_kg = 3000.0;

    // Foundation
    AgentState2D foundation;
    foundation.id = 3;
    foundation.x_m = 10.0;
    foundation.y_m = 0.0;
    foundation.mass_kg = 10000.0;

    load_path.add_state(roof);
    load_path.add_state(column);
    load_path.add_state(foundation);

    // Check load path length (should be 20m vertical)
    EXPECT_DOUBLE_EQ(load_path.total_length_m(), 20.0);

    // Check structure stability
    SafetyMetrics metrics;
    metrics.min_distance_m = 3.0;  // 3m between elements
    metrics.collision_count = 0;   // No clashes
    metrics.collision_probability = 0.0;

    EXPECT_TRUE(metrics.is_safe(2.0));
    EXPECT_GE(metrics.safety_score(), 85.0);  // High safety score
}

int main(int argc, char **argv) {
    ::testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
