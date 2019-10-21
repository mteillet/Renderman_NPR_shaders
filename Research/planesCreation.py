import maya.cmds as cmds

###             Main function               ####
def main():
    firstSelection()
    camList = cameraDirVec(firstSelection)
    faceNormals = polyNormals(firstSelection)
    compareVectors(camList, faceNormals)

####            Separating the first selection with cam and geo variables                 ####
def firstSelection():
    selection = cmds.ls(selection = True)
    cam = selection[0]
    geo = selection[1]
    return(cam, geo)

####            Getting the camera direction vector             ####
def cameraDirVec(firstSelection):
    cmds.select(cam)
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
def polyNormals(firstSelection):
    cmds.select(geo)
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
    comparedVectors = []
    for i in faceNormals:
        x = camList[0] * float(faceNormals[current][0])
        y = camList[1] * float(faceNormals[current][1])
        z = camList[2] * float(faceNormals[current][2])
        comparedVectors[current].insert(x)
        comparedVectors[current].insert(y)
        comparedVectors[current].insert(z)
        current += 1
    print(comparedVectors[1])

        
        


if __name__ == '__main__':
    main()