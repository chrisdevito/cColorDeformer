# import math
import sys
# import array
import copy
# import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
# import maya.OpenMayaAnim as OpenMayaAnim

kPluginNodeTypeName = "cColorDeformer"
kPluginNodeId = OpenMaya.MTypeId(0x96427)


class cColorDeformer(OpenMayaMPx.MPxDeformerNode):
    '''
    Color Collsion Deformer.
    '''
    #Collider object.
    collider = OpenMaya.MObject()
    colliderMatrix = OpenMaya.MObject()
    colliderBBoxSize = OpenMaya.MObject()
    newpoints = OpenMaya.MFloatPointArray()
    mmAccelParams = OpenMaya.MMeshIsectAccelParams()

    def __init__(self):
        '''
        Initializer.
        '''
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def compute(self, plug, dataBlock):
        '''
        Compute function for the node. Calculates all dat maths.
        @param plug - Current plug that is affected.
        @param dataBlock - Datablock that holds all data.
        '''
        colliderPointNormal = OpenMaya.MVector()
        pointNormal = OpenMaya.MVector()
        emptyFloatArray = OpenMaya.MFloatArray()
        deformedPointsIndices = []
        pointInfo = OpenMaya.MPointOnMesh()

        # deformer handle
        multiIndex = plug.logicalIndex()
        thisNode = self.thisMObject()

        envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        envelopeHandle = dataBlock.inputValue(envelope)
        envelopeValue = envelopeHandle.asFloat()

        # intput geometry data
        inputGeo = OpenMayaMPx.cvar.MPxDeformerNode_input
        hInput = dataBlock.inputArrayValue(inputGeo)
        hInput.jumpToArrayElement(multiIndex)

        inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        groupId = OpenMayaMPx.cvar.MPxDeformerNode_groupId

        hInputElement = hInput.inputValue()
        hInputGeom = hInputElement.child(inputGeom)

        inMesh = hInputGeom.asMesh()
        inMeshFn = OpenMaya.MFnMesh(inMesh)

        inPoints = OpenMaya.MFloatPointArray()
        colliderPoints = OpenMaya.MFloatPointArray()
        inMeshFn.getPoints(inPoints, OpenMaya.MSpace.kWorld)

        if self.newpoints.length() == 0:
            self.newpoints = copy.copy(inPoints)

        hOutput = dataBlock.outputValue(plug)
        hOutput.copy(hInputGeom)

        outMesh = hInputGeom.asMesh()
        outMeshFn = OpenMaya.MFnMesh(outMesh)

        colliderHandle = dataBlock.inputValue(self.collider)

        pcounts = OpenMaya.MIntArray()
        pconnect = OpenMaya.MIntArray()

        colliderObject = colliderHandle.asMesh()
        colliderFn = OpenMaya.MFnMesh(colliderObject)
        colliderIter = OpenMaya.MItMeshVertex(colliderHandle.asMesh())
        polycount = colliderFn.numPolygons()
        colliderFn.getVertices(pcounts, pconnect)
        colliderFn.getPoints(colliderPoints, OpenMaya.MSpace.kObject)

        vertexcount = self.newpoints.length()

        dataCreator = OpenMaya.MFnMeshData()
        newColliderData = OpenMaya.MObject(dataCreator.create())

        colliderMatrixHandle = dataBlock.inputValue(self.colliderMatrix)
        colliderMatrixValue = colliderMatrixHandle.asFloatMatrix()

        # get collider boundingbox for threshold
        colliderBBSizeHandle = dataBlock.inputValue(self.colliderBBoxSize)
        colliderBBSizeValue = colliderBBSizeHandle.asDouble3()
        colliderBBVector = OpenMaya.MVector(
            colliderBBSizeValue[0],
            colliderBBSizeValue[1],
            colliderBBSizeValue[2])
        colliderBBSize = colliderBBVector.length()
        thresholdValue = colliderBBSize*2

        newColliderPoints = OpenMaya.MFloatPointArray()

        # do the deformation
        if envelopeValue != 0:
            baseColliderPoints = copy.copy(colliderPoints)

            newColliderPoints.clear()
            for i in range(colliderPoints.length()):

                colliderFn.getVertexNormal(
                    i, colliderPointNormal, OpenMaya.MSpace.kObject)
                newColliderPoint = OpenMaya.MFloatPoint(
                    colliderPoints[i].x + colliderPointNormal.x,
                    colliderPoints[i].y+colliderPointNormal.y,
                    colliderPoints[i].z+colliderPointNormal.z)

                newColliderPoints.append(newColliderPoint)

            self.intersector.create(colliderObject, colliderMatrixValue)
            self.mmAccelParams = colliderFn.autoUniformGridParams()

        checkCollision = 0
        maxDeformation = 0.0

        # direct collision deformation:
        for k in range(self.newpoints.length()):
            inMeshFn.getVertexNormal(k, pointNormal , OpenMaya.MSpace.kWorld)

            # define an intersection ray from the mesh that should be deformed
            raySource = OpenMaya.MFloatPoint(self.newpoints[k].x , self.newpoints[k].y , self.newpoints[k].z )
            rayDirection = OpenMaya.MFloatVector(pointNormal)

            point = OpenMaya.MPoint(self.newpoints[k])

            # MeshFn.allIntersections variables
            faceIds = None
            triIds = None
            idsSorted = True
            space = OpenMaya.MSpace.kWorld
            maxParam = thresholdValue
            tolerance = 1e-9

            # testBothDirs = False
            testBothDirs = True
            accelParams = self.mmAccelParams
            sortHits = True
            hitPoints1 = OpenMaya.MFloatPointArray()
            hitRayParams = OpenMaya.MFloatArray(emptyFloatArray)
            hitFaces = None
            hitTriangles = None
            hitBary1s = None
            hitBary2s = None

            try:
                gotHit = colliderFn.allIntersections(
                    raySource, rayDirection, faceIds,
                    triIds, idsSorted, space, maxParam, testBothDirs,
                    accelParams, sortHits, hitPoints1, hitRayParams,
                    hitFaces, hitTriangles, hitBary1s, hitBary2s)
            except:
                break

            if gotHit:

                hitCount = hitPoints1.length()

            for i in range(hitCount-1):
                if hitRayParams[i] * hitRayParams[i+1] < 0:
                    signChange = i
                    break
                    #signChange = -1
                else:
                    signChange = -1000

            if hitCount == 2 and signChange+1 ==1 and signChange != -1000:
                collision = 1
            elif hitCount > 2 and hitCount/(signChange+1) != 2 and signChange != -1000:
                collision = 1

            if collision == 1:

                checkCollision = checkCollision+1

                # add this point to the collision array
                deformedPointsIndices.append(k)

                # get the closest point on the collider mesh
                self.intersector.getClosestPoint(point, pointInfo)

                closePoint = OpenMaya.MPoint(pointInfo.getPoint())
                closePointNormal = OpenMaya.MFloatVector(pointInfo.getNormal())

                offsetVector = OpenMaya.MVector(
                    closePointNormal.x, closePointNormal.y, closePointNormal.z)

                # normal angle check for backface culling,
                # if the angle is bigger then 90 the face lies
                # on the opposite side of the collider mesh
                angle = closePointNormal*rayDirection

                if angle > 0:
                    # ignore the backfaces, reset the point position
                    worldPoint = OpenMaya.MPoint(hitPoints1[signChange])
                else:
                    worldPoint = closePoint
                    worldPoint = worldPoint * colliderMatrixValue

                weight = self.weightValue(dataBlock, multiIndex, k)

                print(worldPoint.x, worldPoint.y, worldPoint.z)
                dataBlock.setClean(self.outputGeom)


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(cColorDeformer())


