import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import math

class NetworkVisualizer:
    def __init__(self):
        self.colors = {
            'active': '#00ff00',
            'standby': '#ffff00',
            'inactive': '#ff0000',
            'core': '#0066cc',
            'energy_flow': '#ff6600',
            'tunnel': '#666666'
        }
        
    def create_conduit_network_3d(self, conduit_length_miles, num_conduits, active_conduits):
        """Create 3D visualization of SuperConduit network"""
        fig = go.Figure()
        
        # Convert length to meters for visualization scale
        length_m = conduit_length_miles * 1609.34
        
        # Create conduit tunnels
        for i in range(num_conduits):
            # Position conduits in a circular pattern around the core
            angle = (2 * math.pi * i) / num_conduits
            start_x = 50 * math.cos(angle)
            start_y = 50 * math.sin(angle)
            end_x = start_x + length_m * 0.001 * math.cos(angle)  # Scale down for visualization
            end_y = start_y + length_m * 0.001 * math.sin(angle)
            
            # Determine conduit status
            if i < active_conduits:
                color = self.colors['active']
                status = 'Active'
                width = 8
            else:
                color = self.colors['standby']
                status = 'Standby'
                width = 6
                
            # Create conduit tunnel
            fig.add_trace(go.Scatter3d(
                x=[start_x, end_x],
                y=[start_y, end_y],
                z=[-20, -20],  # Underground depth
                mode='lines',
                line=dict(color=color, width=width),
                name=f'Conduit {i+1} ({status})',
                hovertemplate=f'<b>Conduit {i+1}</b><br>' +
                             f'Status: {status}<br>' +
                             f'Length: {conduit_length_miles} miles<br>' +
                             f'Diameter: 48 inches<br>' +
                             '<extra></extra>'
            ))
            
            # Add energy flow indicators for active conduits
            if i < active_conduits:
                # Create flowing energy particles
                flow_points = np.linspace(0, 1, 20)
                flow_x = start_x + (end_x - start_x) * flow_points
                flow_y = start_y + (end_y - start_y) * flow_points
                flow_z = np.full_like(flow_x, -20)
                
                fig.add_trace(go.Scatter3d(
                    x=flow_x,
                    y=flow_y,
                    z=flow_z,
                    mode='markers',
                    marker=dict(color=self.colors['energy_flow'], size=3),
                    name=f'Energy Flow {i+1}',
                    showlegend=False
                ))
        
        # Add central core
        fig.add_trace(go.Scatter3d(
            x=[0],
            y=[0],
            z=[0],
            mode='markers',
            marker=dict(color=self.colors['core'], size=20, 
                       symbol='diamond'),
            name='PulseSuperConduit Core',
            hovertemplate='<b>Core System</b><br>' +
                         'Max Power: 200 GW<br>' +
                         'Max RPM: 200,000<br>' +
                         'Mass: 199 kg<br>' +
                         'Radius: 1.5 m<br>' +
                         '<extra></extra>'
        ))
        
        # Add surface level reference
        surface_size = max(length_m * 0.002, 200)
        fig.add_trace(go.Mesh3d(
            x=[-surface_size, surface_size, surface_size, -surface_size],
            y=[-surface_size, -surface_size, surface_size, surface_size],
            z=[0, 0, 0, 0],
            opacity=0.3,
            color='lightblue',
            name='Surface Level',
            showlegend=False
        ))
        
        fig.update_layout(
            title="SuperConduit Network 3D Visualization",
            scene=dict(
                xaxis_title="Distance (m)",
                yaxis_title="Distance (m)",
                zaxis_title="Depth (m)",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=500
        )
        
        return fig
        
    def create_energy_flow_diagram(self, current_power, storage_levels):
        """Create energy flow diagram"""
        fig = go.Figure()
        
        # Create Sankey diagram for energy flow
        fig.add_trace(go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=["Core Generation", "SuperConduit Storage", "Energy Distribution", 
                      "Peak Demand", "Base Load", "Emergency Reserve"],
                color=["blue", "green", "orange", "red", "yellow", "purple"]
            ),
            link=dict(
                source=[0, 1, 1, 1, 2, 2],
                target=[1, 2, 3, 4, 5, 0],
                value=[current_power, current_power*0.4, current_power*0.3, 
                      current_power*0.2, current_power*0.1, current_power*0.05]
            )
        ))
        
        fig.update_layout(
            title="Energy Flow Distribution",
            font_size=10,
            height=400
        )
        
        return fig
        
    def create_network_status_dashboard(self, conduit_statuses):
        """Create network status dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Network Health', 'Conduit Status', 
                           'Energy Flow', 'Redundancy Status'),
            specs=[[{"type": "indicator"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "pie"}]]
        )
        
        # Network health indicator
        health_score = sum(1 for status in conduit_statuses if status == 'active') / len(conduit_statuses) * 100
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=health_score,
            title={'text': "Network Health %"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkgreen"},
                   'steps': [{'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 80], 'color': "gray"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 90}}
        ), row=1, col=1)
        
        # Conduit status bar chart
        status_counts = {'Active': conduit_statuses.count('active'),
                        'Standby': conduit_statuses.count('standby'),
                        'Inactive': conduit_statuses.count('inactive')}
        
        fig.add_trace(go.Bar(
            x=list(status_counts.keys()),
            y=list(status_counts.values()),
            marker_color=[self.colors['active'], self.colors['standby'], self.colors['inactive']]
        ), row=1, col=2)
        
        # Energy flow over time (simulated)
        time_points = np.arange(0, 24, 0.5)
        energy_flow = 150 + 50 * np.sin(time_points * np.pi / 12) + np.random.normal(0, 10, len(time_points))
        
        fig.add_trace(go.Scatter(
            x=time_points,
            y=energy_flow,
            mode='lines',
            name='Energy Flow',
            line=dict(color=self.colors['energy_flow'])
        ), row=2, col=1)
        
        # Redundancy status pie chart
        redundancy_data = {
            'Active Systems': status_counts['Active'],
            'Backup Systems': status_counts['Standby'],
            'Maintenance': status_counts['Inactive']
        }
        
        fig.add_trace(go.Pie(
            labels=list(redundancy_data.keys()),
            values=list(redundancy_data.values()),
            marker_colors=[self.colors['active'], self.colors['standby'], self.colors['inactive']]
        ), row=2, col=2)
        
        fig.update_layout(
            title="SuperConduit Network Status Dashboard",
            height=600,
            showlegend=False
        )
        
        return fig
        
    def create_safety_visualization(self, kinetic_energy, rpm, material_stress):
        """Create safety status visualization"""
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=('Kinetic Energy', 'RPM Status', 'Material Stress'),
            specs=[[{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}]]
        )
        
        # Kinetic energy gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=kinetic_energy,
            title={'text': "Kinetic Energy (GJ)"},
            delta={'reference': 2217.3},
            gauge={'axis': {'range': [None, 2500]},
                   'bar': {'color': "darkred"},
                   'steps': [{'range': [0, 500], 'color': "lightgreen"},
                            {'range': [500, 1500], 'color': "yellow"},
                            {'range': [1500, 2500], 'color': "lightcoral"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 2217.3}}
        ), row=1, col=1)
        
        # RPM gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=rpm,
            title={'text': "RPM"},
            gauge={'axis': {'range': [None, 200000]},
                   'bar': {'color': "darkblue"},
                   'steps': [{'range': [0, 50000], 'color': "lightgreen"},
                            {'range': [50000, 150000], 'color': "yellow"},
                            {'range': [150000, 200000], 'color': "lightcoral"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 200000}}
        ), row=1, col=2)
        
        # Material stress gauge
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=material_stress,
            title={'text': "Material Stress (%)"},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkorange"},
                   'steps': [{'range': [0, 30], 'color': "lightgreen"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "lightcoral"}],
                   'threshold': {'line': {'color': "red", 'width': 4},
                               'thickness': 0.75, 'value': 100}}
        ), row=1, col=3)
        
        fig.update_layout(
            title="Real-Time Safety Monitoring",
            height=400
        )
        
        return fig
        
    def create_efficiency_comparison(self, scenarios_data):
        """Create efficiency comparison visualization"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Energy Generation by Scenario', 'Efficiency Ratios',
                           'Startup vs Generation', 'Net Energy Gains'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "scatter"}, {"type": "bar"}]]
        )
        
        scenarios = list(scenarios_data.keys())
        daily_energies = [scenarios_data[s]['daily_energy_gwh'] for s in scenarios]
        efficiency_ratios = [scenarios_data[s]['efficiency_ratio'] for s in scenarios]
        startup_costs = [scenarios_data[s]['startup_costs_gwh'] for s in scenarios]
        net_energies = [scenarios_data[s]['net_energy_gwh'] for s in scenarios]
        
        # Daily energy generation
        fig.add_trace(go.Bar(
            x=scenarios,
            y=daily_energies,
            name='Daily Energy',
            marker_color='lightblue'
        ), row=1, col=1)
        
        # Efficiency ratios
        fig.add_trace(go.Bar(
            x=scenarios,
            y=efficiency_ratios,
            name='Efficiency Ratio',
            marker_color='lightgreen'
        ), row=1, col=2)
        
        # Startup vs Generation scatter
        fig.add_trace(go.Scatter(
            x=startup_costs,
            y=daily_energies,
            mode='markers+text',
            text=scenarios,
            textposition="top center",
            marker=dict(size=12, color='red'),
            name='Startup vs Generation'
        ), row=2, col=1)
        
        # Net energy gains
        fig.add_trace(go.Bar(
            x=scenarios,
            y=net_energies,
            name='Net Energy',
            marker_color='gold'
        ), row=2, col=2)
        
        fig.update_layout(
            title="Operational Efficiency Analysis",
            height=600,
            showlegend=False
        )
        
        return fig
