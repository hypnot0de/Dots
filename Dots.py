import random
import copy

class dotsAndBoxes:
    def __init__(self,row,col,plies):
        self.row=row
        self.col=col
        self.plies=plies
        self.state=[]
        self.moves=[]
        self.playerTurn=True
        self.score=[0,0]
        self.equivalent={}
        #game state represented by list of boxes with 4 boolean edges, with all inner edges
        #having a compliment. dictionary maintains equivalency between edges
        #each box has a random point value and an owner associated with it
        #moves maintains list of unfilled edges, non-redundant
        for i in range(0,row):
            for j in range(0,col):
                self.state.append([False,False,False,False,random.randint(1,5),-1])
                self.moves.append((i,j,0))
                self.moves.append((i,j,1))
                if j==0:
                    self.equivalent[(i,j,0)]=-1
                    self.equivalent[(i,j,2)]=(i,j+1,0)
                if i==0:
                    self.equivalent[(i,j,1)]=-1
                    self.equivalent[(i,j,3)]=(i+1,j,1)
                if 0<j<col-1:
                    self.equivalent[(i,j,2)]=(i,j+1,0)
                    self.equivalent[(i,j,0)]=(i,j-1,2)
                if 0<i<row-1:
                    self.equivalent[(i,j,3)]=(i+1,j,1)
                    self.equivalent[(i,j,1)]=(i-1,j,3)
                if j==col-1:
                    self.moves.append((i,j,2))
                    self.equivalent[(i,j,0)]=(i,j-1,2)
                    self.equivalent[(i,j,2)]=-1
                if i==row-1:
                    self.moves.append((i,j,3))
                    self.equivalent[(i,j,1)]=(i-1,j,3)
                    self.equivalent[(i,j,3)]=-1

#updates the state in response to a move
    def makeMove(self,move,state,moves,playerTurn,score):
        i,j,k=move[0],move[1],move[2]
        state[i*(self.col)+j][k]=True
        self.checkBox(move,state,playerTurn,score)
        #if move claims an inner edge updates state of adjacent box as well
        if self.equivalent[move]!=-1:
            y,x,z=self.equivalent[move][0],self.equivalent[move][1],self.equivalent[move][2]
            state[y*(self.col)+x][z]=True
            self.checkBox((y,x,z),state,playerTurn,score)

        if move in moves:
            moves.remove(move)
        else:
            moves.remove(self.equivalent[move])

#checks the relavent box given a move and updates the score and ownership if necessary
    def checkBox(self,move,state,playerTurn,score):
        index=move[0]*self.col+move[1]
        if state[index][0] and state[index][1] and state[index][2] and state[index][3]:
            if playerTurn:
                state[index][5]=0
                score[0]=score[0]+state[index][4]

            else:
                state[index][5]=1
                score[1]=score[1]+state[index][4]
                
