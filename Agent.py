'''
file for inheriting minimax and NN. Used to make sure 
get_move exists and is overruled by the child class.

if this were java, this would be necessary for strong typing too.
'''
class Agent:
	def __init__(self):
		pass
	def get_move(self,board):
		raise(RuntimeError("get_move method not overruled by inheriting class"))