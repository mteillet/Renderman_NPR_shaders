import maya.cmds as cmds
import math
import pymel.core as pm

###             Main function               ####
def main():
    # Get the original selection
    selectionList = firstSelection()
    # Duplicate the selection in order to perform stylization on the duplicate
    newMesh = duplicateMesh(selectionList)
    # Get the Camera Direction Vector
    camList = cameraDirVec(selectionList)
    # Get the normal vector of every face in the selected geo
    allPolyReturns = polyNormals(newMesh)
    faceNormals = allPolyReturns[0]
    originalFaces = allPolyReturns[1]
    # Gets Compares the vectors using a threshold and returns a list of ints corresponding to indexes of faces under the threshold
    returnVectors = compareVectors(camList, faceNormals)
    faceIndexes = returnVectors[0]
    thresoldRatio = returnVectors[1]
    # Selects the faces corresponding to the threshold, duplicates them and deletes the original faces
    # Offset and scaling is done in this function
    createFaces(faceIndexes, newMesh, originalFaces)
    # Orienting the face to the camera direction vector
    facePoly = orientFaces(faceNormals, camList, newMesh, thresoldRatio)
    # Scaling the UV shells
    scaleUVs(facePoly)
    # Duplicating the currently assigned shader
    duplicateShader(newMesh)
    


####            Separating the first selection with cam and geo variables                 ####
def firstSelection():
    selection = cmds.ls(selection = True)
    cmds.select(clear = True)
    return(selection)

####            Makes a copy of the original mesh in order to perform stylization on it
def duplicateMesh(selectionList):
    cmds.select(selectionList[1])
    newMesh = cmds.duplicate()
    newMesh = cmds.rename(newMesh, "stylisedMesh#")
    return(newMesh)

####            Getting the camera direction vector             ####
def cameraDirVec(selectionList):
    ####    Variables
    matrixCam = []
    ####    Function
    cmds.select(selectionList[0])
    invertedCam = cmds.xform(query = True, matrix = True, worldSpace = True)[8:11]
    #Setting variables for the 
    invCount = 0
    #Inverting the vector direction to point in the camera view
    for i in invertedCam:
        matrixCam.append(invertedCam[invCount] * -1)
        invCount += 1
    print(matrixCam)
    return (matrixCam)
    
####            Getting the normal verctors for all the geo's faces         #### 
def polyNormals(newMesh):
    ####    Variables
    sublistGeoNormals = []
    tempFaces = []
    originalFaces = []
    cmds.select(newMesh)
    ####    Function
    geoNormals = cmds.polyInfo(faceNormals = True)
    #Geo normals cannot be used as it is, as each item returned corresponds to one face and is described as it follows : 
    #       FACE_NORMAL      1: 0.440016 -0.725507 0.529174
    #       FACE_NORMAL    120: 0.062810 0.989723 0.128464
    #In order to be able to use the data, we need to get rid of the first 20 elements of every item of the list
    #       0.440016 -0.725507 0.529174
    #       0.062810 0.989723 0.128464
    #And THEN split every item in a sublist, separated by the remaining spaces
    #       [0.440016,-0.725507,0.529174]
    #       [0.062810,0.989723,0.128464]
    #The first part of each string is also stored in the originalFaces variable, so that they can be deleted later on
    nbNormals = len(geoNormals)-1
    counter = 0
    for i in geoNormals:
        string = geoNormals[counter]
        tempFaces.insert(counter, string[:20])
        originalFaces.insert(counter, filter(type(tempFaces[counter]).isdigit, tempFaces[counter]))
        counter += 1
    counter = 0
    for i in originalFaces:
        originalFaces[counter]=(str(newMesh) + ".f[" + str(originalFaces[counter]) + "]")
        counter += 1
    counter = 0
    while counter < nbNormals:
        # storing the geo normal string to a temporal variable
        string = geoNormals[counter]
        # removing the first 20 elements before reassigning to the geonormals variable
        geoNormals[counter] = string[20:]
        # Split the 3 vector coordinates of the list into sublists
        sublistGeoNormals.insert(counter, geoNormals[counter].split(" "))
        counter += 1
    #Refer to sublistGeoNormals to see the new obtained list of sublists
    return (sublistGeoNormals, originalFaces)

