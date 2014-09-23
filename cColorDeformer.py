# import math
import sys
# import array
# import copy
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
