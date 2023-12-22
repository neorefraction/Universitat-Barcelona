#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 11:22:03 2022

@author: ignasi
"""
import copy
import math

import chess
import board
import numpy as np
import sys
import queue
from typing import List

RawStateType = List[List[List[int]]]


from itertools import permutations


class Aichess():
    """
    A class to represent the game of chess.

    ...

    Attributes:
    -----------
    chess : Chess
        represents the chess game

    Methods:
    --------
    startGame(pos:stup) -> None
        Promotes a pawn that has reached the other side to another, or the same, piece

    """

    def __init__(self, TA, myinit=True):

        if myinit:
            self.chess = chess.Chess(TA, True)
        else:
            self.chess = chess.Chess([], False)

        self.listNextStates = []
        self.listVisitedStates = []
        self.listVisitedSituations = []
        self.pathToTarget = []
        self.currentStateW = self.chess.boardSim.currentStateW;
        self.depthMax = 8;
        self.checkMate = False

    def copyState(self, state):
        
        copyState = []
        for piece in state:
            copyState.append(piece.copy())
        return copyState
        
    def isVisitedSituation(self, color, mystate):
        
        if (len(self.listVisitedSituations) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedSituations)):
                    if self.isSameState(list(perm_state[j]), self.listVisitedSituations.__getitem__(k)[1]) and color == \
                            self.listVisitedSituations.__getitem__(k)[0]:
                        isVisited = True

            return isVisited
        else:
            return False


    def getCurrentStateW(self):

        return self.myCurrentStateW

    def getListNextStatesW(self, myState):

        self.chess.boardSim.getListNextStatesW(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def getListNextStatesB(self, myState):
        self.chess.boardSim.getListNextStatesB(myState)
        self.listNextStates = self.chess.boardSim.listNextStates.copy()

        return self.listNextStates

    def isSameState(self, a, b):

        isSameState1 = True
        # a and b are lists
        for k in range(len(a)):

            if a[k] not in b:
                isSameState1 = False

        isSameState2 = True
        # a and b are lists
        for k in range(len(b)):

            if b[k] not in a:
                isSameState2 = False

        isSameState = isSameState1 and isSameState2
        return isSameState

    def isVisited(self, mystate):

        if (len(self.listVisitedStates) > 0):
            perm_state = list(permutations(mystate))

            isVisited = False
            for j in range(len(perm_state)):

                for k in range(len(self.listVisitedStates)):

                    if self.isSameState(list(perm_state[j]), self.listVisitedStates[k]):
                        isVisited = True

            return isVisited
        else:
            return False

    def isWatchedBk(self, currentState):

        self.newBoardSim(currentState)

        bkPosition = self.getPieceState(currentState, 12)[0:2]
        wkState = self.getPieceState(currentState, 6)
        wrState = self.getPieceState(currentState, 2)

        # Si les negres maten el rei blanc, no és una configuració correcta
        if wkState == None:
            return False
        # Mirem les possibles posicions del rei blanc i mirem si en alguna pot "matar" al rei negre
        for wkPosition in self.getNextPositions(wkState):
            if bkPosition == wkPosition:
                # Tindríem un checkMate
                return True
        if wrState != None:
            # Mirem les possibles posicions de la torre blanca i mirem si en alguna pot "matar" al rei negre
            for wrPosition in self.getNextPositions(wrState):
                if bkPosition == wrPosition:
                    return True
        return False
        


    def isWatchedWk(self, currentState):
        self.newBoardSim(currentState)

        wkPosition = self.getPieceState(currentState, 6)
        bkState = self.getPieceState(currentState, 12)
        brState = self.getPieceState(currentState, 8)

        # If whites kill the black king , it is not a correct configuration
        if bkState == None:
            return False
        # We check all possible positions for the black king, and chck if in any of them it may kill the white king
        for bkPosition in self.getNextPositions(bkState):
            if wkPosition == bkPosition:
                # That would be checkMate
                return True
        if brState != None:
            # We check the possible positions of the black tower, and we chck if in any o them it may killt he white king
            for brPosition in self.getNextPositions(brState):
                if wkPosition == brPosition:
                    return True

        return False

    def allBkMovementsWatched(self, current_state):
        self.newBoardSim(current_state)

        # Cogemos el rey negro
        black_king = self.getPieceState(current_state, 12)

        # Si el rey esta contra una pared puede haber jaque
        if black_king[0] == 0 or black_king[0] == 7 or black_king[1] == 0 or black_king[1] == 7:

            white_rook = self.getPieceState(current_state, 2)
            white_state = self.getWhiteState(current_state).copy()

            # Comprobamos el estado del rey en todos sus siguientes posibles movimientos
            for s in self.getListNextStatesB(self.getBlackState(current_state)):

                if white_rook != None and white_rook[0:2] == s[0][0:2]:
                    white_state.remove(white_rook)

                s += white_state

                # Movemos las piezas al siguiente estado
                self.newBoardSim(s)

                # Comprobamos si el rey negro NO está amenazado
                if not self.isWatchedBk(s):
                    return False
        else:
            return False

        return True

    def allWkMovementsWatched(self, current_state):

        self.newBoardSim(current_state)

        # Cogemos el rey blanco
        white_king = self.getPieceState(current_state, 6)

        # Si el rey se encuentra en una pared podemos estar en jaque
        if white_king[0] == 0 or white_king[0] == 7 or white_king[1] == 0 or white_king[1] == 7:

            black_rook = self.getPieceState(current_state, 8)
            black_state = self.getBlackState(current_state).copy()

            # Comprobamos el estado del rey en todos sus siguientes posibles movimientos
            for s in self.getListNextStatesW(self.getWhiteState(current_state)):
                
                if black_rook != None and black_rook[0:2] == s[0][0:2]:
                    black_state.remove(brState)

                state += black_state

                # Movemos las piezas blancas al nuevo estado
                self.newBoardSim(s)

                # Comprobamos que el rey blacno NO esté amenazado
                if not self.isWatchedWk(s):
                    return False
            else:
                return False

        return True

    def isWhiteInCheckMate(self, current_state):
        return self.isWatchedWk(current_state) and self.allWkMovementsWatched(current_state)

    def isBlackInCheckMate(self, current_state):
        return self.isWatchedBk(current_state) and self.allBkMovementsWatched(current_state)

    def newBoardSim(self, listStates):
        # We create a  new boardSim
        TA = np.zeros((8, 8))
        for state in listStates:
            TA[state[0]][state[1]] = state[2]

        self.chess.newBoardSim(TA)

    def getPieceState(self, state, piece):
        pieceState = None
        for i in state:
            if i[2] == piece:
                pieceState = i
                break
        return pieceState

    def getCurrentState(self):
        listStates = []
        for i in self.chess.board.currentStateW:
            listStates.append(i)
        for j in self.chess.board.currentStateB:
            listStates.append(j)
        return listStates

    def getNextPositions(self, state):
        # Given a state, we check the next possible states
        # From these, we return a list with position, i.e., [row, column]
        if state == None:
            return None
        if state[2] > 6:
            nextStates = self.getListNextStatesB([state])
        else:
            nextStates = self.getListNextStatesW([state])
        nextPositions = []
        for i in nextStates:
            nextPositions.append(i[0][0:2])
        return nextPositions

    def getWhiteState(self, currentState):
        whiteState = []
        wkState = self.getPieceState(currentState, 6)
        whiteState.append(wkState)
        wrState = self.getPieceState(currentState, 2)
        if wrState != None:
            whiteState.append(wrState)
        return whiteState

    def getBlackState(self, currentState):
        blackState = []
        bkState = self.getPieceState(currentState, 12)
        blackState.append(bkState)
        brState = self.getPieceState(currentState, 8)
        if brState != None:
            blackState.append(brState)
        return blackState

    def getMovement(self, state, nextState):
        # Given a state and a successor state, return the postiion of the piece that has been moved in both states
        pieceState = None
        pieceNextState = None
        for piece in state:
            if piece not in nextState:
                movedPiece = piece[2]
                pieceNext = self.getPieceState(nextState, movedPiece)
                if pieceNext != None:
                    pieceState = piece
                    pieceNextState = pieceNext
                    break

        return [pieceState, pieceNextState]

    def heuristica(self, currentState, color):
        # In this method, we calculate the heuristics for both the whites and black ones
        # The value calculated here is for the whites, 
        # but finally from everything, as a function of the color parameter, we multiply the result by -1
        value = 0

        bkState = self.getPieceState(currentState, 12)
        wkState = self.getPieceState(currentState, 6)
        wrState = self.getPieceState(currentState, 2)
        brState = self.getPieceState(currentState, 8)

        filaBk = bkState[0]
        columnaBk = bkState[1]
        filaWk = wkState[0]
        columnaWk = wkState[1]

        if wrState != None:
            filaWr = wrState[0]
            columnaWr = wrState[1]
        if brState != None:
            filaBr = brState[0]
            columnaBr = brState[1]

        # We check if they killed the black rook
        if brState == None:
            value += 50
            fila = abs(filaBk - filaWk)
            columna = abs(columnaWk - columnaBk)
            distReis = min(fila, columna) + abs(fila - columna)
            if distReis >= 3 and wrState != None:
                filaR = abs(filaBk - filaWr)
                columnaR = abs(columnaWr - columnaBk)
                value += (min(filaR, columnaR) + abs(filaR - columnaR))/10
            # If we are white white, the closer our king from the oponent, the better
            # we substract 7 to the distance between the two kings, since the max distance they can be at in a board is 7 moves
            value += (7 - distReis)
            # If they black king is against a wall, we prioritize him to be at a corner, precisely to corner him
            if bkState[0] == 0 or bkState[0] == 7 or bkState[1] == 0 or bkState[1] == 7:
                value += (abs(filaBk - 3.5) + abs(columnaBk - 3.5)) * 10
            #If not, we will only prioritize that he approahces the wall, to be able to approach the check mate
            else:
                value += (max(abs(filaBk - 3.5), abs(columnaBk - 3.5))) * 10

        # They killed the white tower. Within this method, we consider the same conditions than in the previous condition
        # Within this method we consider the same conditions than in the previous section, but now with reversed values.
        if wrState == None:
            value += -50
            fila = abs(filaBk - filaWk)
            columna = abs(columnaWk - columnaBk)
            distReis = min(fila, columna) + abs(fila - columna)

            if distReis >= 3 and brState != None:
                filaR = abs(filaWk - filaBr)
                columnaR = abs(columnaBr - columnaWk)
                value -= (min(filaR, columnaR) + abs(filaR - columnaR)) / 10
            # If we are white, the close we have our king from the oponent, the better
            # If we substract 7 to the distance between both kings, as this is the max distance they can be at in a chess board
            value += (-7 + distReis)

            if wkState[0] == 0 or wkState[0] == 7 or wkState[1] == 0 or wkState[1] == 7:
                value -= (abs(filaWk - 3.5) + abs(columnaWk - 3.5)) * 10
            else:
                value -= (max(abs(filaWk - 3.5), abs(columnaWk - 3.5))) * 10

        # We are checking blacks
        if self.isWatchedBk(currentState):
            value += 20

        # We are checking whites
        if self.isWatchedWk(currentState):
            value += -20

        # If black, values are negative, otherwise positive
        if not color:
            value = (-1) * value

        return value


    def minimaxGame(self, depthWhite, depthBlack):
        '''
        '''

        def max_value_white(state, depth):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedWk(state):
                return float('-inf'), state

            if depth == 0:
                return self.heuristica(state, True), state

            v, next_state = float('-inf'), None

            white_state = self.getWhiteState(state).copy()
            black_state = self.getBlackState(state).copy()
            black_rook = self.getPieceState(state, 8)

            for s in self.getListNextStatesW(white_state):

                # Comprobamos si se han comido la torre negra, en caso afirmativo, sacamos la torre del estado
                if black_rook != None and black_rook[0:2] == s[0][0:2]:
                    black_state.remove(black_rook)

                s += black_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey se encuentra en jaque
                if not self.isWatchedWk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = min_value_white(s, depth - 1)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value > v:
                        v, next_state = value, value_state
            
            return v, next_state

        def min_value_white(state, depth):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedBk(state):
                return float('inf'), state

            if depth == 0:
                return self.heuristica(state, True), state

            v, next_state = float('-inf'), None

            white_state = self.getWhiteState(state).copy()
            black_state = self.getBlackState(state).copy()
            white_rook = self.getPieceState(state, 2)

            for s in self.getListNextStatesB(black_state):

                # Comprobamos si se han comido la torre blanca, en caso afirmativo, sacamos la torre del estado
                if white_rook != None and white_rook[0:2] == s[0][0:2]:
                    white_state.remove(white_rook)

                s += white_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey negro se encuentra en jaque
                if not self.isWatchedBk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = max_value_white(s, depth - 1)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value < v:
                        v, next_state = value, value_state
            
            return v, next_state

        def max_value_black(state, depth):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedBk(state):
                return float('-inf'), state

            if depth == 0:
                return self.heuristica(state, False), state

            v, next_state = float('-inf'), None

            white_state = self.getWhiteState(state).copy()
            black_state = self.getBlackState(state).copy()
            white_rook = self.getPieceState(state, 2)

            for s in self.getListNextStatesB(black_state):

                # Comprobamos si se han comido la torre negra, en caso afirmativo, sacamos la torre del estado
                if white_rook != None and white_rook[0:2] == s[0][0:2]:
                    white_state.remove(white_rook)

                s += white_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey se encuentra en jaque
                if not self.isWatchedBk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = min_value_black(s, depth - 1)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value > v:
                        v, next_state = value, value_state
            
            return v, next_state

        def min_value_black(state, depth):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedWk(state):
                return float('inf'), state

            if depth == 0:
                return self.heuristica(state, False), state

            v, next_state = float('-inf'), None

            white_state = self.getWhiteState(state).copy()
            black_state = self.getBlackState(state).copy()
            black_rook = self.getPieceState(state, 8)

            for s in self.getListNextStatesw(white_state):

                # Comprobamos si se han comido la torre negra, en caso afirmativo, sacamos la torre del estado
                if black_rook != None and black_rook[0:2] == s[0][0:2]:
                    black_state.remove(black_rook)

                s += black_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey se encuentra en jaque
                if not self.isWatchedWk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = max_value_black(s, depth - 1)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value < v:
                        v, next_state = value, value_state
            
            return v, next_state

        current_state = self.getCurrentState()

        # Comprobamos que el estado inicial no sea un estado objetivo
        if self.isWhiteInCheckMate(current_state):
            return False  # Ganan las negras
        if self.isBlackInCheckMate(current_state):
            return True  # Ganan las blancas

        # Añadimos el estado a la lista de estados visitados para evitar movimientos en bucle
        self.listVisitedSituations.append((False, current_state))

        turn = -1

        while not self.isWhiteInCheckMate(current_state) and not self.isBlackInCheckMate(current_state):

            turn += 1
            current_state = self.getCurrentState()

            if turn % 2 == 0:  # Turno de las blancas
            
                # Buscamos la siguiente mejor jugada para las blancas
                _, next_state = max_value_white(current_state, depthWhite)

                # Comprobamos que no sea un estado previamente visitado
                if self.isVisitedSituation(True, next_state):
                    break

                self.listVisitedSituations.append((True, next_state))

                print(current_state, next_state)

                # Realizmos el movimiento
                movement = self.getMovement(current_state, next_state)
                self.chess.move(movement[0], movement[1])

                # Comprobamos si las negras están en jaque mate
                if self.isBlackInCheckMate(current_state):
                    return True  # Ganan las blancas

            else:  # Turno de las negras


                # Buscamos la siguiente mejor jugada para las negras
                _, next_state = max_value_black(current_state, depthBlack)

                print(current_state, next_state)

                # Comprobamos que no sea un estado previamente visitado
                if self.isVisitedSituation(False, next_state):
                    break

                self.listVisitedSituations.append((False, next_state))

                # Realizamos el movimient
                movement = self.getMovement(current_state, next_state)
                self.chess.move(movement[0], movement[1])

                # Comprobamos si las blancas están en jaque mate
                if self.isWhiteInCheckMate(current_state):
                    return False  # Ganan las blancas
            
            self.chess.board.print_board()



    def alphaBetaPoda(self, depthWhite, depthBlack):
        """

        """

        def max_value_white(state, depth, alpha, beta):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedWk(state):
                return float('-inf'), state

            if depth == 0:
                return self.heuristica(state, True), state

            v, next_state = float('-inf'), None

            black_rook = self.getPieceState(state, 8)
            white_state = self.getWhiteState(state)
            black_state = self.getBlackState(state)

            for s in self.getListNextStatesW(white_state):
                actual_black_state = black_state.copy()

                # Comprobamos si se han comido la torre negra, en caso afirmativo, sacamos la torre del estado
                if black_rook != None and black_rook[0:2] == s[0][0:2]:
                    actual_black_state.remove(black_rook)

                s += actual_black_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey se encuentra en jaque
                if not self.isWatchedWk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = min_value_white(s, depth - 1, alpha, beta)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value > v:
                        v, next_state = value, value_state

                    # Si el valor del proximo mejor estado es mayor o igual que beta podamos
                    if v >= beta:
                        break

                    # Actualizamos alpha
                    alpha = max(alpha, v)
            
            return v, next_state

        def min_value_white(state, depth, alpha, beta):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedBk(state):
                return float('inf'), state

            if depth == 0:
                return self.heuristica(state, True), state

            v, next_state = float('-inf'), None

            white_rook = self.getPieceState(state, 2)
            white_state = self.getWhiteState(state)
            black_state = self.getBlackState(state)

            for s in self.getListNextStatesB(black_state):
                actual_white_state = white_state.copy()

                # Comprobamos si se han comido la torre blanca, en caso afirmativo, sacamos la torre del estado
                if white_rook != None and white_rook[0:2] == s[0][0:2]:
                    actual_white_state.remove(white_rook)

                s += actual_white_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey negro se encuentra en jaque
                if not self.isWatchedBk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = max_value_white(s, depth - 1, alpha, beta)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value < v:
                        v, next_state = value, value_state

                    # Si el valor del proximo mejor estado es menor o igual que alpha podamos
                    if v <= alpha:
                        break

                    # Actualizamos beta
                    beta = min(beta, v)
            
            return v, next_state

        def max_value_black(state, depth, alpha, beta):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedBk(state):
                return float('-inf'), state

            if depth == 0:
                return self.heuristica(state, False), state

            v, next_state = float('-inf'), None

            white_rook = self.getPieceState(state, 2)
            white_state = self.getWhiteState(state).copy()
            black_state = self.getBlackState(state).copy()

            for s in self.getListNextStatesB(black_state):
                actual_white_state = white_state.copy()

                # Comprobamos si se han comido la torre negra, en caso afirmativo, sacamos la torre del estado
                if white_rook != None and white_rook[0:2] == s[0][0:2]:
                    actual_white_state.remove(white_rook)

                s += actual_white_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey se encuentra en jaque
                if not self.isWatchedBk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = min_value_black(s, depth - 1, alpha, beta)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value > v:
                        v, next_state = value, value_state

                    # Si el valor del proximo mejor estado es mayor o igual que beta podamos
                    if v >= beta:
                        break

                    # Actualizamos alpha
                    alpha = max(alpha, v)
            
            return v, next_state

        def min_value_black(state, depth, alpha, beta):
            '''
            '''
            # Comprobamos si estamos en un estado objetivo
            if self.isWatchedWk(state):
                return float('inf'), state

            if depth == 0:
                return self.heuristica(state, False), state

            v, next_state = float('-inf'), None

            black_rook = self.getPieceState(state, 8)
            white_state = self.getWhiteState(state)
            black_state = self.getBlackState(state)

            for s in self.getListNextStatesw(white_state):
                actual_black_state = black_state.copy()

                # Comprobamos si se han comido la torre negra, en caso afirmativo, sacamos la torre del estado
                if black_rook != None and black_rook[0:2] == s[0][0:2]:
                    actual_black_state.remove(black_rook)

                s += actual_black_state  # Añadimos el estado actual de las piezas blancas
                
                # No tenemos en cuenta los estados donde el rey se encuentra en jaque
                if not self.isWatchedWk(s):

                    # Miramos la siguiente posible jugada
                    value, value_state = max_value_black(s, depth - 1, alpha, beta)

                    # Si es mejor, actualizamos el mejor proximo estado
                    if value < v:
                        v, next_state = value, value_state

                    # Si el valor del proximo mejor estado es mayor o igual que beta podamos
                    if v <= alpha:
                        break

                    # Actualizamos alpha
                    beta = max(beta, v)
            
            return v, next_state

        current_state = self.getCurrentState()

        # Comprobamos que el estado inicial no sea un estado objetivo
        if self.isWhiteInCheckMate(current_state):
            return False  # Ganan las negras
        if self.isBlackInCheckMate(current_state):
            return True  # Ganan las blancas

        # Añadimos el estado a la lista de estados visitados para evitar movimientos en bucle
        self.listVisitedSituations.append(current_state)

        turn = -1

        while not self.isWhiteInCheckMate(current_state) and not self.isBlackInCheckMate(current_state):

            turn += 1
            current_state = self.getCurrentState()

            alpha = float('-inf')
            beta = float('inf')

            if turn % 2 == 0:  # Turno de las blancas

                # Comprobamos si las negras están en jaque mate
                if self.isBlackInCheckMate(current_state):
                    return True  # Ganan las blancas
            
                # Buscamos la siguiente mejor jugada para las blancas
                _, next_state = max_value_white(current_state, depthWhite, alpha, beta)

                # Comprobamos que no sea un estado previamente visitado
                if self.isVisitedSituation(True, next_state):
                    break

                self.listVisitedSituations.append((True, next_state))


                # Realizmos el movimiento
                movement = self.getMovement(current_state, next_state)
                if movement[0] and movement[1]:
                    self.chess.move(movement[0], movement[1])

            else:  # Turno de las negras

                # Comprobamos si las blancas están en jaque mate
                if self.isWhiteInCheckMate(current_state):
                    return False  # Ganan las blancas

                # Buscamos la siguiente mejor jugada para las negras
                _, next_state = max_value_black(current_state, depthBlack, alpha, beta)

                print(current_state, next_state)

                # Comprobamos que no sea un estado previamente visitado
                if self.isVisitedSituation(False, next_state):
                    break

                self.listVisitedSituations.append((False, next_state))

                # Realizamos el movimient
                movement = self.getMovement(current_state, next_state)
                if movement[0] and movement[1]:
                    self.chess.move(movement[0], movement[1])
            
            self.chess.board.print_board()
        
    def expectimax(self, depthWhite, depthBlack):
        
        currentState = self.getCurrentState()    

    def mitjana(self, values):
        sum = 0
        N = len(values)
        for i in range(N):
            sum += values[i]

        return sum / N

    def desviacio(self, values, mitjana):
        sum = 0
        N = len(values)

        for i in range(N):
            sum += pow(values[i] - mitjana, 2)

        return pow(sum / N, 1 / 2)

    def calculateValue(self, values):
        
        if len(values) == 0:
            return 0
        mitjana = self.mitjana(values)
        desviacio = self.desviacio(values, mitjana)
        # If deviation is 0, we cannot standardize values, since they are all equal, thus probability willbe equiprobable
        if desviacio == 0:
            # We return another value
            return values[0]

        esperanca = 0
        sum = 0
        N = len(values)
        for i in range(N):
            #Normalize value, with mean and deviation - zcore
            normalizedValues = (values[i] - mitjana) / desviacio
            # make the values positive with function e^(-x), in which x is the standardized value
            positiveValue = pow(1 / math.e, normalizedValues)
            # Here we calculate the expected value, which in the end will be expected value/sum            
            # Our positiveValue/sum represent the probabilities for each value
            # The larger this value, the more likely
            esperanca += positiveValue * values[i]
            sum += positiveValue

        return esperanca / sum
     

if __name__ == "__main__":
    #   if len(sys.argv) < 2:
    #       sys.exit(usage())

    # intialize board
    TA = np.zeros((8, 8))

    #Configuració inicial del taulell
    TA[7][0] = 2
    TA[7][4] = 6
    TA[0][7] = 8
    TA[0][4] = 12

    # initialise board
    print("stating AI chess... ")
    aichess = Aichess(TA, True)

    algorithms = ['MiniMax', 'Alpha-Beta Prunning', 'ExpectMiniMax']

    print('Que algoritmo quieres probar')
    for i, a in enumerate(algorithms):
        print(f'\t{i + 1}. {a}')

    option = -1

    while option < 1 or option > len(algorithms):
        option = int(input('> '))

    print("printing board")
    aichess.chess.boardSim.print_board()

    if option == 1:
        ganador = aichess.minimaxGame(4,4)
        print(f"Ha ganado {ganador}")

    elif option == 2:
        ganador = aichess.alphaBetaPoda(4,4)
        print(f"Ha ganado {ganador}")

    elif option == 3:
        ganador = aichess.expectimax(4,4)
        print(f"Ha ganado {ganador}")
