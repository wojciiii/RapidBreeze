import sys
import getopt

PARAM_INPUTFILESET="inputFileSet"
PARAM_INPUTFILENAME="inputFilename"

def parseParameters(name, argv):
    HELPSTR =  'Expected command line options:\n'
    HELPSTR += '%s -i <input>' % name
    inputFileSet = False
    inputfile = ''

    try:
        opts, args = getopt.getopt(argv,'i:h',['input=', 'help'])
    except getopt.GetoptError:
        print ("Invalid option given.")
        print (HELPSTR)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            print (HELPSTR)
            sys.exit()
        elif opt in ('-i', '--input'):
            inputfile = arg
            inputFileSet = True

    ret = {PARAM_INPUTFILESET: inputFileSet, PARAM_INPUTFILENAME: inputfile}
    return ret

if __name__ == "__main__":
   paramDescriptor = parseParameters("test", sys.argv[1:])
   print ("File set %d: %s" % (paramDescriptor[PARAM_INPUTFILESET], paramDescriptor[PARAM_INPUTFILENAME]))

def loadCommandsFromFile(filename):
    cmds = []

    with open(filename) as f:
        for line in f:
            s = line.strip()
            if len(s) > 0:
                cmds.append(s)

    return cmds

