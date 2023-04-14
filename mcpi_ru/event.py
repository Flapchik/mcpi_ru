from .vec3 import Vec3


class BlockEvent:
    """An Event related to blocks (e.g. placed, removed, hit)"""
    HIT = 0

    def __init__(self, type_of_event, x, y, z, face, entity_id):
        self.type = type_of_event
        self.pos = Vec3(int(x), int(y), int(z))
        self.face = face
        self.entityId = entity_id

    def __repr__(self):
        s_type = {
            BlockEvent.HIT: "BlockEvent.HIT"
        }.get(self.type, "???")

        return "BlockEvent(%s, %d, %d, %d, %s, %s)" % (
            s_type, self.pos.x, self.pos.y, self.pos.z, self.face, self.entityId)

    @staticmethod
    def hit(x, y, z, face, entity_id):
        return BlockEvent(BlockEvent.HIT, x, y, z, face, entity_id)


class ChatEvent:
    """An Event related to chat (e.g. posts)"""
    POST = 0

    def __init__(self, type_of_event, entity_id, message):
        self.type = type_of_event
        self.entityId = entity_id
        self.message = message

    def __repr__(self):
        s_type = {
            ChatEvent.POST: "ChatEvent.POST"
        }.get(self.type, "???")

        return "ChatEvent(%s, %d, %s)" % (
            s_type, self.entityId, self.message)

    @staticmethod
    def post(entity_id, message):
        return ChatEvent(ChatEvent.POST, entity_id, message)


class ProjectileEvent:
    """An Event related to projectiles (e.g. placed, removed, hit)"""
    HIT = 0

    def __init__(self, type_of_event, x, y, z, face, shooter_name, victim_name):
        self.type = type_of_event
        self.pos = Vec3(int(x), int(y), int(z))
        self.face = face
        self.shooterName = shooter_name
        self.victimName = victim_name

    def __repr__(self):
        s_type = {
            ProjectileEvent.HIT: "ProjectileEvent.HIT"
        }.get(self.type, "???")

        return "ProjectileEvent(%s, %d, %d, %d, %s, %s)" % (
            s_type, self.pos.x, self.pos.y, self.pos.z, self.shooterName, self.victimName)

    @staticmethod
    def hit(x, y, z, face, shooter_name, victim_name):
        return ProjectileEvent(BlockEvent.HIT, x, y, z, face, shooter_name, victim_name)