#function to display the state of the game board
    def displayBoard(self):
        n=self.col
        #nifty one-liner for splitting a list into sublists of length n, here the boxes in each row
        lines= [self.state[i * n:(i + 1) * n] for i in range((len(self.state) + n - 1) // n )]
        #list of strings constituting the board
        stringBoard=[]  
        #build string of column indices
        curLine=['    ']
        for col in range(0,self.col):
            curLine.append(' '+str(col))
        stringBoard.append(curLine)
        stringBoard.append('\n')
        rowNum =0
        #main string building loop
        for row in lines:
            curLine=['    *']
            #build string of the dots and the horizontal edges
            for box in row:
                if box[1]:
                    curLine.append('-*')
                else:
                    curLine.append(' *')
            stringBoard.append(curLine)
            curLine=[str(rowNum) +'   ']
            #build string of the boxes with row indices and box values as well as the vertical edges
            #values replaced with P for Player or C for Computer once a box has been claimed
            for box in row:
                if box[0]:
                    curLine.append('|')
                else:
                    curLine.append(' ')
                if box[5]==-1:
                    curLine.append(str(box[4]))
                elif box[5]==0:
                    curLine.append('P')
                else:
                    curLine.append('C')
            if row[self.col-1][2]:
                curLine.append('|')
            else:
                curLine.append(' ')
            stringBoard.append(curLine)
            rowNum+=1
        #build final horizontal row
        curLine=['    *']
        for box in lines[-1]:
            if box[3]:
                curLine.append('-*')
            else:
                curLine.append(' *')
        stringBoard.append(curLine)
        #and put it all together
        for line in stringBoard:
            print(''.join(line))

#boolean check if all moves have been exhausted
    def isFinished(self,moves):
        if len(moves)==0:
            return True
        else:
            return False

#takes player input and formats it as a valid move tuple, then makes move
    def playerMove(self,moves):
        
        print("Enter move as three ints - col row edge - separated by spaces.")
        print("For edge 0,1,2,3==left,top,right,bottom:")
        
        try:
            Move=tuple(map(int, input().split(" ")))
        except:
            print('Format invalid')
            self.playerMove(moves)
        else:
            try:
                if Move in moves:
                    self.makeMove(Move,self.state,self.moves,self.playerTurn,self.score)
                elif self.equivalent[Move] in moves:
                    self.makeMove(self.equivalent[Move],self.state,self.moves,self.playerTurn,self.score)
                else:
                    print('Move already made')
                    self.playerMove(moves)
            except:
                print('Invalid box or edge indices')
                self.playerMove(moves)
                

#calls the search function and executes the chosen move
    def AIMove(self,moves):
        cMove=self.AlphaBetaSearch(moves)
        self.makeMove(cMove,self.state,self.moves,self.playerTurn,self.score)
        print('AI made move: ',cMove)
        
        
#minmax search using alpha-beta pruning up to specified number of plies
    def AlphaBetaSearch(self,moves):
        bestMove=None
        bestVal=-1000
        beta=1000
        #extra loop consequence of implicit nodes
        #selects max among min values for all possible actions
        for action in moves:
            #suboptimal memory usage here and in max and min functions but I think that I would need
            #to completely rewrite how the state is represented and updated in order to improve it
            state=copy.deepcopy(self.state)
            moves=copy.deepcopy(self.moves)
            score=copy.deepcopy(self.score)
            pTurn=False
            self.makeMove(action,state,moves,pTurn,score)
            val=self.minValue(action,state,moves,not pTurn, score,bestVal,beta,1)
            if val>bestVal:
                bestVal=val
                bestMove=action
        return bestMove

#selects maximum value from set of minimized values among possible actions
    def maxValue(self,move,state,moves,playerTurn,score,alpha,beta,plies):
        if self.isFinished(moves) or plies==self.plies:
            return score[1]-score[0]
        v=-1000
        for action in moves:
            newState=copy.deepcopy(state)
            newMoves=copy.deepcopy(moves)
            newScore=copy.deepcopy(score)
            self.makeMove(action,newState,newMoves,playerTurn,newScore)
            bestMin=self.minValue(action,newState,newMoves,not playerTurn,newScore,alpha,beta,plies+1)
            v=max(v,bestMin)
            if v>=beta:
                return v
            alpha=max(alpha,v)
        return v

#selects minimum value from set of maximized values among possible actions
    def minValue(self,move,state,moves,playerTurn,score,alpha,beta,plies):
        if self.isFinished(moves) or plies==self.plies:
            return score[1]-score[0]
        v=1000
        for action in moves:
            newState=copy.deepcopy(state)
            newMoves=copy.deepcopy(moves)
            newScore=copy.deepcopy(score)
            self.makeMove(action,newState,newMoves,playerTurn,newScore)
            bestMax=self.maxValue(action,newState,newMoves,not playerTurn,newScore,alpha,beta,plies+1)
            v=min(v,bestMax)
            if v<=alpha:
                return v
            beta=min(beta,v)
        return v
#main
if True:
    #accept user input for game specifications
    col=int(input('Enter number of columns: '))
    row=int(input('Enter number of rows: '))
    ply=int(input('Enter depth of search in plies: '))
    #initialze game instance and display empty board
    game=dotsAndBoxes(row,col,ply)
    game.displayBoard()
    #Alternates turns beginning with the player until no valid moves remain
    while(not game.isFinished(game.moves)):
        game.playerMove(game.moves)
        print('Score: You - ',game.score[0],' AI - ',game.score[1])
        game.displayBoard()
        game.playerTurn= not game.playerTurn
        
        if not game.isFinished(game.moves):
            game.AIMove(game.moves)
            print('Score: You -',game.score[0],' AI -',game.score[1])
            game.displayBoard()
            game.playerTurn= not game.playerTurn
    #display results        
    if game.score[0]>game.score[1]:
        print('You win!')
    if game.score[0]==game.score[1]:
        print('It\'s a tie!')
    if game.score[0]<game.score[1]:
        print('You lose')
    print('Final Score: You - ',game.score[0],' AI - ',game.score[1])


            
            
            
            
        
        
        
                
    
        
        
