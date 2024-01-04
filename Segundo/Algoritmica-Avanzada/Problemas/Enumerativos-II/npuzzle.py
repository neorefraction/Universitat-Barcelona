import math
import random
import networkx as nx
import numpy as np
class NPuzzle:
    
    def __init__(self):
        self._board = None
        

    def create_board(self, n=3, moves=10, solved=False):      
        self._board = np.roll(np.arange(n*n),-1).reshape((n,n))
        if solved: return board
        for i in range(moves):
            moves = self.allowed_moves()
            self._board = self.move(random.choice(moves))._board
    
    def allowed_moves(self):
        board = self._board
        moves = []
        n = board.shape[0]
        # Find the 0 in the board
        posy, posx = np.where(board==0)
        posx, posy = posx[0], posy[0]
        if posx>0:moves.append('L')
        if posx<n-1:moves.append('R')
        if posy>0:moves.append('U')
        if posy<n-1:moves.append('D')
        return moves

    def move(self, dd): #dd is the direction noted by: ['R','L','U','D']
        board = np.copy(self._board)
        if not dd in self.allowed_moves(): return self
        posy, posx = np.where(board==0)
        posx, posy = posx[0], posy[0]
        excx, excy = posx, posy
        if dd=='D': excy+=1
        elif dd=='U': excy-=1
        elif dd=='R': excx+=1
        elif dd=='L': excx-=1
        board[posy,posx] = board[excy,excx]
        board[excy,excx] = 0
        xx = NPuzzle()
        xx._board = board
        return xx
    
    def rank(self):
        board = self._board
        sol = np.roll(np.arange(board.shape[0]*board.shape[1]),-1)
        rr = board.ravel()
        return np.sum(sol!=rr)
    
    def get_state_id(self):
        return ','.join([str(x) for x in self._board.flatten()])
    
    def state(self):
        return self.rank()==0
    
    def __lt__(self,other):
        return self.get_state_id() < other.get_state_id()
    
    def __str__(self):
        _str = ""
        board = self._board
        nzeros = int(math.floor(math.log10(np.amax(board))))
        for i in board:
            _str+= "+"+ ("-"*((board.shape[0]*(4+nzeros))-1)) +"+\n"
            _str+= "| "
            for j in i:
                if j != 0:
                    diff = nzeros-int(math.floor(math.log10(j)))
                    _str+= " "*diff + str(j)+" | "
                else:
                    _str+=" "*nzeros +"  | "

            _str+= "\n"
        _str+= "+"+ ("-"*((board.shape[0]*(4+nzeros))-1))+"+\n"
        return _str
    
    def manhattan_distance(self,count_blank=False):
        board = self._board
        sol = np.roll(np.arange(board.shape[0]*board.shape[1]),-1).reshape(board.shape)
        diff = 0
        for i in range(board.shape[0]*board.shape[1]):
            pos_sol = np.asarray(np.where(sol==i)).ravel()
            pos_board = np.asarray(np.where(board==i)).ravel()
            if count_blank or board[pos_board[0],pos_board[1]] != 0:
                diff += np.sum(np.abs(pos_board-pos_sol))
        return diff
    
    def hamming_distance(self):
        board = self._board
        sol = np.roll(np.arange(board.shape[0]*board.shape[1]),-1).reshape(board.shape)
        return np.sum(board!=sol) - int(np.where(board==0) != np.where(sol==0))