def nodeInitializer():
    '''
    Initializes attributes for the node.
    '''
    gAttr = OpenMaya.MFnGenericAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()

    #Collider Mesh.
    cColorDeformer.collider = gAttr.create("collider", "coll")
    gAttr.addDataAccept(OpenMaya.MFnData.kMesh)
    gAttr.setHidden(True)

    #Collider matrix.
    cColorDeformer.colliderMatrix = mAttr.create(
        "colliderMatrix", "colMatr")
    mAttr.setHidden(True)

    #Collider bounding box.
    cColorDeformer.colliderBBoxSize = cAttr.create("colliderBBoxSize", "cbb")
    cAttr.addChild(cColorDeformer.colliderBBoxX)
    cAttr.addChild(cColorDeformer.colliderBBoxY)
    cAttr.addChild(cColorDeformer.colliderBBoxZ)

    #Add attrs
    cColorDeformer.addAttribute(cColorDeformer.collider)
    cColorDeformer.addAttribute(cColorDeformer.colliderMatrix)
    cColorDeformer.addAttribute(cColorDeformer.colliderBBoxSize)

    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    cColorDeformer.attributeAffects(
        cColorDeformer.collider, outputGeom)
    cColorDeformer.attributeAffects(
        cColorDeformer.colliderMatrix, outputGeom)
    cColorDeformer.attributeAffects(
        cColorDeformer.colliderBBoxSize, outputGeom)


def initializePlugin(mObject):
    '''
    Initializes the plugin in maya.
    @param - mObject that maya uses to make the node.
    '''
    mplugin = OpenMayaMPx.MFnPlugin(mObject)

    try:
        mplugin.registerNode(kPluginNodeTypeName,
                             kPluginNodeId,
                             nodeCreator,
                             nodeInitializer,
                             OpenMayaMPx.MPxNode.kDeformerNode)

        sys.stderr.write("Registered node: %s\n" % kPluginNodeTypeName)

    except:
        sys.stderr.write("Failed to register node: %s\n" % kPluginNodeTypeName)
        raise


def uninitializePlugin(mObject):
    '''
    Uninitializes our plugin in maya.
    @param - mObject that maya uses to make the node.
    '''
    mplugin = OpenMayaMPx.MFnPlugin(mObject)

    try:
        mplugin.deregisterNode(kPluginNodeId)
        sys.stderr.write("Deregistered node: %s\n" % kPluginNodeTypeName)

    except:
        sys.stderr.write("Failed to register node: %s\n" % kPluginNodeTypeName)
        raise
