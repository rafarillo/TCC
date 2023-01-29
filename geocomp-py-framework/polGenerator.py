from polygenerator import (
    random_polygon,
    random_star_shaped_polygon,
    random_convex_polygon,
)
import numpy as np

polygon = random_polygon(num_points=2500)
polygon = np.array(polygon)
print('[')
for element in polygon:
    print("    {} {}".format(element[0]*1000, element[1]*1000))
print(']')