import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import math
from datetime import datetime, timedelta

from core_simulator import CoreSimulator
from energy_calculator import EnergyCalculator
from network_visualizer import NetworkVisualizer

# Configure page
st.set_page_config(
    page_title="PulseSuperConduit Energy System Simulation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'simulator' not in st.session_state:
    st.session_state.simulator = CoreSimulator()
if 'calculator' not in st.session_state:
    st.session_state.calculator = EnergyCalculator()
if 'visualizer' not in st.session_state:
    st.session_state.visualizer = NetworkVisualizer()
if 'simulation_running' not in st.session_state:
    st.session_state.simulation_running = False
if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = None

def main():
    st.title("⚡ PulseSuperConduit Energy System Simulation")
    st.markdown("*Revolutionary On-Demand Core Spinning with Underground Energy Storage*")
    
    # Sidebar controls
    st.sidebar.header("🎛️ System Controls")
    
    # Core specifications display
    st.sidebar.subheader("Core Specifications")
    st.sidebar.info(f"""
    **Max Power:** 200 GW @ 200k RPM  
    **Core Mass:** 199 kg  
    **Core Radius:** 1.5 m  
    **Startup Energy:** 2,217 GJ  
    **Design Target:** 50 GW @ 80k → 200 GW @ 200k RPM
    """)
    
    # Conduit configuration
    st.sidebar.subheader("SuperConduit Network")
    conduit_length = st.sidebar.slider("Conduit Length (miles)", 2, 5, 4)
    num_conduits = st.sidebar.slider("Number of Conduits", 2, 5, 3)
    active_conduits = st.sidebar.slider("Active Conduits", 1, num_conduits-1, 2)
    
    # Operational scenarios
    st.sidebar.subheader("Operational Scenarios")
    scenarios = {
        "Peak Demand": {"spin_time_min": 15, "frequency_per_day": 4},
        "Base Load": {"spin_time_min": 30, "frequency_per_day": 2},
        "Emergency": {"spin_time_min": 60, "frequency_per_day": 1},
        "Storage Fill": {"spin_time_min": 120, "frequency_per_day": 0.5}
    }
    
    scenario_name = st.sidebar.selectbox("Select Scenario", list(scenarios.keys()))
    scenario = scenarios[scenario_name]
    
    # Manual controls
    st.sidebar.subheader("Manual Controls")
    manual_spin_time = st.sidebar.slider("Manual Spin Duration (minutes)", 1, 180, 15)
    
    # Start/Stop buttons
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🚀 Start Scenario"):
            st.session_state.simulation_running = True
            st.session_state.current_scenario = scenario
            st.session_state.simulator.start_spin_cycle(scenario["spin_time_min"])
    
    with col2:
        if st.button("⏹️ Emergency Stop"):
            st.session_state.simulation_running = False
            st.session_state.simulator.emergency_stop()
    
    # Main dashboard
    create_main_dashboard(conduit_length, num_conduits, active_conduits, scenario)
    
    # Auto-refresh for real-time updates
    if st.session_state.simulation_running:
        time.sleep(1)
        st.rerun()

def create_main_dashboard(conduit_length, num_conduits, active_conduits, scenario):
    # System status header
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        status = "🟢 ACTIVE" if st.session_state.simulation_running else "🔴 STANDBY"
        st.metric("System Status", status)
    
    with col2:
        current_rpm = st.session_state.simulator.get_current_rpm()
        st.metric("Core RPM", f"{current_rpm:,.0f}")
    
    with col3:
        current_power = st.session_state.simulator.get_current_power()
        st.metric("Power Output", f"{current_power:.1f} GW")
    
    with col4:
        kinetic_energy = st.session_state.simulator.get_kinetic_energy()
        st.metric("Kinetic Energy", f"{kinetic_energy:.0f} GJ")
    
    # Energy flow visualization
    st.subheader("🌊 Real-Time Energy Flow")
    create_energy_flow_chart()
    
    # Network visualization
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌐 SuperConduit Network")
        create_network_visualization(conduit_length, num_conduits, active_conduits)
    
    with col2:
        st.subheader("📊 Storage Capacity Analysis")
        create_storage_analysis(conduit_length, num_conduits)
    
    # Performance metrics
    st.subheader("📈 Performance Metrics")
    create_performance_dashboard(scenario)
    
    # Safety and efficiency analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🛡️ Safety Analysis")
        create_safety_analysis()
    
    with col2:
        st.subheader("⚡ Energy Efficiency")
        create_efficiency_analysis()

def create_energy_flow_chart():
    # Generate energy flow data
    simulator = st.session_state.simulator
    calculator = st.session_state.calculator
    
    # Create time series for the last 60 minutes
    time_points = pd.date_range(start=datetime.now() - timedelta(minutes=60), 
                               end=datetime.now(), freq='1min')
    
    # Generate realistic energy flow data
    energy_generation = []
    energy_storage = []
    energy_distribution = []
    
    for i, time_point in enumerate(time_points):
        # Simulate energy generation cycles
        if st.session_state.simulation_running:
            gen_power = simulator.get_current_power()
        else:
            gen_power = 0
            
        # Simulate storage levels with some variation
        storage_level = 1000 + 500 * math.sin(i * 0.1) + np.random.normal(0, 50)
        
        # Simulate distribution demand
        base_demand = 150 + 50 * math.sin(i * 0.05) + np.random.normal(0, 20)
        
        energy_generation.append(gen_power)
        energy_storage.append(max(0, storage_level))
        energy_distribution.append(max(0, base_demand))
    
    # Create the flow chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=energy_generation,
        mode='lines',
        name='Generation',
        line=dict(color='#00ff00', width=3),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=energy_storage,
        mode='lines',
        name='Storage Level',
        line=dict(color='#0066cc', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=time_points,
        y=energy_distribution,
        mode='lines',
        name='Distribution',
        line=dict(color='#ff6600', width=2)
    ))
    
    fig.update_layout(
        title="Energy Flow Over Time",
        xaxis_title="Time",
        yaxis_title="Power (GW)",
        height=400,
        showlegend=True,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_network_visualization(conduit_length, num_conduits, active_conduits):
    visualizer = st.session_state.visualizer
    
    # Create 3D network visualization
    fig = visualizer.create_conduit_network_3d(conduit_length, num_conduits, active_conduits)
    st.plotly_chart(fig, use_container_width=True)
    
    # Network status
    standby_conduits = num_conduits - active_conduits
    redundancy_factor = num_conduits / active_conduits
    
    st.info(f"""
    **Network Configuration:**
    - Active Conduits: {active_conduits}
    - Standby Conduits: {standby_conduits}
    - Redundancy Factor: {redundancy_factor:.1f}x
    - Failover Capability: Instant switching
    """)

def create_storage_analysis(conduit_length, num_conduits):
    calculator = st.session_state.calculator
    
    # Calculate storage metrics
    conduit_diameter_m = 48 * 0.0254  # 48 inches to meters
    single_conduit_capacity = calculator.calculate_conduit_capacity(conduit_length, conduit_diameter_m)
    total_capacity = single_conduit_capacity * num_conduits
    
    # Create capacity breakdown chart
    fig = go.Figure(data=[
        go.Bar(name='Per Conduit', x=[f'{conduit_length} miles'], y=[single_conduit_capacity]),
        go.Bar(name='Total Network', x=[f'{conduit_length} miles'], y=[total_capacity])
    ])
    
    fig.update_layout(
        title="Storage Capacity Analysis",
        yaxis_title="Capacity (GWh)",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Storage details
    st.success(f"""
    **PulseField Charge (PFC) Storage:**
    - Single Conduit: {single_conduit_capacity:.0f} GWh
    - Total Network: {total_capacity:.0f} GWh
    - Duration at Max Power: {total_capacity/200:.1f} hours
    - Energy Density: 2.5 GWh/m³
    """)

def create_performance_dashboard(scenario):
    calculator = st.session_state.calculator
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        daily_energy = calculator.calculate_daily_energy(scenario)
        st.metric("Daily Energy Generation", f"{daily_energy:.0f} GWh")
    
    with col2:
        efficiency = calculator.calculate_efficiency()
        st.metric("Generation Efficiency", f"{efficiency:.1f}%")
    
    with col3:
        startup_energy = calculator.get_startup_energy()
        st.metric("Startup Energy", f"{startup_energy:.1f} GWh")
    
    with col4:
        net_gain = calculator.calculate_net_energy_gain(scenario)
        st.metric("Net Energy Gain", f"{net_gain:.0f} GWh")
    
    # Performance over time chart
    scenarios = ["Peak Demand", "Base Load", "Emergency", "Storage Fill"]
    daily_energies = [calculator.calculate_daily_energy({"spin_time_min": t, "frequency_per_day": f}) 
                     for t, f in [(15, 4), (30, 2), (60, 1), (120, 0.5)]]
    
    fig = go.Figure(data=[
        go.Bar(x=scenarios, y=daily_energies, 
               marker_color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4'])
    ])
    
    fig.update_layout(
        title="Daily Energy Generation by Scenario",
        yaxis_title="Energy (GWh)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_safety_analysis():
    simulator = st.session_state.simulator
    
    # Safety metrics
    kinetic_energy = simulator.get_kinetic_energy()
    rpm = simulator.get_current_rpm()
    
    # Safety status
    if rpm == 0:
        safety_status = "🟢 MAXIMUM SAFETY"
        safety_msg = "Core at rest - Zero kinetic energy"
    elif rpm < 50000:
        safety_status = "🟡 LOW RISK"
        safety_msg = "Spinning at safe operational speed"
    elif rpm < 150000:
        safety_status = "🟠 MODERATE RISK"
        safety_msg = "High-speed operation - monitoring required"
    else:
        safety_status = "🔴 HIGH ENERGY"
        safety_msg = "Maximum operational speed - full safety protocols"
    
    st.metric("Safety Status", safety_status)
    st.info(safety_msg)
    
    # Safety comparison chart
    continuous_risk = 2217.3 if rpm > 0 else 0
    ondemand_risk = kinetic_energy
    
    fig = go.Figure(data=[
        go.Bar(name='Continuous Operation', x=['Kinetic Energy Risk'], y=[2217.3]),
        go.Bar(name='On-Demand Operation', x=['Kinetic Energy Risk'], y=[ondemand_risk])
    ])
    
    fig.update_layout(
        title="Safety Risk Comparison",
        yaxis_title="Kinetic Energy (GJ)",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_efficiency_analysis():
    calculator = st.session_state.calculator
    
    # Efficiency metrics
    startup_energy = calculator.get_startup_energy()
    generation_15min = 200 * 0.25  # 200 GW for 15 minutes
    efficiency_ratio = generation_15min / startup_energy
    
    # Efficiency breakdown
    fig = go.Figure(data=[
        go.Bar(name='Energy Required', x=['Startup'], y=[startup_energy]),
        go.Bar(name='Energy Generated', x=['15min Generation'], y=[generation_15min])
    ])
    
    fig.update_layout(
        title="Energy Efficiency Analysis",
        yaxis_title="Energy (GWh)",
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.success(f"""
    **Efficiency Metrics:**
    - Startup Energy: {startup_energy:.1f} GWh
    - 15min Generation: {generation_15min:.1f} GWh
    - Efficiency Ratio: {efficiency_ratio:.1f}:1
    - Break-even Time: {startup_energy/200*60:.1f} minutes
    """)

if __name__ == "__main__":
    main()
