import argparse
import sys
import xml.etree.ElementTree as ET
import re

allowedInstructions = {
            'move': 'v s',
            'createframe': '',
            'pushframe': '',
            'popframe': '',
            'defvar': 'v',
            'call': 'l',
            'return': '',
            'pushs': 's',
            'pops': 'v',
            'add': 'v s s',
            'sub': 'v s s',
            'mul': 'v s s',
            'div': 'v s s',
            'idiv': 'v s s',
            'int2float': 'v s',
            'float2int': 'v s',
            'lt': 'v s s',
            'gt': 'v s s',
            'eq': 'v s s',
            'and': 'v s s',
            'or': 'v s s',
            'not': 'v s',
            'int2char': 'v s',
            'stri2int': 'v s s',
            'read': 'v t',
            'write': 's',
            'concat': 'v s s',
            'strlen': 'v s',
            'getchar': 'v s s',
            'setchar': 'v s s',
            'type': 'v s',
            'label': 'l',
            'jump': 'l',
            'jumpifeq': 'l s s',
            'jumpifneq': 'l s s',
            'exit': 's',
            'dprint': 's',
            'break': ''
}

instructionTree = {}

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('It seems you used wrong parameters or you forget to add filename. Try it again or use --help.\n')
        sys.exit(10)

class Instruction:
    def __init__(self, opcode, arg1Type='', arg1Val='', arg2Type='', arg2Val='', arg3Type='', arg3Val=''):
        self.opcode = opcode.lower()
        self.arg1Type = arg1Type
        self.arg2Type = arg2Type
        self.arg3Type = arg3Type
        self.arg1Val = arg1Val
        self.arg2Val = arg2Val
        self.arg3Val = arg3Val

    def __str__(self):
        return self.opcode + ' ' + self.arg1Type + ' ' + self.arg1Val + ' ' + self.arg2Type + ' ' + self.arg2Val + ' ' + self.arg3Val + ' ' + self.arg3Type

    def checkOpcode(self):
        if self.opcode not in allowedInstructions:
            sys.stderr.write('Unsupported instruction.\n')
            sys.exit(32)

    def checkCorrectArgs(self):

        def checkVar(val):
            pattern = re.compile(r'^(?:L|G|T)F@(?:[a-zA-Z]|_|-|\\$|&|%|\*|!|\?)(?:[a-zA-Z0-9]|_|-|\\$|&|%|\*|!|\?)*$')
            if not re.match(pattern, val):
                sys.stderr.write('Regex for variable doesn\'t match!\n')
                sys.exit(32)

        def checkSymb(val):
            pattern = re.compile(r'(?:^(?:L|G|T)F@(?:[a-zA-Z]|_|-|\\$|&|%|\*|!|\?)(?:[a-zA-Z0-9]|_|-|\\$|&|%|\*|!|\?)*$)')
            pattern2 = re.compile(r'^(bool@true|bool@false|int@(?:\+|-)?[0-9]*|nil@nil|string@(?:[^\s#\\]|\\[0-9][0-9][0-9])(?:[^\s#\\]|\\[0-9][0-9][0-9])*|string@)$')
            if not re.match(pattern, val) and not re.match(pattern2, val):
                sys.stderr.write('Regex for symbol doesn\'t match!\n')
                sys.exit(32)

        def checkLabel(val):
            pattern = re.compile(r'^(?:[a-zA-Z]|_|-|\$|&|%|\*|!|\?)(?:[a-zA-Z0-9]|_|-|\$|&|%|\*|!|\?)*$')
            if not re.match(pattern, val):
                sys.stderr.write('Regex for label doesn\'t match!\n')
                sys.exit(32)

        def checkType(val):
            if val != 'int' and val != 'string' and val != 'bool':
                sys.stderr.write('Regex for type doesn\'t match!\n')
                sys.exit(32)

        allowedArgs = allowedInstructions[self.opcode]
        if allowedArgs == '':
            if self.arg1Val != '' or self.arg1Val != '':
                sys.stderr.write('Opcode ' + self.opcode + ' can\'t have any operands!')
                sys.exit(32)
        singleArgs = allowedArgs.split(' ')
        a = 1
        for s in singleArgs:
            type = ''
            val = ''
            if a == 1:
                type = self.arg1Type
                val = self.arg1Val
            elif a == 2:
                type = self.arg2Type
                val = self.arg2Val
            else:
                type = self.arg3Type
                val = self.arg3Val

            if s == 'v':
                if type != 'var':
                    sys.stderr.write('This operand should be var!')
                    sys.exit(32)
                checkVar(val)
            elif s == 's':
                if type != 'var' and type != 'int' and type != 'nil' and type != 'string' and type != 'float' and type != 'bool':
                    sys.stderr.write('This operand should be symb!' + type)
                    sys.exit(32)
                if type != 'var':
                    sendToControl = type + '@' + val
                else:
                    sendToControl = val
                checkSymb(sendToControl)
            elif s == 'l':
                if type != 'label':
                    sys.stderr.write('This operand should be label!' + self.opcode + ' ' + type)
                    sys.exit(32)
                checkLabel(val)
            elif s == 't':
                if type != 'type':
                    sys.stderr.write('This operand should be type!')
                    sys.exit(32)
                checkType(val)
            a += 1


