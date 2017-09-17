bl_info = {
    "name": "Bone utils",
    "description": "Some practical functions for bones",
    "author": "Samuel Bernou",
    "version": (0, 0, 3),
    "blender": (2, 77, 0),
    "location": "View3D",
    "warning": "",
    "wiki_url": "",
    "category": "Object" }


import bpy, re, os

from mathutils import *
from math import radians


def check_widget(ob, link=True):
    if not bpy.context.scene.objects.get(ob.name):
        if link:
            print('linking', ob.name, "to scene")
            bpy.context.scene.objects.link(ob)
            ob.layers = [i==9 for i in range(20)]
        else:
            print(ob.name, 'not in scene')

def VertexGroupToBone(ob, targetRig, targetBone, context):
    '''
    Add a vertex group to the object named afer the given bone
    assign full weight to this vertex group
    return a list of bypassed object (due to vertex group already existed)
    '''

    #if the vertex group related to the chosen bone is'nt here, create i and Skin parent (full weight)
    if not targetBone in [i.name for i in ob.vertex_groups]:
        vg = ob.vertex_groups.new(name=targetBone)

    else: #vertex group exist, or weight it (leave it untouched ?)
        vg = ob.vertex_groups[targetBone]

    verts = [i.index for i in ob.data.vertices]
    vg.add(verts, 1, "ADD")


def CreateArmatureModifier(ob, targetRig):
    '''
    Create armature modifier if necessary and place it on top of stack
    or just after the first miror modifier
    return a list of bypassed objects
    '''

    #get object from armature data with a loop (only way to get armature's owner)
    for obArm in bpy.data.objects:
        if obArm.type == 'ARMATURE' and obArm.data.name == targetRig:
            ArmatureObject = obArm

    #add armature modifier that points to designated rig:
    if not 'ARMATURE' in [m.type for m in ob.modifiers]:
        mod = ob.modifiers.new('Armature', 'ARMATURE')
        mod.object = ArmatureObject#bpy.data.objects[targetRig]

        #bring Armature modifier to the top of the stack
        pos = 1
        if 'MIRROR' in [m.type for m in ob.modifiers]:
            #if mirror, determine it's position
            for mod in ob.modifiers:
                if mod.type == 'MIRROR':
                    pos += 1
                    break
                else:
                    pos += 1

        if len(ob.modifiers) > 1:
            for i in range(len(ob.modifiers) - pos):
                bpy.ops.object.modifier_move_up(modifier="Armature")

    else: #armature already exist
        for m in ob.modifiers:
            if m.type == 'ARMATURE':
                m.object = ArmatureObject#bpy.data.objects[targetRig]


###---Calculate pole angle
def signed_angle(vector_u, vector_v, normal):
    # Normal specifies orientation
    angle = vector_u.angle(vector_v)
    if vector_u.cross(vector_v).angle(normal) < 1:
        angle = -angle
    return angle

def get_pole_angle(base_bone, ik_bone, pole_location):
    pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
    projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
    return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)


def set_angle_IK_pole_angle():
    C = bpy.context
    if C.mode == 'POSE':
        #get bone constraint
        C.active_bone
        IK = C.active_pose_bone.constraints.get('IK')
        if not IK:
            return(1, 'No IK constraint in active bone, select a bone with IK constraint')
        ik_bone = C.active_pose_bone

        #get base bone
        if IK.chain_count == 0:
            #find all top
            base_bone = C.active_pose_bone.parent_recursive[-1]
        else:
            base_bone = C.active_pose_bone.parent_recursive[IK.chain_count-2] #()

        #get pole
        pole_bone = bpy.context.active_object.pose.bones[IK.pole_subtarget]

        #pass in edit mode and do the math
        bpy.ops.object.mode_set(mode='EDIT')

        pole_angle_in_radians = get_pole_angle(base_bone,
                                       ik_bone,
                                       pole_bone.matrix.translation)

        pole_angle_in_deg = round(180*pole_angle_in_radians/3.141592, 3)

        bpy.ops.object.mode_set(mode='POSE')

        mess = 'Pole angle set to', pole_angle_in_deg
        print(mess)
        #apply to pole angle:
        IK.pole_angle = radians(pole_angle_in_deg) #CONVERT TO RADIANS !!!
        return (0, mess)




def increment(match):
    return str(int(match.group(1))+1).zfill(len(match.group(1)))

def renameBoneChain():
    '''rename incremented recursively bone chain from active'''
    print('---renumbering bone chain name---')
    orgBone = bpy.context.active_bone
    org_Name = [b.name for b in orgBone.children_recursive]

    for bone in orgBone.children_recursive:
        bone.name = incremented = re.sub(r'(\d+)', increment, bone.parent.name)

    new_names = [b.name for b in orgBone.children_recursive]
    for i, b in enumerate(org_Name):
        print(org_Name[i] +' >> ' + new_names[i])


