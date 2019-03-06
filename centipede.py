from tkinter import *
import threading, time, itertools, random

class TempEntity:

    def __init__(this, x, y):
        this.x= x
        this.y= y

class Entity:

    @classmethod
    def canUpdate(cls):
        return game.frames % (11 - cls.SPEED ) == 0


    def __init__(this, x, y, **options):
        this.__x, this.__y= x, y

        x, y= Game.toScreen((x, y))
        coords= (x, y, x + Game.ENTITY_LENGTH, y + Game.ENTITY_LENGTH)

        this.__id= game.canvas.create_rectangle(coords, options)

    def __eq__(this, other):
        if this.x == other.x and this.y == other.y:
            return True
        return False

    @property
    def id(this):
        return this.__id

    @property
    def x(this):
        return this.__x

    @property
    def y(this):
        return this.__y

    @property
    def coords(this):
        return this.x, this.y

    @coords.setter
    def coords(this, xy):
        this.__x, this.__y= xy
        x, y= Game.toScreen(xy)
        game.canvas.coords(this.__id, x, y, x + Game.ENTITY_LENGTH, y + Game.ENTITY_LENGTH)

    def update(this):
        if this.SPEED > 0 and this.canUpdate():
            this._update()

    def die(this):
        game.canvas.delete(this.__id)

class Rock(Entity):

    SPEED = 0

    def __init__(this, x, y):
        super().__init__(x= x, y= y, fill= "red")
        this.__health= 4

    def fix(this):
        this.__health= 4

    def collide(this):
        this.__health-= 1

        if this.__health == 3:
            game.canvas.itemconfig(this.id, fill= "#C00000")
        elif this.__health == 2:
            game.canvas.itemconfig(this.id, fill= "#800000")
        elif this.__health == 1:
            game.canvas.itemconfig(this.id, fill= "#400000")
        else:
            this.die()

    def die(this):
        super().die()
        game.removeRock(this)

class AggressiveEntity(Entity):

    def update(this):
        super().update()

        if this == game.player:
            game.player.die()

    def collide(this):
        this.die()

class Centipede(AggressiveEntity):

    SPEED= 5

    def __init__(this, x, y):
        super().__init__(x= x, y= y, fill= "green")
        this.__movingRight= True
        this.__movingDown= True

    def _update(this):

        next= TempEntity(this.x, this.y)
        if this.__movingRight:
            next.x+= 1
        else:
            next.x-= 1

        if next in game.rocks or next.x == -1 or next. x == Game.SIZE:
            next.x= this.x
            if this.__movingDown:
                next.y+= 1
                if next.y + 1 == Game.SIZE:
                    this.__movingDown= False
            else:
                next.y-= 1
                if next.y - 1 == Game.SIZE - 10:
                    this.__movingDown= True
            this.__movingRight= not this.__movingRight

        this.coords= next.x, next.y

    def die(this):
        super().die()
        game.removeCentipede(this)
        game.addRock(Rock(this.x, this.y))

class Spider(AggressiveEntity):
    
    SPEED= 5

    def __init__(this):
        super().__init__(x= -1, y= -1, fill= "yellow")

        this.__isDead= True
        this.__moveRight= False
        this.__direction= 0
        this.__steps= 0

    @property
    def isDead(this):
        return this.__isDead

    def _update(this):
        
        if not this.__isDead:
            
            next= TempEntity(this.x, this.y)

            if this.__direction <= 1:
               next.y-= 1
            else:
                next.y+= 1

            if this.__direction == 1 or this.__direction == 2:
                if this.__moveRight == True:
                    next.x+= 1
                else:
                    next.x-= 1

            if next.x == -1 or next.x == Game.SIZE:
                this.die()
                return

            if next in game.rocks:
                game.rocks[game.rocks.index(next)].die()

            this.coords= next.x, next.y

            this.__steps-= 1
            if this.__steps == 0:
                this.__direction= random.randrange(4)
                this.__steps= random.randrange(10) + 1

    def resurrect(this):
        this.__steps= random.randrange(16) + 1
        this.__isDead= False
        this.__moveRight= not this.__moveRight

        if this.__moveRight:
            this.coords= -1, game.SIZE - 10
        else:
            this.coords= game.SIZE, game.SIZE - 10

        this.__direction= 2

    def die(this):
        this.__isDead= True
        this.coords= - 1, -1

