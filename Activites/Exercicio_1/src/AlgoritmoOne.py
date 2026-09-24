import numpy as np
import math
from geneticalgorithm import geneticalgorithm as ga

# Distance matrix
b = np.array([
	[0, 6, 2, 2, 3],
	[6, 0, 3, 4, 3],
	[2, 3, 0, 3, 6],
	[2, 4, 3, 0, 5],
	[3, 3, 6, 5, 0]
])

inicio = 0
fim = 0

def f(X):
	dim = len(X)
	OF = 0
	# first leg
	OF += b[inicio][int(X[0])]
	# path legs
	for i in range(1, dim):
		OF += b[int(X[i-1])][int(X[i])]
	# penalize duplicate visits
	for i in range(0, dim-1):
		for j in range(i+1, dim):
			if int(X[i]) == int(X[j]):
				OF += 999
	# last leg to finish
	OF += b[int(X[dim-1])][fim]
	return OF

varbound = np.array([[0, len(b)-1]] * len(b))

algorithm_param = {
	'max_num_iteration': None,
	'population_size': 100,
	'mutation_probability': 0.1,
	'elit_ratio': 0.01,
	'crossover_probability': 0.5,
	'parents_portion': 0.3,
	'crossover_type': 'uniform',
	'max_iteration_without_improv': None
}

model = ga(function=f,
		   dimension=len(b),
		   variable_type='int',
		   variable_boundaries=varbound,
		   algorithm_parameters=algorithm_param)
model.run()