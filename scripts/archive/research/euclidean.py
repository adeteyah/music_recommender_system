from scipy import spatial

a = [1, 2]
b = [2, 4]
c = [2.5, 4]
d = [4.5, 5]

print(spatial.distance.euclidean(c, a))

print(spatial.distance.euclidean(c, b))

print(spatial.distance.euclidean(c, d))
