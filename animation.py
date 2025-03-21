import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# --------------------------
# Setup the figure and axes
# --------------------------

def simulation(v,c):
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(12, 8), dpi=100, facecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(-8, 8)
    ax.set_ylim(-6, 6)
    ax.set_xlabel('X Position ', color='white', fontsize=12)
    ax.set_ylabel('Y Position ', color='white', fontsize=12)
    ax.set_title('Cherenkov Radiation Simulation', color='white', fontsize=16)
    ax.tick_params(colors='white')
    ax.grid(True, alpha=0.2)

    # ------------------------------------
    # Define simulation parameters
    # ------------------------------------
    c_medium = 0.7               # Speed of light in medium (normalized, c_medium < 1)
    v_particle = 0.9             # Particle speed (must be > c_medium for Cherenkov radiation)
    theta = np.arccos(c_medium / v_particle)  # Cherenkov angle in radians

    # Refractive index (assuming speed of light in vacuum c=1)
    n_medium = 1 / c_medium

    # ------------------------------------
    # Global data holders
    # ------------------------------------
    waves = []           # list of wavefronts: { 'center': (x,y), 'start_frame': frame, 'circle': Circle }
    particle_trail = []  # store recent particle positions for tracing the path
    angle_lines = []     # holds the two dashed lines indicating the Cherenkov cone

    # ------------------------------------
    # Create interference grid for overlay
    # ------------------------------------
    nx, ny = 200, 150
    x_lin = np.linspace(-8, 8, nx)
    y_lin = np.linspace(-6, 6, ny)
    X, Y = np.meshgrid(x_lin, y_lin)
    intensity = np.zeros_like(X)

    # Use a blue colormap for interference overlay
    intensity_img = ax.imshow(intensity, extent=[-8, 8, -6, 6], origin='lower',
                            cmap='viridis', alpha=0.5, vmin=0, vmax=1)

    # ------------------------------------
    # Create particle and trail display objects
    # ------------------------------------
    particle, = ax.plot([], [], 'wo', markersize=12, markeredgecolor='cyan',
                        markeredgewidth=2, label='Particle')
    trail, = ax.plot([], [], 'w-', alpha=0.4, linewidth=1)

    # ------------------------------------
    # Create static text annotation for simulation parameters 
    # ------------------------------------
    params_str = (
        f"Particle Speed: {v_particle:.2f}c\n"
        f"Light Speed in Medium: {c_medium:.2f}c\n"
        f"Refractive Index: {n_medium:.2f}\n"
        f"Cherenkov Angle: {np.degrees(theta):.1f}°\n\n"
    )
    params_text = ax.text(0.62, 0.92, params_str, transform=ax.transAxes,
                        color='white', fontsize=10, 
                        bbox=dict(facecolor='black', alpha=0.5),
                        verticalalignment='top')

    # ------------------------------------
    # Function to draw Cherenkov angle (cone) lines 
    # ------------------------------------
    def draw_angle_lines(x, y):
        # Remove old angle lines
        for line in angle_lines:
            line.remove()
        angle_lines.clear()
        
        cone_length = 4
        # Lines radiating from the particle at angles +theta and -theta relative to the x-axis.
        x_top = x + cone_length * np.cos(theta)
        y_top = y + cone_length * np.sin(theta)
        x_bot = x + cone_length * np.cos(theta)
        y_bot = y - cone_length * np.sin(theta)
        
        line1, = ax.plot([x, x_top], [y, y_top], '--', color='cyan', alpha=0.5)
        line2, = ax.plot([x, x_bot], [y, y_bot], '--', color='cyan', alpha=0.5)
        angle_lines.extend([line1, line2])

    # ------------------------------------
    # Function to compute interference intensity over the grid
    # ------------------------------------
    def compute_intensity(frame_number):
        damping = 0.1       # Controls the spatial damping of waves
        wavelength = 1.0    # Arbitrary wavelength scale
        wave_speed = 0.1 * c_medium  # Propagation effect in phase
        
        Z = np.zeros_like(X, dtype=complex)
        for wave in waves:
            cx, cy = wave['center']
            # Only incorporate waves within view
            if cx < -8 or cx > 8 or cy < -6 or cy > 6:
                continue
            age = frame_number - wave['start_frame']
            r = np.sqrt((X - cx)**2 + (Y - cy)**2)
            amplitude = np.exp(-damping * r) / (r + 0.1)
            phase = 2 * np.pi * (r - age * wave_speed) / wavelength
            Z += amplitude * np.exp(1j * phase)
        
        I = np.abs(Z)**2
        # Use a nonlinear scaling (power-law) for high contrast in interference features
        I_norm = np.power(I, 0.3)
        I_norm /= (I_norm.max() + 1e-6)
        return I_norm

    # ------------------------------------
    # Initialization function for the animation
    # ------------------------------------
    def init():
        particle.set_data([], [])
        trail.set_data([], [])
        intensity_img.set_array(np.zeros_like(X))
        return [particle, trail, intensity_img, params_text] + angle_lines

    # ------------------------------------
    # Main animation function
    # ------------------------------------
    def animate(frame):
        # Particle moving in a straight horizontal line (y=0)
        x = frame * 0.1 - 4  # Adjust speed and initial offset as needed
        y = 0
        particle.set_data([x], [y])
        
        # Update particle trail (last 30 positions)
        particle_trail.append((x, y))
        if len(particle_trail) > 30:
            particle_trail.pop(0)
        xs, ys = zip(*particle_trail)
        trail.set_data(xs, ys)
        
        # Update the Cherenkov cone lines relative to the current particle position
        draw_angle_lines(x, y)
        
        # Every 5 frames, emit a new wave (if particle is on screen)
        if frame % 5 == 0 and -8 <= x <= 8:
            new_wave = {'center': (x, y), 'start_frame': frame}
            # Draw a subtle yellow circle for the wavefront (low alpha)
            circle = plt.Circle((x, y), 0.1, fill=False, edgecolor='yellow',
                                alpha=0.2, linewidth=1)
            ax.add_patch(circle)
            new_wave['circle'] = circle
            waves.append(new_wave)
        
        # Update existing waves: expand the circles and fade them out
        for wave in waves.copy():
            age = frame - wave['start_frame']
            radius = 0.1 + age * 0.1 * c_medium
            if 'circle' in wave:
                wave['circle'].set_radius(radius)
                new_alpha = max(0, 0.2 - age * 0.01)
                wave['circle'].set_alpha(new_alpha)
                cx, cy = wave['center']
                if new_alpha <= 0.03 or cx < -10 or cx > 10 or cy < -8 or cy > 8:
                    wave['circle'].remove()
                    waves.remove(wave)
        
        # Compute and update the interference intensity overlay
        I_norm = compute_intensity(frame)
        intensity_img.set_array(I_norm)
        
        # Return all animated objects
        return [particle, trail, intensity_img, params_text] + angle_lines + \
            [w['circle'] for w in waves if 'circle' in w]

    # ------------------------------------
    # Create and save the animation
    # ------------------------------------
    anim = FuncAnimation(fig, animate, init_func=init, frames=200,
                        interval=30, blit=True)

    writer = PillowWriter(fps=30, metadata=dict(artist='Me'))
    print("Saving animation...")
    anim.save('cherenkov_radiation.gif', writer=writer,
            savefig_kwargs={'facecolor': 'black'},
            progress_callback=lambda i, n: print(f'Saving frame {i} of {n}'))
    print("Animation saved as 'cherenkov_radiation.gif'")

    plt.close()
