class Graph:
	def __init__(self):
		self.adj = {}
		self.edgelist = []
		self.nodes = []
		self.visited = {}
		self.iscycle = False
		self.curr = []

	def initialize(self, edgelist, nodes):
		self.edgelist = edgelist
		self.nodes = nodes
		self.build()

	def build(self):
		for edge in self.edgelist:
			u,v = edge
			if(u not in self.adj):
				self.adj[u] = []
			self.adj[u] += [v]

	def dfsutil(self, node):
		#print "Node is:", node
		
		self.curr += [node]
		#print "Before:",self.visited
		self.visited[node] = 1
		if (node in self.adj):
			for child in self.adj[node]:
				if self.visited[child] == 0:
					self.dfsutil(child)
				elif(self.visited[child] == 1):
						self.iscycle = True
		self.visited[node] = 2
		#print  "After:",self.visited

	def dfs(self, start_node):
		for node in self.nodes:
			self.visited[node] = 0
		self.dfsutil(start_node)
	def checkCycle(self, edge):
		#Temproary add the edge into the graph
		u,v = edge
		if(u not in self.adj):
			self.adj[u] = []
		self.adj[u] += [v]
		self.dfs(u)
		self.adj[u] = self.adj[u][:-1]
		flag = self.iscycle
		self.iscycle = False
		return flag

	def get_vertices(self, start_node):
		for node in self.nodes:
				self.visited[node] = 0
		self.dfsutil(start_node)
		temp = self.curr
		self.curr = []
		return temp

def main():
	edgelist = [(1,3), (1,4), (2, 4), (2, 5)]
	gr = Graph()
	gr.initialize(edgelist, [1,2,3,4,5]);
	for i in xrange(1,6):
		print gr.get_vertices(i)

if __name__ == '__main__':
	main()
	
'''
1->2
   |
   3
'''
'''
1 2
    Graduate      Important
      
3 4 5
CSC 505  CSC591        Job

'''
		

