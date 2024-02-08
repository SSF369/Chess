''' This class is responsible for storing all the Information about the current state of the chess game. It will also be responsible for determining 
the valid moves at the current state. It will also keep a move log. '''

class GameState():

	def  __init__(self):
		#board is 8x8 2D list, each element of the list has 2 characters.
		#The first character represents the colour of the piece, 'b' or 'w'
		#The second character represents type of the piece, 'K','Q','B','N','p','R' 
		#'--' - represents empty space with no piece.
		self.board = [
			['bR','bN','bB','bQ','bK','bB','bN','bR'],
			['bp','bp','bp','bp','bp','bp','bp','bp'],
			['--','--','--','--','--','--','--','--'],
                        ['--','--','--','--','--','--','--','--'],
                        ['--','--','--','--','--','--','--','--'],
                        ['--','--','--','--','--','--','--','--'],
                        ['wp','wp','wp','wp','wp','wp','wp','wp'],
                        ['wR','wN','wB','wQ','wK','wB','wN','wR']]

		self.moveFunctions = { 'p' : self.getPawnMoves, 'R' : self.getRookMoves, 'N' : self.getKnightMoves, 'B' : self.getBishopMoves, 'Q' : self.getQueenMoves, 'K' : self.getKingMoves }
		self.whiteToMove = True
		self.moveLog = []
		self.whiteKingLocation = (7, 4)
		self.blackKingLocation = (0, 4)
		self.inCheck = False
		self.pins = []
		self.checks = []

#Takes a move as a parameter and executes it (this will not work for castling, pawn promotion, and en-passant

	def makeMove(self, move):
		self.board[move.startRow][move.startCol] = '--'
		self.board[move.endRow][move.endCol] = move.pieceMoved
		self.moveLog.append(move) #log the move so we can undo it later
		self.whiteToMove = not self.whiteToMove #swap players
#To update the king's location if moved
		if move.pieceMoved == 'wK':
			self.whiteKingLocation = (move.endRow, move.endCol)
		elif move.pieceMoved == 'bK':
			self.blackKingLocation = (move.endRow, move.endCol)

#Undo the last move made

	def undoMove(self):
		if len(self.moveLog) != 0: #make sure that there is a move to undo
			move = self.moveLog.pop()
			self.board[move.startRow][move.startCol] = move.pieceMoved
			self.board[move.endRow][move.endCol] = move.pieceCaptured
			self.whiteToMove = not self.whiteToMove #switch turns back
#Update the king's position if needed
			if move.pieceMoved == 'wK':
				self.whiteKingLocation = (move.startRow, move.startCol)
			elif move.pieceMoved == 'bK':
				self.blackKingLocation = (move.startRow, move.startCol)


#All moves considering checks

	def getValidMoves(self):
#1.)generate all possible moves
		moves = [] 
		self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
		if self.whiteToMove:
			kingRow = self.whiteKingLocation[0]
			kingCol = self.whiteKingLocation[1]
		else:
			kingRow = self.blackKingLocation[0]
			kingCol = self.blackKingLocation[1]
		if self.inCheck:
			if len(self.checks) == 1: #Only one check, block check or move king.
				moves = self.getAllPossibleMoves()
#To block a check you must move a piece into one of the squares between the enemy piece and king
				check = self.checks[0] #check information
				checkRow = check[0]
				checkCol = check[1]
				pieceChecking = self.board[checkRow][checkCol] #enemy piece causing the check
				validSquares = [] #Squares that pieces can move to
#What if knight puts a check... We need to capture it or move the king itself
				if pieceChecking[1] == 'N':
					validSquares = [(checkRow, checkCol)]
				else:
					for i in range(1,8):
						validSquare = (kingRow + check[2] * i, kingCol + check[3] * i)
						validSquares.append(validSquare)
						if validSquare[0] == checkRow and validSquare[1] == checkCol:
							break
				for i in range(len(moves) -1, -1, -1):
					if moves[i].pieceMoved[1] != 'K':
						if not (moves[i].endRow, moves[i].endCol) in validSquares:
							moves.remove(moves[i])
			else: #double check , king has to move
				self.getKingMoves(kingRow, kingCol, moves)
		else:
			moves = self.getAllPossibleMoves()
#5.)if they do attack your king, not a valid move
		return moves

#	def inCheck(self): #Determine if the current player is in Check
#		if self.whiteToMove:
#			return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
#		else:
#			return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])

#	def squareUnderAttack(self, r, c): #Detaermine if the enemy can attack the square r, c
#		self.whiteToMove = not self.whiteToMove #switch to opponent's turn
#		oppMoves = self.getAllPossibleMoves()
#		self.whiteToMove = not self.whiteToMove #switch turn back
#		for move in oppMoves:
#			if move.endRow == r and move.endCol == c: #sqaure is under attack
#				return True
#		return False