####        Comparing all normal vectors to the camera direction vector         ####
####        Returns a threshold indexes list containing the indexes of the faces corresponding to the threshold         ####
def compareVectors(camList, faceNormals):
    ####    Variables
    threshold = 1
    productNormal = []
    thresholdPercentage = []
    
    ####    Function
    print(camList)
    print(faceNormals[1])
    current = 0
    for i in faceNormals:
        x = camList[0] * float(faceNormals[current][0])
        y = camList[1] * float(faceNormals[current][1])
        z = camList[2] * float(faceNormals[current][2])
        productNormal.insert(current, x + y + z)
        current += 1
    thresholdIndexes = []
    current = 0
    for i in productNormal:
        if math.sqrt((productNormal[current])*(productNormal[current])) < threshold:
            thresholdIndexes.append(current)
            thresholdPercentage.append(productNormal[current])
        current += 1
    return(thresholdIndexes, thresholdPercentage)

####    Selects the facing ratio faces according to the threshold and the index set in the comparVectors function
def createFaces(faceIndexes, newMesh, originalFaces):
    cmds.select(newMesh)
    ####    Variables
    translateZ = .25
    scale = 1.5
    ####    Function
    current = 0
    facingRatio = []
    print("Processing, wait...")
    for i in faceIndexes:
        facingRatio.append(str(newMesh) + ".f[" + str(faceIndexes[current]) + "]")
        current += 1
    current = 0
    print ("Z faces offset is" + str(translateZ))
    print ("Z faces Scaling is" + str(scale))
    print ("creating faces, wait...")
    cmds.polyChipOff( facingRatio[0:-1], duplicate = True, localTranslateZ = translateZ, keepFacesTogether = False, localScale = (scale, scale, scale))
    # Select the original faces and delete them other wise the script would not work on bigger objects
    cmds.delete(originalFaces)
    cmds.delete(constructionHistory = True)

# Use the camera direction vector to orient the planes
def orientFaces(faceNormals, camList, newMesh, thresoldRatio):
    angleBetweenVectors = []
    geoNormals = cmds.polyInfo(faceNormals = True)
    facePoly = cmds.polyInfo(faceNormals = True)
    print(facePoly)
    # Inverting the Z axis of the Camera direction vector
    camList[2] = -(camList[2])
    current = 0
    # Getting the normal of each face
    for i in geoNormals:
        geoNormals[current] = geoNormals[current][20:]
        geoNormals[current] = geoNormals[current].split(" ")
        current += 1
    # Getting the face ID for ever face
    current = 0
    for i in facePoly:
        tempString = facePoly[current][:20]
        facePoly[current] = filter(type(tempString).isdigit, tempString)
        facePoly[current]=(str(newMesh) + ".f[" + str(facePoly[current]) + "]")
        current += 1
    # Rotating all the faces according to the difference between normal and camera vectors
    # Still a bit slow, would be better to find a more efficient way to make this operation
    print("setting face rotation, wait...")
    current = 0
    print(thresoldRatio)
    for i in facePoly:
        cmds.select(facePoly[current])
        x = float(geoNormals[current][0])
        y = float(geoNormals[current][1])
        z = float(geoNormals[current][2])
        geoNormals[current] = x,y,z
        angleBetweenVectors.append((cmds.angleBetween( euler=True, v1=(geoNormals[current]), v2=(camList))))
        cmds.manipRotateContext( mode = 9, orientObject = facePoly[current], activeHandle=0, rotate = (((1 - abs(thresoldRatio[current]))*(angleBetweenVectors[current][0])), ((1 - abs(thresoldRatio[current])))*(angleBetweenVectors[current][1]), ((1 - abs(thresoldRatio[current]))*(angleBetweenVectors[current][2]))), useManipPivot = True, tweakMode = False)
        current += 1
    cmds.select(clear = True)
    cmds.delete(newMesh)
    cmds.undo()
    return(facePoly)

def scaleUVs(facePoly):
    current = 0
    for i in facePoly:
        cmds.select(facePoly[current])
        cmds.select(cmds.polyListComponentConversion(tuv = True), r = True)
        pivots = cmds.polyEditUV( query=True )
        ptPivotU = (( pivots[0] + pivots[2] + pivots[4] + pivots[6] ) / 4 )
        ptPivotV = (( pivots[1] + pivots[3] + pivots[5] + pivots[7] ) / 4 )
        cmds.polyEditUV(scaleU = 0.1, scaleV = 0.1, pivotU = ptPivotU, pivotV = ptPivotV)
        current += 1

def duplicateShader(newMesh):
    cmds.select(newMesh)
    # Get the shader currently applied
    originalShader = cmds.listConnections(cmds.listHistory(newMesh), type = 'shadingEngine')
    cmds.select(originalShader)
    newShader = pm.duplicate(originalShader, un=True)
    cmds.select(newShader)
    # Setting new string for new shading nodes name
    # Need loop
    
    newSTR = ((str(newShader[0])) + "_BITE")
    print(newSTR)
    cmds.rename(str(newShader[0]), str(newSTR))

if __name__ == '__main__':
    main()