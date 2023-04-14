import os
import math
from typing import overload

from .connection import Connection
from .vec3 import Vec3
from .event import BlockEvent, ChatEvent, ProjectileEvent
from .util import flatten

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

    def __init__(self, connection, package_prefix):
        self.conn = connection
        self.pkg = package_prefix

    def get_pos(self, entity_id: int) -> Vec3:
        """Получить позицию сущности (entityId:int) => Vec3"""
        s = self.conn.send_receive(self.pkg + b".getPos", entity_id)
        return Vec3(*list(map(float, s.split(","))))

    def set_pos(self, entity_id: int, *args):
        """Изменить позицию сущности (entityId:int, x,y,z)"""
        self.conn.send(self.pkg + b".setPos", entity_id, args)

    def get_tile_pos(self, entity_id: int) -> Vec3:
        """Получить положение блока, на котором стоит сущность (entityId:int) => Vec3"""
        s = self.conn.send_receive(self.pkg + b".getTile", entity_id)
        return Vec3(*list(map(int, s.split(","))))

    def set_tile_pos(self, entity_id: int, *args):
        """Изменить положение блока, на котором стоит сущность (entityId:int) => Vec3"""
        self.conn.send(self.pkg + b".setTile", entity_id, int_floor(*args))

    def set_direction(self, entity_id: int, *args):
        """Изменить направление сущности (entityId:int, x,y,z)"""
        self.conn.send(self.pkg + b".setDirection", entity_id, args)

    def get_direction(self, entity_id: int) -> Vec3:
        """Получить направление сущности (entityId:int) => Vec3"""
        s = self.conn.send_receive(self.pkg + b".getDirection", entity_id)
        return Vec3(*map(float, s.split(",")))

    def set_rotation(self, entity_id: int, yaw):
        """Изменить угол поворота сущности (entityId:int, yaw)"""
        self.conn.send(self.pkg + b".setRotation", entity_id, yaw)

    def get_rotation(self, entity_id: int) -> float:
        """Получить угол поворота сущности (entityId:int) => float"""
        return float(self.conn.send_receive(self.pkg + b".getRotation", entity_id))

    def set_pitch(self, entity_id: int, pitch: int):
        """Изменить угол наклона сущности (entityId:int, pitch)"""
        self.conn.send(self.pkg + b".setPitch", entity_id, pitch)

    def get_pitch(self, entity_id: int) -> float:
        """Получить угол наклона сущности (entityId:int) => float"""
        return float(self.conn.send_receive(self.pkg + b".getPitch", entity_id))

    def setting(self, setting: str, status: bool):
        """Изменить настройки игрока (setting, status). keys: autojump"""
        self.conn.send(self.pkg + b".setting", setting, 1 if bool(status) else 0)


class CmdEntity(CmdPositioner):
    """Методы для сущностей"""

    def __init__(self, connection):
        CmdPositioner.__init__(self, connection, b"entity")

    def get_name(self, player_id: int) -> str:
        """Получить список имен игроков, используя ID => [name:str]
        
        Можно использовать для поиска имени сущности, если сущность не является игроком."""
        return self.conn.send_receive(b"entity.getName", player_id)

    def remove(self, player_id: int):
        self.conn.send(b"entity.remove", player_id)


class Entity:
    def __init__(self, conn, entity_uuid, type_name):
        self.p = CmdPositioner(conn, b"entity")
        self.id = entity_uuid
        self.type = type_name

    def get_pos(self) -> Vec3:
        return self.p.get_pos(self.id)

    def set_pos(self, *args):
        return self.p.set_pos(self.id, args)

    def get_tile_pos(self) -> Vec3:
        return self.p.get_tile_pos(self.id)

    def set_tile_pos(self, *args):
        return self.p.set_tile_pos(self.id, args)

    def set_direction(self, *args):
        return self.p.set_direction(self.id, args)

    def get_direction(self) -> Vec3:
        return self.p.get_direction(self.id)

    def set_rotation(self, yaw):
        return self.p.set_rotation(self.id, yaw)

    def get_rotation(self) -> float:
        return self.p.get_rotation(self.id)

    def set_pitch(self, pitch):
        return self.p.set_pitch(self.id, pitch)

    def get_pitch(self) -> float:
        return self.p.get_pitch(self.id)

    def remove(self):
        self.p.conn.send(b"entity.remove", self.id)


class CmdPlayer(CmdPositioner):
    """Methods for the host (Raspberry Pi) player"""

    def __init__(self, connection):
        CmdPositioner.__init__(self, connection, b"player")
        self.conn = connection

    def get_pos(self, **kwargs) -> Vec3:
        return CmdPositioner.get_pos(self, **kwargs)

    @overload
    def set_pos(self, x: float, y: float, z: float):
        """Изменить позицию сущности (x,y,z)"""
        return CmdPositioner.set_pos(self, [], [x, y, z])

    @overload
    def set_pos(self, position: Vec3):
        """Изменить позицию сущности (Vec3)"""
        return CmdPositioner.set_pos(self, [], position)

    def set_pos(self, *args):
        """Изменить позицию сущности (Vec3)"""
        return CmdPositioner.set_pos(self, [], args)

    def get_tile_pos(self):
        return CmdPositioner.get_tile_pos(self, [])

    def set_tile_pos(self, *args):
        return CmdPositioner.set_tile_pos(self, [], args)

    def set_direction(self, *args):
        return CmdPositioner.set_direction(self, [], args)

    def get_direction(self) -> Vec3:
        return CmdPositioner.get_direction(self, [])

    def set_rotation(self, yaw):
        return CmdPositioner.set_rotation(self, [], yaw)

    def get_rotation(self) -> Vec3:
        return CmdPositioner.get_rotation(self, [])

    def set_pitch(self, pitch):
        return CmdPositioner.set_pitch(self, [], pitch)

    def get_pitch(self) -> Vec3:
        return CmdPositioner.get_pitch(self, [])