#All moves without considring checks

	def getAllPossibleMoves(self):
		moves = []
		for r in range(len(self.board)): #number of rows
			for c in range(len(self.board[r])): #number of cols in given row
				turn = self.board[r][c][0]
				if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
					piece = self.board[r][c][1]
					#if piece == 'p':
					#	self.getPawnMoves(r, c, moves)
					#elif piece == 'R':
					#	self.getRookMoves(r, c, moves)
					#	    ....
					#Instead of using this lenghty process we can use the help of Dictionary
					self.moveFunctions[piece](r, c, moves) # here we can call appropriate move funcation based on piece types

		return moves

#Get all the pawn moves for the pawn located at row, col and add these moves to the list

	def getPawnMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = (0, 0)  # Default values
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break
		if not piecePinned or pinDirection == (-1, 0):
			if self.whiteToMove:  # white pawn moves
				if self.board[r-1][c] == '--':  # 1 square pawn advancement
					moves.append(Move((r, c), (r-1, c), self.board))
					if r == 6 and self.board[r-2][c] == '--':  # 2 sqaure pawn advancement
						moves.append(Move((r, c), (r-2, c), self.board))
				if c-1 >= 0:  # pawn captures to the left
					if not piecePinned or pinDirection == (-1, -1):
						if self.board[r-1][c-1][0] == 'b':  # enemy piece to capture
							moves.append(Move((r, c), (r-1, c-1),  self.board))
				if c+1 <= 7:  # pawn captures to the right, can also use len(self.board) instead of 7
					if not piecePinned or pinDirection == (-1, 1):
						if self.board[r-1][c+1][0] == 'b':  # enemy piece to capture
							moves.append(Move((r, c), (r-1, c+1), self.board))
			else:  # black pawn moves
				if not piecePinned or pinDirection == (1, 0):
					if self.board[r+1][c] == '--':  # 1 square pawn advancement
						moves.append(Move((r, c), (r+1, c), self.board))
						if r == 1 and self.board[r+2][c] == '--':  # 2 square pawn advancement
							moves.append(Move((r, c), (r+2, c), self.board))
					if  c-1 >= 0:  # pawn captures to the right
						if not piecePinned or pinDirection == (1, -1):
							if self.board[r+1][c-1][0] == 'w':  # enemy piece to capture
								moves.append(Move((r, c), (r+1, c-1), self.board))
					if c+1 <= 7:  # paws capture to the left
						if not piecePinned or pinDirection == (1, 1):
							if self.board[r+1][c+1][0] == 'w':  # enemy piece to capture
								moves.append(Move((r, c), (r+1, c+1), self.board))


#Get all the rook moves for the pawn located at row, col and add these moves to the list

	def getRookMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				if self.board[r][c][1] != 'Q':
					self.pins.remove(self.pins[i])
				break
		directions = ((-1, 0), (0, -1) , (1, 0), (0, 1)) #up, left, down, right
		enemyColour = 'b' if self.whiteToMove else 'w'
		for d in directions:
			for i in range(1, 8):
				endRow = r + d[0] * i
				endCol = c + d[1] * i
				if 0 <= endRow < 8 and 0 <= endCol < 8: #on board
					if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
						endPiece = self.board[endRow][endCol]
						if endPiece == '--': #empty space valid
							moves.append(Move((r, c), (endRow, endCol), self.board))
						elif endPiece[0] ==  enemyColour: #enemy piece valid
							moves.append(Move((r, c), (endRow, endCol), self.board))
							break
						else: #friendly piece invalid
							break
				else: #off board
					break

#Get all the knight moves for the pawn located at row, col and add these moves to the list

	def getKnightMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break
		knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1,-2), (1, 2), (2, -1), (2, 1))
		allyColor = 'w' if self.whiteToMove else 'b'
		for m in knightMoves:
			endRow = r + m[0]
			endCol = c + m[1]
			if 0 <= endRow < 8 and 0 <= endCol < 8:
				if not piecePinned:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] != allyColor:
						moves.append(Move((r, c), (endRow, endCol), self.board))

#Get all the bishop moves for the pawn located at row, col and add these moves to the list

	def getBishopMoves(self, r, c, moves):
		piecePinned = False
		pinDirection = ()
		for i in range(len(self.pins)-1, -1, -1):
			if self.pins[i][0] == r and self.pins[i][1] == c:
				piecePinned = True
				pinDirection = (self.pins[i][2], self.pins[i][3])
				self.pins.remove(self.pins[i])
				break
		directions =  ((-1, -1), (-1, 1), (1, -1), (1, 1)) #4 diagonals
		enemyColour = 'b' if self.whiteToMove else 'w'
		for d in directions:
			for i in range(1, 8): #bishop can move max of 7 square
				endRow = r + d[0] * i
				endCol = c + d[1] * i
				if 0 < endRow < 8 and 0 <= endCol < 8: #on board
					if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
						endPiece = self.board[endRow][endCol]
						if endPiece == '--': #empty space valid
							moves.append(Move((r, c), (endRow, endCol), self.board))
						elif endPiece[0] ==  enemyColour: #enemy piece valid
							moves.append(Move((r, c), (endRow, endCol), self.board))
							break
						else: #friendly piece invalid
							break
				else: #off board
					break


