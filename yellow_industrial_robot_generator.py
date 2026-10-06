import bpy, math
from mathutils import Vector

# Yellow Industrial Robot - procedural game-asset starter
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

def material(name, color, metallic=0.4, roughness=0.35, emission=None):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1)
    m.use_nodes=True; p=m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value=(*color,1)
    p.inputs["Metallic"].default_value=metallic
    p.inputs["Roughness"].default_value=roughness
    if emission:
        p.inputs["Emission Color"].default_value=(*emission,1)
        p.inputs["Emission Strength"].default_value=5
    return m

YELLOW=material("Industrial Yellow",(0.95,0.48,0.035),.55,.30)
DARK=material("Charcoal",(0.045,0.055,0.065),.8,.32)
GRAY=material("Warm Gray",(.34,.35,.34),.6,.38)
LIGHT=material("Light Armor",(.62,.61,.57),.55,.36)
BLUE=material("Eye Glow",(.01,.18,1),.1,.2,(.01,.3,1))
BLACK=material("Rubber",(.012,.014,.016),.05,.7)
ORANGE=material("Orange",(1,.20,.01),.4,.3)

def cube(name,loc,scale,mat,bevel=.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    if bevel:
        b=o.modifiers.new("Bevel","BEVEL"); b.width=bevel; b.segments=3
    o.data.materials.append(mat); return o

def cyl(name,loc,radius,depth,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object; o.name=name; o.data.materials.append(mat)
    b=o.modifiers.new("Bevel","BEVEL"); b.width=min(radius*.15,.06); b.segments=2
    return o

bpy.ops.object.empty_add(type="PLAIN_AXES",location=(0,0,3.5))
root=bpy.context.object; root.name="ROBOT_ROOT"
bpy.context.view_layer.update()

# keep each part at its modeled world position when parenting to the offset root
def P(o): o.parent=root; o.matrix_parent_inverse=root.matrix_world.inverted()

# torso
for n,l,s,m,b in [
("Torso_Main",(0,0,4.35),(1.35,.68,1.25),DARK,.16),
("Chest_Armor",(0,-.70,4.55),(1.16,.14,.88),YELLOW,.10),
("Chest_Lower",(0,-.84,3.95),(.78,.10,.30),LIGHT,.06),
("Backpack",(0,.78,4.45),(1.10,.38,1.05),YELLOW,.13),
("Backpack_Center",(0,1.18,4.45),(.65,.10,.65),LIGHT,.07),
("Hip_Core",(0,0,2.85),(.72,.55,.40),DARK,.10)]:
    P(cube(n,l,s,m,b))

# head
P(cyl("Neck",(0,0,5.62),.34,.35,DARK))
P(cube("Head",(0,-.02,6.22),(.78,.68,.55),LIGHT,.13))
P(cube("Face_Screen",(0,-.69,6.22),(.60,.055,.34),DARK,.07))
for x in (-.28,.28): P(cube("Eye",(x,-.76,6.22),(.17,.025,.19),BLUE,.08))
P(cyl("Side_Sensor",(.83,-.03,6.25),.23,.16,ORANGE,(0,math.radians(90),0)))
P(cyl("Antenna_Base",(-.55,-.02,6.82),.10,.12,DARK))
P(cyl("Antenna",(-.55,-.02,7.15),.035,.62,DARK))
P(cyl("Antenna_Tip",(-.55,-.02,7.47),.075,.10,ORANGE))

# shoulders and arms
for x,side in [(-1.48,"L"),(1.48,"R")]:
    P(cyl(f"{side}_Shoulder", (x,0,5.05),.42,.34,DARK,(0,math.radians(90),0)))
    P(cube(f"{side}_Shoulder_Armor",(x,0,5.05),(.38,.55,.48),YELLOW,.10))
    P(cube(f"{side}_UpperArm",(x,-.02,4.45),(.38,.45,.58),GRAY,.10))
    P(cyl(f"{side}_Elbow",(x,-.02,3.75),.27,.35,DARK,(0,math.radians(90),0)))
    P(cube(f"{side}_Forearm",(x,-.12,3.30),(.34,.42,.48),YELLOW,.10))
    P(cyl(f"{side}_Wrist",(x,-.12,2.76),.18,.28,DARK))
    P(cube(f"{side}_Palm",(x,-.20,2.48),(.31,.22,.32),LIGHT,.08))
    for i in range(3):
        P(cube(f"{side}_Finger_{i}",(x+(i-1)*.13,-.47,2.25),(.055,.11,.20),DARK,.04))

# hips and legs
for x,side in [(-.72,"L"),(.72,"R")]:
    P(cyl(f"{side}_Hip",(x,0,2.70),.34,.35,DARK,(0,math.radians(90),0)))
    P(cube(f"{side}_Hip_Armor",(x,-.08,2.78),(.42,.42,.34),YELLOW,.08))
    P(cube(f"{side}_Thigh",(x,0,2.05),(.43,.47,.68),GRAY,.10))
    P(cyl(f"{side}_Knee",(x,-.02,1.30),.30,.38,DARK,(0,math.radians(90),0)))
    P(cube(f"{side}_Knee_Armor",(x,-.30,1.35),(.34,.12,.30),YELLOW,.06))
    P(cube(f"{side}_Shin",(x,0,.72),(.38,.45,.60),LIGHT,.10))
    P(cyl(f"{side}_Ankle",(x,-.02,.05),.25,.30,DARK))
    P(cube(f"{side}_Foot",(x,-.34,-.20),(.52,.72,.28),YELLOW,.12))
    P(cube(f"{side}_Sole",(x,-.34,-.48),(.53,.70,.10),DARK,.05))

# ground
bpy.ops.mesh.primitive_plane_add(size=30,location=(0,0,-.60))
bpy.context.object.data.materials.append(DARK)

# lights
for loc,energy,size in [((4,-6,9),1000,5),((-5,-2,5),600,4),((0,4,7),900,3)]:
    bpy.ops.object.light_add(type="AREA",location=loc)
    l=bpy.context.object; l.data.energy=energy; l.data.shape="DISK"; l.data.size=size
    l.rotation_euler=(math.radians(35),0,math.radians(25))

# camera
bpy.ops.object.camera_add(location=(10,-15,7))
cam=bpy.context.object
direction=Vector((0,0,3.4))-cam.location
cam.rotation_euler=direction.to_track_quat("-Z","Y").to_euler()
cam.data.lens=58
bpy.context.scene.camera=cam

scene=bpy.context.scene
scene.render.engine="BLENDER_EEVEE_NEXT"
scene.render.resolution_x=800; scene.render.resolution_y=900; scene.render.resolution_percentage=100
scene.world.color=(.025,.025,.03)
bpy.context.view_layer.objects.active=root
root.select_set(True)

print("Robot generated. Modular objects are named for editing and future rigging.")
