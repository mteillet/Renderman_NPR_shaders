import maya.cmds as cmds
import math

###             Main function               ####
def main():
    # Get the original selection
    selectionList = firstSelection()
    # Duplicate the selection in order to perform stylization on the duplicate
    newMesh = duplicateMesh(selectionList)
    # Get the Camera Direction Vector
    camList = cameraDirVec(selectionList)
    # Get the normal vector of every face in the selected geo
    faceNormals = polyNormals(newMesh)
    # Gets Compares the vectors using a threshold and returns a list of ints corresponding to indexes of faces under the threshold
    faceIndexes = compareVectors(camList, faceNormals)
    # Selects the faces corresponding to the threshold
    getFaceMatrices(faceIndexes, newMesh)


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
    nbNormals = len(geoNormals)-1
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
    return (sublistGeoNormals)

####        Comparing all normal vectors to the camera direction vector         ####
####        Returns a threshold indexes list containing the indexes of the faces corresponding to the threshold         ####
def compareVectors(camList, faceNormals):
    ####    Variables
    threshold = 0.45
    productNormal = []
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
        current += 1
    return(thresholdIndexes)

####    Selects the facing ratio faces according to the threshold and the index set in the comparVectors function
def getFaceMatrices(faceIndexes, newMesh):
    cmds.select(newMesh)
    ####    Variables
    translateZ = 1
    rotateZ = 0
    ####    Function
    current = 0
    facingRatio = []
    print("Processing, wait...")
    for i in faceIndexes:
        facingRatio.append(str(newMesh) + ".f[" + str(faceIndexes[current]) + "]")
        current += 1
    current = 0
    print ("Z faces offset is" + str(translateZ))
    print ("Z faces Rotation is" + str(rotateZ))
    print ("creating faces, wait...")
    polyString = ', '.join(map(str, facingRatio))
    print (polyString) 
    print (facingRatio[0:-1])
    cmds.polyChipOff( facingRatio[0:-1], duplicate = True, localTranslateZ = translateZ, keepFacesTogether = False)

#   Try to duplicate original before face creation, after face creation on the new mesh, delete the original face ?
    
# store its corresponding face ID in a new list, in order to be able to select it and create geometry on it
# need to convert euclidian to degrees for face normals data ?



if __name__ == '__main__':
    main()