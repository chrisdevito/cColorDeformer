import maya.cmds as cmds
import maya.OpenMaya as OpenMaya

if __name__ == '__main__':

    meshA, meshB = "pSphere1", "pSphere2"

    #Add MSelection.
    mSel = OpenMaya.MSelectionList()
    mSel.add(meshA)
    mSel.add(meshB)

    cmds.polyColorPerVertex(
        meshA, colorRGB=[0.0, 0.0, 1.0], alpha=1.0, colorDisplayOption=True)

    #Set Mesh.
    source_mDagPath = OpenMaya.MDagPath()
    collider_mDagPath = OpenMaya.MDagPath()

    # Get DagPath and extend to shape.
    mSel.getDagPath(0, source_mDagPath)
    source_mDagPath.extendToShape()

    # Get DagPath and extend to shape.
    mSel.getDagPath(1, collider_mDagPath)
    collider_mDagPath.extendToShape()

    #Get points.
    collider_MfnMesh = OpenMaya.MFnMesh(collider_mDagPath)
    collider_Pnts = OpenMaya.MFloatPointArray()
    collider_MfnMesh.getPoints(collider_Pnts, OpenMaya.MSpace.kObject)

    #Get Bounding box.
    collider_BBVec = OpenMaya.MVector(
        *cmds.getAttr("%s.boundingBox.boundingBoxSize" % meshB)[0])

    #BondingBBSize and threshhold.
    thresholdValue = collider_BBVec.length()*2

    #Accelerator.
    mmAccelParams = collider_MfnMesh.autoUniformGridParams()

    #Get points.
    source_MfnMesh = OpenMaya.MFnMesh(source_mDagPath)
    source_Pnts = OpenMaya.MFloatPointArray()
    source_MfnMesh.getPoints(source_Pnts, OpenMaya.MSpace.kWorld)

    #Defining used variables.
    checkCollision = 0
    maxDeformation = 0.0
    dummyFloatArray = OpenMaya.MFloatArray()
    source_pntNormal = OpenMaya.MVector()


    #Get Vertex color.
    vertexColorList = OpenMaya.MColorArray()
    source_MfnMesh.getVertexColors(vertexColorList)
    collideColor = OpenMaya.MColor(1.0, 0.0, 0.0, 1.0)
    lenVertexList = vertexColorList.length()

    #Get Vert list.
    fnComponent = OpenMaya.MFnSingleIndexedComponent()
    fullComponent = fnComponent.create(OpenMaya.MFn.kMeshVertComponent)
    fnComponent.setCompleteData(lenVertexList)
    vertexIndexList = OpenMaya.MIntArray()
    fnComponent.getElements(vertexIndexList)

    # direct collision deformation:
    for k in xrange(source_Pnts.length()):
        source_MfnMesh.getVertexNormal(
            k, source_pntNormal, OpenMaya.MSpace.kWorld)

        # define an intersection ray from the mesh that should be deformed
        raySource = OpenMaya.MFloatPoint(source_Pnts[k].x,
                                         source_Pnts[k].y,
                                         source_Pnts[k].z)
        rayDirection = OpenMaya.MFloatVector(source_pntNormal)

        # MeshFn.allIntersections variables
        faceIds = None
        triIds = None
        idsSorted = True
        space = OpenMaya.MSpace.kWorld
        maxParam = thresholdValue
        tolerance = 1e-9
        testBothDirs = True
        accelParams = mmAccelParams
        sortHits = True
        hitPoints = OpenMaya.MFloatPointArray()
        hitRayParams = OpenMaya.MFloatArray(dummyFloatArray)
        hitFaces = None
        hitTriangles = None
        hitBary1s = None
        hitBary2s = None

        gotHit = collider_MfnMesh.allIntersections(
            raySource,
            rayDirection,
            faceIds,
            triIds,
            idsSorted,
            space,
            maxParam,
            testBothDirs,
            accelParams,
            sortHits,
            hitPoints,
            hitRayParams,
            hitFaces,
            hitTriangles,
            hitBary1s,
            hitBary2s)

        if gotHit:

            hitCount = hitPoints.length()

            #Check for direction (Negative means it is inside mesh.).
            for i in xrange(hitCount-1):
                if hitRayParams[i] * hitRayParams[i+1] < 0:
                    signChange = i
                    break
                else:
                    signChange = -1000

            collision = 0

            #Check collision on.
            if hitCount == 2 and signChange+1 == 1 and signChange != -1000:
                collision = 1
            elif hitCount > 2 and hitCount/(signChange+1) != 2 and signChange != -1000:
                collision = 1

            if collision == 1:
                vertexColorList.set(collideColor, k)

    source_MfnMesh.setVertexColors(vertexColorList, vertexIndexList, None)