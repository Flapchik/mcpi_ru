import os
import math

from functools import singledispatchmethod

from connection import Connection
from vec3 import Vec3
from event import BlockEvent, ChatEvent, ProjectileEvent
from util import flatten

""" Minecraft PI low level api v0.1_1

    Note: many methods have the parameter *arg. This solution makes it
    simple to allow different types, and variable number of arguments.
    The actual magic is a mix of flatten_parameters() and __iter__. Example:
    A Cube class could implement __iter__ to work in Minecraft.setBlocks(c, id).

    (Because of this, it's possible to "erase" arguments. CmdPlayer removes
     entityId, by injecting [] that flattens to nothing)

    @author: Aron Nieminen, Mojang AB"""

""" Updated to include functionality provided by RaspberryJuice:
- getBlocks()
- getDirection()
- getPitch()
- getRotation()
- getPlayerEntityId()
- pollChatPosts()
- setSign()
- spawnEntity()"""


def int_floor(*args):
    return [int(math.floor(x)) for x in flatten(args)]


class CmdPositioner:
    """Методы для получения и изменения позиции"""

    def __init__(self, connection, packagePrefix):
        self.conn = connection
        self.pkg = packagePrefix

    def getPos(self, id: int) -> Vec3:
        """Получить позицию сущности (entityId:int) => Vec3"""
        s = self.conn.send_receive(self.pkg + b".getPos", id)
        return Vec3(*list(map(float, s.split(","))))

    def setPos(self, id: int, *args):
        """Изменить позицию сущности (entityId:int, x,y,z)"""
        self.conn.send(self.pkg + b".setPos", id, args)

    def getTilePos(self, id) -> Vec3:
        """Получить положение блока, на котором стоит сущность (entityId:int) => Vec3"""
        s = self.conn.send_receive(self.pkg + b".getTile", id)
        return Vec3(*list(map(int, s.split(","))))

    def setTilePos(self, id, *args):
        """Изменить положение блока, на котором стоит сущность (entityId:int) => Vec3"""
        self.conn.send(self.pkg + b".setTile", id, int_floor(*args))

    def setDirection(self, id, *args):
        """Изменить направление сущности (entityId:int, x,y,z)"""
        self.conn.send(self.pkg + b".setDirection", id, args)

    def getDirection(self, id) -> Vec3:
        """Получить направление сущности (entityId:int) => Vec3"""
        s = self.conn.send_receive(self.pkg + b".getDirection", id)
        return Vec3(*map(float, s.split(",")))

    def setRotation(self, id, yaw):
        """Изменить поворот сущности (entityId:int, yaw)"""
        self.conn.send(self.pkg + b".setRotation", id, yaw)

    def getRotation(self, id) -> Vec3:
        """Получить поворот сущности (entityId:int) => float"""
        return float(self.conn.send_receive(self.pkg + b".getRotation", id))

    def setPitch(self, id, pitch):
        """Set entity pitch (entityId:int, pitch)"""
        self.conn.send(self.pkg + b".setPitch", id, pitch)

    def getPitch(self, id) -> float:
        """get entity pitch (entityId:int) => float"""
        return float(self.conn.send_receive(self.pkg + b".getPitch", id))

    def setting(self, setting, status):
        """Изменить настройки игрока (setting, status). keys: autojump"""
        self.conn.send(self.pkg + b".setting", setting, 1 if bool(status) else 0)


class CmdEntity(CmdPositioner):
    """Методы для сущностей"""

    def __init__(self, connection):
        CmdPositioner.__init__(self, connection, b"entity")

    def getName(self, id) -> str:
        """Получить список имен игроков, используя ID => [name:str]
        
        Можно использовать для поиска имени сущности, если сущность не является игроком."""
        return self.conn.send_receive(b"entity.getName", id)

    def remove(self, id):
        self.conn.send(b"entity.remove", id)


