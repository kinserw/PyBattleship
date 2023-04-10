# need to expand classes to keep track of labels for each object so that I don't have to maintain multiple lists and risk getting them out of synch. 

import tkinter as tk
import time # needed for the wait in the main
import random # needed for ship generation (makeShips)
from typing import Dict 
from datetime import datetime # used as an ID for moveable objects

# The current date and time is 2022-07-12 10:22:00.776664
#
# This is an ad hoc effort to learn Python. It is not pretty 
# because I am still figuring out what is available. So,
# ignore the global variables and incorrect data structure 
# choices. I will fix this as I evolve my understanding of the
# language.

window = tk.Tk()
maxWidth=500
maxHeight=500

class Point: 
  def __init__(self, coord1:int,coord2:int):
    self.x = coord1
    self.y = coord2

  def __str__(self):
    return f"({self.x},{self.y})"

    
    
exitProgram=False
numberOfShips=0
maxShips=10
numberOfMissiles=0
maxMissiles=5
missileWidth=15
missileHeight=21
shipWidth=26
shipHeight=21
numberOfExplosions=0
currentScore=0
ships=[]      # array of Moveable
missiles=[]   # array of Moveable
explosions=dict() # Point.__str__ and stage
displayedItems=dict()
missileLabels=[]     # array of displayed labels; TODO replace with images
shipLabels=[]        # array of displayed labels; TODO replace with images
explosionStages=[]   # array of text based explosion images
explosions =[]         # array of Moveable
    
class Moveable:
    def __init__(self,x,y):
        self.coord = Point(x,y)
        self.direction=Point(0,0) # 0=no direction, 1=positive direction, -1=negative direction
        self.speed = Point(0,0) #0=no speed, >0=forward, <0=backward
        self.ID=datetime.now()

        
    def move(self):
        self.coord.x=self.coord.x+self.direction.x*self.speed.x
        self.coord.y=self.coord.y+self.direction.y*self.speed.y
        
    def __str__(self):
        return f"({self.coord} with {self.direction} direction at {self.speed} speed)"

        
        
frame = tk.Frame(master=window, width=maxWidth, height=maxHeight)
frame.pack()

# create list of labels for both missiles and ships
# each time a new missile/ship is created, it is associated
# with a label. When the missile/ship goes away (off the screen
# or due to collision), the label needs to be removed from the 
# label list and added to the end to prevent new missiles/ships
# from being associated with a label already in use 
# An alternative solution is to create a method to return 
# the next available label (one that is in the label list but
# not in the displayedItems dictionary) BUT you would need to know if it is a missile or a ship .
for i in range(maxMissiles):
    missileLabels.insert(i, tk.Label(master=frame, text="^", bg="blue"))

for i in range(maxShips):
    shipLabels.insert(i, tk.Label(master=frame, text="\__/", bg="green"))

explosionStages.append("()")
explosionStages.append("<#>")
explosionStages.append("{ }")


def moveThings() :
    for missile in missiles:
        missile.move()
        
        #remove missile if goes off screen
        if (missile.coord.y < (0-2*missileHeight)):
            removeMissile(missile)

    for ship in ships:
        ship.move()
        
        # remove ship if goes off screen
        if ((ship.coord.x < (0-shipWidth)) or (ship.coord.x > maxWidth+shipWidth)):
            removeShip(ship)
            
    for explosion in explosions :
        explosion.speed.x = explosion.speed.x + 1
        if (explosion.speed.x >= len(explosionStages)):
            removeExplosion(explosion)

def removeMissile(missile : Moveable):
    missiles.remove(missile) #remove from list of active missiles
    
    #When the missile/ship goes away (off the screen
    # or due to collision), the label needs to be 
    # removed from the label list and added to the 
    # end to prevent new missiles/ships
    # from being associated with a label already in use
    label:tk.Label = missileLabels.pop(0) # always the first one since they travel as uniform constant speed
    missileLabels.append(label)  # move it to the end of list
    label.place(x=-60,y=-60) #move label off screen to "hide" it
    displayedItems.pop(missile.ID)
    
    del missile
    
