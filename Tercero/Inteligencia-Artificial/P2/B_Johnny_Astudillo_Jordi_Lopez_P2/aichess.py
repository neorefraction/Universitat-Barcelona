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

    def allBkMovementsWatched(self, currentState):
        # En aquest mètode mirem si el rei negre està amenaçat per les peces blanques

        self.newBoardSim(currentState)
        # Agafem l'estat del rei negre
        bkState = self.getPieceState(currentState, 12)
        allWatched = False
        # Rei negre es troba a una paret, llavors tots els seus moviments poden estar vigilats
        if bkState[0] == 0 or bkState[0] == 7 or bkState[1] == 0 or bkState[1] == 7:
            wrState = self.getPieceState(currentState, 2)
            whiteState = self.getWhiteState(currentState)
            allWatched = True
            # Obtenim els estats futur de les peces negres
            nextBStates = self.getListNextStatesB(self.getBlackState(currentState))

            for state in nextBStates:
                newWhiteState = whiteState.copy()
                # Comprovem si s'han menjat la torre blanca. En cas afirmatiu, la treiem de l'estat
                if wrState != None and wrState[0:2] == state[0][0:2]:
                    newWhiteState.remove(wrState)
                state = state + newWhiteState
                # Movem les peces negres al nou state
                self.newBoardSim(state)

                # Comprovem si en aquesta posició el rei negre no està amenaçat, que implica que no tots els seus moviments estan vigilats
                if not self.isWatchedBk(state):
                    allWatched = False
                    break
        self.newBoardSim(currentState)
        return allWatched

    def isBlackInCheckMate(self, currentState):
        if self.isWatchedBk(currentState) and self.allBkMovementsWatched(currentState):
            return True

        return False

    def isWatchedWk(self, currentState):
        self.newBoardSim(currentState)

        wkPosition = self.getPieceState(currentState, 6)[0:2]
        bkState = self.getPieceState(currentState, 12)
        brState = self.getPieceState(currentState, 8)

        # Si les blanques maten el rei negre, no és una configuració correcta
        if bkState == None:
            return False
        # Mirem les possibles posicions del rei negre i mirem si en alguna pot "matar" al rei blanc
        for bkPosition in self.getNextPositions(bkState):
            if wkPosition == bkPosition:
                # Tindríem un checkMate
                return True
        if brState != None:
            # Mirem les possibles posicions de la torre negra i mirem si en alguna pot "matar" al rei blanc
            for brPosition in self.getNextPositions(brState):
                if wkPosition == brPosition:
                    return True

        return False

    def allWkMovementsWatched(self, currentState):
        self.newBoardSim(currentState)
        # En aquest mètode mirem si el rei blanc està amenaçat per les peces negres
        # Agafem l'estat del rei blanc
        wkState = self.getPieceState(currentState, 6)
        allWatched = False
        # Rei blanc es troba a una paret, llavors es pot donar un checkMate
        if wkState[0] == 0 or wkState[0] == 7 or wkState[1] == 0 or wkState[1] == 7:
            # Obtenim l'estat de les nostres peces negres
            brState = self.getPieceState(currentState, 8)
            blackState = self.getBlackState(currentState)
            allWatched = True
            # Obtenim els estats futur de les peces blanques
            nextWStates = self.getListNextStatesW(self.getWhiteState(currentState))
            for state in nextWStates:
                newBlackState = blackState.copy()
                # Comprovem si s'han menjat la torre negra. En cas afirmatiu, treiem l'estat de la torre negra
                if brState != None and brState[0:2] == state[0][0:2]:
                    newBlackState.remove(brState)
                state = state + newBlackState
                # Movem les peces blanques al nou state
                self.newBoardSim(state)
                # Comprovem si en aquesta posició el rei blanc no està amenaçat, que implica que no tots els seus moviments estan vigilats
                if not self.isWatchedWk(state):
                    allWatched = False
                    break
        self.newBoardSim(currentState)
        return allWatched

    def isWhiteInCheckMate(self, currentState):
        if self.isWatchedWk(currentState) and self.allWkMovementsWatched(currentState):
            return True
        return False

    def newBoardSim(self, listStates):
        # Creem una nova boardSim
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
        # Donat un estat, mirem els següents possibles estats
        # A partir d'aquests retornem una llista amb les posicions, és a dir, [fila,columna]
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
        #Donat un estat i un estat successor, retornem la posició de la peça moguda en tots dos estats,
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
        #En aquest mètode, es calcula l'heurística tant per les blanques com per les negres.
        #El value que calculem és per les blanques però al final de tot, segons el paràmetre color que tinguem, multipliquem per -1 el resultat.
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

        # Mirem si han matat la torre negra
        if brState == None:
            value += 50
            fila = abs(filaBk - filaWk)
            columna = abs(columnaWk - columnaBk)
            distReis = min(fila, columna) + abs(fila - columna)
            if distReis >= 3 and wrState != None:
                filaR = abs(filaBk - filaWr)
                columnaR = abs(columnaWr - columnaBk)
                value += (min(filaR, columnaR) + abs(filaR - columnaR))/10
            # Si som les blanques, com més aprop tinguem el nostre rei de l'altre, millor.
            # Li restem 7 a la distància que hi ha entre els dos reis, ja que en un taulell d'escacs poden estar a una distància màxima de 7 moviments.
            value += (7 - distReis)
            #Si el rei negre està en una paret, prioritzem que estigui prop d'una cantonada, per així arraconar-lo.
            if bkState[0] == 0 or bkState[0] == 7 or bkState[1] == 0 or bkState[1] == 7:
                value += (abs(filaBk - 3.5) + abs(columnaBk - 3.5)) * 10
            #Si no, només prioritzem que s'apropi a una paret, per així arribar al check mate.
            else:
                value += (max(abs(filaBk - 3.5), abs(columnaBk - 3.5))) * 10

        # Han matat la torre blanca. A dins del mètode es considerem les mateixes condicions que en l'apartat anterior però amb els valors invertits.
        if wrState == None:
            value += -50
            fila = abs(filaBk - filaWk)
            columna = abs(columnaWk - columnaBk)
            distReis = min(fila, columna) + abs(fila - columna)

            if distReis >= 3 and brState != None:
                filaR = abs(filaWk - filaBr)
                columnaR = abs(columnaBr - columnaWk)
                value -= (min(filaR, columnaR) + abs(filaR - columnaR)) / 10
            # Si som les blanques, com més aprop tinguem el nostre rei de l'altre, millor.
            # Li restem 7 a la distància que hi ha entre els dos reis, ja que en un taulell d'escacs poden estar a una distància màxima de 7 moviments.
            value += (-7 + distReis)

            if wkState[0] == 0 or wkState[0] == 7 or wkState[1] == 0 or wkState[1] == 7:
                value -= (abs(filaWk - 3.5) + abs(columnaWk - 3.5)) * 10
            else:
                value -= (max(abs(filaWk - 3.5), abs(columnaWk - 3.5))) * 10

        # S'està fent un check a les negres
        if self.isWatchedBk(currentState):
            value += 20

        # S'està fent un check a les blanques
        if self.isWatchedWk(currentState):
            value += -20

        # Si són les negres, els valors negatius, són positius
        if not color:
            value = (-1) * value

        return value

    def minimaxGame(self, depthWhite,depthBlack):
        currentState = self.getCurrentState()
        
        #Is it an end state?
        if self.isWhiteInCheckMate(currentState):
            return False
        if self.isWatchedBk(currentState):
            return True
        
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()
            
            #With the module, we know if we move whites or blacks
            if i % 2 != 0:
                if not self.minimaxWhite(currentState, depthWhite):
                    break
                if self.isBlackInCheckMate(currentState):
                    colorWin = True
                    break

            else:
                if not self.minimaxBlack(currentState, depthBlack):
                    break
                if self.isWhiteInCheckMate(currentState):
                    colorWin = False
                    break

            self.chess.board.print_board()

        self.chess.board.print_board()
        return colorWin

    def minimaxWhite(self, state, depthMax):
        
        nextState = self.maxValueWhite(state, 0, depthMax)
        copyState = self.copyState(nextState)
        
        if self.isVisitedSituation(True, copyState):
            return False
        
        self.listVisitedSituations.append((True, copyState))

        movement = self.getMovement(state, nextState)

        self.chess.move(movement[0], movement[1])
        return True

    def maxValueWhite(self, currentState, depth, depthMax):
        #If the king is in check, is checkmate, else is tie
        if self.allWkMovementsWatched(currentState):

            if self.isWatchedWk(currentState):
                return -1000

            return 0

        if depth == depthMax:
            return self.heuristica(currentState, True)

        maxValue = -10000
        maxState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        brState = self.getPieceState(currentState, 8)
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            
            #Black Rook taken?
            if brState != None and brState[0:2] == state[0][0:2]:
                newBlackState.remove(brState)

            state = state + newBlackState

            if not self.isWatchedWk(state):
                valueSate = self.minValueWhite(state, depth + 1, depthMax)
       
                if valueSate > maxValue:
                    maxValue = valueSate
                    maxState = state

        if depth == 0:
            return maxState
        return maxValue

    def minValueWhite(self, currentState, depth, depthMax):
        #If the king is in check, is checkmate, else is tie
        if self.allBkMovementsWatched(currentState):
            
            if self.isWatchedBk(currentState):
                return 10000 / depth
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, True)
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        wrState = self.getPieceState(currentState, 2)

        minValue = 10000
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()

            if wrState != None and wrState[0:2] == state[0][0:2]:
                newWhiteState.remove(wrState)
            state = state + newWhiteState

            if not self.isWatchedBk(state):
                minValue = min(minValue, self.maxValueWhite(state, depth + 1, depthMax))

        return minValue

    def minimaxBlack(self, state, depthMax):
        nextState = self.maxValueBlack(state, 0, depthMax)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))

        movement = self.getMovement(state, nextState)

        self.chess.move(movement[0], movement[1])
        return True

    def maxValueBlack(self, currentState, depth, depthMax):

        if self.allBkMovementsWatched(currentState):
            if self.isWatchedBk(currentState):
                return -1000
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, False)

        maxValue = -10000
        maxState = None
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        wrState = self.getPieceState(currentState, 2)
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()

            if wrState != None and wrState[0:2] == state[0][0:2]:
                newWhiteState.remove(wrState)
            state = state + newWhiteState
            
            if not self.isWatchedBk(state):
                valueSate = self.minValueBlack(state, depth + 1, depthMax)
                if valueSate > maxValue:
                    maxValue = valueSate
                    maxState = state

        if depth == 0:
            return maxState
        return maxValue

    def minValueBlack(self, currentState, depth, depthMax):

        if self.allWkMovementsWatched(currentState):
            if self.isWatchedWk(currentState):
                return 10000 / depth
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, False)
        
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        brState = self.getPieceState(currentState, 8)

        minValue = 10000
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()

            if brState != None and brState[0:2] == state[0][0:2]:
                newBlackState.remove(brState)
            state = state + newBlackState
            if not self.isWatchedWk(state):
                minValue = min(minValue, self.maxValueBlack(state, depth + 1, depthMax))

        return minValue

    def alphaBetaPoda(self, depthWhite,depthBlack):

        currentState = self.getCurrentState()

        if self.isWhiteInCheckMate(currentState):
            return False
        
        if self.isWatchedBk(currentState):
            return True
        
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        colorWin = None
        
        for i in range(50):
            currentState = self.getCurrentState()
            if i % 2 != 0:
                if not self.podaWhite(currentState, depthWhite):
                    break
                if self.isBlackInCheckMate(currentState):
                    colorWin = True
                    break
            else:
                if not self.podaBlack(currentState, depthBlack):
                    break
                if self.isWhiteInCheckMate(currentState):
                    colorWin = False
                    break

            self.chess.board.print_board()

        self.chess.board.print_board()
        return colorWin
    
    def prunningBlacksMinimaxWhites(self, depthWhite,depthBlack):
        '''
        This method makes Whites play with minmax and blacks with prunning
        '''
        currentState = self.getCurrentState()

        if self.isWhiteInCheckMate(currentState):
            return False
        
        if self.isWatchedBk(currentState):
            return True
        
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        colorWin = None
        
        for i in range(50):
            currentState = self.getCurrentState()

            if i % 2 != 0:
                if not self.minimaxWhite(currentState, depthWhite):
                    break
                if self.isBlackInCheckMate(currentState):
                    colorWin = True
                    break

            else:
                if not self.podaBlack(currentState, depthBlack):
                    break
                if self.isWhiteInCheckMate(currentState):
                    colorWin = False
                    break

            self.chess.board.print_board()

        self.chess.board.print_board()
        return colorWin

    def podaWhite(self, state, depthMax):
        alpha = -10000
        beta = 10000
        nextState = self.podaMaxValueWhite(state, 0, depthMax, alpha, beta)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))

        movement = self.getMovement(state, nextState)

        self.chess.move(movement[0], movement[1])
        return True

    def podaMaxValueWhite(self, currentState, depth, depthMax, alpha, beta):

        if self.allWkMovementsWatched(currentState):

            if self.isWatchedWk(currentState):
                return -1000

            return 0

        if depth == depthMax:
            return self.heuristica(currentState, True)

        maxValue = -10000
        maxState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        brState = self.getPieceState(currentState, 8)
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()

            if brState != None and brState[0:2] == state[0][0:2]:
                newBlackState.remove(brState)

            state = state + newBlackState

            if not self.isWatchedWk(state):
                valueSate = self.podaMinValueWhite(state, depth + 1, depthMax, alpha, beta)

                if valueSate > maxValue:
                    maxValue = valueSate
                    maxState = state
                    
                #Prune
                if maxValue >= beta:
                    break
                alpha = max(alpha, maxValue)

        if depth == 0:
            return maxState
        return maxValue

    def podaMinValueWhite(self, currentState, depth, depthMax, alpha, beta):

        if self.allBkMovementsWatched(currentState):
            if self.isWatchedBk(currentState):
                return 10000 / depth
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, True)
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        wrState = self.getPieceState(currentState, 2)

        minValue = 10000
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()

            if wrState != None and wrState[0:2] == state[0][0:2]:
                newWhiteState.remove(wrState)
                
            state = state + newWhiteState

            if not self.isWatchedBk(state):
                minValue = min(minValue, self.podaMaxValueWhite(state, depth + 1, depthMax, alpha, beta))
                #Prun
                if minValue <= alpha:
                    break

                beta = min(beta, minValue)

        return minValue

    def podaBlack(self, state, depthMax):
        alpha = -10000
        beta = 10000
        nextState = self.podaMaxValueBlack(state, 0, depthMax, alpha, beta).copy()
        copyState = self.copyState(nextState)
        
        if self.isVisitedSituation(False, copyState):
            return False
        
        self.listVisitedSituations.append((False, copyState))

        movement = self.getMovement(state, nextState)
        self.chess.move(movement[0], movement[1])
        return True

    def podaMaxValueBlack(self, currentState, depth, depthMax, alpha, beta):

        if self.allBkMovementsWatched(currentState):
            if self.isWatchedBk(currentState):
                return -1000
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, False)

        maxValue = -10000
        maxState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        wrState = self.getPieceState(currentState, 2)
        
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()

            if wrState != None and wrState[0:2] == state[0][0:2]:
                newWhiteState.remove(wrState)
                
            state = state + newWhiteState
            
            if not self.isWatchedBk(state):
                valueSate = self.podaMinValueBlack(state, depth + 1, depthMax, alpha, beta)

                if valueSate > maxValue:
                    maxValue = valueSate
                    maxState = state

                if maxValue >= beta:
                    break
                alpha = max(alpha, maxValue)

        if depth == 0:
            return maxState
        return maxValue

    def podaMinValueBlack(self, currentState, depth, depthMax, alpha, beta):

        if self.allWkMovementsWatched(currentState):
            
            if self.isWatchedWk(currentState):
                return 10000 / depth
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, False)
        
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        brState = self.getPieceState(currentState, 8)

        minValue = 10000
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()

            if brState != None and brState[0:2] == state[0][0:2]:
                newBlackState.remove(brState)
                
            state = state + newBlackState
            
            if not self.isWatchedWk(state):
                minValue = min(minValue, self.podaMaxValueBlack(state, depth + 1, depthMax, alpha, beta))

                if minValue <= alpha:
                    break

                beta = min(beta, minValue)

        return minValue


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

        if desviacio == 0:
            return values[0]

        esperanca = 0
        sum = 0
        N = len(values)
        for i in range(N):
            normalizedValues = (values[i] - mitjana) / desviacio
            positiveValue = pow(1 / math.e, normalizedValues)
            esperanca += positiveValue * values[i]
            sum += positiveValue

        return esperanca / sum

    def expectimax(self, depthWhite, depthBlack):
        currentState = self.getCurrentState()

        if self.isWhiteInCheckMate(currentState):
            return False
        if self.isWatchedBk(currentState):
            return True
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        colorWin = None
        for i in range(50):
            currentState = self.getCurrentState()

            if i % 2 != 0:
                if not self.expectimaxWhite(currentState, depthWhite):
                    break
                if self.isBlackInCheckMate(currentState):
                    colorWin = True
                    break

            else:
                if not self.expectimaxBlack(currentState, depthBlack):
                    break
                if self.isWhiteInCheckMate(currentState):
                    colorWin = False
                    break

            self.chess.board.print_board()

        self.chess.board.print_board()
        return colorWin

    def expectimaxWhite(self, state, depthMax):
        nextState = self.expMaxValueWhite(state, 0, depthMax)
        copyState = self.copyState(nextState)
        if self.isVisitedSituation(True, copyState):
            return False
        self.listVisitedSituations.append((True, copyState))

        movement = self.getMovement(state, nextState)

        self.chess.move(movement[0], movement[1])
        return True

    def expMaxValueWhite(self, currentState, depth, depthMax):

        if self.allWkMovementsWatched(currentState):
            if self.isWatchedWk(currentState):
                return -1000
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, True)

        maxValue = -10000
        maxState = None
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        brState = self.getPieceState(currentState, 8)
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()

            if brState != None and brState[0:2] == state[0][0:2]:
                newBlackState.remove(brState)
            state = state + newBlackState
            
            if not self.isWatchedWk(state):
                valueSate = self.expValueWhite(state, depth + 1, depthMax)

                if valueSate > maxValue:
                    maxValue = valueSate
                    maxState = state

        if depth == 0:
            return maxState
        
        return maxValue

    def expValueWhite(self, currentState, depth, depthMax):

        if self.allBkMovementsWatched(currentState):
            if self.isWatchedBk(currentState):
                return 10000 / depth
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, True)
        
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        wrState = self.getPieceState(currentState, 2)

        values = []
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()

            if wrState != None and wrState[0:2] == state[0][0:2]:
                newWhiteState.remove(wrState)
            state = state + newWhiteState
            if not self.isWatchedBk(state):

                value = self.expMaxValueWhite(state, depth + 1, depthMax)
                values.append(value)

        return self.calculateValue(values)

    def expectimaxBlack(self, state, depthMax):
        nextState = self.expMaxValueBlack(state, 0, depthMax)
        copyState = self.copyState(nextState)
        
        if self.isVisitedSituation(True, copyState):
            return False
        
        self.listVisitedSituations.append((True, copyState))

        movement = self.getMovement(state, nextState)

        self.chess.move(movement[0], movement[1])
        return True

    def expMaxValueBlack(self, currentState, depth, depthMax):

        if self.allBkMovementsWatched(currentState):
            if self.isWatchedBk(currentState):
                return -1000
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, False)

        maxValue = -10000
        maxState = None
        blackState = self.getBlackState(currentState)
        whiteState = self.getWhiteState(currentState)
        wrState = self.getPieceState(currentState, 2)
        
        for state in self.getListNextStatesB(blackState):
            newWhiteState = whiteState.copy()

            if wrState != None and wrState[0:2] == state[0][0:2]:
                newWhiteState.remove(wrState)
            state = state + newWhiteState
            if not self.isWatchedBk(state):
                valueSate = self.expValueBlack(state, depth + 1, depthMax)
                if valueSate > maxValue:
                    maxValue = valueSate
                    maxState = state

        if depth == 0:
            return maxState
        return maxValue

    def expValueBlack(self, currentState, depth, depthMax):

        if self.allWkMovementsWatched(currentState):
            if self.isWatchedWk(currentState):
                return 10000 / depth
            
            return 0

        if depth == depthMax:
            return self.heuristica(currentState, False)
        
        whiteState = self.getWhiteState(currentState)
        blackState = self.getBlackState(currentState)
        brState = self.getPieceState(currentState, 8)

        values = []
        for state in self.getListNextStatesW(whiteState):
            newBlackState = blackState.copy()
            if brState != None and brState[0:2] == state[0][0:2]:
                newBlackState.remove(brState)
                
            state = state + newBlackState
            if not self.isWatchedWk(state):
                values.append(self.expMaxValueBlack(state, depth + 1, depthMax))

        return self.calculateValue(values)

    def expectWhitePodaBlack(self, depthWhite, depthBlack):
        currentState = self.getCurrentState()

        if self.isWhiteInCheckMate(currentState):
            return False
        
        if self.isWatchedBk(currentState):
            return True
        
        copyState = self.copyState(currentState)
        self.listVisitedSituations.append((False, copyState))
        colorWin = None
        
        for i in range(50):
            currentState = self.getCurrentState()

            if i % 2 != 0:
                if not self.expectimaxWhite(currentState, depthWhite):
                    break
                if self.isBlackInCheckMate(currentState):
                    colorWin = True
                    break

            else:
                if not self.podaBlack(currentState, depthBlack):
                    break
                if self.isWhiteInCheckMate(currentState):
                    colorWin = False
                    break

            self.chess.board.print_board()

        self.chess.board.print_board()
        return colorWin

