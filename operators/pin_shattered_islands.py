import bpy
import bmesh
from bpy.props import IntProperty, FloatVectorProperty
from bpy.types import Operator

from ..utils.uv_utils import (
    get_islands_simple,
)


class PinShatteredIslands(Operator):
    bl_idname = "uv.toolkit_pin_shattered_islands"
    bl_label = "Pin Shattered Islands"
    bl_description = "Pin islands consisting of suspiciously low numbers of faces"
    bl_options = {'REGISTER', 'UNDO'}

    tolerance: IntProperty(
        name="Tolerance",
        description="The lowest number faces an island must contain to not get pinned",
        default=4,
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        for o in bpy.context.objects_in_mode:
            bm = bmesh.from_edit_mesh(o.data)

            uv_layer, islands = get_islands_simple(bm)
            shattered_islands = [i for i in islands if len(i) < self.tolerance]

            if len(shattered_islands) < 1:
                continue

            bm.faces.ensure_lookup_table()

            for island in shattered_islands:
                for face in island:
                    for loop in face.loops:
                        loop[uv_layer].uv = (0, 1)
                        loop[uv_layer].pin_uv = True
            
            bmesh.update_edit_mesh(o.data)
            bm.free()
        return {'FINISHED'}
