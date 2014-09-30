# import math
import sys
# import maya.mel as mel
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
# import maya.OpenMayaAnim as OpenMayaAnim

kPluginNodeTypeName = "cColorDeformer"
kPluginNodeId = OpenMaya.MTypeId(0x96427)


class cColorDeformer(OpenMayaMPx.MPxDeformerNode):
    '''
    Color Collsion Deformer.
    Inherits OpenMaya.MPxDeformerNode
    '''
    def __init__(self):
        '''
        Initializer.
        '''
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIterator, matrix, geometryIndex):
        '''
        Compute function for the node. Calculates all dat maths.
        @param dataBlock - Datablock that holds all data.
        @param geoIterator - Current geoIterator that is affected.
        @param matrix - Current matrix that is affected.
        @param geometryIndex - Current geometry index that is affected.
        '''
        input = OpenMayaMPx.cvar.MPxDeformerNode_input
        # 1. Attach a handle to input Array Attribute.
        dataHandleInputArray = dataBlock.outputArrayValue(input)
        # 2. Jump to particular element
        dataHandleInputArray.jumpToElement(geometryIndex)
        # 3. Attach a handle to specific data block
        dataHandleInputElement = dataHandleInputArray.outputValue()
        # 4. Reach to the child - inputGeom
        inputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
        dataHandleInputGeom = dataHandleInputElement.child(inputGeom)
        inMesh = dataHandleInputGeom.asMesh()

        #Envelope
        envelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
        dataHandleEnvelope = dataBlock.inputValue(envelope)
        envelopeValue = dataHandleEnvelope.asFloat()


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(cColorDeformer())


def nodeInitializer():
    '''
    Initializes attributes for the node.
    '''
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom


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
