import math
import time
import numpy as np
from datetime import datetime

class CoreSimulator:
    def __init__(self):
        # Core specifications from the document
        self.max_power_gw = 200.0  # GW at 200k RPM
        self.core_mass = 199  # kg
        self.core_radius = 1.5  # meters
        self.max_rpm = 200000  # Maximum RPM
        self.startup_energy_gj = 2217.3  # GJ required for startup
        
        # Current state
        self.current_rpm = 0
        self.target_rpm = 0
        self.is_spinning = False
        self.spin_start_time = None
        self.spin_duration_minutes = 0
        self.acceleration_rate = 1000  # RPM per second during startup
        
        # Energy tracking
        self.total_energy_generated = 0
        self.spin_cycles_completed = 0
        
    def start_spin_cycle(self, duration_minutes):
        """Start a new spin cycle with specified duration"""
        self.spin_duration_minutes = duration_minutes
        self.target_rpm = self.max_rpm
        self.is_spinning = True
        self.spin_start_time = time.time()
        self.spin_cycles_completed += 1
        
    def emergency_stop(self):
        """Emergency stop - immediate shutdown"""
        self.target_rpm = 0
        self.is_spinning = False
        self.spin_start_time = None
        
    def update_simulation(self):
        """Update the simulation state"""
        if not self.is_spinning:
            self.current_rpm = 0
            return
            
        current_time = time.time()
        elapsed_time = current_time - self.spin_start_time if self.spin_start_time else 0
        
        # Spin up phase (15 minutes to reach max RPM)
        spinup_time_seconds = 15 * 60  # 15 minutes
        
        if elapsed_time < spinup_time_seconds:
            # Accelerating to target RPM
            progress = elapsed_time / spinup_time_seconds
            self.current_rpm = self.target_rpm * progress
        elif elapsed_time < (self.spin_duration_minutes * 60):
            # At maximum RPM
            self.current_rpm = self.target_rpm
        else:
            # Spin down phase (natural deceleration)
            self.current_rpm = max(0, self.current_rpm - self.acceleration_rate)
            if self.current_rpm <= 0:
                self.is_spinning = False
                self.spin_start_time = None
                
    def get_current_rpm(self):
        """Get current RPM"""
        self.update_simulation()
        return self.current_rpm
        
    def get_current_power(self):
        """Get current power output in GW"""
        self.update_simulation()
        # Power scales with RPM (linear approximation)
        power_ratio = self.current_rpm / self.max_rpm
        return self.max_power_gw * power_ratio
        
    def get_kinetic_energy(self):
        """Get current kinetic energy in GJ"""
        self.update_simulation()
        # KE = 0.5 * I * ω²
        # I = 0.5 * m * r² for solid cylinder
        moment_of_inertia = 0.5 * self.core_mass * (self.core_radius ** 2)
        angular_velocity = (self.current_rpm * 2 * math.pi) / 60  # rad/s
        kinetic_energy_j = 0.5 * moment_of_inertia * (angular_velocity ** 2)
        return kinetic_energy_j / 1e9  # Convert to GJ
        
    def get_startup_energy_required(self):
        """Get startup energy required in GWh"""
        return self.startup_energy_gj / 1000  # Convert GJ to GWh
        
    def calculate_energy_generated(self, duration_minutes):
        """Calculate energy generated over a duration"""
        power_gw = self.get_current_power()
        duration_hours = duration_minutes / 60
        return power_gw * duration_hours
        
    def get_simulation_stats(self):
        """Get overall simulation statistics"""
        return {
            "total_energy_generated": self.total_energy_generated,
            "spin_cycles_completed": self.spin_cycles_completed,
            "current_rpm": self.get_current_rpm(),
            "current_power": self.get_current_power(),
            "kinetic_energy": self.get_kinetic_energy(),
            "is_spinning": self.is_spinning
        }
        
    def calculate_material_stress(self):
        """Calculate current material stress level"""
        # Centrifugal stress increases with RPM²
        stress_factor = (self.current_rpm / self.max_rpm) ** 2
        return stress_factor * 100  # Percentage of maximum stress
        
    def get_safety_status(self):
        """Get current safety status"""
        kinetic_energy = self.get_kinetic_energy()
        rpm = self.get_current_rpm()
        
        if rpm == 0:
            return {
                "status": "MAXIMUM SAFETY",
                "level": "green",
                "message": "Core at rest - Zero kinetic energy hazard"
            }
        elif rpm < 50000:
            return {
                "status": "LOW RISK",
                "level": "yellow",
                "message": "Low speed operation - minimal risk"
            }
        elif rpm < 150000:
            return {
                "status": "MODERATE RISK",
                "level": "orange",
                "message": "High speed operation - monitoring required"
            }
        else:
            return {
                "status": "HIGH ENERGY",
                "level": "red",
                "message": "Maximum operational speed - full safety protocols active"
            }