class RockThrower(AggressiveEntity):

    SPEED= 5

    def __init__(this):
        super().__init__(-1, - 1, fill= "orange")
        this.__isDead= True

    @property
    def isDead(this):
        return this.__isDead

    def _update(this):

        if not this.__isDead:

            this.coords= this.x, this.y + 1

            if this.y == Game.SIZE:
                this.die()
                return

            if not this in game.rocks:

                if random.randrange(7) == 0:
                    game.addRock(Rock(this.x, this.y))

    def resurrect(this):
        
        this.coords= random.randrange(Game.SIZE), -1
        this.__isDead= False

    def die(this):
        this.coords= - 1, -1
        this.__isDead= True

class Bullet(Entity):

    SPEED= 9

    def __init__(this):
        super().__init__(x= -1, y= -1, fill= "white")
        
        this.__isDead= True

    def _update(this):
        
        if not this.isDead:

            next= TempEntity(this.x, this.y - 1)

            this.coords= next.x, next.y

            if next in game.enemies:
                game.enemies[game.enemies.index(next)].collide()
                this.__isDead= True

            if this.y < 0:
                this.__isDead= True

            if this.isDead:
                this.die()

    @property
    def isDead(this):
        return this.__isDead

    def fire(this):
        this.__isDead= False

    def die(this):
        this.coords= -1, -1

class Player(Entity):

    SPEED= 6

    def __init__(this, x, y):
        super().__init__(x= x, y= y, fill= "blue")

        this.moveLeft= False
        this.moveRight= False
        this.moveUp= False
        this.moveDown= False
        this.fireBullet= False
        this.__isDead= False

    @property
    def isDead(this):
        return this.__isDead

    def _update(this):
        
        if this.fireBullet and game.bullet.isDead:
            game.bullet.coords= this.x, this.y
            game.bullet.fire()

        next= TempEntity(this.x, this.y)
        
        if this.moveLeft:
            next.x-= 1
        elif this.moveRight:
            next.x+= 1

        if this.moveUp:
            next.y-= 1
        elif this.moveDown:
            next.y+= 1

        if not (next in game.rocks or next.y == Game.SIZE or next.y == Game.SIZE - 10 or next.x == Game.SIZE or next.x == -1):
            this.coords= next.x, next.y

    def die(this):
        this.__isDead= True
    