def incrementFirstValue():
    print('---renumbering deleting trail (if exists) and sum it to number in name---')
    C = bpy.context
    if C.mode == 'POSE':
        bonelist = bpy.context.selected_pose_bones
    elif C.mode == 'EDIT_ARMATURE':
        bonelist = bpy.context.selected_bones

    for b in bonelist:
        name = b.name
        #check for .### ending
        end = re.search(r'.*\.(\d\d\d)$', name)
        if end:
            #check for .### ending
            num = re.search(r'(\d+)', os.path.splitext(name)[0])
            if num:
                num = num.group(1)
                end = end.group(1)
                newnum = str(int(num) + int(end)).zfill(len(num))

                new = os.path.splitext(name)[0] #strip the end '.###'
                new = re.sub('(\d+)', newnum, new)
                b.name = new
                print(name +' >> '+ new )
            else:
                print(name, 'skipped > not ending with .###')
        else:
             print(name, 'skipped > no number found before extension')



######---CLASS

class parentConverter_OP(bpy.types.Operator):
    bl_idname = "boneutils.parent_converter"
    bl_label = "Direct parent to armature"
    bl_description = "Convert direct parent on selected objects to armature skinned parenting"
    bl_options = {"REGISTER"}

    keep_transform = bpy.props.BoolProperty()

    def execute(self, context):
        ct = 0
        print('-'*5)
        for ob in bpy.context.selected_objects:
            if ob.parent:
                # print("ob has parent", ob.parent.name)#Dbg
                targetRig = ob.parent.data.name
                if ob.parent_type == 'BONE':
                    # print("is bone parented to")#Dbg
                    if ob.parent_bone:
                        targetBone = ob.parent_bone
                        # print("ob.parent_bone", ob.parent_bone)#Dbg
                        print ('Convert:', ob.name, '>', ob.parent.name, '>', ob.parent_bone)
                        ct += 1
                        if self.keep_transform:
                            #Clear and keep transform (matrix reattribution)
                            matrixcopy = ob.matrix_world.copy()
                            ob.parent = None
                            ob.matrix_world = matrixcopy
                        else:
                            ob.parent = None

                        #replace by armature
                        CreateArmatureModifier(ob, targetRig)
                        VertexGroupToBone(ob, targetRig, targetBone, bpy.context)
        if ct:
            mess = str(ct) + ' parent converted'
        else:
            mess = 'Nothing to convert'
        self.report({'INFO'}, mess)
        return {"FINISHED"}


class calculatePoleTargetAngle(bpy.types.Operator):
    bl_idname = "boneutils.calculate_pole_target_angle"
    bl_label = "Calculate IK pole target angle"
    bl_description = "Calculate pole target angle of the IK constraint"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        err, mess = set_angle_IK_pole_angle()
        if err:
            self.report({'ERROR'}, mess)
        return {"FINISHED"}

class increment_values(bpy.types.Operator):
    bl_idname = "boneutils.increment_values"
    bl_label = "Increment bones duplication"
    bl_description = "renumbering deleting trail (if exists) and sum it to number in name\ne.g: 'obj_01.L.002' become 'obj_03.L'"
    bl_options = {"REGISTER"}

    def execute(self, context):
        incrementFirstValue()
        return {"FINISHED"}



class rename_bone_chain(bpy.types.Operator):
    bl_idname = "boneutils.rename_bone_chain"
    bl_label = "Rename bone chain recursively"
    bl_description = "rename incremented bone chain recursively from active bone"
    bl_options = {"REGISTER"}

    def execute(self, context):
        renameBoneChain()
        return {"FINISHED"}

class relink_widgets_for_selection_OP(bpy.types.Operator):
    bl_idname = "boneutils.relink_selected_widgets"
    bl_label = "Relink Widgets for selection"
    bl_description = "Relink widget (custom shape) for selected posebone"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def execute(self, context):
        if bpy.context.mode == 'POSE':
            for b in bpy.context.selected_pose_bones:
                if b.custom_shape:
                    check_widget(b.custom_shape)
                else:
                    print('no custom shape')
        return {"FINISHED"}

class relink_all_widgets_OP(bpy.types.Operator):
    bl_idname = "boneutils.relink_all_widgets"
    bl_label = "Relink All Widgets"
    bl_description = "Relink all widget (custom shape) not in scene\nObject starting with 'WGT'"
    bl_options = {"REGISTER"}

    def execute(self, context):
        for ob in bpy.data.objects:
            if ob.name.startswith('WGT-'):
                check_widget(ob)
        return {"FINISHED"}

######---DRAW

class boneUtilsPanel(bpy.types.Panel):
    bl_idname = "bone_utils"
    bl_space_type="VIEW_3D"
    bl_region_type="TOOLS"
    bl_category="RIG Tools"
    bl_label = "Bone utils"

    def draw(self, context):
        layout = self.layout
        layout.operator(operator = 'boneutils.calculate_pole_target_angle')
        row = layout.row(align=False)
        row.operator(operator = 'boneutils.parent_converter', text='Convert parent to skin').keep_transform = 0
        row.operator(operator = 'boneutils.parent_converter', text='keep transform').keep_transform = 1

        row = layout.row(align=False)
        row.operator(operator = 'boneutils.relink_all_widgets')
        row.operator(operator = 'boneutils.relink_selected_widgets')

        layout.separator()
        layout.label('rename utils')
        layout.operator(operator = 'boneutils.increment_values')
        layout.operator(operator = 'boneutils.rename_bone_chain')



######---REGISTER

def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

if __name__ == "__main__":
    register()
