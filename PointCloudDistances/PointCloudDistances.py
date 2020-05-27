import numpy as np
import os
from pyntcloud import PyntCloud
import matplotlib.pyplot as plt
from sklearn.neighbors import KDTree

"""
This script reads a point cloud file and computes the distance to the nearest
neighbour via sklearn.neighbour KDTree method.

A filter based on the robust z-score is used to filter outliers, then the 
resultant points plotted as a histogram

Requires the pyntcloud module to process point cloud files:
    https://pyntcloud.readthedocs.io/en/latest/
"""

def outlier(points, thresh = 3.5):
    """
    Determines if a point is an outlier (z-score > 3.5) using the robust
    z-score method, using the median absolute deviation
    """    
    median = np.median(points)
    abs_diff = np.absolute(points - median)
    median_abs_diff = np.median(abs_diff)
    robust_z_score = 0.6745 * abs_diff / median_abs_diff
    # 0.675 is 0.75th of standard normal distribution which mean abs diff 
    # converges to
    
    return robust_z_score > thresh

#%%
os.chdir(os.getcwd())
print(os.getcwd())

cloud = PyntCloud.from_file("PhoneCar.ply")
#%%
xyz = cloud.points.iloc[:, [0, 1, 2]]
tree = KDTree(xyz)
closest_dist , closest_ind= KDTree(xyz).query(xyz, k = 2)
# Gets the second closest neighbour for each point as the closest is itself
closest_dist = closest_dist[:, 1]

#%%
closest_dist_filtered = closest_dist[~outlier(closest_dist)]

#%%
num_bins = 400
n, bins, patches = plt.hist(closest_dist_filtered, num_bins)
plt.xlabel("Distance to Closest Neighbour (mm)")
plt.ylabel("Number of Points")
plt.title("Histogram with " + str(len(closest_dist_filtered)) + " Points and " 
          + str(num_bins) + " Bins")
plt.grid(axis = "y")
plt.savefig("Trial.png", dpi = 2000)