class Entity:
    def __init__(self, conn, entity_uuid, typeName):
        self.p = CmdPositioner(conn, b"entity")
        self.id = entity_uuid
        self.type = typeName

    def getPos(self) -> Vec3:
        return self.p.getPos(self.id)

    def setPos(self, *args):
        return self.p.setPos(self.id, args)

    def getTilePos(self) -> Vec3:
        return self.p.getTilePos(self.id)

    def setTilePos(self, *args):
        return self.p.setTilePos(self.id, args)

    def setDirection(self, *args):
        return self.p.setDirection(self.id, args)

    def getDirection(self) -> Vec3:
        return self.p.getDirection(self.id)

    def setRotation(self, yaw):
        return self.p.setRotation(self.id, yaw)

    def getRotation(self) -> Vec3:
        return self.p.getRotation(self.id)

    def setPitch(self, pitch):
        return self.p.setPitch(self.id, pitch)

    def getPitch(self):
        return self.p.getPitch(self.id)

    def remove(self):
        self.p.conn.send(b"entity.remove", self.id)


class CmdPlayer(CmdPositioner):
    """Methods for the host (Raspberry Pi) player"""

    def __init__(self, connection):
        CmdPositioner.__init__(self, connection, b"player")
        self.conn = connection

    def getPos(self) -> Vec3:
        return CmdPositioner.getPos(self, [])

    @singledispatchmethod
    def setPos(self, *args):
        return CmdPositioner.setPos(self, [], args)

    @setPos.register(int, int, int)
    def _(self, x, y, z):
        return CmdPositioner.setPos(self, [], [x, y, z])

    @setPos.register(float, float, float)
    def _(self, x, y, z):
        return CmdPositioner.setPos(self, [], [x, y, z])

    @setPos.register(Vec3)
    def _(self, position):
        return CmdPositioner.setPos(self, [], position)

    def getTilePos(self):
        return CmdPositioner.getTilePos(self, [])

    def setTilePos(self, *args):
        return CmdPositioner.setTilePos(self, [], args)

    def setDirection(self, *args):
        return CmdPositioner.setDirection(self, [], args)

    def getDirection(self) -> Vec3:
        return CmdPositioner.getDirection(self, [])

    def setRotation(self, yaw):
        return CmdPositioner.setRotation(self, [], yaw)

    def getRotation(self) -> Vec3:
        return CmdPositioner.getRotation(self, [])

    def setPitch(self, pitch):
        return CmdPositioner.setPitch(self, [], pitch)

    def getPitch(self) -> Vec3:
        return CmdPositioner.getPitch(self, [])


class CmdCamera:
    def __init__(self, connection):
        self.conn = connection

    def setNormal(self, *args):
        """Set camera mode to normal Minecraft view ([entityId])"""
        self.conn.send(b"camera.mode.setNormal", args)

    def setFixed(self):
        """Set camera mode to fixed view"""
        self.conn.send(b"camera.mode.setFixed")

    def setFollow(self, *args):
        """Set camera mode to follow an entity ([entityId])"""
        self.conn.send(b"camera.mode.setFollow", args)

    def setPos(self, *args):
        """Set camera entity position (x,y,z)"""
        self.conn.send(b"camera.setPos", args)


class CmdEvents:
    """События"""

    def __init__(self, connection):
        self.conn = connection

    def clearAll(self):
        """Очистить список старых событий"""
        self.conn.send(b"events.clear")

    def pollBlockHits(self) -> list:
        """При ударе мечом => [BlockEvent]"""
        s = self.conn.send_receive(b"events.block.hits")
        events = [e for e in s.split("|") if e]
        return [BlockEvent.Hit(*e.split(",")) for e in events]

    def pollChatPosts(self) -> list:
        """При использовании чата => [ChatEvent]"""
        s = self.conn.send_receive(b"events.chat.posts")
        events = [e for e in s.split("|") if e]
        return [ChatEvent.Post(int(e[:e.find(",")]), e[e.find(",") + 1:]) for e in events]

    def pollProjectileHits(self) -> list:
        """При использовании снарядов => [BlockEvent]"""
        s = self.conn.send_receive(b"events.projectile.hits")
        events = [e for e in s.split("|") if e]
        return [ProjectileEvent.Hit(*e.split(",")) for e in events]


