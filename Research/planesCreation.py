import maya.cmds as cmds
import math
import pymel.core as pm
import maya.mel as mel
import rfm2

####    Script made and owned by Teillet Martin    ####
####    Special thanks to :
#               - proxe (HardOps and BoxCutter developper) for his help with matrices
#               - Tony Kaap (Autodesk Developper) for his help regarding the manipRotateContext issues


####             Main function               ####
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
    # Creating a new UVset
    newUVset(facePoly, newMesh)
    # Duplicating the currently assigned shader
    stylizedShadingGroup = duplicateShader(newMesh)
    # Creating the stylized PxrOSL Node
    setUpOSL(stylizedShadingGroup, newMesh)

    


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
    translateZ = 0
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

# Based on Tony Kaap's input
def getCenterOfFace(facePoly, current):
    facePts = cmds.xform(facePoly[current],q=1,t=1,ws=1)
    numPts = len(facePts) / 3
    center = [0]*3
    for pt in xrange(numPts):
        center[0] += facePts[pt*3]
        center[1] += facePts[pt*3+1]
        center[2] += facePts[pt*3+2]
    invNumPts = 1.0/numPts
    center[0] *= invNumPts
    center[1] *= invNumPts
    center[2] *= invNumPts

    return center

# Use the camera direction vector to orient the planes
def orientFaces(faceNormals, camList, newMesh, thresoldRatio):
    faceTranslate = 0.1
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
    # Need to hide the output from these calcultations in order to speedUp the following proccess
    for i in facePoly:
        cmds.select(facePoly[current])
        # Moving the faces
        cmds.move(((1 - abs(thresoldRatio[current]))*faceTranslate), 0, 0, facePoly[current], relative = True, componentSpace = True)
        # Get the center of the face
        faceCenter = getCenterOfFace(facePoly, current)
        # Determining the normal axis of the faces
        x = float(geoNormals[current][0])
        y = float(geoNormals[current][1])
        z = float(geoNormals[current][2])
        geoNormals[current] = x,y,z
        # Finding the angle between all the faces
        angleBetweenVectors.append((cmds.angleBetween( euler=True, v1=(geoNormals[current]), v2=(camList))))
        # Rotation of the faces
        cmds.rotate(((1 - abs(thresoldRatio[current]))*(angleBetweenVectors[current][0])), ((1 - abs(thresoldRatio[current]))*(angleBetweenVectors[current][1])), ((1 - abs(thresoldRatio[current]))*(angleBetweenVectors[current][2])), facePoly[current], pivot=faceCenter)
        current += 1
    #cmds.select(clear = True)
    #cmds.delete(newMesh)
    #cmds.undo()
    return(facePoly)

# Scalin UV shells of the new mesh in order to get as few colors as possible in the albedo
def scaleUVs(facePoly):
    current = 0
    for i in facePoly:
        cmds.select(facePoly[current])
        cmds.select(cmds.polyListComponentConversion(tuv = True), r = True)
        pivots = cmds.polyEditUV( query=True )
        # Storing the odd and even (U and V) indexes in two different lists
        Ucoord = pivots[0::2]
        Vcoord = pivots[1::2]
        ptPivotU = 0
        ptPivotV = 0
        counter = 0
        for i in Ucoord:
            ptPivotU += Ucoord[counter]
            ptPivotV += Vcoord[counter]
            counter += 1
        ptPivotU /= len(Ucoord)
        ptPivotV /= len(Vcoord)
        cmds.polyEditUV(scaleU = 0.1, scaleV = 0.1, pivotU = ptPivotU, pivotV = ptPivotV)
        current += 1

# Duplicating, renaming and assigning the new shader to the stylized mesh
def duplicateShader(newMesh):
    cmds.select(newMesh)
    # Get the shading Engine
    originalShader = cmds.listConnections(cmds.listHistory(newMesh), type = 'shadingEngine')
    cmds.select(clear = True)
    newShader = pm.duplicate(originalShader, upstreamNodes=True)
    cmds.select(newShader)
    # Setting new string for new shading group and PxrSurface name
    newShadgingGroup = ((str(newShader[0])) + "_STYLIZED")
    newPxrSurface = ((str(newShader[3])) + "_STYLIZED")
    stylizedShadingGroup = cmds.rename(str(newShader[0]), str(newShadgingGroup))
    stylizedPxrSurface = cmds.rename(str(newShader[3]), str(newPxrSurface))
    cmds.select(newMesh)
    cmds.hyperShade(assign = (stylizedPxrSurface))
    return (stylizedPxrSurface, stylizedShadingGroup)

# Creating a new UVset on which the alpha can be used
def newUVset(facePoly, newMesh):
    newUVset = "stylizedUvSet"
    cmds.select(newMesh)
    originalUvSet = cmds.polyUVSet(newMesh, query = True, allUVSets = True)
    cmds.polyUVSet( copy = True, nuv = newUVset, uvSet = originalUvSet[0] )
    cmds.polyUVSet( currentUVSet = True,  uvSet = newUVset)
    cmds.select(facePoly)
    cmds.polyForceUV( unitize = True )

# Creating the OSL node and compiling it using the .osl in the document/maya/scripts directory
# Then linking the outputRGBR to the presence of the new stylized duplicated shader
def setUpOSL(stylizedShadingGroup, newMesh):
    # Creating new PxrTexture and PxrManifold2D nodes
    # Still need to connect the pxrTexture RGBR to the presence of the pxr surface
    newPxrTexture = rfm2.api.nodes.create_node("","PxrTexture")
    newManifold = rfm2.api.nodes.create_node("","PxrManifold2D")
    newPxrTexture = newPxrTexture.split('"')
    newManifold = newManifold.split('"')
    # Connecting the manifold to the PxrTexture and the UVset[1] name to the PxrMAnifold.primvarS/T
    cmds.connectAttr(((newManifold[1])+".result"), ((newPxrTexture[1])+".manifold"))
    cmds.connectAttr((str(newMesh)+".uvSet[1].uvSetName"), (str(newManifold[1])+".primvarT"))
    cmds.connectAttr((str(newMesh)+".uvSet[1].uvSetName"), (str(newManifold[1])+".primvarS"))

    
    
if __name__ == '__main__':
    main()