def translate(s):
    """
    Translates traditional board coordinates of chess into list indices
    """

    try:
        row = int(s[0])
        col = s[1]
        if row < 1 or row > 8:
            print(s[0] + "is not in the range from 1 - 8")
            return None
        if col < 'a' or col > 'h':
            print(s[1] + "is not in the range from a - h")
            return None
        dict = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
        return (8 - row, dict[col])
    except:
        print(s + "is not in the format '[number][letter]'")
        return None


if __name__ == "__main__":
    #   if len(sys.argv) < 2:
    #       sys.exit(usage())

    # intiialize board
    TA = np.zeros((8, 8))

    #Configuració inicial del taulell
    TA[7][0] = 2
    TA[7][4] = 6
    TA[0][7] = 8
    TA[0][4] = 12

    # initialise board
    print("stating AI chess... ")
    aichess = Aichess(TA, True)

    print("printing board")
    aichess.chess.boardSim.print_board()

    
    '''
    PROBLEMA 1
    Whites - Minmax depth 4
    Blacks - Minmax depth 4
    
    aichess.minimaxGame(4,4)
    '''
    
    
    
    '''
    PROBLEMA 2
    Whites - Minmax depth 3 - 7
    Blacks - Minmax depth 3 - 7

    for i in range(3,8):
            resultats = {'-':0,'W':0,'B':0}
            for j in range(3,8):
                aichess = Aichess(TA, True)
                aichess.chess.boardSim.print_board()
                resultatPoda = aichess.prunningBlacksMinimaxWhites(i,j)
                print(resultatPoda)
                if resultatPoda == None:
                    resultats['-'] += 1
                elif resultatPoda:
                    resultats['W'] += 1
                else:
                    resultats['B'] += 1
                print("Resultats: ",resultats)
    '''
    
    
    
    '''
    PROBLEMA 3
    Whites - Minmax depth 4
    Blacks - Prunning depth 4
    if numExercici == 3:
        aichess.alphaBetaPoda(4,4)
    '''
    
    
    
    '''
    PROBLEMA 4
    Whites - Prunning depth 1 - 4
    Blacks - Prunning depth 1 - 4
    
    resultats = {'-':0,'W':0,'B':0}
    for i in range(1,4):
        for j in range(1,4):
            aichess = Aichess(TA, True)
            aichess.chess.boardSim.print_board()
            resultatPoda = aichess.alphaBetaPoda(i,j)
            print(resultatPoda)
            if resultatPoda == None:
                resultats['-'] += 1
            elif resultatPoda:
                resultats['W'] += 1
            else:
                resultats['B'] += 1
            print("Resultats: ",resultats)
    '''
    
    
        
    '''
    PROBLEMA 5
    Whites - Expectimax depth 4
    Blacks - Prunning depth 4

    aichess.expectWhitePodaBlack(4,4)

    '''


