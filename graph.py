from collections import defaultdict
import math
import copy
import inspect
import itertools as it
 
# representation for our graph of transactions
# u ---w---> v means: u owes v the amount of w dollars
class Graph:
 
	def __init__(self, vertices, balances={}):
		self.vertices = vertices 
		
		self.graph = defaultdict(list) 

		self.weights = defaultdict(dict)

		self.edges = []

		self.balances = copy.deepcopy(balances)

		self.preset_balances = True if balances!={} else False

	# functions to initialize graph ----------------------------------------------
	def add_edge(self, u, v, w):

		self.graph[u].append(v)
		self.graph[v].append(u)

		self.edges.append((u, v ,w))

		self.__add_edge_weight(u, v, w)

	def __add_edge_w_to_balances(self, vertex, w):
		wSign = w if not self.preset_balances else -1.0 * w
		if vertex in self.balances:
			self.balances[vertex] += wSign
		else:
			self.balances[vertex] = wSign

	def __add_edge_weight_by_dir(self, u, v, w):
		self.weights[u][v] = w
		self.__add_edge_w_to_balances(u, w)

	def __add_edge_weight(self, u, v, w):
		self.__add_edge_weight_by_dir(u, v, w)
		self.__add_edge_weight_by_dir(v, u, -1.0 * w)

	# helper functions to get bipartite transfer graph -----------------------------
	def get_pos_b_vertices(self):
		return [u for u, b in self.balances.items() if b > 0]
	def get_neg_b_vertices(self):
		return [u for u, b in self.balances.items() if b < 0]
	def get_zero_b_vertices(self):
		return [u for u, b in self.balances.items() if b == 0]

	def is_bipartite(self):
		for u, info in self.weights.items():
			pos_nums = False
			neg_nums = False
			for v, w in info.items():
				if w > 0:
					pos_nums = True
				elif w < 0:
					neg_nums = True
			if pos_nums and neg_nums:
				return False
		return True

	# prodders ---------------------------------------------------------------------

	def how_much_does_u_owe(self, u):
		if u in self.weights:
			return sum(self.weights[u].values())
		return 0.0

	def __str__(self):
		s = str()
		for u, info in self.weights.items():
			for v, w in info.items():
				if w > 0:
					s += u + " -" + str(w).rjust(5, '-') + "--> " + v + "\n"
		return s


# contrusts bipartite transger graph, which 
# minimizes the amount in each transaction (edge)
# while still holding that everyone owes and is owed the same total amount in the end 
# on its own, does NOT minimize the number of transactions between people. ---------------------------------

def construct_bipartite_transfer_graph(vertices, balances):
	working_g = _construct_bipartite_transfer_graph_recurs(Graph(copy.deepcopy(vertices), copy.deepcopy(balances)))
	
	bipartite_g = Graph(copy.deepcopy(working_g.vertices))
	
	for edge in copy.deepcopy(working_g.edges):
		u, v, w = edge
		bipartite_g.add_edge(u, v, w)

	return bipartite_g

def _construct_bipartite_transfer_graph_recurs(g):
	if len(g.vertices) == len(g.get_zero_b_vertices()):
		return g

	u = g.get_pos_b_vertices()[0]
	v = g.get_neg_b_vertices()[0]

	m = min(g.balances[u], abs(g.balances[v]))
	g.add_edge(u, v, m)

	return _construct_bipartite_transfer_graph_recurs(g)


# helper functions for construct_maximized_component_graph ----------------------------vvv

def calculate_r_range(k, rest, components):
	r_max = len(rest) - k + len(components)+1
	r_min = len(rest) if len(components)+1==k else 1
	return range(r_min, r_max+1)

def all_subsets(names, r_range):
	all_combs = []
	for r in r_range:
		combs = list(it.combinations(names, r))
		for c in combs:
			all_combs.append(c)
	return all_combs

# maximize components to minimize transfers

# iterate thru k = min(pos_balances, neg_balances)
# first try every combo with k components 
# a combo works if the sum of the balances of each subset are zero
# if it doesnt work, subtract 1 from k and keep chuggin'
# if k=1, thats  just one component, aka the original graph is the best you can do -------------------

