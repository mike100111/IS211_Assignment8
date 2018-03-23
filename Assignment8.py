import time
import random
import sys
import argparse

# Declare Class to represent a Player
class Player:

    # Initialize the player
    def __init__(self, playerName):        
        self.turnTotal = 0
        self.gameTotal = 0
        self.playerName = playerName

    # Get the players Name
    def getPlayerName(self):
        return str(self.playerName)

    #Gets the players Game Total
    def getGameTotal(self):
        return self.gameTotal

    # Returns the players turn total
    def getTurnTotal(self):
        return self.turnTotal

    # Updates the players turn total
    def updateTurnTotal(self, rollAmount):
        self.turnTotal += rollAmount

    #Ends the players turn. Accepts Boolean indicating whether the turn points shold be added to the players game total. Used when rolling a one
    def endTurn(self, keepPoints):
        if keepPoints == True:
            self.gameTotal += self.turnTotal
        self.turnTotal = 0
        if self.gameTotal >= 100:
            return True

    # Get the users Decision to roll or hold
    def getDecision(self, roll):        

        # Get users choince
        userInput = raw_input('You rolled a ' + str(roll)+ '. Your turn total is ' + str(self.turnTotal) + ', and your game total is ' + str(self.gameTotal) + '. Type r to roll again or h to hold -->')

        #Keep requesting a decision until a valid one is entered
        while userInput != 'h' and userInput != 'r':
           userInput = raw_input('Sorry, that was an invalid entry. Your game total is ' + str(self.gameTotal) + ', your turn total is ' + str(self.turnTotal) + ', and you rolled a ' + str(roll) + '. Type r to roll again or h to hold -->')

        return userInput

class ComputerPlayer(Player):

    def __init__(self, playerName):
        Player.__init__(self, playerName)

    def getDecision(self, roll):
        holdAmount = 100 - (self.gameTotal + self.turnTotal)
        if holdAmount > 25:
            holdAmount = 25

        if self.turnTotal > holdAmount:
            return 'h'
        else:
            return 'r'

class PlayerFactory(object):

    def createPlayer(self, playerType, playerName):
        if playerType == 'human':
            return Player('Human ' + playerName)
        elif playerType == 'computer':
            return ComputerPlayer('Computer ' + playerName)
        else:
            raise ValueError('An invalid Player Value was entered. Valid options are: "human" or "computer".')
                        

# Declare Class to represent the game Die
class Die:

    #Initialize the die to seed the random
    def __init__(self):
        random.seed(0)
    
    # Rolls the die
    def rollDie(self):
        roll = random.randint(1,6)        
        return roll

class Game:

    # Initialize Game and objects. Accepts player count
    def __init__(self):
        self.die = Die()
        self.players = []
        self.playerIndex = 0        

    # Returns the game die
    def getGameDie(self):
        return self.die

    # Returns the active player
    def getActivePlayer(self):
        return self.players[self.playerIndex]

    # Iterates to the next player. 
    def iteratePlayer(self):
        if self.playerIndex == len(self.players) - 1:
            self.playerIndex = 0
        else:
            self.playerIndex += 1

    # Iitializes players and prints startup message
    def startGame(self, player1Type, player2Type):
        factory = PlayerFactory()
        self.players.append(factory.createPlayer(player1Type, 'Player #1'))
        self.players.append(factory.createPlayer(player2Type, 'Player #2'))
        print 'Game starting...'
        print 'Player #1 is up:'
        
    # Method PlayGame runns the while loop calling the next turn
    def playGame(self):
        while True :

           self.nextTurn()
           
    # Abstract turn to separate function so while loop can be in playGame method to be overriden in timeProxy
    def nextTurn(self):
         # Roll the die
            roll = self.getGameDie().rollDie()            

            # If player rolled a 1
            if roll == 1:
                # End the players turn with out adding turn points
                self.getActivePlayer().endTurn(False)
                # Move to the next player
                self.iteratePlayer()
                # Print message
                print '\nUh Oh!! You rolled a 1 and lost all your turns points. \n\n'+ self.getActivePlayer().getPlayerName() + ' is up!\n'        

            # Else player rolled a valid number
            else:
                # Update the active players turn total
                self.getActivePlayer().updateTurnTotal(roll)
                # Get a decision from the active player
                decision = self.getActivePlayer().getDecision(roll)

                # If player decided to hold
                if decision == 'h':

                    #print points earned this turn
                    print '\nSmart choice!! You scored '+ str(self.getActivePlayer().getTurnTotal())+' points this turn. Your points have been added to your game total!'

                    # End Players Turn and check if they won
                    if self.getActivePlayer().endTurn(True) == True:
                        # Print game won message
                        print '\n\nGame Over!! ' + self.getActivePlayer().getPlayerName() +' won with a score of ' + str(self.getActivePlayer().getGameTotal())
                        # Exit Program
                        sys.exit()
                
                    # Print new game total
                    print 'Your new game total is ' + str(self.getActivePlayer().getGameTotal()) + '.\n'

                    #Switch the player
                    self.iteratePlayer()
                    # Print next players name
                    print self.getActivePlayer().getPlayerName() + ' is up!\n'

            
class TimedGameProxy():
    
    def __init__(self, timed):        
        self.timeStart = time.time()
        self.__game = Game()
        self.timed = timed
        
    def __getattr__(self, name):        
        return getattr(self.__game, name)

    #Override PlayGame to check for time up every roll
    def playGame(self):

          while True:
              
              # If time is up              
              if self.timed == True and time.time() - self.timeStart >= 60:
                    # Find winner by highest point
                    winner = self.getWinner()
                    print '\n\nGame Over!! Time ran out!! ' + winner[0] +' won with a score of ' + str(winner[1])
                    # Exit Program
                    sys.exit()
                    
              else:
                  self.__game.nextTurn()

    def getWinner(self):
        highScore = 0
        for i  in range(0, len(self.players)):
            if self.players[i].getGameTotal() > highScore:
                highScore = self.players[i].getGameTotal()

        return (self.players[i].getPlayerName(), highScore)
   
def main():

    # Add Num Players argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--player1", help="The type of player. enter 'human' or 'computer'.")
    parser.add_argument("--player2", help="The type of player. enter 'human' or 'computer'.")
    parser.add_argument("--timed", help="Indicates whether the game should be timed or not.")
    args = parser.parse_args()

    # Start Game
    game = TimedGameProxy(args.timed)
    game.startGame(args.player1, args.player2)
    game.playGame()

main()
