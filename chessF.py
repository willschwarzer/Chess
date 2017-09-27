import pygame
import sys
import copy
import random

class Piece(object):
    def __init__(self,side,row,col,board,image,surface):
        '''Given a side ("black" or "white"), a position (row,col), a board, and a surface, creates a piece'''
        global boardScale
        self.side = side
        self.width = int(50*boardScale)
        self.height = int(50*boardScale)
        self.row = row
        self.col = col
        self.board = board
        self.surface = surface
        self.image = pygame.transform.scale(image,(int(50*boardScale),int(50*boardScale)))
        self.hasMoved = False
        
    def getBoard(self):
        '''Given a piece, returns the piece's board'''
        return self.board
        
    def getSurface(self):
        '''Given a piece, returns the piece's pygame surface'''
        return self.surface
        
    def getRow(self):
        '''Given a piece, returns the piece's row on the board'''
        return self.row
        
    def getCol(self):
        '''Given a piece, returns the piece's column on the board'''
        return self.col
        
    def getPosition(self):
        '''Given a piece, return's the pieces position (coordinates) on the board'''
        return [self.getRow(), self.getCol()]
        
    def getSide(self):
        '''Given a piece, returns a string "black" or "white" depending on the piece's side'''
        return self.side
        
    def setPosition(self, newPosition):
        '''moves a piece to a position newPosition'''
        self.row = newPosition[0]
        self.col = newPosition[1]
        
    def hasFriend(self, row, col, board):
        '''Given a piece, coordinate, and board, returns a boolean of wheter the piece in the coordinate on teh baord is of the same side of the piece that the method is called on'''
        mySide = self.getSide()
        if board.boardList[row][col] is None:
            return False
        otherSide = board.boardList[row][col].getSide()
        return (mySide == otherSide)
        
    def hasEnemy(self, row, col, board):
        '''Given a piece, coordinate, and board, returns a boolean of wheter the piece in the coordinate on teh baord is of the opposite side of the piece that the method is called on'''
        mySide = self.getSide()
        if board.boardList[row][col] is None:
            return False
        #if self.__str__() == 'pawn':
        #    for enpassantSquare in board.enPassantList:
        #        if enpassantSquare.getPosition() == [row, col]:
        #            return True
        otherSide = board.boardList[row][col].getSide()
        return (mySide != otherSide)
        
    def hasEnemyExceptKing(self, row, col, board):
        '''Given a piece, coordinate, and board, returns a boolean of wheter the piece in the coordinate on teh baord is of the opposite side of the piece that the method is called on, but also returns false if the piece there is a king'''
        mySide = self.getSide()
        if board.boardList[row][col] is None or board.boardList[row][col].__str__() == 'king':
            return False
        otherSide = board.boardList[row][col].getSide()
        return (mySide != otherSide)
        
    def outOfBounds(self, row, col):
        '''retuns whether coordinate is out of bounds'''
        return (row > 7 or col > 7 or row < 0 or col <0)
        
    def draw(self):
        '''Given a piece, it draws that piece in the pygame image window'''
        rect = pygame.Rect(self.col*100*boardScale + (50 - self.width/2)*boardScale, self.row*100*boardScale  + (50 - self.height/2)*boardScale, self.col*100*boardScale + (50 + self.width/2)*boardScale, self.row*100*boardScale + (50 + self.height/2)*boardScale)
        self.surface.blit(self.image, rect)
        
    #def animate(...):
        #TODO: animate piece based on time and how many squares it's moving
        
    def isThreatened(self, row, col, board):
        '''Given a piece, coordinate, and board, returns whether that piece is threatened by any other pieces'''
        for piece in board.pieceList:
            if piece.getSide() != self.getSide():
                for move in piece.squaresThreatened(board):
                    if move == [row, col]:
                        return True
        return False
        
    def testMovesForCheck(self, moves, board):
        '''Given a piece, its moves, and a board, returns a boolean of wheter that piece's moves can cause check'''
        side = self.getSide()
        goodMoves = []
        for move in moves:
            boardCopy = copy.deepcopy(board)
            boardCopy.makeMove(self.getPosition(), move, isAI = True)
            boardCopy.updateBoardList()
            checkValue = boardCopy.getCheck()
            if side == 'white':
                if checkValue != 2:
                    goodMoves.append(move)
            else:
                if checkValue != 1:
                    goodMoves.append(move)
        
        return goodMoves
    def canCastle(self):
        '''by default, most pieces can't castle, so retuns 0 for whether it can castle or not - see King for actual canCastle'''
        return 0

class Pawn(Piece):
    def pieceMoves(self, board, isAI = False):
        '''Given a piece, a board, and a boolean, returns a list of coordinates on that board that that piece can mvoe to'''
        row = self.getRow()
        col = self.getCol()
        side = self.getSide()
        
        if side == "black": #Black => going down
            moveZero = [row+2, col]
            moveA = [row+1, col]
            moveB = [row+1, col+1]
            moveC = [row+1, col-1]   
        elif side  == "white": # White => going up
            moveZero = [row-2,col]
            moveA = [row-1,col]
            moveB = [row-1,col+1]
            moveC = [row-1, col-1]
            
        goodMoves = []
        if not self.hasMoved and board.boardList[moveA[0]][moveA[1]] == None and board.boardList[moveZero[0]][moveZero[1]] == None:
            goodMoves.append(moveZero)
        if not self.outOfBounds(moveB[0], moveB[1]) and not self.hasFriend(moveB[0], moveB[1], board) and self.hasEnemy(moveB[0], moveB[1], board):
            goodMoves.append(moveB)
        if not self.outOfBounds(moveC[0], moveC[1]) and not self.hasFriend(moveC[0], moveC[1], board) and self.hasEnemy(moveC[0], moveC[1], board):
            goodMoves.append(moveC)
        if not self.outOfBounds(moveA[0], moveA[1]) and not self.hasFriend(moveA[0],moveA[1], board) and not self.hasEnemy(moveA[0], moveA[1],board):
            goodMoves.append(moveA)
            
        if not isAI:
            goodMoves = self.testMovesForCheck(goodMoves, board)
        
        return goodMoves
        
        
    def squaresThreatened(self, board, isAI = False):
        '''Given a piece, a board, and a boolean, returns a list of coordinates of squares that the piece can attack'''
        row = self.getRow()
        col = self.getCol()
        side = self.getSide()
        if side == "black": #Black => going down
            moveB = [row+1, col+1]
            moveC = [row+1, col-1]
           
        elif side  == "white": # White => going up
            moveB = [row-1,col+1]
            moveC = [row-1, col-1]
            
            
        return [moveB, moveC]
        
    def getMaterial(self):
        '''Given a piece, returns an int of that piece's material worth'''
        return 1
        
    def getAdjustedMaterial(self):
        '''Returns the piece's adjusted material, based on additional factors such as position and attack power'''
        valueSoFar = 1
        if self.board.moveCounter >= 20 or self.getCol() == 3 or self.getCol() == 4:
            if self.row == 3 or self.row == 4:
                valueSoFar += 0.5
        return valueSoFar
    
    def __str__(self):
        '''Returns a string of what the piece is'''
        return 'pawn'

