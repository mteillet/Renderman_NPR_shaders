import maya.cmds as cmds

###             Main function               ####
def main():
    selectionList = firstSelection()
    print (selectionList)
    camList = cameraDirVec(selectionList)
    faceNormals = polyNormals(selectionList)
    vectorProduct = compareVectors(camList, faceNormals)

####            Separating the first selection with cam and geo variables                 ####
def firstSelection():
    selection = cmds.ls(selection = True)
    return(selection)


####            Getting the camera direction vector             ####
def cameraDirVec(selectionList):
    cmds.select(selectionList[0])
    invertedCam = cmds.xform(query = True, matrix = True, worldSpace = True)[8:11]
    #Setting variables for the 
    invCount = 0
    matrixCam = []
    #Inverting the vector direction to point in the camera view
    for i in invertedCam:
        matrixCam.append(invertedCam[invCount] * -1)
        invCount += 1
    print(matrixCam)
    return (matrixCam)
    
####            Getting the normal verctors for all the geo's faces         #### 
def polyNormals(selectionList):
    cmds.select(selectionList[1])
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
    sublistGeoNormals = []
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
def compareVectors(camList, faceNormals):
    print(camList)
    print(faceNormals[1])
    current = 0
    for i in faceNormals:
        faceNormals[current][0] = camList[0] * float(faceNormals[current][0])
        faceNormals[current][1] = camList[1] * float(faceNormals[current][1])
        faceNormals[current][2] = camList[2] * float(faceNormals[current][2])
        current += 1
    print(comparedVectors[1])
    return(faceNormals)

####        Need to store the face IDs          ####
# Face IDs and output of compare vectors function will have the same indexes
# if compared vectors output is close to 0
# store its corresponding face ID in a new list, in order to be able to select it and create geometry on it
# need to convert euclidian to degrees for face normals data ?



if __name__ == '__main__':
    main()