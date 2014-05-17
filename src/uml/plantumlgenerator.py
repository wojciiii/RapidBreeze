from core.model import Generator
from core.model import Entity
from core.model import Connection
from core.cmodel import ClassEntity
from core.cmodel import Member

import core.constants as constants

class PlantUmlGenerator(Generator):

    def __init__(self):
        self.text = ""
        self.typeDict = { 
            constants.ASSOCIATION: self.outputAssociation,
            constants.WEAK_AGGREGATION: self.outputWeakAggregation,
            constants.STRONG_AGGREGATION: self.outputStrongAggregation,
            constants.SPECIALIZATION: self.outputSpecialization,
            constants.IMPLEMENTATION: self.outputImplementation,
            constants.DEPENDENCY: self.outputDependency
        }

    def start(self):
        self.text = ""
        print("start")
        self.text += "@startuml\n\n"

        self.text += """skinparam class {
BackgroundColor White
ArrowColor SeaGreen
BorderColor Black
}
skinparam stereotypeCBackgroundColor LightGreen
skinparam stereotypeIBackgroundColor SpringGreen\n"""

    def add_entity(self, e):
        if e.getType() == constants.CLASS:
            self.outputClass(e)
        elif e.getType() == constants.INTERFACE:
            self.outputInterface(e)

    def outputClass(self, e):
        self.text += """class %s {\n}\n""" % (e.getName())
        if type(e) is ClassEntity:
            m = e.getMembers()
            self.outputMembers(e.getName(), m)
            self.text += "\n"

    visibility_conversion = {
        constants.ACCESS_PRIVATE: "-",
        constants.ACCESS_PROTECTED: "#",
        constants.ACCESS_PUBLIC: "+",
        constants.ACCESS_PACKAGE: "~"
    }

    def outputMembers(self, name, members):
        for m in members:
            if m.getAccess() in self.visibility_conversion:
                visibility = self.visibility_conversion[m.getAccess()]
            else:
                visibility = ""

            if m.getType() == constants.TYPE_VARIABLE:
                self.text += "%s : %s%s\n" % (name, visibility, m.getName())
            elif m.getType() == constants.TYPE_METHOD:
                self.text += "%s : %s%s()\n" % (name, visibility, m.getName())
        
    def outputInterface(self, e):
        self.text += """interface %s\n""" % (e.getName())
        if type(e) is ClassEntity:
            m = e.getMembers()
            self.outputMembers(e.getName(), m)
            self.text += "\n"

    def add_connection(self, c, src, dst):
        #print("add_connection")
        self.typeDict[c.getConnType()](c, src, dst)

    def outputAssociation(self, c, src, dst):
#        print("outputAssociation")
        self.text += src.getName() + " *-- " + dst.getName()
        self.text += '\n'

    # Empty diamond
    def outputWeakAggregation(self, c, src, dst):
        self.text += src.getName() + " o--> " + dst.getName()
        self.text += '\n'
    # contains: *-- 

    # Full diamond
    def outputStrongAggregation(self, c, src, dst):
        self.text += src.getName() + " *--> " + dst.getName()
        self.text += '\n'
    # contains: *-- 

    def outputSpecialization(self, c, src, dst):
        self.text += src.getName() + " <|-- " + dst.getName()
        self.text += '\n'

    def outputImplementation(self, c, src, dst):
#        print("outputImplementation %s:%s" % (src.getName(), dst.getName()))
        self.text += src.getName() + " <|-- " + dst.getName()
        self.text += '\n'

    def outputDependency(self, c, src, dst):
        self.text += src.getName() + " .. " + dst.getName()
        self.text += '\n'

    def end(self):
        self.text += "\n@enduml\n"
        print("end")

    def getText(self):
        return self.text

 
