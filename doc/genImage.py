import matplotlib.pyplot as plt
import numpy as np

# Define the grid size
nx, ny = 5, 5  # Number of nodes in the x and y directions

# Generate the grid points
x = np.linspace(0, 1, nx)
y = np.linspace(0, 1, ny)

# Create a meshgrid for plotting
X, Y = np.meshgrid(x, y)

# Plot the grid representing the node centers
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(X, Y, 'ko')  # Plot nodes as points
ax.plot(X, Y, color='black')  # Plot vertical lines
ax.plot(X.T, Y.T, color='black')  # Plot horizontal lines

# Function to draw control volumes with correct positioning
def draw_cv(ax, i, j, label=None):
    # Adjust control volume boundaries based on cell location
    if i == 0:  # Left side
        dx_left = 0
        dx_right = dx
    elif i == nx - 1:  # Right side
        dx_left = dx
        dx_right = 0
    else:  # Center cells
        dx_left = dx
        dx_right = dx

    if j == 0:  # Bottom side
        dy_bottom = 0
        dy_top = dy
    elif j == ny - 1:  # Top side
        dy_bottom = dy
        dy_top = 0
    else:  # Center cells
        dy_bottom = dy
        dy_top = dy

    cv_x = [x[i] - dx_left, x[i] + dx_right, x[i] + dx_right, x[i] - dx_left, x[i] - dx_left]
    cv_y = [y[j] - dy_bottom, y[j] - dy_bottom, y[j] + dy_top, y[j] + dy_top, y[j] - dy_bottom]
    
    ax.plot(cv_x, cv_y, 'b--')  # Use blue color for dashed lines
    if label != None:
        ax.annotate(label, (x[i], y[j]), textcoords="offset points", xytext=(5,5))

# Control volume dimensions around a node
dx = (x[1] - x[0]) / 2
dy = (y[1] - y[0]) / 2

# Draw control volumes for corner cells
draw_cv(ax, 0, 0,)  # Top left corner
draw_cv(ax, nx-1, 0)  # Top right corner
draw_cv(ax, 0, ny-1)  # Bottom left corner
draw_cv(ax, nx-1, ny-1)  # Bottom right corner

# Draw control volumes for one cell on each side
draw_cv(ax, nx//2, 0)  # Top side
draw_cv(ax, nx//2, ny-1)  # Bottom side
draw_cv(ax, 0, ny//2)  # Left side
draw_cv(ax, nx-1, ny//2)  # Right side

# Draw control volume for one normal cell in the center
draw_cv(ax, nx//2, ny//2, 'i, j')  # Center

# Remove title, axes, and ticks
ax.set_axis_off()

plt.savefig("control_volumes.pdf")