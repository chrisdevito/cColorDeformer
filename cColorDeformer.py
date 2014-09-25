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
    '''
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
        pass


def nodeCreator():
    return OpenMayaMPx.asMPxPtr(cColorDeformer())


def nodeInitializer():
    '''
    Initializes attributes for the node.
    '''
    pass


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