class Game:

    SIZE= 32
    SCREEN_HEIGHT= 800
    ENTITY_LENGTH= SCREEN_HEIGHT / SIZE

    @staticmethod
    def toScreen(coords):
        x, y= coords
        return x * Game.ENTITY_LENGTH, y * Game.ENTITY_LENGTH

    def __init__(this):

        this.__player= None
        this.__spider= None
        this.__rockThrower= None
        this.__bullet= None
        this.__enemies= []
        this.__rocks= []
        this.__centipedes= []

        this.__master= Tk()
        this.__master.title("Centipede")

        this.__canvas= Canvas(this.__master, width= Game.SCREEN_HEIGHT, height= Game.SCREEN_HEIGHT, bg= "black")
        this.__canvas.pack()

        this.__setKeyBindings()

        this.frames= 0

    def start(this):
        threading.Thread(target= this.__mainloop, daemon= True).start()
        this.__master.mainloop()

    @property
    def canvas(this):
        return this.__canvas

    @property
    def rocks(this):
        return this.__rocks

    @property
    def centipedes(this):
        return this.__centipedes

    @property
    def enemies(this):
        return this.__enemies

    @property
    def spider(this):
        return this.__spider

    @property
    def rockThrower(this):
        return this.__rockThrower

    @property
    def bullet(this):
        return this.__bullet

    @property
    def player(this):
        return this.__player

    def addRock(this, rock):
        this.rocks.append(rock)
        this.enemies.append(rock)

    def addCentipede(this, centipede):
        this.centipedes.append(centipede)
        this.enemies.append(centipede)

    def removeRock(this, rock):
        this.rocks.remove(rock)
        this.enemies.remove(rock)

    def removeCentipede(this, centipede):
        this.centipedes.remove(centipede)
        this.enemies.remove(centipede)

    def __mainloop(this):
        this.__player= Player(Game.SIZE / 2, Game.SIZE - 3)
        this.__bullet= Bullet()
        this.__spider= Spider()
        this.__rockThrower= RockThrower()
        this.enemies.append(this.spider)
        this.enemies.append(this.rockThrower)

        for i in range(50):
            rock= Rock(random.randrange(0, Game.SIZE), random.randrange(3, Game.SIZE - 1))
            while rock in this.enemies or rock == this.__player:
                rock.coords= random.randrange(0, Game.SIZE), random.randrange(3, Game.SIZE - 1)
            this.addRock(rock)

        for level in itertools.count(1):
            numCentipedes= 10
            playing= True
            this.spider.resurrect()
            while playing and not this.player.isDead:
                if numCentipedes > 0 and Centipede.canUpdate():
                    this.addCentipede(Centipede(Game.SIZE / 2, 0))
                    numCentipedes-= 1
                this.player.update()
                this.bullet.update()
                
                if this.frames % 500 == 0 and this.spider.isDead:
                    this.spider.resurrect()

                if level > 1 and this.frames % 1000 == 0 and this.rockThrower.isDead:
                    this.rockThrower.resurrect()

                for enemy in this.enemies:
                    enemy.update()

                if not this.centipedes:
                    playing= False

                this.frames+= 1

                if this.frames > 10000:
                    this.frames= 0

                time.sleep(0.01)

            if this.player.isDead:
                this.canvas.create_text(Game.SCREEN_HEIGHT / 2, Game.SCREEN_HEIGHT / 2, text= "Game Over! You made it past " + str(level - 1) + " levels!", fill= "white")
                break

    def setMoveLeft(this, moveLeft):
        this.player.moveLeft= moveLeft

    def setMoveRight(this, moveRight):
        this.player.moveRight= moveRight

    def setMoveUp(this, moveUp):
        this.player.moveUp= moveUp

    def setMoveDown(this, moveDown):
        this.player.moveDown= moveDown

    def setFireBullet(this, fireBullet):
        this.player.fireBullet= fireBullet

    def __setKeyBindings(this):

        this.__master.bind("<Left>", lambda e: this.setMoveLeft(True))
        this.__master.bind("a", lambda e: this.setMoveLeft(True))
        this.__master.bind("<KeyRelease-Left>", lambda e: this.setMoveLeft(False))
        this.__master.bind("<KeyRelease-a>", lambda e: this.setMoveLeft(False))

        this.__master.bind("<Right>", lambda e: this.setMoveRight(True))
        this.__master.bind("d", lambda e: this.setMoveRight(True))
        this.__master.bind("<KeyRelease-Right>", lambda e: this.setMoveRight(False))
        this.__master.bind("<KeyRelease-d>", lambda e: this.setMoveRight(False))

        this.__master.bind("<Down>", lambda e: this.setMoveDown(True))
        this.__master.bind("s", lambda e: this.setMoveDown(True))
        this.__master.bind("<KeyRelease-Down>", lambda e: this.setMoveDown(False))
        this.__master.bind("<KeyRelease-s>", lambda e: this.setMoveDown(False))

        this.__master.bind("<Up>", lambda e: this.setMoveUp(True))
        this.__master.bind("w", lambda e: this.setMoveUp(True))
        this.__master.bind("<KeyRelease-Up>", lambda e: this.setMoveUp(False))
        this.__master.bind("<KeyRelease-w>", lambda e: this.setMoveUp(False))

        this.__master.bind("<space>", lambda e: this.setFireBullet(True))
        this.__master.bind("<KeyRelease-space>", lambda e: this.setFireBullet(False))

if __name__ == "__main__":
    global game
    game= Game()
    game.start()