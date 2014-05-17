import subprocess

# 
# Execute plantuml with input from stdin and output to stdout. 
#
class PlantUML(object):

    def __init__(self, 
                 javaInterpreter="/usr/bin/java", 
                 jarFile="./plantuml.jar"):
        self.javaInterpreter = javaInterpreter
        self.jarFile         = jarFile
        self.output          = None
        self.retcode         = -1;

    def convert(self, text_input):
        proc = subprocess.Popen([self.javaInterpreter, 
                                "-jar", 
                                self.jarFile,
                                "-pipe"], 
                                stdin=subprocess.PIPE, 
                                stdout=subprocess.PIPE)

        self.output = proc.communicate(input=text_input)[0]
        self.retcode = proc.returncode

        return self.retcode

    def save(self, outputFile):
        o = open(outputFile, 'w')
        o.write(self.output)

    def getOutput(self):
        return self.output

if __name__ == "__main__":
    print("Testing ..")

    p = PlantUML();
    ret = p.execute("test");

    print("rc = " + str(ret))

    o = p.getOutput()
