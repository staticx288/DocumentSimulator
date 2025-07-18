from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import json
import time
import threading
from datetime import datetime
import math

from core_simulator import CoreSimulator
from energy_calculator import EnergyCalculator
from network_visualizer import NetworkVisualizer

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pulsesuperconduit_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global simulation state
simulator = CoreSimulator()
calculator = EnergyCalculator()
visualizer = NetworkVisualizer()
simulation_thread = None
simulation_running = False

def background_simulation():
    """Background thread for simulation updates"""
    global simulation_running
    while simulation_running:
        # Update simulation state
        simulator.update_simulation()
        
        # Get current metrics
        data = {
            'rpm': simulator.get_current_rpm(),
            'power': simulator.get_current_power(),
            'kinetic_energy': simulator.get_kinetic_energy(),
            'safety_status': simulator.get_safety_status(),
            'material_stress': simulator.calculate_material_stress(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Emit to all connected clients
        socketio.emit('simulation_update', data)
        time.sleep(0.5)  # Update every 500ms

@app.route('/')
def index():
    """Main simulation interface"""
    return render_template('index.html')

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start simulation with given parameters"""
    global simulation_thread, simulation_running
    
    data = request.json
    scenario = data.get('scenario', 'Peak Demand')
    duration = data.get('duration', 15)
    
    # Start the simulation
    simulator.start_spin_cycle(duration)
    
    if not simulation_running:
        simulation_running = True
        simulation_thread = threading.Thread(target=background_simulation)
        simulation_thread.daemon = True
        simulation_thread.start()
    
    return jsonify({'status': 'started', 'scenario': scenario, 'duration': duration})

@app.route('/api/stop_simulation', methods=['POST'])
def stop_simulation():
    """Emergency stop simulation"""
    global simulation_running
    
    simulator.emergency_stop()
    simulation_running = False
    
    return jsonify({'status': 'stopped'})

@app.route('/api/system_status')
def system_status():
    """Get current system status"""
    return jsonify({
        'rpm': simulator.get_current_rpm(),
        'power': simulator.get_current_power(),
        'kinetic_energy': simulator.get_kinetic_energy(),
        'safety_status': simulator.get_safety_status(),
        'material_stress': simulator.calculate_material_stress(),
        'is_spinning': simulator.is_spinning,
        'total_cycles': simulator.spin_cycles_completed
    })

@app.route('/api/network_config', methods=['POST'])
def update_network_config():
    """Update network configuration"""
    data = request.json
    
    conduit_length = data.get('conduit_length', 4)
    num_conduits = data.get('num_conduits', 3)
    active_conduits = data.get('active_conduits', 2)
    
    # Calculate network metrics
    single_capacity = calculator.calculate_conduit_capacity(conduit_length, 48 * 0.0254)
    total_capacity = single_capacity * num_conduits
    redundancy = calculator.calculate_network_redundancy_benefits(num_conduits, active_conduits)
    
    return jsonify({
        'single_conduit_capacity': single_capacity,
        'total_capacity': total_capacity,
        'redundancy_factor': redundancy['redundancy_factor'],
        'standby_conduits': redundancy['standby_conduits']
    })

@app.route('/api/scenarios')
def get_scenarios():
    """Get available operational scenarios"""
    scenarios = {
        "Peak Demand": {"spin_time_min": 15, "frequency_per_day": 4},
        "Base Load": {"spin_time_min": 30, "frequency_per_day": 2},
        "Emergency": {"spin_time_min": 60, "frequency_per_day": 1},
        "Storage Fill": {"spin_time_min": 120, "frequency_per_day": 0.5}
    }
    
    # Calculate energy metrics for each scenario
    scenario_data = {}
    for name, params in scenarios.items():
        analysis = calculator.analyze_scenario_efficiency(name)
        scenario_data[name] = {
            'params': params,
            'daily_energy': analysis['daily_energy_gwh'],
            'net_energy': analysis['net_energy_gwh'],
            'efficiency_ratio': analysis['efficiency_ratio']
        }
    
    return jsonify(scenario_data)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'data': 'Connected to PulseSuperConduit simulation'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)