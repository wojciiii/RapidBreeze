import constants
from illegalargumenterror import IllegalArgumentError

class Generator(object):

    def __init__(self):
        pass

    def start(self):
        raise NotImplementedError("Method not implemented in generator.")

    def add_entity(self, e):
        raise NotImplementedError("Method not implemented in generator.")
    
    def add_connection(self, c, src, dst):
        raise NotImplementedError("Method not implemented in generator.")

    def end(self):
        raise NotImplementedError("Method not implemented in generator.")

class Entity(object):

    def __init__(self, entity_type, entity_name):
        self.mId         = constants.INVALID_ID
        self.entity_type = entity_type
        self.entity_name = entity_name

    def setId(self, instanceId):
        self.mId = instanceId

    def getId(self):
        return self.mId

    def getName(self):
        return self.entity_name

    def getType(self):
        return self.entity_type

    def dump(self):
        pass

class Connection(object):

    def __init__(self, source_id, destination_id, connType):

        if not self.checkType(connType):
            raise IllegalArgumentError("Unknown connection type")

        self.connType = connType
        self.src      = source_id
        self.dst      = destination_id

    def checkType(self, connType):
        # None are accepted per default.
        # This needs to be implemented.
        return False

    def getSource(self):
        return self.src

    def getDestination(self):
        return self.dst

    def pointsTo(self, entity_id):
        status = False

        if self.src == entity_id:
            status = True
        elif self.dst == entity_id:
            status = True
        return status

    def setConnType(self, connType):

        if not self.checkType(connType):
            raise IllegalArgumentError("Unknown connection type")

        self.connType = connType

    def getConnType(self):
        return self.connType

class Database(object):

    def __init__(self):
        self.mId         = 0
        self.entities    = []
        self.connections = []

    def reset(self):
        self.mId         = 0
        self.entities    = []
        self.connections = []
        print("DB reset.")

    def add(self, *arg):
        res = []
        for a in arg:
            id = self.addEntity(a)
            res.append(id)
        return res

    def addEntity(self, entity):
        ret_id = self.mId
        entity.setId(ret_id)
        print ("Adding entity %d: %s." % (entity.getId(), entity.getName()))
        self.entities.append(entity);
        self.mId += 1
        return ret_id

    def delete(self, entity):
        eId = entity.getId()
        print ("Deleting entity %d." % eId)

        toDelete = []
        for c in self.connections:
            if c.pointsTo(eId):
                toDelete.append(c)

        for c in toDelete:
            print ("Deleting connection from %d to %d" % (c.getSource(), c.getDestination()))
            self.connections.remove(c)

        self.entities.remove(entity)

    def deleteById(self, entity_id):
        for e in self.entities:
            if (e.getId() == entity_id):
                self.delete(e)
                break

    def addConnection(self, c):
        if self.getEntity(c.getSource()) == None:
            raise IllegalArgumentError("Connection, src is invalid.")

        if self.getEntity(c.getDestination()) == None:
            raise IllegalArgumentError("Connection, dst is invalid.")

        self.connections.append(c)

#    def connect(self, entity1, entity2, connection_type):
#        self.connectById(entity1.getId(), entity2.getId(), connection_type)

#    def connectById(self, id1, id2, connection_type):
#        if id1 == constants.INVALID_ID:
#            raise IllegalArgumentError("First id is invalid.")
#        if id2 == constants.INVALID_ID:
#            raise IllegalArgumentError("Second id is invalid.")

#        c = Connection(id1, id2, connection_type)
#        self.connections.append(c)

    def generate(self, generator):
        generator.start()
        for e in self.entities:
            generator.add_entity(e)

        for c in self.connections:
            src = self.getEntity(c.getSource())
            dst = self.getEntity(c.getDestination())
            generator.add_connection(c, src, dst)

        generator.end()

    def dump(self):
        # dump contents of this db.

        print("Entities:")
        for e in self.entities:
            e.dump()
#            print ("--")
#            print ("Entity %d: \"%s\" of type %d" % (e.getId(), e.getName(), e.getType()))
#            for m in e.getMembers():
#                print ("member %s type %s access %s" % (m.getName(), m.getType(), m.getAccess()))
#            if e.hasAttribute():
#                print ("Attribute: " + e.getAttribute().getId())

        print ("%d Connections:" % len(self.connections))
        for c in self.connections:
            srcId = c.getSource()
            e     = self.getEntity(srcId)
            if e == None:
                srcName = 'UNKN'
            else:
                srcName = e.getName()

            dstId = c.getDestination()
            e     = self.getEntity(dstId)
            if e == None:
                dstName = 'UNKN'
            else:
                dstName = e.getName()
            print ("From %s (id %d) to %s (id %d), type %s" % (srcName, c.getSource(), dstName, c.getDestination(), constants.CONNECTION_TYPE[c.getConnType()]))

    def getEntity(self, entityId):
        res = None
        for e in self.entities:
            #print ("Entity %d" % e.getId())
            if (e.getId() == entityId):
                res = e
                break

        if res == None:
            print("Entity not found for id %d." % entityId)
        return res

#
# Test
#

def test_database():
    print("Testing ..")

    test_entity_type = 1

    e1 = Entity(entity_type=test_entity_type, entity_name='test1')

    e2 = Entity(entity_type=test_entity_type, entity_name='test2')

    e3 = Entity(entity_type=test_entity_type, entity_name='test3')

    db = Database()
    db.add(e1)
    db.add(e2)
    db.add(e3)

    db.dump()

    db.reset()
        
    s = Entity(entity_type=test_entity_type, entity_name='Sender')
    r = Entity(entity_type=test_entity_type, entity_name='Receiver')
        
    db.add(s)
    db.add(r)

    #db.connect(s, r, constants.ASSOCIATION)
        
    superC = Entity(entity_type=test_entity_type, entity_name='Super')
    subC1  = Entity(entity_type=test_entity_type, entity_name='Sub1')

    db.add(superC)
    db.add(subC1)
    #db.connect(subC1, superC, constants.SPECIALIZATION)

    subC2  = Entity(entity_type=test_entity_type, entity_name='Sub2')
    db.add(subC2)
    #db.connect(subC2, superC, constants.SPECIALIZATION)

    db.dump()

    db.delete(superC)

    db.dump()

def test_entity():
    print("Testing ..")

    e = Entity(entity_type=0, entity_name="test_if")

    print("e = " + str(e.getType()) + ", " + e.getName())

def test_connection():
    print("Testing ..")

    try:
        c = Connection(1, 10, -1) 
    except IllegalArgumentError as e:
        print ("Exception: " + str(e))

    try:
        c = Connection(1, 10, constants.SPECIALIZATION) 
    except IllegalArgumentError:
        print("Caught expected exception")

    #print ("Connection type: " + str(c.getConnType()))    

def test_Generator():
    print("Testing generator ..")

    g = Generator()
    try:
        g.start()
    except NotImplementedError as e:
        print ("Caught NotImplementedError as expected.")

    
if __name__ == "__main__":
    test_entity()
    test_connection()
    test_Generator()
    test_database()

