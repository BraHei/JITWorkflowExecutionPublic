import matplotlib.pyplot as plt
import numpy as np

# Data from your table
# labels = ['Empty Primary \nEndpoint', 
#          'Half Filled \nPrimary Endpoint', 
#          'Full Primary \nEndpoint']

# Data from your table
labels = ['Empty Primary \nEndpoint',
          'Full Primary \nEndpoint',
          'Empty Primary Endpoint \nWith Replication Service']

# Means and standard deviations
means = [449, 429, 424]
std_devs = [10, 9, 11]

# RED '#d62728'
# ORANGE '#ff7f0e'
# BLUE '#1f77b4'
# GREEN '#2ca02c'

# Color scheme for consistency
#colors = ['#d62728', '#ff7f0e', '#2ca02c']
colors = ['#d62728', '#2ca02c', '#1f77b4']

# Set figure size and resolution (in inches and DPI)
fig_width = 8   # width in inches
fig_height = 6  # height in inches
dpi = 300       # resolution

# Bar width set to fill space (no gaps)
bar_width = 0.9

# Create bar plot
plt.figure(figsize=(10, 6))  # Adjust figure size as needed
plt.bar(labels, means, yerr=std_devs, capsize=10, color=colors, width=bar_width)

# Y-axis label and optional title
plt.ylabel('Argo Workflow Job Time (s)', fontsize=12)
plt.xlabel('Different Primary Endpoint Setups')
plt.title('Small Files Set With Replication', fontsize=14)
#plt.title('Large Files Set With Replication', fontsize=14)

# Optional: rotate labels if necessary for readability
plt.xticks(rotation=15, ha='center')

# Add grid for better readability
plt.grid(axis='y')

# Tight layout to prevent label cutoff
plt.tight_layout()
plt.savefig('small_replication.png', dpi=dpi)
plt.show()