#Get all the queen moves for the pawn located at row, col and add these moves to the list

	def getQueenMoves(self, r, c, moves):
		self.getRookMoves(r, c, moves)
		self.getBishopMoves(r, c, moves)

#Get all the King moves for the pawn located at row, col and add these moves to the list

	def getKingMoves(self, r, c, moves):
		rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
		colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
		allyColor = 'w' if self.whiteToMove else 'b'
		for i in range(8):
			endRow = r + rowMoves[i]
			endCol = c + colMoves[i]
			if 0 <= endRow < 8 and 0 <= endCol <8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] != allyColor:
					if allyColor == 'w':
						self.whiteKingLocation = (endRow, endCol)
					else:
						self.blackKingLocation = (endRow, endCol)
					inCheck, pin, checks = self.checkForPinsAndChecks()
					if not inCheck:
						moves.append(Move((r, c), (endRow, endCol), self.board))
					if allyColor == 'w':
						self.whiteKingLocation = (r, c)
					else:
						self.blackKingLocation = (r, c)

#returns if the player is in check, a list of pins, and a list of checks
	def checkForPinsAndChecks(self):
		pins = []
		checks = []
		inCheck = False
		if self.whiteToMove:
			enemyColor = 'b'
			allyColor = 'w'
			startRow = self.whiteKingLocation[0]
			startCol = self.whiteKingLocation[1]
		else:
			enemyColor = 'w'
			allyColor = 'b'
			startRow = self.blackKingLocation[0]
			startCol = self.blackKingLocation[1]
		directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
		for j in range(len(directions)):
			d = directions[j]
			possiblePin = ()
			for i in range(1, 8):
				endRow = startRow + d[0] * i
				endCol = startCol + d[1] * i
				if 0 <= endRow <8 and 0 <= endCol < 8:
					endPiece = self.board[endRow][endCol]
					if endPiece[0] == allyColor and endPiece[1] != 'K':
						if possiblePin == ():
							possiblePin = (endRow, endCol, d[0], d[1])
						else:
							break
					elif endPiece[0] == enemyColor:
						type = endPiece[1]
						if (0 <=j <=3 and type == 'R') or (4 <=j <= 7 and type == 'B') or (i == 1 and type == 'p' and ((enemyColor == 'w' and 6 <=j <= 7) or (enemyColor == 'b' and 4 <= j <=5))) or (type == 'Q') or (i == 1 and type == 'K') :
							if possiblePin == ():
								inCheck = True
								checks.append((endRow, endCol, d[0], d[1]))
								break
							else:
								pins.append(possiblePin)
								break
						else:
							break
				else:
					break
#check for Knight Checks
		knightMoves =((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1,-2), (1, 2), (2, -1), (2, 1))
#                allyColor = 'w' if self.whiteToMove else 'b'
		for m in knightMoves:
			endRow = startRow + m[0]
			endCol = startCol + m[1]
			if 0 <= endRow < 8 and 0 <+ endCol < 8:
				endPiece = self.board[endRow][endCol]
				if endPiece[0] == enemyColor and endPiece[1] == 'N':
					inCheck = True
					checks.append((endRow, endCol, m[0], m[1]))
		return inCheck, pins, checks

class Move():
	# maps keys to values
	# key : values
	ranksToRows = { '1':7,'2':6,'3':5,'4':4,'5':3,'6':2,'7':1,'8':0 }
	rowsToRanks = {v:k for k,v in ranksToRows.items()}
	filesToCols = { 'a':0,'b':1,'c':2,'d':3,'e':4,'f':5,'g':6,'h':7 }
	colsToFiles = {v:k for k, v in filesToCols.items()}

	def __init__(self, startSq, endSq, board):
		self.startRow = startSq[0]
		self.startCol = startSq[1]
		self.endRow = endSq[0]
		self.endCol = endSq[1]
		self.pieceMoved = board[self.startRow][self.startCol]
		self.pieceCaptured = board[self.endRow][self.endCol]
		self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
		#print(self.moveID)

#Overriding the equals method

	def __eq__(self, other):
		if isinstance(other, Move):
			return self.moveID == other.moveID
		return False

	def getChessNotation(self):
		#you can add to make this real chess notation
		return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

	def getRankFile(self, r, c):
		return self.colsToFiles[c] + self.rowsToRanks[r]