def _construct_maximized_component_graph_recurs(k, components, balances):
	new_components = copy.deepcopy(components)
	rest = [x for x in balances if not x in [y for comp in new_components for y in comp]]
	#print("k: " + str(k) + ", rest: " + str(rest) + ", components: " + str(new_components))
	if(rest == []):
		#print("NEW COMPONENTS: " + str(new_components))
		return new_components
	if(k <= 1):
		new_components.append(rest)
		return new_components 

	for subset in all_subsets(rest, calculate_r_range(k, rest, new_components)):
		subset_sum = sum([balances[key] for key in subset])

		#print("subset: " + str(subset) + ", subset_sum: " + str(subset_sum))

		if subset_sum == 0:
			new_components.append(subset)
			return _construct_maximized_component_graph_recurs(k, new_components, balances)

def construct_maximized_component_graph(g):
	#print(g.balances)
	k_max = min(len(g.get_pos_b_vertices()), len(g.get_neg_b_vertices()))
	for k in range(k_max, 0, -1):
		components = _construct_maximized_component_graph_recurs(k, copy.deepcopy(list()), copy.deepcopy(g.balances))
		if components != None:
			return components

# optimize transactions function that puts it all together! 
# construct maximized component graph first, then for each component, construct the bipartite transfer graph
# then combine all of them back into one graph for easy querying!---------------------------------------------------

def optimize_transactions(g):
	components = construct_maximized_component_graph(g)
	final_g = Graph(g.vertices)
	for vertices in components:
		balances = {key: g.balances[key] for key in vertices}
		g_comp = construct_bipartite_transfer_graph(vertices, balances)
		for u,v,w in g_comp.edges:
			final_g.add_edge(u,v,w)
	return final_g

 
# TESTS ----------------------------------------------------------

class Tester():

	def __init__(self):

		print("\nTesting Unit: " + inspect.stack()[1][4][0].split('(')[0])
		self.num_tests = 0

	def assertEquals(self, expected, actual, msg=""):
		self.num_tests += 1

		if expected != actual:
			print("Test #" + str(self.num_tests) + " FAILED.")
			print("Expected: " + str(expected) + ", Got: " + str(actual))
		else:
			print("Test #" + str(self.num_tests) + " passed.")


def test_construct_bipartite_transfer_graph(t):

	vertices = ["A","B","C","D"]
	start_g = Graph(vertices)
	start_g.add_edge("A", "D", 3.0)
	start_g.add_edge("B", "D", 3.0)
	start_g.add_edge("B", "C", 2.0)
	start_g.add_edge("D", "C", 3.0)

	end_g = construct_bipartite_transfer_graph(start_g.vertices, start_g.balances)
	print(end_g)

	# verifies that, in total, the group does not owe more/less than is owed, and vice versa
	t.assertEquals(sum(start_g.balances.values()), 0)
	t.assertEquals(sum(end_g.balances.values()), 0)

	# verifies that everyone owes and is owed the same total amount in the end 
	for u in vertices:
		t.assertEquals(start_g.balances[u], end_g.balances[u])

	#verfies that the graph returned is indeed bipartite
	t.assertEquals(True, end_g.is_bipartite())

def test_optimize_transactions(t):
	vertices = ["A","B","C","D","E","F","G"]
	start_g = Graph(vertices)
	start_g.add_edge("A", "D", 3.0)
	start_g.add_edge("B", "D", 3.0)
	start_g.add_edge("B", "C", 2.0)
	start_g.add_edge("D", "C", 3.0)
	start_g.add_edge("E", "F", 5.0)
	start_g.add_edge("F", "A", 3.0)
	start_g.add_edge("F", "G", 1.0)
	start_g.add_edge("A", "G", 1.0)

	end_g = optimize_transactions(start_g)
	print(end_g)

	# verifies that, in total, the group does not owe more/less than is owed, and vice versa
	t.assertEquals(sum(start_g.balances.values()), 0)
	t.assertEquals(sum(end_g.balances.values()), 0)

	# verifies that everyone owes and is owed the same total amount in the end 
	for u in vertices:
		t.assertEquals(start_g.balances[u], end_g.balances[u])

	#verfies that the graph returned is indeed bipartite
	t.assertEquals(True, end_g.is_bipartite())

	#TODO: to verify that the number of transactions is minimized, i might just have to do it by hand and check(?)



test_construct_bipartite_transfer_graph(Tester())
test_optimize_transactions(Tester())