class XMLTree:
    def __init__(self, tree):
        self.tree = tree

    def checkValidity(self):
        root = self.tree.getroot()
        if root.tag != 'program':
            sys.stderr.write('The first element must be <program>.\n')
            sys.exit(32)
        for attrib in root.attrib:
            if attrib != 'language' and attrib != 'name' and attrib != 'description':
                sys.stderr.write('The <program> element can\'t have this attribute.\n')
                sys.exit(32)
            if attrib == 'language' and root.get('language').lower() != 'ippcode19':
                sys.stderr.write('The language attribute can\'t have this value.\n')
                sys.exit(32)
        for child in root:
            if child.tag != 'instruction':
                sys.stderr.write('Unsupported element.\n')
                sys.exit(32)
            try:
                order = child.attrib['order']
                opcode = child.attrib['opcode']
            except KeyError:
                sys.stderr.write('The <instruction> element needs attributes order and opcode.\n')
                sys.exit(32)
            if len(child.attrib) != 2:
                sys.stderr.write('The <instruction> element can only have two attributes.\n')
                sys.exit(32)
            try:
                int(order)
            except ValueError:
                sys.stderr.write('The order has to be integer.\n')
                sys.exit(32)

            # arg1, arg2, arg3
            i = 1
            arg1 = ''
            arg1Val = ''
            arg2 = ''
            arg2Val = ''
            arg3 = ''
            arg3Val = ''
            for childOfChild in child:

                try:
                    type = childOfChild.attrib['type']
                except KeyError:
                    sys.stderr.write('The <arg> element needs attribute type.\n')
                    sys.exit(32)

                if i == 1:
                    arg1 = type
                    arg1Val = str(childOfChild.text)
                elif i == 2:
                    arg2 = type
                    arg2Val = str(childOfChild.text)
                else:
                    arg3 = type
                    arg3Val = str(childOfChild.text)

                i += 1

            # create a new Instruction
            ins = Instruction(opcode, arg1, arg1Val, arg2, arg2Val, arg3, arg3Val)
            ins.checkOpcode()
            ins.checkCorrectArgs()

            instructionTree[order] = ins

class Frame:
    def __init__(self):
        self.vars = {}

    def variableExists(self, name):
        if name in self.vars:
            return True
        else:
            return False

    def createVar(self, name):
        self.vars[name] = None

    def getVal(self, name):
        return self.vars[name]

    def setVal(self, name, value):
        self.vars[name] = value

    def __str__(self):
        text = ''
        for i in self.vars:
            text = text + str(i) + ': ' + str(self.vars[i]) + '\n'
        return text


# maintain arguments
parser = MyParser(add_help=False)

parser.add_argument('--help', '-help', action='store_true')
parser.add_argument('--source', '-source')
parser.add_argument('--input', '-input')
parser.add_argument('--stati', '-stati')
parser.add_argument('--insts', '-insts', action='store_true')
parser.add_argument('--vars', '-vars', action='store_true')