def removeShip(ship : Moveable) :
    ships.remove(ship) # remove from active ships list

    #make label available to next ship by moving to end of list
    label:tk.Label = displayedItems.get(ship.ID)
    shipLabels.remove(label)
    shipLabels.append(label)
    label.place(x=-60,y=-60) #move label off screen to "hide" it
    
    displayedItems.pop(ship.ID)
    
    del ship

def removeExplosion(explosion : Moveable):
    explosions.remove(explosion)
    eLabel:tk.Label = displayedItems.get(explosion.ID)
    displayedItems.pop(explosion.ID)
    
    del eLabel
    
    del explosion
            
def detectCollisions() :
    # iterate over the ships
    # a ship can only be hit if it is in the middle of the screen
    # since all missiles go straight up
    
    for ship in ships:
        leadingEdge = ship.coord.x+shipWidth
        trailingEdge = ship.coord.x
        
        if ((leadingEdge > ((maxWidth/2)-missileWidth)) and
             (trailingEdge < ((maxWidth/2)+missileWidth))):
             # we have a possible collision
             # now check if a missile is at same height as ship
             for missile in missiles:
                leadingEdge = missile.coord.y-missileHeight
                trailingEdge = missile.coord.y
                
                if ((leadingEdge < (ship.coord.y)) and
                    (trailingEdge > (ship.coord.y-shipHeight))):
                    #BOOM
                    # createExplosion (do before removing ship/missile)
                    explosion = Moveable(missile.coord.x,missile.coord.y)
                    explosion.direction = 0 #stationary
                    explosion.speed.x = 0
                    explosions.append(explosion)
                    newLabel = tk.Label(master=frame, text=explosionStages[0], bg="red")
                    newLabel.place(x=missile.coord.x, y=missile.coord.y)
                    displayedItems.update({explosion.ID : newLabel})
                    print ("explosion id " , explosion.ID)
                    print ("ship id ", ship.ID)
                    
                    # remove ship and missile
                    removeShip(ship)
                    removeMissile(missile)

def makeMissile() :
    if len(missiles) < maxMissiles:
        newMissile= Moveable(maxWidth/2,maxHeight)
        newMissile.direction.y=-1
        newMissile.speed.y=15
        missiles.append(newMissile)
        displayedItems.update({newMissile.ID : missileLabels[len(missiles)-1]})

def makeShips() :
    if len(ships) < maxShips:
        #if ships can be made only make them 15% of the time
        chance = random.randint(0,99)
        if (chance < 15):
            # pick a random direction (left or right)
            shipX = 0 #default to left
            if (random.randint(0,99) < 50) :
                shipX = maxWidth
                
            # pick row at random (only top half of screen)
            shipY = random.randint(0,maxHeight/2)
            
            newShip = Moveable(shipX,shipY)
            newShip.speed.x = random.randint(5,30)
            newShip.direction.x = (1 if shipX == 0 else -1)
            ships.append(newShip)
            displayedItems.update({newShip.ID : shipLabels[len(ships)-1]})
            

# capture keypress
# exit program if esc key is pressed
# attempt to fire a missile if spacebar pressed
def escape_press(event):
    exitProgram=True
    window.destroy()
    #TODO      display score

def space_press(event):
    makeMissile()


# Bind  event to event handlers
window.bind("<Escape>", escape_press)
window.bind("<space>", space_press)

def drawMissiles():
    for missile in missiles:
        dMissile:tk.Label = displayedItems.get(missile.ID) 
        dMissile.place(x=missile.coord.x, y=missile.coord.y)

def drawShips() :
    for ship in ships:
        dShip:tk.Label = displayedItems.get(ship.ID)
        # I shouldn't need this if statement but sometimes 
        # after a collision, the label entry for one of the 
        # ships is deleted but not removed from displayedItems
        if dShip: dShip.place(x=ship.coord.x, y=ship.coord.y)

def drawExplosions() :
    for explosion in explosions:
        dExplosion:tk.Label = displayedItems.get(explosion.ID)
        if (explosion.speed.x < len(explosionStages)):
            dExplosion.config(text= explosionStages[explosion.speed.x])
        

def main ():
    window.after(200,main)
    moveThings()
    makeShips()
    drawShips()
    drawMissiles()
    detectCollisions()
    drawExplosions()
    window.update()
    
main()
window.mainloop()