class CmdCamera:
    def __init__(self, connection):
        self.conn = connection

    def set_normal(self, *args):
        """Set camera mode to normal Minecraft view ([entityId])"""
        self.conn.send(b"camera.mode.setNormal", args)

    def set_fixed(self):
        """Set camera mode to fixed view"""
        self.conn.send(b"camera.mode.setFixed")

    def set_follow(self, *args):
        """Set camera mode to follow an entity ([entityId])"""
        self.conn.send(b"camera.mode.setFollow", args)

    def set_pos(self, *args):
        """Set camera entity position (x,y,z)"""
        self.conn.send(b"camera.setPos", args)


class CmdEvents:
    """События"""

    def __init__(self, connection):
        self.conn = connection

    def clear_all(self):
        """Очистить список старых событий"""
        self.conn.send(b"events.clear")

    def poll_block_hits(self) -> list:
        """При ударе мечом => [BlockEvent]"""
        s = self.conn.send_receive(b"events.block.hits")
        events = [e for e in s.split("|") if e]
        return [BlockEvent.hit(*e.split(",")) for e in events]

    def poll_chat_posts(self) -> list:
        """При использовании чата => [ChatEvent]"""
        s = self.conn.send_receive(b"events.chat.posts")
        events = [e for e in s.split("|") if e]
        return [ChatEvent.post(int(e[:e.find(",")]), e[e.find(",") + 1:]) for e in events]

    def poll_projectile_hits(self) -> list:
        """При использовании снарядов => [BlockEvent]"""
        s = self.conn.send_receive(b"events.projectile.hits")
        events = [e for e in s.split("|") if e]
        return [ProjectileEvent.hit(*e.split(",")) for e in events]


class Minecraft:
    """The main class to interact with a running instance of Minecraft Pi."""

    def __init__(self, connection):
        self.conn = connection

        self.camera = CmdCamera(connection)
        self.entity = CmdEntity(connection)
        self.player = CmdPlayer(connection)
        self.events = CmdEvents(connection)

    def get_block(self, *args) -> int:
        """Получить блок (x,y,z) => id:int"""
        return self.conn.send_receive(b"world.getBlock", int_floor(args))

    def get_block_with_data(self, *args):
        """Получить блок с параметрами (x,y,z) => Block"""
        return self.conn.send_receive(b"world.getBlockWithData", int_floor(args)).split(",")

    def get_blocks(self, *args):
        """Получить блоки в координатах (x0,y0,z0,x1,y1,z1) => [id:int]"""
        # s = self.conn.sendReceive(b"world.getBlocks", intFloor(args))
        s = self.conn.send_receive(b"world.getBlocks", *args)
        return s.split(",")

    def set_block(self, *args):
        """Изменить блок (x,y,z,nameOfBlock,[data])"""
        self.conn.send(b"world.setBlock", *args)

    def set_blocks(self, *args):
        """Изменить блоки в координатах (x0,y0,z0,x1,y1,z1,nameOfBlock,[data])"""
        self.conn.send(b"world.setBlocks", *args)

    def set_sign(self, *args):
        """Установить табличку 
        (x, y, z, sign_type, направление, линия1, линия2, линия3, линия4)
        направление: 0-север, 1-восток, 2-юг 3-запад
        """
        self.conn.send(b"world.setSign", *args)

    def spawn_entity(self, *args):
        """Создать сущность (x,y,z,id,[data])"""
        return Entity(self.conn, self.conn.send_receive(b"world.spawnEntity", *args), args[3])

    def spawn_particle(self, *args):
        """Сущность частицу (x,y,z,id,[data])"""
        return self.conn.send(b"world.spawnParticle", *args)

    def get_nearby_entities(self, *args) -> list:
        """Получить сущности поблизости (x,y,z)"""
        entities = []
        for i in self.conn.send_receive(b"world.getNearbyEntities", *args).split(","):
            name, eid = i.split(":")
            entities.append(Entity(self.conn, eid, name))
        return entities

    def remove_entity(self, *args):
        """Удалить сущность (x,y,z,id,[data])"""
        return self.conn.send_receive(b"world.removeEntity", *args)

    def get_height(self, *args) -> int:
        """Получить самый высокостоящий блок (x,z) => int"""
        return int(self.conn.send_receive(b"world.getHeight", int_floor(args)))

    def get_player_entity_ids(self):
        """Получить ID игроков, находящихся в игре => [id:int]"""
        ids = self.conn.send_receive(b"world.getPlayerIds")
        return ids.split("|")

    def get_player_entity_id(self, name) -> int:
        """Получить ID игрока, используя его ник => [id:int]"""
        return self.conn.send_receive(b"world.getPlayerId", name)

    def save_checkpoint(self):
        """Сохранить мир, чтобы затем его восстановить"""
        self.conn.send(b"world.checkpoint.save")

    def restore_checkpoint(self):
        """Восстановить мир до точки восстановления"""
        self.conn.send(b"world.checkpoint.restore")

    def post_to_chat(self, msg):
        """Написать сообщение в чате"""
        self.conn.send(b"chat.post", msg)

    def setting(self, setting, status):
        """Изменить настройки мира (setting, status). keys: world_immutable, nametags_visible"""
        self.conn.send(b"world.setting", setting, 1 if bool(status) else 0)

    def set_player(self, name) -> bool:
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
    mc.post_to_chat("Hello, Minecraft!")