class enPassant(Piece):
    #stores what global move number it was made on and after three moves, deletes itself
    '''The en passant piece is an invisible piece that is utilized in makeMove that allows the  en passant maneuver'''
    def __init__(self,side,row,col,board,image,surface):
        super().__init__(side,row,col,board,image,surface)
        
        self.moveCreated = board.moveCounter
    def squaresThreatened(self, board, isAi = False):
        return None
    def getMoveCreated(self):
        return self.moveCreated
    def pieceMoves(self):
        return None
    def __str__(self):
        return "enpassant"
    def getMaterial(self):
        return 0
    
class Knight(Piece):
    def pieceMoves(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        moves = [[row+2, col-1],[row+2, col+1],[row+1,col-2], [row+1,col+2],[row-1,col-2],[row-1,col+2],[row-2,col-1],[row-2, col+1]]
        for move in moves:
            if not self.outOfBounds(move[0],move[1]) and not self.hasFriend(move[0],move[1],board):
                goodMoves.append(move)
        
        if not isAI:
            goodMoves = self.testMovesForCheck(goodMoves, board)
            
        return goodMoves
        
    def squaresThreatened(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        moves = [[row+2, col-1],[row+2, col+1],[row+1,col-2], [row+1,col+2],[row-1,col-2],[row-1,col+2],[row-2,col-1],[row-2, col+1]]
        for move in moves:
            if not self.outOfBounds(move[0],move[1]):
                goodMoves.append(move)
        return goodMoves
        
    def getMaterial(self):
        return 3
        
    def getAdjustedMaterial(self):
        value = 3
        value += 0.05*len(self.squaresThreatened(self.board))
        if self.board.moveCounter <= 20:
            if self.getSide() == 'white':
                if self.getRow() == 7:
                    value -= 0.25
            else:
                if self.getRow() == 0:
                    value -= 0.25
        return value
        
    def __str__(self):
        return 'knight'
    
    
    
class Bishop(Piece):
    def pieceMoves(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        i = 1
        #going down right
        while not self.outOfBounds(row+i, col+i) and not self.hasFriend(row+i, col+i, board) and not self.hasEnemy(row+i, col+i,board):
            goodMoves.append([row+i, col+i])
            i += 1
        if not self.outOfBounds(row+i, col+i) and self.hasEnemy(row+i, col+i, board):
            goodMoves.append([row+i,col+i])
        #going down left
        i = 1
        while not self.outOfBounds(row+i, col-i) and not self.hasFriend(row+i, col-i, board) and not self.hasEnemy(row+i, col-i,board):
            goodMoves.append([row+i, col-i])
            i += 1
        if not self.outOfBounds(row+i, col-i) and self.hasEnemy(row+i, col-i, board):
            goodMoves.append([row+i,col-i])
            
        #going up right
        i = 1
        while not self.outOfBounds(row-i, col+i) and not self.hasFriend(row-i, col+i, board) and not self.hasEnemy(row-i, col+i,board):
            goodMoves.append([row-i, col+i])
            i += 1
        if not self.outOfBounds(row-i, col+i) and self.hasEnemy(row-i, col+i, board):
            goodMoves.append([row-i,col+i])
        #going up left
        i = 1
        while not self.outOfBounds(row-i, col-i) and not self.hasFriend(row-i, col-i, board) and not self.hasEnemy(row-i, col-i,board):
            goodMoves.append([row-i, col-i])
            i += 1
        if not self.outOfBounds(row-i, col-i) and self.hasEnemy(row-i, col-i, board):
            goodMoves.append([row-i,col-i])
            
        if not isAI:
            goodMoves = self.testMovesForCheck(goodMoves, board)    
            
        return goodMoves
        
    def squaresThreatened(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        i = 1
        #going down right
        while not self.outOfBounds(row+i, col+i) and not self.hasFriend(row+i, col+i, board) and not self.hasEnemyExceptKing(row+i, col+i,board):
            goodMoves.append([row+i, col+i])
            i += 1
        if not self.outOfBounds(row+i, col+i):
            goodMoves.append([row+i,col+i])
        #going down left
        i = 1
        while not self.outOfBounds(row+i, col-i) and not self.hasFriend(row+i, col-i, board) and not self.hasEnemyExceptKing(row+i, col-i,board):
            goodMoves.append([row+i, col-i])
            i += 1
        if not self.outOfBounds(row+i, col-i):
            goodMoves.append([row+i,col-i])
            
        #going up right
        i = 1
        while not self.outOfBounds(row-i, col+i) and not self.hasFriend(row-i, col+i, board) and not self.hasEnemyExceptKing(row-i, col+i,board):
            goodMoves.append([row-i, col+i])
            i += 1
        if not self.outOfBounds(row-i, col+i):
            goodMoves.append([row-i,col+i])
        #going up left
        i = 1
        while not self.outOfBounds(row-i, col-i) and not self.hasFriend(row-i, col-i, board) and not self.hasEnemyExceptKing(row-i, col-i,board):
            goodMoves.append([row-i, col-i])
            i += 1
        if not self.outOfBounds(row-i, col-i):
            goodMoves.append([row-i,col-i])
        return goodMoves
        
    def getMaterial(self):
        return 3
        
    def getAdjustedMaterial(self):
        value = 3
        value += 0.05*len(self.squaresThreatened(self.board))
        if self.board.moveCounter <= 20:
            if self.getSide() == 'white':
                if self.getRow() == 7:
                    value -= 0.25
            else:
                if self.getRow() == 0:
                    value -= 0.25
        return value
        
    def __str__(self):
        return 'bishop'
        
    
class Rook(Piece):
    def pieceMoves(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        r = 1
        c = 1
        #going right
        while not self.outOfBounds(row, col+c) and not self.hasFriend(row, col+c, board) and not self.hasEnemy(row, col+c,board):
            goodMoves.append([row, col+c])
            c += 1
        if not self.outOfBounds(row, col+c) and self.hasEnemy(row, col+c, board):
            goodMoves.append([row,col+c])
        #going left
        c = 1
        while not self.outOfBounds(row, col-c) and not self.hasFriend(row, col-c, board) and not self.hasEnemy(row, col-c,board):
            goodMoves.append([row, col-c])
            c += 1
        if not self.outOfBounds(row, col-c) and self.hasEnemy(row, col-c, board):
            goodMoves.append([row,col-c])
            
        #going down
        while not self.outOfBounds(row+r, col) and not self.hasFriend(row+r, col, board) and not self.hasEnemy(row+r, col,board):
            goodMoves.append([row+r, col])
            r += 1
        if not self.outOfBounds(row+r, col) and self.hasEnemy(row+r, col, board):
            goodMoves.append([row+r,col])
        #going up
        r = 1
        while not self.outOfBounds(row-r, col) and not self.hasFriend(row-r, col, board) and not self.hasEnemy(row-r, col,board):
            goodMoves.append([row-r, col])
            r += 1
        if not self.outOfBounds(row-r, col) and self.hasEnemy(row-r, col, board):
            goodMoves.append([row-r,col])
            
        if not isAI:
            goodMoves = self.testMovesForCheck(goodMoves, board)    
            
        return goodMoves
        
    def squaresThreatened(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        r = 1
        c = 1
        #going right
        while not self.outOfBounds(row, col+c) and not self.hasFriend(row, col+c, board) and not self.hasEnemyExceptKing(row, col+c,board):
            goodMoves.append([row, col+c])
            c += 1
        if not self.outOfBounds(row, col+c):
            goodMoves.append([row,col+c])
        #going left
        c = 1
        while not self.outOfBounds(row, col-c) and not self.hasFriend(row, col-c, board) and not self.hasEnemyExceptKing(row, col-c,board):
            goodMoves.append([row, col-c])
            c += 1
        if not self.outOfBounds(row, col-c):
            goodMoves.append([row,col-c])
            
        #going down
        while not self.outOfBounds(row+r, col) and not self.hasFriend(row+r, col, board) and not self.hasEnemyExceptKing(row+r, col,board):
            goodMoves.append([row+r, col])
            r += 1
        if not self.outOfBounds(row+r, col):
            goodMoves.append([row+r,col])
        #going up
        r = 1
        while not self.outOfBounds(row-r, col) and not self.hasFriend(row-r, col, board) and not self.hasEnemyExceptKing(row-r, col,board):
            goodMoves.append([row-r, col])
            r += 1
        if not self.outOfBounds(row-r, col):
            goodMoves.append([row-r,col])
        return goodMoves
        
    def getMaterial(self):
        return 5
        
    def getAdjustedMaterial(self):
        return 5 + 0.05*len(self.squaresThreatened(self.board))
        
    def __str__(self): return 'rook'
        
class Queen(Piece):
    def pieceMoves(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        r = 1
        c = 1
        #going right
        while not self.outOfBounds(row, col+c) and not self.hasFriend(row, col+c, board) and not self.hasEnemy(row, col+c,board):
            goodMoves.append([row, col+c])
            c += 1
        if not self.outOfBounds(row, col+c) and self.hasEnemy(row, col+c, board):
            goodMoves.append([row,col+c])
        #goind left
        c = 1
        while not self.outOfBounds(row, col-c) and not self.hasFriend(row, col-c, board) and not self.hasEnemy(row, col-c,board):
            goodMoves.append([row, col-c])
            c += 1
        if not self.outOfBounds(row, col-c) and self.hasEnemy(row, col-c, board):
            goodMoves.append([row,col-c])
            
        #going down
        while not self.outOfBounds(row+r, col) and not self.hasFriend(row+r, col, board) and not self.hasEnemy(row+r, col,board):
            goodMoves.append([row+r, col])
            r += 1
        if not self.outOfBounds(row+r, col) and self.hasEnemy(row+r, col, board):
            goodMoves.append([row+r,col])
        #going up
        r = 1
        while not self.outOfBounds(row-r, col) and not self.hasFriend(row-r, col, board) and not self.hasEnemy(row-r, col,board):
            goodMoves.append([row-r, col])
            r += 1
        if not self.outOfBounds(row-r, col) and self.hasEnemy(row-r, col, board):
            goodMoves.append([row-r,col])
        
        #going down right
        i = 1
        while not self.outOfBounds(row+i, col+i) and not self.hasFriend(row+i, col+i, board) and not self.hasEnemy(row+i, col+i,board):
            goodMoves.append([row+i, col+i])
            i += 1
        if not self.outOfBounds(row+i, col+i) and self.hasEnemy(row+i, col+i, board):
            goodMoves.append([row+i,col+i])
        #going down left
        i = 1
        while not self.outOfBounds(row+i, col-i) and not self.hasFriend(row+i, col-i, board) and not self.hasEnemy(row+i, col-i,board):
            goodMoves.append([row+i, col-i])
            i += 1
        if not self.outOfBounds(row+i, col-i) and self.hasEnemy(row+i, col-i, board):
            goodMoves.append([row+i,col-i])
        #going up right
        i = 1
        while not self.outOfBounds(row-i, col+i) and not self.hasFriend(row-i, col+i, board) and not self.hasEnemy(row-i, col+i,board):
            goodMoves.append([row-i, col+i])
            i += 1
        if not self.outOfBounds(row-i, col+i) and self.hasEnemy(row-i, col+i, board):
            goodMoves.append([row-i,col+i])
        #going up left
        i = 1
        while not self.outOfBounds(row-i, col-i) and not self.hasFriend(row-i, col-i, board) and not self.hasEnemy(row-i, col-i,board):
            goodMoves.append([row-i, col-i])
            i += 1
        if not self.outOfBounds(row-i, col-i) and self.hasEnemy(row-i, col-i, board):
            goodMoves.append([row-i,col-i])
            
        if not isAI:
            goodMoves = self.testMovesForCheck(goodMoves, board)    
            
        return goodMoves
        
    def squaresThreatened(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        r = 1
        c = 1
        #going right
        while not self.outOfBounds(row, col+c) and not self.hasFriend(row, col+c, board) and not self.hasEnemyExceptKing(row, col+c,board):
            goodMoves.append([row, col+c])
            c += 1
        if not self.outOfBounds(row, col+c):
            goodMoves.append([row,col+c])
        #going left
        c = 1
        while not self.outOfBounds(row, col-c) and not self.hasFriend(row, col-c, board) and not self.hasEnemyExceptKing(row, col-c,board):
            goodMoves.append([row, col-c])
            c += 1
        if not self.outOfBounds(row, col-c):
            goodMoves.append([row,col-c])
            
        #going down
        while not self.outOfBounds(row+r, col) and not self.hasFriend(row+r, col, board) and not self.hasEnemyExceptKing(row+r, col,board):
            goodMoves.append([row+r, col])
            r += 1
        if not self.outOfBounds(row+r, col):
            goodMoves.append([row+r,col])
        #going up
        r = 1
        while not self.outOfBounds(row-r, col) and not self.hasFriend(row-r, col, board) and not self.hasEnemyExceptKing(row-r, col,board):
            goodMoves.append([row-r, col])
            r += 1
        if not self.outOfBounds(row-r, col):
            goodMoves.append([row-r,col])
            
        i = 1
        #going down right
        while not self.outOfBounds(row+i, col+i) and not self.hasFriend(row+i, col+i, board) and not self.hasEnemyExceptKing(row+i, col+i,board):
            goodMoves.append([row+i, col+i])
            i += 1
        if not self.outOfBounds(row+i, col+i):
            goodMoves.append([row+i,col+i])
        #going down left
        i = 1
        while not self.outOfBounds(row+i, col-i) and not self.hasFriend(row+i, col-i, board) and not self.hasEnemyExceptKing(row+i, col-i,board):
            goodMoves.append([row+i, col-i])
            i += 1
        if not self.outOfBounds(row+i, col-i):
            goodMoves.append([row+i,col-i])
            
        #going up right
        i = 1
        while not self.outOfBounds(row-i, col+i) and not self.hasFriend(row-i, col+i, board) and not self.hasEnemyExceptKing(row-i, col+i,board):
            goodMoves.append([row-i, col+i])
            i += 1
        if not self.outOfBounds(row-i, col+i):
            goodMoves.append([row-i,col+i])
        #going up left
        i = 1
        while not self.outOfBounds(row-i, col-i) and not self.hasFriend(row-i, col-i, board) and not self.hasEnemyExceptKing(row-i, col-i,board):
            goodMoves.append([row-i, col-i])
            i += 1
        if not self.outOfBounds(row-i, col-i):
            goodMoves.append([row-i,col-i])
            
        return goodMoves
        
    def getMaterial(self):
        return 9
        
    def getAdjustedMaterial(self):
        value = 9
        value += 0.025*len(self.squaresThreatened(self.board))
        if self.board.moveCounter <= 10:
            if self.getSide() == 'white':
                if self.getRow() == 7:
                    value += 0.25
            else:
                if self.getRow() == 0:
                    value += 0.25
        return value
        
        
    def __str__(self):
        return 'queen'
    
class King(Piece):
        
    def pieceMoves(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        moves = [[row, col+1], [row+1,col], [row+1, col+1], [row-1, col],[row,col-1], [row-1, col-1], [row+1, col-1], [row-1, col+1]]
        for move in moves:
            if not self.outOfBounds(move[0],move[1]) and not self.hasFriend(move[0],move[1], board):
                goodMoves.append(move)
                
        castleValue = self.canCastle()
                
        if castleValue == 3:
            goodMoves.append([row,col+2])
            goodMoves.append([row,col-2])
        elif castleValue == 2:
            goodMoves.append([row,col-2])
        elif castleValue == 1:
            goodMoves.append([row,col+2])
                
        if not isAI:
            goodMoves = self.testMovesForCheck(goodMoves, board)        
                
        return goodMoves
        
        
    def squaresThreatened(self, board, isAI = False):
        row = self.getRow()
        col = self.getCol()
        goodMoves = []
        moves = [[row, col+1], [row+1,col], [row+1, col+1], [row-1, col],[row,col-1], [row-1, col-1], [row+1, col-1], [row-1, col+1]]
        for move in moves:
            if not self.outOfBounds(move[0],move[1]):
                goodMoves.append(move)
        return goodMoves
    
    def canCastle(self):
        '''Returns an int that signifies whether this king meets the criteria to preform a castle maneuver - 0 means no, 1 means it can castle left, 2 means it can castle right, and 3 means it can castle either side'''
        board = self.board
        row = self.getRow()
        col = self.getCol()
        enemyMoves = []
        for piece in board.pieceList:
            if piece.getSide() != self.getSide() and str(piece) != "king":
                for square in piece.squaresThreatened(board):
                    enemyMoves.append(square)
        
        #0 = no
        #1 = only left
        #2 = only right
        #3 = both ways
        castleCondition = 0
        if self.hasMoved == False:
            if str(board.boardList[row][col+3]) == "rook" and board.boardList[row][col+3].getSide() == self.getSide() and board.boardList[row][col+3].hasMoved == False:
                if board.boardList[row][col+1] is None and board.boardList[row][col+2] is None:
                    if [row, col] not in enemyMoves and [row, col+1] not in enemyMoves and [row, col+2] not in enemyMoves:
                        castleCondition += 1
            if str(board.boardList[row][col-4]) == "rook" and board.boardList[row][col-4].getSide() == self.getSide() and board.boardList[row][col-4].hasMoved == False:
                if board.boardList[row][col-1] is None and board.boardList[row][col-2] is None and board.boardList[row][col-3]:
                    if [row, col] not in enemyMoves and [row, col-1] not in enemyMoves and [row, col-2] not in enemyMoves and [row, col-3] not in enemyMoves:
                        castleCondition += 2
        return castleCondition
        
    def getMaterial(self):
        return 0
        
    def getAdjustedMaterial(self):
        value = 1000
        #king safety
        if self.getBoard().moveCounter <= 30:
            if self.getCol() == 1 or self.getCol() == 6:
                if self.getSide() == 'white' and self.getRow() == 7:
                    value += 0.5
                elif self.getSide() == 'black' and self.getRow() == 0:
                    value += 0.5
            elif self.getCol() == 2:
                if self.getSide() == 'white' and self.getRow() == 7:
                    value += 0.25
                elif self.getSide() == 'black' and self.getRow() == 0:
                    value += 0.25
        return value
        
    def __str__(self):
        return 'king'


class Board(object):
    def __init__(self, image, surface):
        self.image = image
        self.surface = surface
        self.boardList = []
        self.enPassantList = []
        self.moveCounter = 0
        for row in range(8):
            self.boardList.append([None, None, None, None, None, None, None, None])
        
    def __str__(self): #not actually used in our code, but it's not hard to imagine situations - i.e. hashing - where this could be useful
        string = ""
        for row in self.boardList:
            for square in row:
                if square is None:
                    string += "None"
                else:
                    string += square.__str__()
        return string
    
    def highlightSquare(self, square):
        '''Given a board and a coordinate, blit's a highlight token on that square'''
        global boardScale
        highlightImage = pygame.image.load("highlight.png")
        highlightImage = pygame.transform.scale(highlightImage, (int(100*boardScale), int(100*boardScale)))
        row = square[0]
        col = square[1]        
        imagerect = highlightImage.get_rect()
        rect = pygame.Rect((col*100*boardScale,row*100*boardScale),(100*boardScale,100*boardScale))
        self.surface.blit(highlightImage, rect)
        
    def unHighlightSquare(self,square):
        '''Given a board and a square, removes the highlight token from that square'''
        self.drawEverything()
        
    def setBoard(self):
        '''Given an empty board, initializes a set of pieces for a standard game of chess'''
        whitePawnImage = pygame.image.load("whitepawn.png")
        blackPawnImage = pygame.image.load("blackpawn.png")
        whiteKnightImage = pygame.image.load("whiteknight.png")
        blackKnightImage = pygame.image.load("blackknight.png")
        whiteBishopImage = pygame.image.load("whitebishop.png")
        blackBishopImage = pygame.image.load("blackbishop.png")
        whiteRookImage = pygame.image.load("whiterook.png")
        blackRookImage = pygame.image.load("blackrook.png")
        whiteQueenImage = pygame.image.load("whitequeen.png")
        blackQueenImage = pygame.image.load("blackqueen.png")
        whiteKingImage = pygame.image.load("whiteking.png")
        blackKingImage = pygame.image.load("blackking.png")
        
        self.pieceList = []
        for col in range(8):
            self.boardList[1][col] = Pawn('black', 1, col, self, blackPawnImage, self.surface)
            self.boardList[6][col] = Pawn('white', 6, col, self, whitePawnImage, self.surface)
        self.boardList[0][1] = Knight('black', 0, 1, self, blackKnightImage, self.surface)
        self.boardList[0][6] = Knight('black', 0, 6, self, blackKnightImage, self.surface)
        self.boardList[7][1] = Knight('white', 7, 1, self, whiteKnightImage, self.surface)
        self.boardList[7][6] = Knight('white', 7, 6, self, whiteKnightImage, self.surface)
        self.boardList[0][2] = Bishop('black', 0, 2, self, blackBishopImage, self.surface)
        self.boardList[0][5] = Bishop('black', 0, 5, self, blackBishopImage, self.surface)
        self.boardList[7][2] = Bishop('white', 7, 2, self, whiteBishopImage, self.surface)
        self.boardList[7][5] = Bishop('white', 7, 5, self, whiteBishopImage, self.surface)
        self.boardList[0][0] = Rook('black', 0, 0, self, blackRookImage, self.surface)
        self.boardList[0][7] = Rook('black', 0, 7, self, blackRookImage, self.surface)
        self.boardList[7][0] = Rook('white', 7, 0, self, whiteRookImage, self.surface)
        self.boardList[7][7] = Rook('white', 7, 7, self, whiteRookImage, self.surface)
        self.boardList[0][3] = Queen('black', 0, 3, self, blackQueenImage, self.surface)
        self.boardList[7][3] = Queen('white', 7, 3, self, whiteQueenImage, self.surface)
        self.boardList[0][4] = King('black', 0, 4, self, blackKingImage, self.surface)
        self.boardList[7][4] = King('white', 7, 4, self, whiteKingImage, self.surface)
        
        for row in self.boardList:
            for square in row:
                if square != None:
                    self.pieceList.append(square)
        
    def getPieceList(self):
        '''Given a board, returns a list of pieces that are on that board'''
        return self.pieceList
        
    def getCheck(self):
        '''Given a board, returns an int of whether check is present on the board - 0 means no, 1 means white is in check, 2 means black is in check'''
        for piece in self.pieceList:
            if piece.__str__() == 'king' and piece.isThreatened(piece.getPosition()[0], piece.getPosition()[1], self):
                if piece.getSide() == 'white':
                    return 2
                else:
                    return 1
        else:
            return 0
                    
    def getCheckmate(self):
        '''Gieven a board, returns an int of whether check mate is present on the board - 0 means no, 1 means white is in checkmate, 2 means black is in checkmate, and 3 means the game is a draw by stalemate.'''
        for piece in self.pieceList:
            if piece.__str__() == 'king' and piece.isThreatened(piece.getPosition()[0], piece.getPosition()[1], self):
                for otherPiece in self.pieceList:
                    if otherPiece.getSide() == piece.getSide():
                        pieceMoves = otherPiece.pieceMoves(self)
                        if pieceMoves != []:
                            return 0
                if piece.getSide() == 'white':
                    return 2
                else:
                    return 1
                    
            elif piece.__str__() == 'king' and not piece.isThreatened(piece.getPosition()[0], piece.getPosition()[1], self):
                for otherPiece in self.pieceList:
                    if otherPiece.getSide() == piece.getSide():
                        pieceMoves = otherPiece.pieceMoves(self)
                        if pieceMoves != []:
                            return 0
                return 3
        else:
            return 0
            
    
    def drawSelf(self):
        '''Given a board, uses pygame to graphically display the UI'''
        rect = pygame.Rect(0, 0, self.surface.get_width(), self.surface.get_width())
        self.surface.blit(self.image, rect)
    
    def drawEverything(self):
        '''Given a board, uses pygame to graphically display everything that should be visible on the board'''
        self.drawSelf()
        for piece in self.pieceList:
            piece.draw()
            
    def getPieceMoves(self, position):
        '''Given a board and a position on that board, returns a list of moves the piece in that square can make'''
        piece = self.boardList[position[0]][position[1]]
        return piece.pieceMoves(self)
        
    def getAllMoves(self, side):
        '''Given a board and a side, returns a list of every possible move by that side on the given board'''
        moves = []
        for piece in self.pieceList:
            if piece.getSide() == side:
                for move in piece.pieceMoves(self):
                    moves.append([piece.getPosition(), move])
        return moves
        
    def incMoveCounter(self):
        self.moveCounter += 1
        
    def makeMove(self, oldPosition, newPosition, isAI = False):
        '''Given a move, makes that move, implementing any special rules involved with that move'''
        #note: the reason the board needs to know whether the AI is making the move is so that if the AI promotes a pawn it doesn't query the player what piece it should be promoted to
        piece = self.boardList[oldPosition[0]][oldPosition[1]]
        board = piece.getBoard()
        newSquare = self.boardList[newPosition[0]][newPosition[1]]
        #castling
        if piece.__str__() == "king" and piece.hasMoved == False and newPosition[1] == 6:
            self.pieceList.pop(self.pieceList.index(self.boardList[newPosition[0]][7]))
            piece.setPosition(newPosition)
            if piece.getSide() == "black":
                image = pygame.image.load("blackrook.png")
            else:
                image = pygame.image.load("whiterook.png")
            self.pieceList.append(Rook(piece.getSide(), oldPosition[0], 5, self, image, self.surface))
            
        elif piece.__str__() == "king" and piece.hasMoved == False and newPosition[1] == 2:
            self.pieceList.pop(self.pieceList.index(self.boardList[newPosition[0]][0]))
            piece.setPosition(newPosition)
            if piece.getSide() == "black":
                image = pygame.image.load("blackrook.png")
            else:
                image = pygame.image.load("whiterook.png")
            self.pieceList.append(Rook(piece.getSide(), oldPosition[0], 3, self, image, self.surface))
        #en passant & promotion
           
        #normal move        
        if newSquare != None:
            if newSquare.__str__() == 'enpassant':
                if newSquare.getSide() == 'white':
                    deadPawn = self.boardList[newPosition[0] - 1][newPosition[1]]
                    self.pieceList.pop(self.pieceList.index(deadPawn))
                elif newSquare.getSide() == 'black':
                    deadPawn = self.boardList[newPosition[0] + 1][newPosition[1]]
                    self.pieceList.pop(self.pieceList.index(deadPawn))
                self.enPassantList.pop(self.enPassantList.index(newSquare))
                
            else:
                self.pieceList.pop(self.pieceList.index(newSquare))      
        piece.setPosition(newPosition)
        piece.hasMoved = True
        
        #promotion and creating en passant squares
        if piece.__str__() == 'pawn':
            if piece.getSide() == 'white' and piece.getRow() == 0:
                self.promote(piece, 'white', isAI)
            elif piece.getSide() == 'black' and piece.getRow() == 7:
                self.promote(piece, 'black', isAI)
            elif abs(oldPosition[0] - newPosition[0]) == 2:
                #create an enPassant in the "middle" space
                image = pygame.image.load("deadpiece.png")
                side = piece.getSide()
                if newPosition[0] < oldPosition[0]:
                    enPassantSquare = [newPosition[0]+1, newPosition[1]]
                else:
                    enPassantSquare = [newPosition[0]-1, newPosition[1]]
                self.boardList[enPassantSquare[0]][enPassantSquare[1]] = enPassant(side, enPassantSquare[0], enPassantSquare[1], self, image, self.surface)
                self.enPassantList.append(self.boardList[enPassantSquare[0]][enPassantSquare[1]]) 
                
        self.incMoveCounter()        
        
    def makeAIMove(self, ai):
        '''Given a board an an AI, executes the AI's move'''
        move = ai.aiMove(self)
        self.makeMove(move[0], move[1], isAI = True)
        
    def updateBoardList(self):
        '''Given a board, updates the board's list of pieces'''
        self.boardList = []
        for row in range(8):
            self.boardList.append([None, None, None, None, None, None, None, None])
        for piece in self.pieceList:
            self.boardList[piece.getPosition()[0]][piece.getPosition()[1]] = piece
        for enPassantSquare in self.enPassantList:
            if self.moveCounter >= enPassantSquare.moveCreated + 2:
                self.enPassantList.pop(self.enPassantList.index(enPassantSquare))
            else:
                self.boardList[enPassantSquare.getPosition()[0]][enPassantSquare.getPosition()[1]] = enPassantSquare
            
    def promote(self, piece, side, isAI):
        '''Given a board, piece, side, and boolean, allows the user to change a piece into another'''
        whiteKnightImage = pygame.image.load("whiteknight.png")
        blackKnightImage = pygame.image.load("blackknight.png")
        whiteBishopImage = pygame.image.load("whitebishop.png")
        blackBishopImage = pygame.image.load("blackbishop.png")
        whiteRookImage = pygame.image.load("whiterook.png")
        blackRookImage = pygame.image.load("blackrook.png")
        whiteQueenImage = pygame.image.load("whitequeen.png")
        blackQueenImage = pygame.image.load("blackqueen.png")
        
        invalidInput = True
        
        if not isAI:
            while invalidInput:
                newPieceType = input('What piece would you like to promote to? (bishop, knight, rook, queen): ')
                if newPieceType == 'bishop' or newPieceType == 'knight' or newPieceType == 'rook' or newPieceType == 'queen':
                    invalidInput = False
                    square = piece.getPosition()
                    side = piece.getSide()
                    self.pieceList.pop(self.pieceList.index(piece))
                    if newPieceType == 'bishop' and side == 'white':
                        self.pieceList.append(Bishop(side, square[0], square[1], self, whiteBishopImage, self.surface))
                    elif newPieceType == 'bishop' and side == 'black':
                        self.pieceList.append(Bishop(side, square[0], square[1], self, blackBishopImage, self.surface))
                    elif newPieceType == 'knight' and side == 'white':
                        self.pieceList.append(Knight(side, square[0], square[1], self, whiteKnightImage, self.surface))
                    elif newPieceType == 'knight' and side == 'black':
                        self.pieceList.append(Knight(side, square[0], square[1], self, blackKnightImage, self.surface))
                    elif newPieceType == 'rook' and side == 'white':
                        self.pieceList.append(Rook(side, square[0], square[1], self, whiteRookImage, self.surface))
                    elif newPieceType == 'rook' and side == 'black':
                        self.pieceList.append(Rook(side, square[0], square[1], self, blackRookImage, self.surface))
                    elif newPieceType == 'queen' and side == 'white':
                        self.pieceList.append(Queen(side, square[0], square[1], self, whiteQueenImage, self.surface))
                    elif newPieceType == 'queen' and side == 'black':
                        self.pieceList.append(Queen(side, square[0], square[1], self, blackQueenImage, self.surface))
                    
        else: 
            square = piece.getPosition()
            side = piece.getSide()
            self.pieceList.pop(self.pieceList.index(piece))
            if side == 'white':
                self.pieceList.append(Queen(side, square[0], square[1], self, whiteQueenImage, self.surface))
            else:
                self.pieceList.append(Queen(side, square[0], square[1], self, blackQueenImage, self.surface))
                    
class AI(object):
    
    def __init__(self, depth, side):
        self.maxDepth = depth
        self.side = side
        self.materialWeight = 1
        self.checkWeight = 0.25
        self.twoMovesAndValuesList = []
        self.move1 = None
        
    def aiMove(self, board):
        moveAndValueList = []
        self.twoMovesAndValuesList = []
        if self.side == 'white':
            maximizingPlayer = True
            for move in self.orderMovesAlphaBeta(board, self.side):
                self.twoMovesAndValuesList.append(move)
                moveAndValueList.append([move, self.alphaBeta(copy.deepcopy(board), move, 0, -1e309, 1e309, 'black')])
        else:
            maximizingPlayer = False
            for move in self.orderMovesAlphaBeta(board, self.side):
                self.twoMovesAndValuesList.append(move)
                moveAndValueList.append([move, self.alphaBeta(copy.deepcopy(board), move, 0, -1e309, 1e309, 'white')])
        
        #add randomness
        for pair in moveAndValueList:
            pair[1] += (random.randint(-1000, 1000)/1000000)
            
        sortedMoveAndValueList = sorted(moveAndValueList, key = lambda x: x[1], reverse = maximizingPlayer)
        return sortedMoveAndValueList[0][0]
        

    def evaluate(self, board):
        '''Returns a value between (approximately) -1000 and 1000 indicating how favorable the board is for each player. Smaller (more negative) scores favor Black, whereas larger scores favor White.'''
        total = 0
        whiteMaterial = 0
        blackMaterial = 0
        for piece in board.getPieceList():
            if piece.getSide() == 'white':
                whiteMaterial += piece.getAdjustedMaterial() #this function call is the real workhorse: it includes king safety, pawn position, attack power, etc.
            elif piece.getSide() == 'black':
                blackMaterial += piece.getAdjustedMaterial()
                   
        materialScore = whiteMaterial - blackMaterial
        
        #see whether either side is in check
        #checkScore = 0
        #if board.getCheck() == 1:
        #    checkScore = 1
        #elif board.getCheck() == 2:
        #    checkScore = -1
        
        total = materialScore*self.materialWeight #+ checkScore*self.checkWeight
        
        return total
        
    	
    def orderMovesNaive(self, board, side):
        '''Given a board and a side, naively orders the set of all possible moves based solely on whether or not they involve the capture of a piece, and if so, how much the piece is worth.'''
        orderedMoves = []
        moveAndValueList = []
        for move in board.getAllMoves(side):
            value = 0
            if board.boardList[move[1][0]][move[1][1]] != None:
                value += board.boardList[move[1][0]][move[1][1]].getMaterial()
            moveAndValueList.append([move, value])
        sortedMoveAndValueList = sorted(moveAndValueList, key = lambda x: x[1], reverse = True)
        for i in range(len(sortedMoveAndValueList)):
            orderedMoves.append(sortedMoveAndValueList[i][0])
        return orderedMoves
        
    def orderMovesAlphaBeta(self, board, side):
        '''Given a board and a side, orders the set of all possible moves by calling alpha-beta on each move with maximum depth 1.'''
        moves = self.orderMovesNaive(board, side)
        moveAndValueList = []
        if self.side == 'white':
            maximizingPlayer = True
            for move in moves:
                moveAndValueList.append([move, self.alphaBeta(copy.deepcopy(board), move, self.maxDepth - 1, -1e309, 1e309, 'black')])
        else:
            maximizingPlayer = False
            for move in moves:
                moveAndValueList.append([move, self.alphaBeta(copy.deepcopy(board), move, self.maxDepth - 1, -1e309, 1e309, 'white')])
                
        sortedMoveAndValueList = sorted(moveAndValueList, key = lambda x: x[1], reverse = maximizingPlayer) #if these moves are being sorted for white, he/she wants the highest ranked move first
        sortedMoveList = list(map(lambda x: x[0], sortedMoveAndValueList))
        return sortedMoveList
    
    def alphaBeta(self, board, move, depth, alpha, beta, side):
        '''Given a board and a move, returns an evaluation for that move by recursing over every possible move in each state until the depth limit is reached, then using the evaluate() function and passing the values back up through minimax with alpha-beta pruning.'''
        board.makeMove(move[0], move[1], isAI = True)
        board.updateBoardList()
        if  depth == self.maxDepth:
            value = self.evaluate(board)
            return value
            
        #uses naive move ordering instead of alpha-beta, since otherwise it would never stop!    
        orderedMoves = self.orderMovesNaive(board, side)
            
        if side == 'white':
            value = -1000
            for move in orderedMoves:
                value = max(value, self.alphaBeta(copy.deepcopy(board), move, depth+1, alpha, beta, 'black'))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break #white's worst (minimum) value is less than black's worst(maximum) value; the players would never voluntarily reach this position, so it and its children can safely be pruned
            return value
        else:
            value = 1000
            for move in orderedMoves:
                value = min(value, self.alphaBeta(copy.deepcopy(board), move, depth+1, alpha, beta, 'white'))
                beta = min(beta, value)
                if beta <= alpha:
                    break
            return value
    		

            
            
            
def twoPlayer():
    '''Method for allowing two humans to play against each other'''
    global boardScale
    boardImage = pygame.image.load("chessboard.jpg")
    pygame.init()
    
    validScale = False
    validDepth = False
    validSide = False
    while validScale == False:
        boardScale = input("Enter the scaling factor for the board (1 corresponds to 800x800):")
        try:
            boardScale = float(boardScale)
        except:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
        if 0 < boardScale and boardScale <= 10:
            validScale = True
        else:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
    
    pygame.init()
    width = int(800*boardScale)
    height = int(800*boardScale)
    surface = pygame.display.set_mode([width, height])
    boardImage = pygame.transform.scale(boardImage,(width,height))
    board = Board(boardImage, surface)
    board.setBoard()
	
    surface.fill([0, 0, 0])
    board.drawEverything()
    pygame.display.flip()
	
    playerSide = 'white'
    firstClick = True
    checkmateValue = 0
	
    while True:
        clickPosition = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and checkmateValue == 0: #i.e. when the game is over, the only thing the players can do is exit
                clickPosition[0] = event.pos[0]
                clickPosition[1] = event.pos[1]
                clickSquare = [clickPosition[1]//int(100*boardScale), clickPosition[0]//int(100*boardScale)]
                piece = board.boardList[clickSquare[0]][clickSquare[1]]
                if firstClick:
                    if piece != None and piece.getSide() == playerSide:
                        moves = board.getPieceMoves(clickSquare)
                        #highlight available moves
                        highlightedSquares = []
                        for move in moves:
                            board.highlightSquare(move)
                            highlightedSquares.append(move)
                            pygame.display.flip()
                        firstClickSquare = clickSquare
                        firstClick = False
                        continue #restart the event code, this time getting the move-determining (or selection-cancelling) click
                        
                if not firstClick:
                    for square in highlightedSquares:
                            board.unHighlightSquare(square)
                    pygame.display.flip()
                    validMove = False
                    for move in moves:
                        if move == clickSquare:
                            validMove = True
                    if validMove:
                        board.makeMove(firstClickSquare, clickSquare)
                        board.updateBoardList()
                        surface.fill([0, 0, 0])
                        board.drawEverything()
                        pygame.display.flip()

                        checkmateValue = board.getCheckmate()
                        if checkmateValue == 1:
                            print('White wins!')
                        elif checkmateValue == 2:
                            print('Black wins!')
                        elif checkmateValue == 3:
                            print('The game is a draw by stalemate.')
                        checkValue = board.getCheck()
                        if checkValue != 0 and checkmateValue == 0:
                            print('Check.')
                        
                        if playerSide == 'white':
                            playerSide = 'black'
                        else:
                            playerSide = 'white'
                            
                    firstClick = True
                    
                    
def vsAI():
    '''Launches a game against an AI'''
    global boardScale
    boardImage = pygame.image.load("chessboard.jpg")
    pygame.init()
    
    validScale = False
    validDepth = False
    validSide = False
    while validScale == False:
        boardScale = input("Enter the scaling factor for the board (1 corresponds to 800x800):")
        try:
            boardScale = float(boardScale)
        except:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
        if 0 < boardScale and boardScale <= 10:
            validScale = True
        else:
            print("Please enter a positive number less than or equal to 10 as the scaling factor.")
            continue
            
    while validDepth == False:
        depth = input("What depth should the AI search to? 2 is recommended - 3 is more advanced but can take multiple minutes to think.")
        try:
            depth = int(depth)
        except:
            print("Please choose an integer greater than or equal to 0 for the AI's depth.")
            continue
        if depth >= 0:
            validDepth = True
        else:
            print("Please choose an integer greater than or equal to 0 for the AI's depth.")
            continue
            
    while validSide == False:
        side = input("Which side would you like to play as? Please enter \"white\" or \"black\".")
        if side == 'white' or side == 'White' or side == 'black' or side == 'Black':
            validSide = True
        elif side == "\"white\" or \"black\"":
            print("Very funny.")
            continue
        else:
            print("Please enter a valid side (white or black).")
            continue
    
    
    width = int(800*boardScale)
    height = int(800*boardScale)
    surface = pygame.display.set_mode([width, height])
    boardImage = pygame.transform.scale(boardImage, (width, height))

    board = Board(boardImage, surface)
    board.setBoard()
    
    if side == 'white':
        ai = AI(depth, 'black')
    else:
        ai = AI(depth, 'white')
	
    surface.fill([0, 0, 0])
    board.drawEverything()
    pygame.display.flip()
	
    playerSide = side
    firstClick = True
    checkmateValue = 0
	
    while True:
        #handle the AI being white by just adding an extra move to the start before the event handling code
        if side == 'black' and board.moveCounter == 0:
            board.makeAIMove(ai)
            board.updateBoardList()
            surface.fill([0, 0, 0])
            board.drawEverything()
            pygame.display.flip()
            
        clickPosition = [0, 0]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and checkmateValue == 0:
                clickPosition[0] = event.pos[0]
                clickPosition[1] = event.pos[1]
                clickSquare = [clickPosition[1]//int(100*boardScale), clickPosition[0]//int(100*boardScale)]
                piece = board.boardList[clickSquare[0]][clickSquare[1]]
                
                if firstClick:
                    if piece != None and piece.getSide() == playerSide:
                        moves = board.getPieceMoves(clickSquare)
                        highlightedSquares = []
                        for move in moves:
                            board.highlightSquare(move)
                            highlightedSquares.append(move)
                            pygame.display.flip()
                        firstClickSquare = clickSquare
                        firstClick = False
                        continue
                        
                if not firstClick:
                    for square in highlightedSquares:
                            board.unHighlightSquare(square)
                    pygame.display.flip()
                    validMove = False
                    for move in moves:
                        if move == clickSquare:
                            validMove = True        
                    if validMove:
                        board.makeMove(firstClickSquare, clickSquare)
                        board.updateBoardList()
                        surface.fill([0, 0, 0])
                        board.drawEverything()
                        pygame.display.flip()
                        
                        checkmateValue = board.getCheckmate()
                        if checkmateValue == 1:
                            print('White wins!')
                            continue
                        elif checkmateValue == 2:
                            print('Black wins!')
                            continue
                        elif checkmateValue == 3:
                            print('The game is a draw by stalemate.')
                            continue
                            
                        checkValue = board.getCheck()
                        if checkValue != 0 and checkmateValue == 0:
                            print('Check.')
                            
                        board.makeAIMove(ai)
                        board.updateBoardList()
                        surface.fill([0, 0, 0])
                        board.drawEverything()
                        pygame.display.flip()
                        
                        checkmateValue = board.getCheckmate()
                        if checkmateValue == 1:
                            print('White wins!')
                            continue
                        elif checkmateValue == 2:
                            print('Black wins!')
                            continue
                        elif checkmateValue == 3:
                            print('The game is a draw by stalemate.')
                            
                        checkValue = board.getCheck()
                        if checkValue != 0 and checkmateValue == 0:
                            print('Check.')
                        
                    firstClick = True
    

if __name__ == "__main__":
    while True:
        mode = input("How many players are playing?(1 or 2)")
        try:
            mode = int(mode)
        except:
            print("Please choose a valid answer - 1 to play against an AI or 2 to play against another human.")
            continue
        if mode == 1:
            vsAI()
        elif mode == 2:
            twoPlayer()
        else:
            print("Please choose a valid answer - 1 to play against an AI or 2 to play against another human.")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
