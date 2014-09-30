import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import math

nodeName = "RippleDeformer"
nodeId = OpenMaya.MTypeId(0x102fff)


class Ripple(OpenMayaMPx.MPxDeformerNode):
    '''
    Commands ----> MPxCommand
    Custom   ----> MPxNode
    Deformer ----> MPxDeformerNode
    '''
    mObj_Amplitude = OpenMaya.MObject()
    mObj_Displace = OpenMaya.MObject()

    def __init__(self):
        OpenMayaMPx.MPxDeformerNode.__init__(self)

    def deform(self, dataBlock, geoIterator, matrix, geometryIndex):
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

        # Amplitude
        dataHandleAmplitude = dataBlock.inputValue(Ripple.mObj_Amplitude)
        amplitudeValue = dataHandleAmplitude.asFloat()

        # Displace
        dataHandleDisplace = dataBlock.inputValue(Ripple.mObj_Displace)
        displaceValue = dataHandleDisplace.asFloat()

        mFloatVectorArray_normal = OpenMaya.MFloatVectorArray()
        mFnMesh = OpenMaya.MFnMesh(inMesh)
        mFnMesh.getVertexNormals(
            False, mFloatVectorArray_normal, OpenMaya.MSpace.kObject)

        mPointArray_meshVert = OpenMaya.MPointArray()
        while(not geoIterator.isDone()):
            pointPosition = geoIterator.position()
            pointPosition.x = pointPosition.x + math.sin(geoIterator.index() + displaceValue) * amplitudeValue * mFloatVectorArray_normal[geoIterator.index()].x * envelopeValue
            pointPosition.y = pointPosition.y + math.sin(geoIterator.index() + displaceValue) * amplitudeValue * mFloatVectorArray_normal[geoIterator.index()].y * envelopeValue
            pointPosition.z = pointPosition.z + math.sin(geoIterator.index() + displaceValue) * amplitudeValue * mFloatVectorArray_normal[geoIterator.index()].z * envelopeValue
            mPointArray_meshVert.append(pointPosition)
            #geoIterator.setPosition(pointPosition)
            geoIterator.next()
        geoIterator.setAllPositions(mPointArray_meshVert)


def deformerCreator():
    nodePtr = OpenMayaMPx.asMPxPtr(Ripple())
    return nodePtr


def nodeInitializer():
    '''
    Create Attributes - check
    Attach Attributes - check
    Design Circuitry  - check
    '''
    mFnAttr = OpenMaya.MFnNumericAttribute()
    Ripple.mObj_Amplitude = mFnAttr.create(
        "AmplitudeValue", "AmplitudeVal", OpenMaya.MFnNumericData.kFloat, 0.0)
    mFnAttr.setKeyable(1)
    mFnAttr.setMin(0.0)
    mFnAttr.setMax(1.0)

    Ripple.mObj_Displace = mFnAttr.create(
        "DisplaceValue", "DispVal", OpenMaya.MFnNumericData.kFloat, 0.0)
    mFnAttr.setKeyable(1)
    mFnAttr.setMin(0.0)
    mFnAttr.setMax(10.0)

    Ripple.addAttribute(Ripple.mObj_Amplitude)
    Ripple.addAttribute(Ripple.mObj_Displace)
    '''
    SWIG - Simplified Wrapper Interface Generator
    '''
    outputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
    Ripple.attributeAffects(Ripple.mObj_Amplitude, outputGeom)
    Ripple.attributeAffects(Ripple.mObj_Displace, outputGeom)


def initializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject, "Chayan Vinayak", "1.0")
    try:
        mplugin.registerNode(
            nodeName, nodeId,
            deformerCreator, nodeInitializer,
            OpenMayaMPx.MPxNode.kDeformerNode)
    except:
        sys.stderr.write("Failed to register node: %s" % nodeName)
        raise


def uninitializePlugin(mobject):
    mplugin = OpenMayaMPx.MFnPlugin(mobject)
    try:
        mplugin.deregisterNode(nodeId)
    except:
        sys.stderr.write("Failed to deregister node: %s" % nodeName)
        raise
