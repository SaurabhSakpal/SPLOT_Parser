import xml.etree.ElementTree as ET
import sys
import re
from TreeNode import *
from Model import *
from Constraint import *


class SPLOTParser:

    def __init__(self):
        self.previousParent = {}

    def getNodeType(self, line):
        match = re.search(':[rmog]* ',line)
        if match:
            type = match.group(0)
            if len(type) == 3:
                if type[1] == 'm':
                    return "Mandatory"
                elif type[1] == 'g':
                    return "Featured Group"
                elif type[1] == 'o':
                    return "Optional"
                elif type[1] == 'r':
                    return "Root"
            elif len(type) == 2:
                if type[1] == ' ':
                    return "Group"
        else:
            raise Exception('Exception : Invalid Node Structure')


    def getNodeName(self, line):
        pattern = re.compile(':[rmog]* ')
        match = pattern.split(line)[1]
        name = match[:match.index('(')]
        return name


    def parseConstraints(self, structure, splotModel):
        lines = structure.split("\n")
        constraintList = []
        for line in lines:
            line = line.strip()
            if len(line) > 0:
                splitArr = line.split(":")
                constraintId = splitArr[0]
                cnf = splitArr[1]
                clauseList = [clause.strip() for clause in cnf.split("or")]
                treeNodeIdList = [clause if (clause.find("~") == -1) else clause[1:] for clause in clauseList]
                constraintList.append(Constraint(constraintId, clauseList, treeNodeIdList, splotModel))
        return constraintList


    def parseTree(self, structure, splotModel):
        lines = structure.split("\n")
        rootNode = ""
        count = 0
        previousId = 0;
        for line in lines:
            if len(line) > 0:
                line = line.strip()
                match = re.search('\(.*\)',line)
                if match:
                    id = match.group(0)[1:-1]
                    nodeType = self.getNodeType(line)
                    name = self.getNodeName(line)
                    if len(name) == 0:
                        name = id
                    #print id, id.count("_")
                    if count == 0:
                        previousId = id.count("_")
                        treeNode = TreeNode(id, name, nodeType)
                        self.previousParent[previousId] = treeNode
                        rootNode = treeNode
                        splotModel.addTreeNodeToMap(treeNode)
                    else :
                        currentIdLen = id.count("_")
                        if currentIdLen > previousId:
                            treeNode = TreeNode(id, name, nodeType)
                            self.previousParent[currentIdLen] = treeNode
                            self.previousParent[previousId].children.append(treeNode)
                            previousId = currentIdLen
                            splotModel.addTreeNodeToMap(treeNode)
                        elif currentIdLen < previousId:
                            treeNode = TreeNode(id, name, nodeType)
                            self.previousParent[currentIdLen] = treeNode
                            self.previousParent[currentIdLen - 1].children.append(treeNode)
                            previousId = currentIdLen
                            splotModel.addTreeNodeToMap(treeNode)
                        elif currentIdLen == previousId:
                            treeNode = TreeNode(id, name, nodeType)
                            self.previousParent[currentIdLen] = treeNode
                            self.previousParent[currentIdLen - 1].children.append(treeNode)
                            previousId = currentIdLen
                            splotModel.addTreeNodeToMap(treeNode)
                    #print previousParent
                    count += 1
                else:
                    raise Exception('EXCEPTION: ID not present on Node')
        return rootNode


    def parse(self, modelFile):
        tree = ET.parse(modelFile)
        xmlRoot = tree.getroot()
        rootNode = None
        modelName = xmlRoot.get("name")
        print "MODEL NAME: ", modelName
        splotModel = SplotModel(modelName)
        for child in xmlRoot:
            #print child.tag, child.text
            if child.tag == "feature_tree":
                rootNode = self.parseTree(child.text, splotModel);
                splotModel.updateRootNode(rootNode)
            elif child.tag == "constraints":
                constraintList = self.parseConstraints(child.text, splotModel)
                splotModel.setConstraints(constraintList)
        return splotModel


def main():
    assert len(sys.argv) == 2, "SPLOT Parser takes path to model.xml file as argument"
    modelFile = sys.argv[1]
    model = SPLOTParser().parse(modelFile)
    model.printTree(model.root, 0)
    model.printConstraints()

if __name__ == "__main__":
    main()