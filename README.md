# BoneUtils
Blender Addon - Various tool to rigging purpose  
  
---
  
### Description:  

added to RIG tool category in Toolbar

Functions  

**Calculate pole target angle** - for IK et the pole target angle to match rest pose for Ik constraint bones and pole target  

**Parent converter (keep transform on/off)** - direct existing parent (ctrl+p) in selection become a skinned parent with armature  

**Relink all widgets (all/selection)** - Relink all bones custom shapes objects that aren'nt in the scene on layer 10 (everything or current posebone selection)  
  
renaming utility:  
**Increment values** - increment bone name for duplication based on suffix number  
i.e: bone_05.001 >> bone_06, bone_06.002 >> bone_08

**Rename bone chain** - rename recursively child bones in bone chain based on number in name of parent  
i.e: selected bones : Arm_01.L, childs will be Arm_02.L then Arm_03.L and so on.