arguments = parser.parse_args()

if arguments.help:
    if len(sys.argv) != 2:
        sys.stderr.write('It seems you used wrong parameters. You can\'t use --help with other parameters.\n')
        sys.exit(10)
    print('********************************************************************************\n' +
         '** Run script:                                                                **\n' +
         '** 1. with parameter --help (shows help)                                      **\n' +
         '** 2. with parameter --source or --input (you can use both, source is for     **\n' +
         '**    source code and input can contain user\'s input                          **\n' +
         '** 3. with parameter --stati=file and --insts|--vars                          **\n' +
         '**    (saves statistics into file)                                            **\n' +
         '**                                                                            **\n' +
         '** It is NECESSARY to use either --source or --input! The other one           **\n' +
         '** is loaded from stdin.                                                      **\n' +
         '**                                                                            **\n' +
         '** Examples:                                                                  **\n' +
         '** python3.6 interpret.py --source=file1 --input=file2 --stati --inst         **\n' +
         '** python3.6 interpret.py --help                                              **\n' +
         '** python3.6 interpret.py --input=file2                                       **\n' +
         '********************************************************************************\n')
elif arguments.source or arguments.input:
    if (arguments.source and arguments.source == '' and (not arguments.input or arguments.input == '')) or (arguments.input and arguments.input == '' and (not arguments.source or arguments.source == '')):
        sys.stderr.write('You have to specify either input file or source file or both.\n')
        sys.exit(10)
    if arguments.stati and not arguments.input == '' and not (arguments.insts or arguments.vars):
        sys.stderr.write('You have to specify what statistics you need.\n')
        sys.exit(10)

    # run the program!
    if arguments.source:
        try:
            tree = ET.parse(arguments.source)
        except FileNotFoundError:
            sys.stderr.write('Can\'t open the file.\n')
            sys.exit(11)
        except Exception:
            sys.stderr.write('Your XML is not well-formed.\n')
            sys.exit(31)
    else:
        tree = ET.parse(sys.stdin)

    myTree = XMLTree(tree)
    myTree.checkValidity()

    # check order
    for i in range(1, len(instructionTree)+1):
        if str(i) not in instructionTree:
            sys.stderr.write('Error in the order of instructions.\n')
            sys.exit(32)

    # start interpret

    # at first find all labels and save them
    instructionPointer = 1
    labels = {}

    while instructionPointer <= len(instructionTree):
        keyValue = str(instructionPointer)
        if instructionTree[keyValue].opcode == 'label':
            # save the label for future
            if instructionTree[keyValue].arg1Val in labels:
                sys.stderr.write('Error in instruction ' + keyValue + ': This label already exists.\n')
                sys.exit(52)
            else:
                labels[instructionTree[keyValue].arg1Val] = keyValue
        instructionPointer = instructionPointer+1

    # interpret instructions

    instructionPointer = 1
    # define GF, TF and stack for LFs
    globalFrame = Frame()
    temporaryFrame = None
    localFrame = None
    stack = []
    callsStack = []
    programStack = []


    # functions for tasks needed during interpretation
    def chooseFrame(frame):
        f = None
        if frame == 'GF':
            f = globalFrame
        elif frame == 'TF':
            if temporaryFrame is None:
                sys.stderr.write(
                    'Error in instruction ' + keyValue + ': You\'ve tried to use undefined temporary frame.\n')
                sys.exit(55)
            else:
                f = temporaryFrame
        elif frame == 'LF':
            if not stack:
                sys.stderr.write(
                    'Error in instruction ' + keyValue + ': You\'ve tried to use undefined local frame.\n')
                sys.exit(55)
            else:
                f = stack.pop()
                # TODO: tady byl ten problem !!!
                stack.append(f)
        return f

    def getTypeOfSymb(symb):
        regex = r'^(?:\+|-)?[0-9]*$'
        if symb == 'nil':
            return 'nil'
        elif symb == 'false' or symb == 'true':
            return 'bool'
        elif symb == None:
            return ''
        elif re.match(regex, symb):
            return 'int'
        else:
            return 'string'

    def extractValueFromSymb(number, keyValue):
        copyVal = None
        if number == 2:
            if 'F@' in instructionTree[keyValue].arg2Val:
                frame, at, name = instructionTree[keyValue].arg2Val.partition('@')
                frameObject = chooseFrame(frame)
                if frameObject.variableExists(name):
                    copyVal = frameObject.getVal(name)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                    sys.exit(54)
            else:
                copyVal = instructionTree[keyValue].arg2Val
        elif number == 1:
            if 'F@' in instructionTree[keyValue].arg1Val:
                frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
                frameObject = chooseFrame(frame)
                if frameObject.variableExists(name):
                    copyVal = frameObject.getVal(name)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                    sys.exit(54)
            else:
                copyVal = instructionTree[keyValue].arg1Val
        elif number == 3:
            if 'F@' in instructionTree[keyValue].arg3Val:
                frame, at, name = instructionTree[keyValue].arg3Val.partition('@')
                frameObject = chooseFrame(frame)
                if frameObject.variableExists(name):
                    copyVal = frameObject.getVal(name)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                    sys.exit(54)
            else:
                copyVal = instructionTree[keyValue].arg3Val

        return copyVal

    def doArithmeticOperation(keyValue, operator):
        frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
        frameObject = chooseFrame(frame)
        if frameObject.variableExists(name):
            copyVal = extractValueFromSymb(2, keyValue)
            type = getTypeOfSymb(copyVal)
            if type == 'int':
                copyVal2 = extractValueFromSymb(3, keyValue)
                type2 = getTypeOfSymb(copyVal2)
                if type2 == 'int':
                    if operator == '+':
                        val = int(copyVal) + int(copyVal2)
                    elif operator == '-':
                        val = int(copyVal) - int(copyVal2)
                    elif operator == '*':
                        val = int(copyVal) * int(copyVal2)
                    elif operator == '/':
                        try:
                            val = int(copyVal) / int(copyVal2)
                        except ZeroDivisionError:
                            sys.stderr.write('Error in instruction ' + keyValue + ': Division by zero.\n')
                            sys.exit(57)
                    frameObject.setVal(name, str(val))
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can use arithmetic operators only with integers.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': You can use arithmetic operators only with integers.\n')
                sys.exit(53)
        else:
            sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
            sys.exit(54)


    def compare(keyValue, instruction):
        frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
        frameObject = chooseFrame(frame)
        if frameObject.variableExists(name):
            copyVal = extractValueFromSymb(2, keyValue)
            type = getTypeOfSymb(copyVal)
            copyVal2 = extractValueFromSymb(3, keyValue)
            type2 = getTypeOfSymb(copyVal2)
            if type == type2:
                if type == 'nil' and instruction != 'eq':
                    sys.stderr.write('Error in instruction ' + keyValue + ': Only EQ instruction is allowed for nil.\n')
                    sys.exit(53)
                else:
                    if instruction == 'lt':
                        if type == 'int':
                            if int(copyVal) < int(copyVal2):
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                        if type == 'bool':
                            if copyVal == 'false':
                                copyVal = False
                            else:
                                copyVal = True
                            if copyVal == 'false':
                                copyVal = False
                            else:
                                copyVal = True
                            if int(copyVal) < int(copyVal2):
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                        if type == 'string':
                            if copyVal < copyVal2:
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                    if instruction == 'gt':
                        if type == 'int':
                            if int(copyVal) > int(copyVal2):
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                        if type == 'bool':
                            if copyVal == 'false':
                                copyVal = False
                            else:
                                copyVal = True
                            if copyVal == 'false':
                                copyVal = False
                            else:
                                copyVal = True
                            if int(copyVal) > int(copyVal2):
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                        if type == 'string':
                            if copyVal > copyVal2:
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                    if instruction == 'eq':
                        if type == 'int':
                            if int(copyVal) == int(copyVal2):
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')
                        if type == 'bool' or type == 'string' or type == 'nil':
                            if copyVal == copyVal2:
                                frameObject.setVal(name, 'true')
                            else:
                                frameObject.setVal(name, 'false')

            else:
                sys.stderr.write(
                    'Error in instruction ' + keyValue + ': You can\'t compare variables of different types.\n')
                sys.exit(53)
        else:
            sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
            sys.exit(54)

    def boolOp(keyValue, instruction):
        frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
        frameObject = chooseFrame(frame)
        if frameObject.variableExists(name):
            copyVal = extractValueFromSymb(2, keyValue)
            type = getTypeOfSymb(copyVal)
            if type == 'bool':
                if copyVal == 'false':
                    copyVal = False
                else:
                    copyVal = True
                if instruction == 'not':
                    frameObject.setVal(name, str(not copyVal).lower())
                else:
                    copyVal2 = extractValueFromSymb(3, keyValue)
                    type2 = getTypeOfSymb(copyVal2)
                    if type2 == 'bool':
                        if copyVal2 == 'false':
                            copyVal2 = False
                        else:
                            copyVal2 = True
                        if instruction == 'and':
                            frameObject.setVal(name, str(copyVal and copyVal2).lower())
                        else:
                            frameObject.setVal(name, str(copyVal or copyVal2).lower())
                    else:
                        sys.stderr.write('Error in instruction ' + keyValue + ': AND/OR can only be used with bool variables.\n')
                        sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': AND/OR/NOT can only be used with bool variables.\n')
                sys.exit(53)
        else:
            sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
            sys.exit(54)


    while instructionPointer <= len(instructionTree):
        keyValue = str(instructionPointer)
        jumpInstr = 0


        if instructionTree[keyValue].opcode == 'createframe':
            temporaryFrame = Frame()
        elif instructionTree[keyValue].opcode == 'pushframe':
            if temporaryFrame is None:
                sys.stderr.write('Error in instruction ' + keyValue + ': You\'ve tried to use undefined temporary frame.\n')
                sys.exit(55)
            else:
                stack.append(temporaryFrame)
                temporaryFrame = None
        elif instructionTree[keyValue].opcode == 'popframe':
            if not stack:
                sys.stderr.write('Error in instruction ' + keyValue + ': You\'ve tried to use undefined local frame.\n')
                sys.exit(55)
            else:
                temporaryFrame = stack.pop()
        elif instructionTree[keyValue].opcode == 'label':
            # do nothing because labels were already processed
            pass
        elif instructionTree[keyValue].opcode == 'call':
            callsStack.append(instructionPointer+1)
            if instructionTree[keyValue].arg1Val not in labels:
                sys.stderr.write('Error in instruction ' + keyValue + ': This label doesn\'t exist.\n')
                sys.exit(52)
            else:
                jumpInstr = labels[instructionTree[keyValue].arg1Val]
        elif instructionTree[keyValue].opcode == 'return':
            if not callsStack:
                sys.stderr.write('Error in instruction ' + keyValue + ': You didn\'t specify where to return.\n')
                sys.exit(56)
            jumpInstr = callsStack.pop()
        elif instructionTree[keyValue].opcode == 'jump':
            if instructionTree[keyValue].arg1Val not in labels:
                sys.stderr.write('Error in instruction ' + keyValue + ': This label doesn\'t exist.\n')
                sys.exit(52)
            else:
                jumpInstr = labels[instructionTree[keyValue].arg1Val]
        elif instructionTree[keyValue].opcode == 'exit':
            copyVal = extractValueFromSymb(1, keyValue)

            pattern = re.compile(r'\d+')
            if not re.match(pattern, copyVal):
                sys.stderr.write('Error in instruction ' + keyValue + ': This exit code is not allowed.\n')
                sys.exit(57)
            else:
                if int(copyVal) < 0 or int(copyVal) > 49:
                    sys.stderr.write('Error in instruction ' + keyValue + ': This exit code is not allowed.\n')
                    sys.exit(57)
                else:
                    sys.exit(int(copyVal))
        elif instructionTree[keyValue].opcode == 'defvar':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable already exists.\n')
                sys.exit(52)
            else:
                frameObject.createVar(name)
        elif instructionTree[keyValue].opcode == 'move':
            copyVal = extractValueFromSymb(2, keyValue)

            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                frameObject.setVal(name, copyVal)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'write':
            copyVal = extractValueFromSymb(1, keyValue)
            if copyVal is None:
                print('', end='')
            else:
                if instructionTree[keyValue].arg1Type == 'string' or getTypeOfSymb(copyVal) == 'string':
                    copyValArray = re.split(r'(?=\\[0-9]{3})|(?<=\\[0-9]{3})', copyVal)
                    for i in copyValArray:
                        if i.startswith('\\'):
                            match = re.search(r'[1-9][0-9]{1,2}', i)
                            print(chr(int(match[0])), end='')
                        else:
                            print(i, end='')
                else:
                    print(copyVal, end='')
        elif instructionTree[keyValue].opcode == 'dprint':
            copyVal = extractValueFromSymb(1, keyValue)
            if copyVal is None:
                sys.stderr.write('')
            else:
                if instructionTree[keyValue].arg1Type == 'string' or getTypeOfSymb(copyVal) == 'string':
                    copyValArray = re.split(r'(?=\\[0-9]{3})|(?<=\\[0-9]{3})', copyVal)
                    for i in copyValArray:
                        if i.startswith('\\'):
                            match = re.search(r'[1-9][0-9]{1,2}', i)
                            sys.stderr.write(chr(int(match[0])))
                        else:
                            sys.stderr.write(i)
                else:
                    sys.stderr.write(copyVal)
        elif instructionTree[keyValue].opcode == 'type':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                if 'F@' in instructionTree[keyValue].arg2Val:
                    val = extractValueFromSymb(2, keyValue)
                    if val is not None:
                        type = getTypeOfSymb(val)
                        frameObject.setVal(name, type)
                    else:
                        frameObject.setVal(name, '')
                else:
                    frameObject.setVal(name, instructionTree[keyValue].arg2Type)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'break':
            sys.stderr.write('\n********************************************************************************\n' +
         'Number of executed instructions: '+str(instructionPointer)+'\n')
            sys.stderr.write('\nGlobal frame:\n')
            sys.stderr.write(str(globalFrame))
            sys.stderr.write('\n')
            sys.stderr.write('\nTemporary frame:\n')
            if temporaryFrame is not None:
                sys.stderr.write(str(temporaryFrame))
            sys.stderr.write('\n')
            sys.stderr.write('\nLocal frame:\n')
            if stack:
                tmp = stack.pop()
                sys.stderr.write(str(tmp))
                stack.append(tmp)
            sys.stderr.write('\n')
            sys.stderr.write('\nProgram stack:\n')
            if programStack:
                sys.stderr.write(str(programStack))
            sys.stderr.write('\n')
            sys.stderr.write('********************************************************************************\n')
        elif instructionTree[keyValue].opcode == 'pushs':
            copyVal = extractValueFromSymb(1, keyValue)
            programStack.append(copyVal)
        elif instructionTree[keyValue].opcode == 'pops':
            if programStack:
                frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
                frameObject = chooseFrame(frame)
                if frameObject.variableExists(name):
                    frameObject.setVal(name, programStack.pop())
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                    sys.exit(54)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': You\'ve tried to read from an empty stack.\n')
                sys.exit(56)
        elif instructionTree[keyValue].opcode == 'jumpifeq':
            if instructionTree[keyValue].arg1Val not in labels:
                sys.stderr.write('Error in instruction ' + keyValue + ': This label doesn\'t exist.\n')
                sys.exit(52)
            else:
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                copyVal2 = extractValueFromSymb(3, keyValue)
                type2 = getTypeOfSymb(copyVal2)
                if type == type2:
                    if type == 'int':
                        copyVal = copyVal.replace('+', '')
                        copyVal2 = copyVal2.replace('+', '')
                    if copyVal == copyVal2:
                        jumpInstr = labels[instructionTree[keyValue].arg1Val]
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can\'t compare variables of different types.\n')
                    sys.exit(53)
        elif instructionTree[keyValue].opcode == 'jumpifneq':
            if instructionTree[keyValue].arg1Val not in labels:
                sys.stderr.write('Error in instruction ' + keyValue + ': This label doesn\'t exist.\n')
                sys.exit(52)
            else:
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                copyVal2 = extractValueFromSymb(3, keyValue)
                type2 = getTypeOfSymb(copyVal2)
                if type == type2:
                    if type == 'int':
                        copyVal = copyVal.replace('+', '')
                        copyVal2 = copyVal2.replace('+', '')
                    if copyVal != copyVal2:
                        jumpInstr = labels[instructionTree[keyValue].arg1Val]
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can\'t compare variables of different types.\n')
                    sys.exit(53)
        elif instructionTree[keyValue].opcode == 'concat':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                copyVal2 = extractValueFromSymb(3, keyValue)
                type2 = getTypeOfSymb(copyVal2)
                if type == 'string' and type2 == 'string':
                    val = copyVal + copyVal2
                    frameObject.setVal(name, val)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can only concatenate strings.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'strlen':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                if type == 'string':
                    copyVal = re.sub(r'\\[0-9]{3}', '.', copyVal)
                    frameObject.setVal(name, str(len(copyVal)))
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can use strlen only with string.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'getchar':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                if type == 'string':
                    copyVal2 = extractValueFromSymb(3, keyValue)
                    type2 = getTypeOfSymb(copyVal2)
                    if type2 == 'int':
                        withoutEscapeSeqs = re.sub(r'\\[0-9]{3}', '.', copyVal)
                        length = len(withoutEscapeSeqs)
                        copyVal2 = copyVal2.replace('+', '')
                        if int(copyVal2) >= 0 and int(copyVal2) < length:
                            matches = re.search(r'\\[0-9]{3}', copyVal)
                            result = withoutEscapeSeqs[int(copyVal2):int(copyVal2)+1]
                            if result == '.':
                                sliced = withoutEscapeSeqs[0:int(copyVal2)+1]
                                index = sliced.count('.')
                                result = matches[index-1]
                            frameObject.setVal(name, result)
                        else:
                            sys.stderr.write('Error in instruction ' + keyValue + ': Getchar index out of range.\n')
                            sys.exit(58)
                    else:
                        sys.stderr.write('Error in instruction ' + keyValue + ': You can only index string with integer.\n')
                        sys.exit(53)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can use strlen only with string.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'setchar':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                copyVal = extractValueFromSymb(1, keyValue)
                type = getTypeOfSymb(copyVal)
                if type == 'string':
                    copyVal2 = extractValueFromSymb(2, keyValue)
                    type2 = getTypeOfSymb(copyVal2)
                    if type2 == 'int':
                        copyVal2 = copyVal2.replace('+', '')
                        withoutEscapeSeqs = re.sub(r'\\[0-9]{3}', '.', copyVal)
                        length = len(withoutEscapeSeqs)
                        if int(copyVal2) >= 0 and int(copyVal2) < length:
                            copyVal3 = extractValueFromSymb(3, keyValue)
                            type3 = getTypeOfSymb(copyVal3)
                            if type3 == 'string':
                                matches = re.findall(r'\\[0-9]{3}', copyVal)
                                result = withoutEscapeSeqs[int(copyVal2) - 1:int(copyVal2)]
                                if result == '.':
                                    sliced = withoutEscapeSeqs[0:int(copyVal2)+1]
                                    index = sliced.count('.')
                                    matches[index - 1] = copyVal3[0]
                                else:
                                    withoutEscapeSeqs = withoutEscapeSeqs[:copyVal2] + copyVal3[0] + withoutEscapeSeqs[copyVal2 + 1:]
                                for i in matches:
                                    withoutEscapeSeqs = withoutEscapeSeqs.replace('.', i, 1)
                                frameObject.setVal(name, withoutEscapeSeqs)
                            else:
                                sys.stderr.write('Error in instruction ' + keyValue + ': You can only replace by char.\n')
                                sys.exit(53)
                        else:
                            sys.stderr.write('Error in instruction ' + keyValue + ': Setchar index out of range.\n')
                            sys.exit(58)
                    else:
                        sys.stderr.write('Error in instruction ' + keyValue + ': You can only index string with integer.\n')
                        sys.exit(53)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can use setchar only with string.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'stri2int':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                if type == 'string':
                    copyVal2 = extractValueFromSymb(3, keyValue)
                    type2 = getTypeOfSymb(copyVal2)
                    if type2 == 'int':
                        withoutEscapeSeqs = re.sub(r'\\[0-9]{3}', '.', copyVal)
                        length = len(withoutEscapeSeqs)
                        copyVal2 = copyVal2.replace('+', '')
                        if int(copyVal2) >= 0 and int(copyVal2) < length:
                            matches = re.search(r'\\[0-9]{3}', copyVal)
                            result = withoutEscapeSeqs[int(copyVal2):int(copyVal2)+1]
                            if result == '.':
                                copyVal = withoutEscapeSeqs[0:int(copyVal2)+1]
                                index = copyVal.count('.')
                                result = matches[index - 1]
                                match = re.search(r'[1-9][0-9]{1,2}', result)
                                frameObject.setVal(name, match[0])
                            else:
                                frameObject.setVal(name, str(ord(result)))
                        else:
                            sys.stderr.write('Error in instruction ' + keyValue + ': Stri2int index out of range.\n')
                            sys.exit(58)
                    else:
                        sys.stderr.write(
                            'Error in instruction ' + keyValue + ': You can only index string with integer.\n')
                        sys.exit(53)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can use strlen only with string.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'int2char':
            frame, at, name = instructionTree[keyValue].arg1Val.partition('@')
            frameObject = chooseFrame(frame)
            if frameObject.variableExists(name):
                copyVal = extractValueFromSymb(2, keyValue)
                type = getTypeOfSymb(copyVal)
                if type == 'int':
                    try:
                        val = chr(int(copyVal))

                    except ValueError:
                        sys.stderr.write('Error in instruction ' + keyValue + ': Int2char index out of range.\n')
                        sys.exit(58)
                    frameObject.setVal(name, val)
                else:
                    sys.stderr.write('Error in instruction ' + keyValue + ': You can use int2char only with int.\n')
                    sys.exit(53)
            else:
                sys.stderr.write('Error in instruction ' + keyValue + ': This variable doesn\'t exist.\n')
                sys.exit(54)
        elif instructionTree[keyValue].opcode == 'add':
            doArithmeticOperation(keyValue, '+')
        elif instructionTree[keyValue].opcode == 'sub':
            doArithmeticOperation(keyValue, '-')
        elif instructionTree[keyValue].opcode == 'mul':
            doArithmeticOperation(keyValue, '*')
        elif instructionTree[keyValue].opcode == 'idiv':
            doArithmeticOperation(keyValue, '/')
        elif instructionTree[keyValue].opcode == 'lt':
            compare(keyValue, 'lt')
        elif instructionTree[keyValue].opcode == 'gt':
            compare(keyValue, 'gt')
        elif instructionTree[keyValue].opcode == 'eq':
            compare(keyValue, 'eq')
        elif instructionTree[keyValue].opcode == 'and':
            boolOp(keyValue, 'and')
        elif instructionTree[keyValue].opcode == 'or':
            boolOp(keyValue, 'or')
        elif instructionTree[keyValue].opcode == 'not':
            boolOp(keyValue, 'not')
        else:
            sys.stderr.write('Error in instruction ' + keyValue + ': Unsupported instruction.\n')
            sys.exit(52)


        # end of main while loop


        if jumpInstr != 0:
            instructionPointer = int(jumpInstr)
        else:
            instructionPointer = instructionPointer + 1





else:
    sys.stderr.write('It seems you used wrong parameters. Try it again or use --help.\n')
    sys.exit(10)