class Minecraft:
    """The main class to interact with a running instance of Minecraft Pi."""

    def __init__(self, connection):
        self.conn = connection

        self.camera = CmdCamera(connection)
        self.entity = CmdEntity(connection)
        self.player = CmdPlayer(connection)
        self.events = CmdEvents(connection)

    def getBlock(self, *args) -> int:
        """Получить блок (x,y,z) => id:int"""
        return self.conn.send_receive(b"world.getBlock", int_floor(args))

    def getBlockWithData(self, *args):
        """Получить блок с параметрами (x,y,z) => Block"""
        return self.conn.send_receive(b"world.getBlockWithData", int_floor(args)).split(",")

    def getBlocks(self, *args):
        """Получить блоки в координатах (x0,y0,z0,x1,y1,z1) => [id:int]"""
        # s = self.conn.sendReceive(b"world.getBlocks", intFloor(args))
        s = self.conn.send_receive(b"world.getBlocks", *args)
        return s.split(",")

    def setBlock(self, *args):
        """Изменить блок (x,y,z,nameOfBlock,[data])"""
        self.conn.send(b"world.setBlock", *args)

    def setBlocks(self, *args):
        """Изменить блоки в координатах (x0,y0,z0,x1,y1,z1,nameOfBlock,[data])"""
        self.conn.send(b"world.setBlocks", *args)

    def setSign(self, *args):
        """Установить табличку 
        (x, y, z, sign_type, направление, линия1, линия2, линия3, линия4)
        направление: 0-север, 1-восток, 2-юг 3-запад
        """
        self.conn.send(b"world.setSign", *args)

    def spawnEntity(self, *args):
        """Создать сущность (x,y,z,id,[data])"""
        return Entity(self.conn, self.conn.send_receive(b"world.spawnEntity", *args), args[3])

    def spawnParticle(self, *args):
        """Сущность частицу (x,y,z,id,[data])"""
        return self.conn.send(b"world.spawnParticle", *args)

    def getNearbyEntities(self, *args) -> list:
        """Получить сущности поблизости (x,y,z)"""
        entities = []
        for i in self.conn.send_receive(b"world.getNearbyEntities", *args).split(","):
            name, eid = i.split(":")
            entities.append(Entity(self.conn, eid, name))
        return entities

    def removeEntity(self, *args):
        """Удалить сущность (x,y,z,id,[data])"""
        return self.conn.send_receive(b"world.removeEntity", *args)

    def getHeight(self, *args) -> int:
        """Получить самый высокостоящий блок (x,z) => int"""
        return int(self.conn.send_receive(b"world.getHeight", int_floor(args)))

    def getPlayerEntityIds(self):
        """Получить ID игроков, находящихся в игре => [id:int]"""
        ids = self.conn.send_receive(b"world.getPlayerIds")
        return ids.split("|")

    def getPlayerEntityId(self, name) -> int:
        """Получить ID игрока, используя его ник => [id:int]"""
        return self.conn.send_receive(b"world.getPlayerId", name)

    def saveCheckpoint(self):
        """Сохранить мир, чтобы затем его восстановить"""
        self.conn.send(b"world.checkpoint.save")

    def restoreCheckpoint(self):
        """Восстановить мир до точки восстановления"""
        self.conn.send(b"world.checkpoint.restore")

    def postToChat(self, msg):
        """Написать сообщение в чате"""
        self.conn.send(b"chat.post", msg)

    def setting(self, setting, status):
        """Изменить настройки мира (setting, status). keys: world_immutable, nametags_visible"""
        self.conn.send(b"world.setting", setting, 1 if bool(status) else 0)

    def setPlayer(self, name) -> bool:
        """Указать игрока, с которым будет происходить работу
        Вернет True, если игрок найден. False, если не найден
        """
        return self.conn.send_receive(b"setPlayer", name)

    @staticmethod
    def create(address="localhost", port=4711, debug=False):
        """Создать подключение к серверу."""
        if "JRP_API_HOST" in os.environ:
            address = os.environ["JRP_API_HOST"]
        if "JRP_API_PORT" in os.environ:
            try:
                port = int(os.environ["JRP_API_PORT"])
            except ValueError:
                pass
        return Minecraft(Connection(address, port, debug))


def mcpy(func):
    # these will be created as global variable in module, so not good idea
    # func.__globals__['mc'] = Minecraft.create()
    # func.__globals__['pos'] = func.__globals__['mc'].player.getTilePos()
    # func.__globals__['direction'] = func.__globals__['mc'].player.getDirection()
    func.__doc__ = ("_mcpy :" + func.__doc__) if func.__doc__ else "_mcpy "
    return func


if __name__ == "__main__":
    mc = Minecraft.create()
    mc.postToChat("Hello, Minecraft!")
