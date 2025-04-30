#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D Visualization of H II Region using Streamlit and PyVista

This program provides an interactive web application for 3D visualization of H II regions.

Author: Erfan Mohamadnia
"""

import streamlit as st
import numpy as np
import pyvista as pv
from stpyvista import stpyvista
import matplotlib.pyplot as plt
from scipy.special import erf
import os


class HIIRegionModel:
    """
    H II Region Modeling Class

    This class simulates a simplified model of an H II region, including:
    - A central star as the source of ionizing radiation
    - Distribution of hydrogen gas density
    - Calculation of ionization fraction at different distances from the star
    - Calculation of temperature distribution based on ionization level

    This class follows object-oriented principles and divides different responsibilities
    into separate methods:
    - Density calculation (calculate_density)
    - Ionization calculation (calculate_ionization)
    - Temperature calculation (calculate_temperature)
    - Visualization creation (create_visualization_plotter)
    - Radial profile plotting (plot_radial_profile)
    """

    def __init__(self, radius=50.0, resolution=150, star_temperature=40000,
                 density_profile='uniform', density_factor=1.0, progress_callback=None):
        """
        Initialize the HIIRegionModel class

        Parameters:
            radius (float): Simulation region radius in parsecs
            resolution (int): Number of points in each dimension for the grid
            star_temperature (float): Central star temperature in Kelvin
            density_profile (str): Type of density profile ('uniform', 'exponential', 'power_law')
            density_factor (float): Scaling factor for density
            progress_callback (callable): Function for displaying calculation progress (optional)
        """
        self.radius = radius
        self.resolution = resolution
        self.star_temperature = star_temperature
        self.density_profile = density_profile
        self.density_factor = density_factor
        self.progress_callback = progress_callback

        # Call progress callback if defined
        if self.progress_callback:
            self.progress_callback("Creating 3D grid...", 0.1)

        # Create 3D grid
        self.grid = pv.ImageData(
            dimensions=(resolution, resolution, resolution),
            spacing=(2*radius/resolution, 2*radius/resolution, 2*radius/resolution),
            origin=(-radius, -radius, -radius)
        )

        if self.progress_callback:
            self.progress_callback("Calculating distances...", 0.2)

        # Calculate distance of each point from center
        x, y, z = np.meshgrid(
            np.linspace(-radius, radius, resolution),
            np.linspace(-radius, radius, resolution),
            np.linspace(-radius, radius, resolution),
            indexing='ij'
        )

        self.distances = np.sqrt(x**2 + y**2 + z**2)

        if self.progress_callback:
            self.progress_callback("Calculating gas density...", 0.4)

        # Calculate gas density
        self.calculate_density()

        if self.progress_callback:
            self.progress_callback("Calculating ionization level...", 0.6)

        # Calculate ionization
        self.calculate_ionization()

        if self.progress_callback:
            self.progress_callback("Calculating temperature...", 0.8)

        # Calculate temperature
        self.calculate_temperature()

        if self.progress_callback:
            self.progress_callback("Model successfully created!", 1.0)

    def calculate_density(self):
        """
        Calculate hydrogen gas density distribution based on the selected profile

        This method computes the density distribution according to the specified profile:
        - uniform: Constant density throughout the region
        - exponential: Density decreases exponentially from the center
        - power_law: Density follows a power law distribution (typical in molecular clouds)
        """
        if self.density_profile == 'uniform':
            # Uniform density
            self.density = np.ones_like(self.distances) * self.density_factor

        elif self.density_profile == 'exponential':
            # Exponentially decreasing density from center
            scale_length = self.radius / 5.0  # Characteristic length
            self.density = self.density_factor * np.exp(-self.distances / scale_length)

        elif self.density_profile == 'power_law':
            # Power law density distribution
            power = -2.0  # Typical power in molecular clouds
            # Avoid division by zero at center
            safe_distances = np.maximum(self.distances, 0.01 * self.radius)
            self.density = self.density_factor * (safe_distances / self.radius) ** power

        else:
            raise ValueError(f"Density profile '{self.density_profile}' is not supported")

        # Add density to the grid
        self.grid.point_data["density"] = self.density.flatten()

    def calculate_ionization(self):
        """
        Calculate ionization fraction at each point in space

        This function implements a simple model of ionization based on distance from the star
        using the complementary error function.
        """
        # Calculate Stromgren radius based on star temperature
        # In reality, this depends on the star's ionizing flux (which depends on temperature)
        # and ambient density
        #
        # The relationship between star temperature and ionizing photon output is roughly:
        # Q_0 ∝ T^4 (Stefan-Boltzmann law) for the total radiation
        # But for ionizing photons (>13.6 eV), the relationship is even steeper
        #
        # Simplified model: Stromgren radius ∝ Q_0^(1/3) ∝ T^(4/3)
        #
        # Base temperature: 30,000 K -> stromgren_radius = self.radius / 2.0
        base_temp = 30000.0
        base_radius = self.radius / 2.0

        # Calculate Stromgren radius based on temperature
        # Use a power law relationship with a cap to prevent extreme values
        temp_factor = min(3.0, max(0.3, (self.star_temperature / base_temp)**(4/3)))
        stromgren_radius = base_radius * temp_factor

        # Ensure Stromgren radius doesn't exceed simulation radius
        stromgren_radius = min(stromgren_radius, self.radius * 0.95)

        # Store Stromgren radius for use in other methods
        self.stromgren_radius = stromgren_radius

        # Width of the transition layer
        transition_width = stromgren_radius / 10.0

        # Calculate ionization fraction using complementary error function
        # Gas is almost fully ionized at distances less than the Stromgren radius
        # and ionization decreases with increasing distance
        self.ionization_fraction = 0.5 * (1.0 - erf((self.distances - stromgren_radius) / transition_width))

        # Add ionization fraction to the grid
        self.grid.point_data["ionization"] = self.ionization_fraction.flatten()

    def calculate_temperature(self):
        """
        Calculate temperature distribution in the H II region

        Temperature in the H II region depends on the ionization level. In highly ionized regions,
        temperature is higher (around 10000 K), while in neutral regions, temperature is lower.
        """
        # Temperature of ionized region (around 10000 K)
        ionized_temp = 10000.0

        # Temperature of neutral region (around 100 K)
        neutral_temp = 100.0

        # Calculate temperature based on ionization fraction
        self.temperature = neutral_temp + (ionized_temp - neutral_temp) * self.ionization_fraction

        # Add temperature to the grid
        self.grid.point_data["temperature"] = self.temperature.flatten()

    def get_star_color(self):
        """
        Calculate star color based on its temperature using blackbody radiation principles

        This method converts star temperature to RGB color using an approximation of blackbody radiation.
        The color ranges from red (cooler stars) to blue-white (hotter stars).

        Returns:
            tuple: RGB color values as a tuple (r, g, b) with values between 0 and 1
        """
        # Temperature range for stars (in Kelvin)
        # O stars: 30,000 - 50,000 K (blue)
        # B stars: 10,000 - 30,000 K (blue-white)
        # A stars: 7,500 - 10,000 K (white)
        # F stars: 6,000 - 7,500 K (yellow-white)
        # G stars: 5,000 - 6,000 K (yellow) - like our Sun
        # K stars: 3,500 - 5,000 K (orange)
        # M stars: 2,000 - 3,500 K (red)

        temp = self.star_temperature

        # Initialize RGB values
        r, g, b = 0, 0, 0

        # Simplified approximation of blackbody radiation color
        # Based on temperature ranges for different star types
        if temp < 3500:  # M stars (red)
            r = 1.0
            g = 0.5 * (temp - 2000) / 1500 if temp > 2000 else 0
            b = 0.0
        elif temp < 5000:  # K stars (orange)
            r = 1.0
            g = 0.5 + 0.3 * (temp - 3500) / 1500
            b = 0.2 * (temp - 3500) / 1500
        elif temp < 6000:  # G stars (yellow)
            r = 1.0
            g = 0.8 + 0.2 * (temp - 5000) / 1000
            b = 0.2 + 0.3 * (temp - 5000) / 1000
        elif temp < 7500:  # F stars (yellow-white)
            r = 1.0
            g = 1.0
            b = 0.5 + 0.3 * (temp - 6000) / 1500
        elif temp < 10000:  # A stars (white)
            r = 1.0
            g = 1.0
            b = 0.8 + 0.2 * (temp - 7500) / 2500
        elif temp < 30000:  # B stars (blue-white)
            r = 1.0 - 0.4 * (temp - 10000) / 20000
            g = 1.0 - 0.4 * (temp - 10000) / 20000
            b = 1.0
        else:  # O stars (blue)
            r = 0.6 - 0.3 * min(1.0, (temp - 30000) / 20000)
            g = 0.6 - 0.3 * min(1.0, (temp - 30000) / 20000)
            b = 1.0

        # Ensure values are within valid range
        r = max(0, min(1, r))
        g = max(0, min(1, g))
        b = max(0, min(1, b))

        return (r, g, b)

    def create_visualization_plotter(self, property_name="ionization", cmap="plasma", opacity=0.7,
                                    show_star=True, show_boundaries=True, add_dust=True):
        """
        Create PyVista plotter for 3D visualization of the H II region

        This method creates a 3D visualization of the H II region that includes:
        1. Volumetric display of the H II region based on selected property (ionization, density, or temperature)
        2. Display of the central star with lighting effects
        3. Display of the H II region boundaries (Stromgren radius)
        4. Display of dust particles with random distribution and varying colors based on distance from center

        This method uses the PyVista library for 3D visualization and employs various
        techniques to enhance the visual quality of the display.

        Parameters:
            property_name (str): Name of property to display ("density", "ionization", "temperature")
            cmap (str): Name of colormap to use
            opacity (float): Display opacity (between 0 and 1)
            show_star (bool): Whether to display the central star
            show_boundaries (bool): Whether to display region boundaries
            add_dust (bool): Whether to add random dust particles

        Returns:
            pv.Plotter: PyVista plotter ready for display
        """
        # Create PyVista plotter
        plotter = pv.Plotter()
        plotter.background_color = "black"

        # Add H II region volumetrically with enhanced effects
        # Use advanced techniques for volumetric display
        if property_name == "ionization":
            # For ionization, use blue-purple colors with variable opacity
            opacity_function = [0, 0.0, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]  # Higher opacity for higher values
            plotter.add_volume(self.grid, scalars=property_name, cmap=cmap, opacity=opacity_function,
                              opacity_unit_distance=self.radius/5, shade=True)
        elif property_name == "temperature":
            # For temperature, use warm colors with variable opacity
            opacity_function = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
            plotter.add_volume(self.grid, scalars=property_name, cmap=cmap, opacity=opacity_function,
                              opacity_unit_distance=self.radius/5, shade=True)
        elif property_name == "density":
            # For density, use constant opacity
            plotter.add_volume(self.grid, scalars=property_name, cmap=cmap, opacity=opacity,
                              opacity_unit_distance=self.radius/5, shade=True)
        else:
            # Default case
            plotter.add_volume(self.grid, scalars=property_name, cmap=cmap, opacity=opacity)

        # Add central star
        if show_star:
            # Get star color based on temperature
            star_color = self.get_star_color()

            # Calculate glow color - slightly shift towards yellow/white for visual effect
            glow_r = min(1.0, star_color[0] + 0.2)
            glow_g = min(1.0, star_color[1] + 0.2)
            glow_b = star_color[2]
            glow_color = (glow_r, glow_g, glow_b)

            # Main star - use surface style with smooth_shading to remove grid lines
            star = pv.Sphere(radius=self.radius/50, center=(0, 0, 0), theta_resolution=36, phi_resolution=36)
            plotter.add_mesh(star, color=star_color, ambient=0.8, specular=1.0, smooth_shading=True)

            # Glowing effect around the star - use smooth_shading
            glow = pv.Sphere(radius=self.radius/25, center=(0, 0, 0), theta_resolution=36, phi_resolution=36)
            plotter.add_mesh(glow, color=glow_color, opacity=0.1, ambient=0.3, smooth_shading=True)

            # Add information about star temperature and color to the plotter
            temp_text = f"Star Temperature: {self.star_temperature:,} K"
            plotter.add_text(temp_text, position=(0.02, 0.05), font_size=12, color='white')

        # Add region boundaries
        if show_boundaries:
            # Use the Stromgren radius calculated based on star temperature
            stromgren_radius = self.stromgren_radius

            # Add text showing the Stromgren radius
            radius_text = f"Stromgren Radius: {stromgren_radius:.2f} pc"
            plotter.add_text(radius_text, position=(0.02, 0.02), font_size=12, color='white')

            # Instead of wireframe, use a semi-transparent sphere with smooth_shading
            boundary = pv.Sphere(radius=stromgren_radius, center=(0, 0, 0), theta_resolution=36, phi_resolution=36)

            # Display as semi-transparent surface with very light blue color
            plotter.add_mesh(boundary, color='cyan', opacity=0.07, smooth_shading=True, specular=0.2)

            # Create circular lines in three main planes

            # Number of points for each circle
            n_points = 700

            # Create points on circle in XY plane
            theta_xy = np.linspace(0, 2*np.pi, n_points)
            x_xy = stromgren_radius * np.cos(theta_xy)
            y_xy = stromgren_radius * np.sin(theta_xy)
            z_xy = np.zeros_like(theta_xy)
            points_xy = np.column_stack((x_xy, y_xy, z_xy))

            # Create points on circle in XZ plane
            theta_xz = np.linspace(0, 2*np.pi, n_points)
            x_xz = stromgren_radius * np.cos(theta_xz)
            y_xz = np.zeros_like(theta_xz)
            z_xz = stromgren_radius * np.sin(theta_xz)
            points_xz = np.column_stack((x_xz, y_xz, z_xz))

            # Create points on circle in YZ plane
            theta_yz = np.linspace(0, 2*np.pi, n_points)
            x_yz = np.zeros_like(theta_yz)
            y_yz = stromgren_radius * np.cos(theta_yz)
            z_yz = stromgren_radius * np.sin(theta_yz)
            points_yz = np.column_stack((x_yz, y_yz, z_yz))

            # Create lines for each circle
            lines_xy = pv.lines_from_points(points_xy)
            lines_xz = pv.lines_from_points(points_xz)
            lines_yz = pv.lines_from_points(points_yz)

            # Add lines to plotter
            plotter.add_mesh(lines_xy, color='yellow', opacity=0.05, line_width=1)
            plotter.add_mesh(lines_xz, color='yellow', opacity=0.05, line_width=1)
            plotter.add_mesh(lines_yz, color='yellow', opacity=0.05, line_width=1)

        # Add random dust particles
        if add_dust:
            # Number of dust particles
            n_dust = 1500

            # Create random positions for dust particles
            np.random.seed(42)  # For reproducibility

            # Random positions in spherical space with higher concentration at H II region edges
            theta = np.random.uniform(0, 2*np.pi, n_dust)
            phi = np.random.uniform(0, np.pi, n_dust)

            # Radial distribution with higher concentration at H II region edges
            # Use the Stromgren radius calculated based on star temperature
            stromgren_radius = self.stromgren_radius
            r_base = np.random.uniform(0, 1, n_dust)
            # Transform uniform distribution to one concentrated in the middle
            r_base = 0.5 + (r_base - 0.5) * (r_base - 0.5) * np.sign(r_base - 0.5)
            r = stromgren_radius * (0.8 + 0.6 * r_base)  # Scale to desired range

            # Convert to Cartesian coordinates
            x = r * np.sin(phi) * np.cos(theta)
            y = r * np.sin(phi) * np.sin(theta)
            z = r * np.cos(phi)

            # Add noise to positions to create cloudy appearance
            noise_scale = self.radius * 0.05
            x += np.random.normal(0, noise_scale, n_dust)
            y += np.random.normal(0, noise_scale, n_dust)
            z += np.random.normal(0, noise_scale, n_dust)

            # Create points for dust particles
            dust_points = np.column_stack((x, y, z))
            dust_cloud = pv.PolyData(dust_points)

            # Distance from center for color determination
            distances = np.sqrt(x**2 + y**2 + z**2)
            normalized_distances = distances / self.radius  # Normalize distances

            # Add dust particles with fixed size and different colors based on distance
            dust_cloud.point_data["distances"] = normalized_distances
            plotter.add_points(dust_cloud, scalars="distances", cmap='coolwarm',
                              opacity=0.6, point_size=2.0, render_points_as_spheres=True)

            # Instead of filtering arrays, use three separate point groups
            # Create three point groups with different sizes in different regions

            # Group 1: Points close to center (red color)
            close_x = []
            close_y = []
            close_z = []

            # Group 2: Middle points (purple color)
            mid_x = []
            mid_y = []
            mid_z = []

            # Group 3: Points far from center (blue color)
            far_x = []
            far_y = []
            far_z = []

            # Divide points into three groups based on distance
            # Convert multidimensional arrays to one-dimensional for easier access
            flat_x = x.flatten()
            flat_y = y.flatten()
            flat_z = z.flatten()
            flat_distances = normalized_distances.flatten()

            for i in range(len(flat_distances)):
                if flat_distances[i] < 0.33:
                    close_x.append(flat_x[i])
                    close_y.append(flat_y[i])
                    close_z.append(flat_z[i])
                elif flat_distances[i] < 0.66:
                    mid_x.append(flat_x[i])
                    mid_y.append(flat_y[i])
                    mid_z.append(flat_z[i])
                else:
                    far_x.append(flat_x[i])
                    far_y.append(flat_y[i])
                    far_z.append(flat_z[i])

            # Create points for each group
            if len(close_x) > 0:
                close_points = np.column_stack((close_x, close_y, close_z))
                close_cloud = pv.PolyData(close_points)
                plotter.add_mesh(close_cloud, color='red', opacity=0.7,
                                render_points_as_spheres=True, point_size=3.0)

            if len(mid_x) > 0:
                mid_points = np.column_stack((mid_x, mid_y, mid_z))
                mid_cloud = pv.PolyData(mid_points)
                plotter.add_mesh(mid_cloud, color='purple', opacity=0.5,
                                render_points_as_spheres=True, point_size=2.0)

            if len(far_x) > 0:
                far_points = np.column_stack((far_x, far_y, far_z))
                far_cloud = pv.PolyData(far_points)
                plotter.add_mesh(far_cloud, color='blue', opacity=0.4,
                                render_points_as_spheres=True, point_size=1.0)

        return plotter

    def plot_radial_profile(self, property_name="ionization"):
        """
        Plot the variation of a property as a function of distance from center

        This method creates a 2D plot of the variation of a property (density, ionization, or temperature)
        as a function of distance from the center of the H II region. This plot helps the user
        to better understand the radial distribution of different properties in the H II region.

        For each property, appropriate calculations are performed:
        - For density: based on the selected profile (uniform, exponential, or power law)
        - For ionization: using the complementary error function and Stromgren radius
        - For temperature: based on ionization level and temperatures of ionized and neutral regions

        Parameters:
            property_name (str): Name of property to display ("density", "ionization", "temperature")

        Returns:
            matplotlib.figure.Figure: matplotlib figure for display
        """
        # Create array of distances for the plot
        r = np.linspace(0, self.radius, 1000)

        # Calculate property values at each distance
        if property_name == "density":
            if self.density_profile == 'uniform':
                values = np.ones_like(r) * self.density_factor
            elif self.density_profile == 'exponential':
                scale_length = self.radius / 5.0
                values = self.density_factor * np.exp(-r / scale_length)
            elif self.density_profile == 'power_law':
                safe_r = np.maximum(r, 0.01 * self.radius)
                values = self.density_factor * (safe_r / self.radius) ** (-2.0)

        elif property_name == "ionization":
            # Use the Stromgren radius calculated based on star temperature
            stromgren_radius = self.stromgren_radius
            transition_width = stromgren_radius / 10.0
            values = 0.5 * (1.0 - erf((r - stromgren_radius) / transition_width))

        elif property_name == "temperature":
            # Use the Stromgren radius calculated based on star temperature
            stromgren_radius = self.stromgren_radius
            transition_width = stromgren_radius / 10.0
            ionization = 0.5 * (1.0 - erf((r - stromgren_radius) / transition_width))
            values = 100.0 + (10000.0 - 100.0) * ionization

        else:
            raise ValueError(f"Property '{property_name}' is not supported")

        # Create plot
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(r, values, 'b-', linewidth=2)
        ax.grid(True, alpha=0.3)
        ax.set_xlabel('Distance from center (parsec)', fontsize=12)

        if property_name == "density":
            ax.set_ylabel('Relative density', fontsize=12)
            ax.set_title('Radial density profile in H II region', fontsize=14)
        elif property_name == "ionization":
            ax.set_ylabel('Ionization fraction', fontsize=12)
            ax.set_title('Radial ionization profile in H II region', fontsize=14)
        elif property_name == "temperature":
            ax.set_ylabel('Temperature (K)', fontsize=12)
            ax.set_title('Radial temperature profile in H II region', fontsize=14)

        plt.tight_layout()
        return fig


def main():
    """
    Main function of the Streamlit application

    This function is responsible for launching the Streamlit user interface and managing user interaction.
    The overall structure of the application is as follows:
    1. Initial page setup
    2. Loading CSS
    3. Creating a two-column layout (sidebar and main content)
    4. Displaying settings and descriptions in the sidebar
    5. Creating and displaying the model in the main column
    6. Displaying different tabs for 3D visualization and radial plots
    """
    st.set_page_config(
        page_title="H II Region Visualization",
        page_icon="🌌",
        layout="wide"
    )

    # Load CSS file
    def load_css():
        css_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
        with open(css_file, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Load CSS
    load_css()

    # Add RTL text class to the entire page
    st.markdown('<div class="rtl-text">', unsafe_allow_html=True)

    st.title("3D Visualization of H II Region")

    # Define main column for use later in the code
    col_sidebar, col_main = st.columns([1, 3])
    with col_sidebar:
        # Introduction and description section
        st.markdown('<div class="description-card">', unsafe_allow_html=True)
        st.markdown("""
        ### درباره ناحیه H II

        ناحیه H II منطقه‌ای از گاز بسیار رقیق است که در آن هیدروژن به صورت یونیزه وجود دارد.
        این نواحی معمولاً در اطراف ستارگان جوان و داغ تشکیل می‌شوند.

        این برنامه یک تجسم‌سازی سه‌بعدی از ناحیه H II را ارائه می‌دهد که به شما امکان می‌دهد
        پارامترهای مختلف را تغییر داده و تأثیر آن‌ها را بر روی ساختار ناحیه مشاهده کنید.
        """)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        st.markdown("""
        ### شعاع استرومگرن

        شعاع استرومگرن، شعاع تقریبی ناحیه یونیزه در اطراف یک ستاره است. این شعاع به شار فوتون‌های یونیزه‌کننده ستاره و چگالی محیط اطراف بستگی دارد و از رابطه زیر محاسبه می‌شود:

        R_s = (3 * Q_0 / (4 * π * n_H^2 * α_B))^(1/3)

        که در آن:
        - Q_0: تعداد فوتون‌های یونیزه‌کننده منتشر شده توسط ستاره در واحد زمان
        - n_H: چگالی اتم‌های هیدروژن
        - α_B: ضریب بازترکیب
        """)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.sidebar:
        # Settings section
        st.header("تنظیمات")

        # Model settings
        st.markdown('<div class="parameter-card">', unsafe_allow_html=True)
        st.subheader("پارامترهای مدل")
        radius = st.slider("شعاع ناحیه (پارسک)", 1.0, 20.0, 5.0)
        resolution = st.slider("وضوح شبکه", 20, 100, 50)
        star_temp = st.slider("دمای ستاره (کلوین)", 20000, 50000, 40000)

        density_profile = st.selectbox(
            "پروفایل چگالی",
            ["uniform", "exponential", "power_law"],
            format_func=lambda x: {
                "uniform": "یکنواخت",
                "exponential": "نمایی",
                "power_law": "قانون توانی"
            }.get(x, x)
        )

        density_factor = st.slider("ضریب مقیاس چگالی", 0.1, 5.0, 1.0)
        st.markdown('</div>', unsafe_allow_html=True)

        # Display settings
        st.markdown('<div class="parameter-card">', unsafe_allow_html=True)
        st.subheader("تنظیمات نمایش")
        property_name = st.selectbox(
            "ویژگی برای نمایش",
            ["ionization", "density", "temperature"],
            format_func=lambda x: {
                "ionization": "میزان یونیزاسیون",
                "density": "چگالی",
                "temperature": "دما"
            }.get(x, x)
        )

        cmap = st.selectbox(
            "نقشه رنگی",
            ["plasma", "viridis", "inferno", "coolwarm", "jet"],
            index=0
        )

        opacity = st.slider("شفافیت", 0.1, 1.0, 0.7)

        show_star = st.checkbox("نمایش ستاره مرکزی", True)
        show_boundaries = st.checkbox("نمایش مرزهای ناحیه", True)
        add_dust = st.checkbox("نمایش ذرات غبار", True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Add update button and explanation
        st.markdown('<div class="info-card">', unsafe_allow_html=True)
        if st.button("به‌روزرسانی مدل", help="برای اعمال تغییرات کلیک کنید"):
            # Clear model cache to force creation of a new model
            if 'model_params' in st.session_state:
                del st.session_state.model_params
            st.markdown('<div class="success-message">مدل با موفقیت به‌روزرسانی شد!</div>', unsafe_allow_html=True)

        st.markdown('<div class="info-message">تغییرات به صورت خودکار اعمال می‌شوند، اما در صورت عدم اعمال، از دکمه به‌روزرسانی استفاده کنید.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Main column
    with col_main:
        # Create progress bar
        progress_container = st.container()
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()

        # Function to update progress bar
        def update_progress(message, progress):
            status_text.text(message)
            progress_bar.progress(progress)

        with st.spinner("Creating model..."):
            # Use st.session_state to store and manage model state
            model_params = {
                "radius": radius,
                "resolution": resolution,
                "star_temperature": star_temp,
                "density_profile": density_profile,
                "density_factor": density_factor
            }

            # Check for changes in parameters
            if 'model_params' not in st.session_state or st.session_state.model_params != model_params:
                # Parameters have changed, clear plot cache
                if 'plot_cache' in st.session_state:
                    st.session_state.plot_cache = {}

                # Create new model
                st.session_state.model_params = model_params
                st.session_state.model = HIIRegionModel(
                    radius=radius,
                    resolution=resolution,
                    star_temperature=star_temp,
                    density_profile=density_profile,
                    density_factor=density_factor,
                    progress_callback=update_progress  # Add progress function
                )
            else:
                # If model hasn't changed, complete the progress bar
                update_progress("Model already created.", 1.0)

            # Use model stored in session_state
            model = st.session_state.model

        # Display tabs for different visualization types
        tab1, tab2 = st.tabs(["نمایش سه‌بعدی", "نمودار شعاعی"])

        with tab1:
            st.markdown(f'<h3 class="rtl-text">نمایش سه‌بعدی {property_name}</h3>', unsafe_allow_html=True)

            # Create PyVista plotter
            plotter = model.create_visualization_plotter(
                property_name=property_name,
                cmap=cmap,
                opacity=opacity,
                show_star=show_star,
                show_boundaries=show_boundaries,
                add_dust=add_dust
            )

            # Display 3D visualization using stpyvista
            # Create a unique key based on model parameters and display settings
            view_params = f"{property_name}_{cmap}_{opacity}_{show_star}_{show_boundaries}_{add_dust}"
            model_key = f"{radius}_{resolution}_{star_temp}_{density_profile}_{density_factor}"
            unique_key = f"pv_viewer_{model_key}_{view_params}"

            with st.container():
                st.markdown('<div class="visualization-container">', unsafe_allow_html=True)
                # Use unique key to update component
                stpyvista(plotter, key=unique_key)
                st.markdown('</div>', unsafe_allow_html=True)

        with tab2:
            st.markdown(f'<h3 class="rtl-text">نمودار تغییرات شعاعی {property_name}</h3>', unsafe_allow_html=True)

            # Create a unique key for the plot based on model parameters and selected property
            plot_key = f"plot_{model_key}_{property_name}"

            # Cache plot for better performance
            if 'plot_cache' not in st.session_state:
                st.session_state.plot_cache = {}

            # If plot is not in cache or parameters have changed, create new plot
            if plot_key not in st.session_state.plot_cache:
                # Plot radial profile
                fig = model.plot_radial_profile(property_name=property_name)
                st.session_state.plot_cache[plot_key] = fig

            # Display plot from cache
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.pyplot(st.session_state.plot_cache[plot_key])
                st.markdown('</div>', unsafe_allow_html=True)

        # Additional information at the bottom of the page
        with st.container():
            st.markdown('<div class="info-card">', unsafe_allow_html=True)
            st.markdown("### لایه انتقالی")
            st.markdown("""
            در مرز ناحیه H II، یک لایه انتقالی وجود دارد که در آن میزان یونیزاسیون از تقریباً 100% به صفر کاهش می‌یابد.
            ضخامت این لایه به میانگین مسیر آزاد فوتون‌های یونیزه‌کننده بستگی دارد.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    # Close rtl-text tag
    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
