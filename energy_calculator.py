import math

class EnergyCalculator:
    def __init__(self):
        # System specifications
        self.core_max_power_gw = 200.0
        self.conduit_diameter_m = 48 * 0.0254  # 48 inches to meters
        self.pfc_density_gwh_per_m3 = 2.5  # PulseField Charge density
        self.startup_energy_gwh = 2217.3 / 1000  # Convert GJ to GWh
        self.generation_efficiency = 0.9  # 90% efficiency
        
        # Scenario definitions
        self.scenarios = {
            "Peak Demand": {"spin_time_min": 15, "frequency_per_day": 4},
            "Base Load": {"spin_time_min": 30, "frequency_per_day": 2},
            "Emergency": {"spin_time_min": 60, "frequency_per_day": 1},
            "Storage Fill": {"spin_time_min": 120, "frequency_per_day": 0.5}
        }
        
    def calculate_conduit_capacity(self, length_miles, diameter_m):
        """Calculate energy storage capacity of a SuperConduit"""
        length_m = length_miles * 1609.34  # Convert miles to meters
        volume_m3 = math.pi * (diameter_m / 2) ** 2 * length_m
        return volume_m3 * self.pfc_density_gwh_per_m3
        
    def calculate_network_capacity(self, length_miles, num_conduits):
        """Calculate total network storage capacity"""
        single_conduit_capacity = self.calculate_conduit_capacity(length_miles, self.conduit_diameter_m)
        return single_conduit_capacity * num_conduits
        
    def calculate_daily_energy(self, scenario):
        """Calculate daily energy generation for a scenario"""
        spin_time_hours = scenario["spin_time_min"] / 60
        frequency = scenario["frequency_per_day"]
        daily_energy = spin_time_hours * self.core_max_power_gw * frequency
        return daily_energy
        
    def calculate_net_energy_gain(self, scenario):
        """Calculate net energy gain after accounting for startup costs"""
        daily_energy = self.calculate_daily_energy(scenario)
        startup_costs = self.startup_energy_gwh * scenario["frequency_per_day"]
        return daily_energy - startup_costs
        
    def calculate_efficiency(self):
        """Calculate overall system efficiency"""
        return self.generation_efficiency * 100
        
    def get_startup_energy(self):
        """Get startup energy requirement"""
        return self.startup_energy_gwh
        
    def calculate_break_even_time(self):
        """Calculate break-even time for energy generation"""
        return self.startup_energy_gwh / self.core_max_power_gw  # Hours
        
    def calculate_storage_duration(self, capacity_gwh, power_gw):
        """Calculate how long stored energy will last at given power"""
        return capacity_gwh / power_gw  # Hours
        
    def analyze_scenario_efficiency(self, scenario_name):
        """Analyze efficiency of a specific scenario"""
        scenario = self.scenarios[scenario_name]
        
        # Energy calculations
        daily_energy = self.calculate_daily_energy(scenario)
        startup_costs = self.startup_energy_gwh * scenario["frequency_per_day"]
        net_energy = daily_energy - startup_costs
        efficiency_ratio = daily_energy / startup_costs if startup_costs > 0 else 0
        
        return {
            "scenario": scenario_name,
            "daily_energy_gwh": daily_energy,
            "startup_costs_gwh": startup_costs,
            "net_energy_gwh": net_energy,
            "efficiency_ratio": efficiency_ratio,
            "break_even_minutes": self.calculate_break_even_time() * 60
        }
        
    def calculate_pfc_advantages(self):
        """Calculate PulseField Charge storage advantages"""
        return {
            "no_leakage": True,
            "dimensionless_energy": True,
            "universal_conversion": True,
            "energy_density": self.pfc_density_gwh_per_m3,
            "storage_efficiency": 100,  # No losses in PFC storage
            "retrieval_efficiency": 95   # 95% efficiency in energy retrieval
        }
        
    def compare_operational_models(self):
        """Compare continuous vs on-demand operational models"""
        continuous_model = {
            "startup_energy": self.startup_energy_gwh,
            "continuous_stress": 100,  # 100% material stress continuously
            "safety_risk": 2217.3,    # Continuous kinetic energy in GJ
            "maintenance_downtime": 24  # Hours per month
        }
        
        ondemand_model = {
            "startup_energy_per_cycle": self.startup_energy_gwh,
            "stress_only_during_generation": True,
            "safety_risk_at_rest": 0,
            "maintenance_downtime": 0  # No downtime - maintenance when at rest
        }
        
        return {
            "continuous": continuous_model,
            "on_demand": ondemand_model,
            "advantage_factor": {
                "safety": "infinite",  # Zero risk when at rest vs continuous risk
                "maintenance": "infinite",  # Zero downtime vs scheduled downtime
                "material_longevity": 10  # 10x longer material life
            }
        }
        
    def calculate_network_redundancy_benefits(self, total_conduits, active_conduits):
        """Calculate benefits of network redundancy"""
        redundancy_factor = total_conduits / active_conduits
        standby_conduits = total_conduits - active_conduits
        
        return {
            "redundancy_factor": redundancy_factor,
            "standby_conduits": standby_conduits,
            "failover_time": 0,  # Instant failover
            "system_availability": 99.99,  # 99.99% uptime
            "load_balancing": True,
            "maintenance_capability": "hot_swap"  # Maintenance without downtime
        }
        
    def project_planetary_scale_impact(self, num_facilities):
        """Project impact of planetary-scale deployment"""
        single_facility_daily_gwh = self.calculate_daily_energy(self.scenarios["Base Load"])
        total_daily_gwh = single_facility_daily_gwh * num_facilities
        
        # Global energy consumption approximation
        global_daily_consumption_gwh = 65000  # Approximate global daily consumption
        
        coverage_percentage = (total_daily_gwh / global_daily_consumption_gwh) * 100
        
        return {
            "facilities": num_facilities,
            "total_daily_energy_gwh": total_daily_gwh,
            "global_coverage_percentage": min(coverage_percentage, 100),
            "co2_reduction_potential": total_daily_gwh * 0.5,  # Assuming 0.5 kg CO2/kWh saved
            "fossil_fuel_displacement": "complete" if coverage_percentage >= 100 else "partial"
        }
