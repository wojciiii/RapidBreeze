from illegalargumenterror import IllegalArgumentError
from model import Entity
from model import Connection
import constants

class ClassEntity(Entity):

    def __init__(self, entity_type=constants.CLASS, entity_name="name"):
        super(ClassEntity,self).__init__(entity_type, entity_name)
        self.attribute   = None
        self.memberList  = []

    def hasAttribute(self):
        return self.attribute != None

    def setAttribute(self, attribute):
        self.attribute = attribute

    def getAttribute(self):
        return self.attribute

    def addVariable(self, name, access):
        m = Member(member_type=constants.TYPE_VARIABLE, 
            member_name=name, 
            member_access=access)
        self.addMember(m)

    def addMethod(self, name, access):
        m = Member(member_type=constants.TYPE_METHOD, 
                   member_name=name,
                   member_access=access)
        self.addMember(m)

    def addMember(self, member):
        nameToAdd = member.getName()
        for cmember in self.memberList:
            if cmember.getName() == nameToAdd:
                raise IllegalArgumentError("Member " + nameToAdd + " already present")
        self.memberList.append(member)

    def getMembers(self):
        return self.memberList

    def dump(self):
        print ("Entity id=%d name=%s type=%d" % (self.mId, self.entity_name, self.entity_type))

acceptedTypes = [constants.ASSOCIATION,
                 constants.WEAK_AGGREGATION,
                 constants.STRONG_AGGREGATION,
                 constants.SPECIALIZATION, 
                 constants.IMPLEMENTATION,
                 constants.DEPENDENCY]

class ClassConnection(Connection):

    def __init__(self, source_id, destination_id, connType):

        super(ClassConnection,self).__init__(source_id, destination_id, connType)
    @staticmethod
    def fromList(ids, connType):
        if not (len(ids) == 2):
            raise IllegalArgumentError("Array of len 2 expected")
        return ClassConnection(ids[0], ids[1], connType)

    def checkType(self, connType):
        status = False
        if connType in acceptedTypes:
            status = True
        return status

class Member(object):

    def __init__(self, 
                 member_type=constants.TYPE_METHOD, 
                 member_name="name", 
                 member_access = constants.ACCESS_PUBLIC):
        self.member_type   = member_type
        self.member_name   = member_name
        self.member_access = member_access

    def setAccess(self, a):
        self.member_access = a

    def getAccess(self):
        return self.member_access

    def getName(self):
        return self.member_name

    def getType(self):
        return self.member_type

    def __str__(self):
        return str(self.__dict__)

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__

class Attribute(object):

    def __init__(self, attribute_id=constants.ATTRIB_NONE):
        self.attribute_id = attribute_id

    def getId(self):
        return self.attribute_id

#
# Test
#

def test_cconnection():
    print("Testing ..")

    try:
        c = ClassConnection(1, 10, -1) 
    except IllegalArgumentError as e:
        print ("Exception: " + str(e))

    c = ClassConnection(1, 10, constants.SPECIALIZATION) 
    print ("Connection type: " + str(c.getConnType()))    

def test_centity():
    print("Testing ..")

    e = Entity(entity_type=constants.INTERFACE, entity_name="test_if")

    print("e = " + str(e.getType()) + ", " + e.getName())

def test_member():
    print("Testing member ..")

    m = Member(constants.TYPE_METHOD, "computeSum");

    print("m = " + str(m.getType()) + ", " + m.getName())

    m1 = Member(constants.TYPE_VARIABLE, "mStr1");
    m2 = Member(constants.TYPE_VARIABLE, "mStr1");
    m3 = Member(constants.TYPE_VARIABLE, "mStr2");

    # Equality:
    print(m1 == m2)
    print(m1 == m3)

def test_attribute():
    print("Testing attribute ..")
    a = Attribute("test")
    print("attribute id = " + str(a.getId()))

if __name__ == "__main__":
    test_centity()
    test_cconnection()
    test_member()
    test_attribute()
