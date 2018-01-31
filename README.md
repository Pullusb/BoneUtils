# BoneUtils
Blender Addon - Various tool to rigging purpose  

**[Download latest](https://raw.githubusercontent.com/Pullusb/BoneUtils/master/boneUtils.py)** (right click, save Target as)  
  
---
  
### Description:  

added to RIG tool category in Toolbar

Functions  

**Copy selected bones** - Copy selected bones to another armature in selection (new armature if no secondary armature selected) and copy transform every bones to source bones (created to extract boens from proxy)  

**Calculate pole target angle** - for IK et the pole target angle to match rest pose for Ik constraint bones and pole target  

**Parent converter (keep transform on/off)** - direct existing parent (ctrl+p) in selection become a skinned parent with armature  

**Relink all widgets (all/selection)** - Relink all bones custom shapes objects that aren'nt in the scene on layer 10 (everything or current posebone selection)  
  
renaming utility:  
**Increment values** - increment bone name for duplication based on suffix number  
i.e: bone_05.001 >> bone_06, bone_06.002 >> bone_08

**Rename bone chain** - rename recursively child bones in bone chain based on number in name of parent  
i.e: selected bones : Arm_01.L, childs will be Arm_02.L then Arm_03.L and so on.

**Retarget armature modifier** - change target armature of armature modifier existing for selected objects
(if nothing in the target field, target the armature in selection)

Update 2017/12/5 - v0.0.7:
  - retarget armature field and button
