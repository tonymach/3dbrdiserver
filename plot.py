import re
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Read path data from the text file
with open('path_data.txt', 'r') as file:
    lines = file.readlines()

timestamps = []
x_positions = []
y_positions = []
z_positions = []

# Parse path data from each line
for line in lines:
    timestamp, x, y, z = re.findall(r"Time: (.*?), Position: \(([\d.-]+),([\d.-]+),([\d.-]+)\)", line)[0]
    timestamps.append(float(timestamp))
    x_positions.append(float(x))
    y_positions.append(float(y))
    z_positions.append(float(z))

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the path
ax.plot(x_positions, y_positions, z_positions, '-o', markersize=5)

# Label axes
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Display the plot
plt.show()
