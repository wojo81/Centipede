from tkinter import *
import threading, time, itertools, random

class TempEntity:

    def __init__(this, x, y):
        this.x= x
        this.y= y

class Entity:

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
        pass

    def die(this):
        game.canvas.delete(this.__id)

class Rock(Entity):

    def __init__(this, x, y):
        super().__init__(x, y, fill= "red")
        this.__health= 4

    def fix(this):
        this.__health= 4

    def collide(this):
        this.__health-= 1
        if this.__health == 0:
            this.die()

    def die(this):
        super().die()
        game.removeRock(this)

class Centipede(Entity):

    def __init__(this, x, y):
        super().__init__(x, y, fill= "green")
        this.__movingRight= True
        this.__movingDown= True

    def update(this):

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

        if this == game.player:
            game.player.die()

    def collide(this):
        this.die()

    def die(this):
        super().die()
        game.removeCentipede(this)
        game.addRock(Rock(this.x, this.y))

class Bullet(Entity):

    def __init__(this):
        super().__init__(-1, -1, fill= "white")
        this.__isDead= True

    def update(this):
        
        if not this.__isDead:

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
    def __init__(this, x, y):
        super().__init__(x, y, fill= "blue")

        this.moveLeft= False
        this.moveRight= False
        this.moveUp= False
        this.moveDown= False
        this.fireBullet= False
        this.__isDead= False

    @property
    def isDead(this):
        return this.__isDead

    def update(this):
        
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

    SIZE= 40
    SCREEN_HEIGHT= 800
    ENTITY_LENGTH= SCREEN_HEIGHT / SIZE

    @staticmethod
    def toScreen(coords):
        x, y= coords
        return x * Game.ENTITY_LENGTH, y * Game.ENTITY_LENGTH

    def __init__(this):

        this.__player= None
        this.__spider= None
        this.__bullet= None
        this.__enemies= []
        this.__rocks= []
        this.__centipedes= []

        this.__master= Tk()
        this.__master.title("Centipede")

        this.__canvas= Canvas(this.__master, width= Game.SCREEN_HEIGHT, height= Game.SCREEN_HEIGHT, bg= "black")
        this.__canvas.pack()

        this.__setKeyBindings()

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

        for i in range(50):
            rock= Rock(random.randrange(3, Game.SIZE), random.randrange(3, Game.SIZE - 3))
            while rock in this.enemies or rock == this.__player:
                rock.coords= random.randrange(3, Game.SIZE), random.randrange(3, Game.SIZE - 5)
            this.addRock(rock)

        for level in itertools.count():
            numCentipedes= 7
            playing= True
            while playing and not this.player.isDead:
                if numCentipedes > 0:
                    this.addCentipede(Centipede(Game.SIZE / 2, 0))
                    numCentipedes-= 1
                this.player.update()
                this.bullet.update()
                
                for enemy in this.enemies:
                    enemy.update()

                if not this.centipedes:
                    playing= False

                time.sleep(0.05)

            if this.player.isDead:
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