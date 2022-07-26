# 
# IMPORT SATURN LEV
# 

import os, sys
sys.path.append(os.path.dirname(__file__))

# custom modules
import kaitaistruct
from lev_quake import LevQuake
from lev_powerslave import LevPowerslave
from lev_duke import LevDuke
from dat_skank import DatSkank

# python modules
from collections import defaultdict
from operator import add
import math
from enum import Flag
import numpy
import wave

# blender python modules
import bpy
import bmesh
from mathutils import *
from bpy_extras.io_utils import *
from bpy.props import *

# bl_info
bl_info = {
	"name": "Sega Saturn SD Engine Level (.lev) format",
	"author": "Jaycie Ewald",
	"version": (0, 0, 1),
	"blender": (3, 2, 0),
	"location": "File > Import",
	"description": "Import .lev",
	"warning": "",
	"doc_url": "",
	"support": "COMMUNITY",
	"category": "Import",
}

def register():
	bpy.utils.register_class(ImportLEV)
	bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
	bpy.utils.unregister_class(ImportLEV)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	register()

def menu_func(self, context):
	self.layout.operator(ImportLEV.bl_idname, text="Sega Saturn SD Engine Level (.lev)")

class ImportLEV(bpy.types.Operator, ImportHelper):
	"""Load a Sega Saturn SD Engine Level (.lev) File"""
	bl_idname = "import.lev"
	bl_label = "Import LEV"
	bl_options = {'UNDO'}

	# hidden properties
	filepath : StringProperty(name="File Path", description="File filepath used for importing the LEV file", maxlen=1024, default="", options={'HIDDEN'})
	files : CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN'})
	directory : StringProperty(maxlen=1024, default="", subtype='FILE_PATH', options={'HIDDEN'})
	filter_folder : BoolProperty(name="Filter Folders", description="", default=True, options={'HIDDEN'})
	filter_glob : StringProperty(default="*.lev;*.dat;", options={'HIDDEN'})

	level_formats = (
		("QUAKE", "Quake", "Sega Saturn SD Engine (Quake)"),
		("POWERSLAVE", "PowerSlave (Experimental)", "Sega Saturn SD Engine (PowerSlave)"),
		("DUKE3D", "Duke Nukem 3D (Experimental)", "Sega Saturn SD Engine (Duke Nukem 3D)"),
		("POWERSLAVEPSX", "PowerSlave PSX (Experimental)", "PlayStation SD Engine (PowerSlave)")
	)

	# user controllable properties
	bExtractTextures : BoolProperty(name="Extract Textures", default=True)
	bExtractPalettes : BoolProperty(name="Extract Texture Palettes", default=False)
	bExtractSkyTextures : BoolProperty(name="Extract Sky Textures", default=True)
	bExtractSounds : BoolProperty(name="Extract Sounds", default=True)
	bExtractRawSounds : BoolProperty(name="Extract Raw Sounds", default=False)
	bExtractEntities : BoolProperty(name="Extract Entities", default=True)
	bFixRotation : BoolProperty(name="Fix Rotation", default=True)
	bImportNodes : BoolProperty(name="Import Node Data", default=False)
	bFlagPlanes : BoolProperty(name="Generated Flagged Planes", default=False)
	bGenerateMapFile : BoolProperty(name="Generate .map File", default=False)

	ImportScale : FloatProperty(name="Import Scale", default=1.0)
	LevelFormat : EnumProperty(name="Level Format", items=level_formats, default="QUAKE")

	# debug properties (removeme)
	debug_planes : BoolProperty(name="DEBUG: show planes with tiles", default=False)
	debug_plane_index : IntProperty(name="DEBUG: show only this specific plane index", default=-1)

	def execute(self, context):
		print("Reading %s..." % self.filepath)

		name = bpy.path.display_name(bpy.path.basename(self.filepath), has_ext=False, title_case=False)
		scene = bpy.context.scene

		resource_path = self.filepath + "_resources/"

		debug_mat_fix = Matrix.Identity(4)

		if self.bFixRotation:
			# Because the empties (and the planes as I am constructing them) do not
			# have their origin at zero, we cant just throw the same rotate-and-
			# flip-x approach to fixing the rotation as elsewhere. So instead for
			# those we use this matrix which does the same thing.
			debug_mat_fix[0] = [-1.0, 0.0, 0.0, 0.0]
			debug_mat_fix[1] = [ 0.0, 0.0,-1.0, 0.0]
			debug_mat_fix[2] = [ 0.0, 1.0, 0.0, 0.0]
			debug_mat_fix[3] = [ 0.0, 0.0, 0.0, 1.0]

		#
		# useful functions
		#

		def generate_vertex_colors(mesh, palette, values):
			vertex_map = defaultdict(list)

			for poly in mesh.polygons:
				for vert_static_index, vert_loop_index in zip(poly.vertices, poly.loop_indices):
					vertex_map[vert_static_index].append(vert_loop_index)

			for vert_static_index, vert_loop_indexes in vertex_map.items():
				for vert_loop_index in vert_loop_indexes:
					color = [31 + x for x in palette[values[vert_static_index]]]
					color = [x / 31 for x in color] + [0]
					mesh.vertex_colors.active.data[vert_loop_index].color = color

		def generate_vertex_brightness(mesh, values):
			vertex_map = defaultdict(list)

			for poly in mesh.polygons:
				for vert_static_index, vert_loop_index in zip(poly.vertices, poly.loop_indices):
					vertex_map[vert_static_index].append(vert_loop_index)

			for vert_static_index, vert_loop_indexes in vertex_map.items():
				for vert_loop_index in vert_loop_indexes:
					brightness = 16 - values[vert_static_index] / 16
					color = [brightness, brightness, brightness] + [0]
					mesh.vertex_colors.active.data[vert_loop_index].color = color

		def compute_palette(item, container, bFixTransparency):
			palette_entries = []

			for i, item in enumerate(container):
				if bFixTransparency and i == 255:
					palette_entries.append([(item.r / 31), (item.g / 31), (item.b / 31), False])
				else:
					palette_entries.append([(item.r / 31), (item.g / 31), (item.b / 31), item.a])

			return palette_entries

		def compute_quake_palette(item, container):
			palette_entries = []

			for i, item in enumerate(container):
				if i == 255:
					palette_entries.append([(item[0] / 255), (item[1] / 255), (item[2] / 255), False])
				else:
					palette_entries.append([(item[0] / 255), (item[1] / 255), (item[2] / 255), item.a])

			return palette_entries

		def compute_texture(item, imagesize):
			pixels = []

			for y in range(imagesize[1]):
				for x in range(imagesize[0]):
					pos = (y * imagesize[0]) + x
					# uncomment this to flip the textures correctly, but breaks UVs
					#pos = ((imagesize[1] - y) * imagesize[0]) + x
					pixel = item[pos]
					pixels.append(pixel[0])
					pixels.append(pixel[1])
					pixels.append(pixel[2])
					pixels.append(pixel[3])

			return pixels

		def compute_texture_paletted(container, imagesize, palette):
			pixels = []

			for y in range(imagesize[1]):
				for x in range(imagesize[0]):
					pos = (y * imagesize[0]) + x
					# uncomment this to flip the textures correctly, but breaks UVs
					#pos = ((imagesize[1] - y - 1) * imagesize[0]) + x
					pixel = palette[container[pos]]
					pixels.append(pixel[0])
					pixels.append(pixel[1])
					pixels.append(pixel[2])
					pixels.append(pixel[3])

			return pixels

		def write_png(imagename, imagesize, a, pixel_struct):
			if not os.path.exists(resource_path):
				os.makedirs(resource_path)

			image = bpy.data.images.new(name=imagename, alpha=a, width=imagesize[0], height=imagesize[1])
			image.pixels = pixel_struct
			image.filepath_raw = resource_path + imagename + ".png"
			image.file_format = "PNG"
			image.update()
			image.save()

		def add_mesh(name, vertices, edges, polys):
			mesh = bpy.data.meshes.new(name)
			mesh.from_pydata(vertices, edges, polys)
			mesh.vertex_colors.new()
			mesh.uv_layers.new()
			mesh.update()

			return mesh

		def add_object(name, mesh):
			object = bpy.data.objects.new(name, mesh)

			return object

		def calc_object_rotation_scale(object):
			if self.bFixRotation:
				object.scale = [-self.ImportScale, self.ImportScale, self.ImportScale]
				object.rotation_euler = [math.radians(90), 0, 0]
			else:
				object.scale = [self.ImportScale, self.ImportScale, self.ImportScale]

		def link_object(object):
			scene.collection.objects.link(object)

		def write_material(name, index):
			mat = bpy.data.materials.new(name = name)
			mat.use_nodes = True
			bsdf = mat.node_tree.nodes["Principled BSDF"]
			texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
			texImage.image = bpy.data.images.load(f"{resource_path}texture{index:04d}.png")
			mat.node_tree.links.new(bsdf.inputs['Base Color'], texImage.outputs['Color'])

			return mat

		def match_entity(ent):
			match ent:
				# lights and light subtypes
				case 38: return "light" # static white
				case 92: return "light" # (style?)
				case 110: return "light" # heavy red pulse
				case 232: return "light" # flicker
				case 235: return "light" # (style?)
				case 253: return "light" # (style?)
				# ammo and items
				case 29: return "item_shells"
				case 88: return "item_armor1"
				# player
				case 13: return "info_player_start"
				# monsters
				case 243: return "monster_army"
				case 244: return "monster_dog"
				# miscellaneous
				case 113: return "light_flame_large_yellow"
				# poly objects
				case 146: return "misc_polymover"
				# default
				case _: return str(ent)

		#
		# defs
		#

		lev_saturncolors = [
					[-16,-16,-16],	[-16,-15,-15],	[-15,-14,-14],
					[-14,-13,-13],	[-13,-12,-12],	[-12,-11,-11],
					[-11,-10,-10],	[-10,-9,-9],	[-9,-8,-8],
					[-8,-7,-7],		[-7,-6,-6],		[-6,-5,-5],
					[-5,-4,-4],		[-4,-3,-3],		[-3,-2,-2],
					[-2,-1,-1],		[-1,0,0],		[0,0,0]
		]

		lev_quakepalette = [
			[0, 0, 0, False], [2, 2, 2, True], [4, 4, 4, True], [6, 6, 6, True], [8, 8, 8, True], [9, 9, 9, True], [11, 11, 11, True], [13, 13, 13, True], [15, 15, 15, True], [17, 17, 17, True], [19, 19, 19, True], [21, 21, 21, True], [23, 23, 23, True], [25, 25, 25, True], [27, 27, 27, True], [29, 29, 29, True],
			[2, 1, 1, True], [3, 2, 1, True], [4, 3, 1, True], [5, 3, 2, True], [6, 4, 2, True], [7, 5, 3, True], [8, 6, 3, True], [9, 7, 3, True], [10, 7, 3, True], [11, 8, 4, True], [12, 9, 4, True], [13, 10, 4, True], [14, 11, 4, True], [15, 12, 4, True], [16, 13, 4, True], [17, 13, 4, True],
			[1, 1, 2, True], [2, 2, 3, True], [3, 3, 5, True], [5, 5, 6, True], [6, 6, 8, True], [7, 7, 9, True], [8, 8, 11, True], [9, 9, 13, True], [10, 10, 14, True], [11, 11, 15, True], [12, 12, 17, True], [13, 13, 18, True], [14, 14, 20, True], [15, 15, 21, True], [16, 16, 23, True], [17, 17, 25, True],
			[0, 0, 0, True], [1, 1, 0, True], [1, 1, 0, True], [2, 2, 0, True], [3, 3, 0, True], [4, 4, 0, True], [5, 5, 1, True], [6, 6, 1, True], [7, 7, 1, True], [8, 8, 1, True], [9, 9, 1, True], [9, 9, 1, True], [10, 10, 1, True], [11, 11, 1, True], [12, 12, 1, True], [13, 13, 2, True],
			[1, 0, 0, True], [2, 0, 0, True], [3, 0, 0, True], [4, 0, 0, True], [5, 0, 0, True], [6, 0, 0, True], [7, 0, 0, True], [8, 0, 0, True], [9, 0, 0, True], [10, 0, 0, True], [11, 0, 0, True], [12, 0, 0, True], [13, 0, 0, True], [13, 0, 0, True], [14, 0, 0, True], [15, 0, 0, True],
			[2, 2, 0, True], [3, 3, 0, True], [4, 4, 0, True], [6, 5, 0, True], [7, 6, 0, True], [8, 7, 0, True], [9, 7, 1, True], [11, 8, 1, True], [12, 9, 1, True], [13, 9, 1, True], [14, 10, 2, True], [16, 11, 2, True], [17, 11, 2, True], [18, 12, 3, True], [20, 12, 4, True], [21, 13, 4, True],
			[4, 2, 1, True], [6, 3, 1, True], [7, 4, 2, True], [9, 4, 2, True], [11, 5, 3, True], [12, 6, 4, True], [14, 7, 4, True], [15, 7, 5, True], [17, 8, 6, True], [19, 10, 6, True], [21, 12, 6, True], [23, 14, 6, True], [25, 17, 5, True], [27, 21, 5, True], [29, 25, 4, True], [31, 30, 3, True],
			[1, 1, 0, True], [3, 2, 0, True], [5, 4, 2, True], [7, 5, 2, True], [9, 6, 3, True], [10, 7, 4, True], [12, 8, 5, True], [13, 9, 6, True], [15, 10, 8, True], [17, 12, 9, True], [19, 13, 10, True], [20, 15, 12, True], [22, 16, 13, True], [24, 18, 15, True], [26, 20, 17, True], [28, 22, 18, True],
			[21, 17, 20, True], [19, 15, 18, True], [18, 14, 16, True], [17, 13, 15, True], [15, 11, 13, True], [14, 10, 12, True], [13, 9, 11, True], [12, 8, 9, True], [11, 7, 8, True], [9, 6, 7, True], [8, 5, 6, True], [7, 4, 4, True], [5, 3, 3, True], [4, 2, 2, True], [3, 1, 1, True], [2, 1, 1, True],
			[23, 14, 19, True], [21, 13, 17, True], [20, 12, 16, True], [18, 11, 14, True], [17, 10, 13, True], [15, 9, 12, True], [14, 8, 10, True], [13, 7, 9, True], [12, 6, 8, True], [10, 5, 7, True], [9, 4, 5, True], [7, 4, 4, True], [6, 3, 3, True], [4, 2, 2, True], [3, 1, 1, True], [2, 1, 1, True],
			[27, 24, 23, True], [25, 22, 20, True], [23, 20, 19, True], [21, 18, 17, True], [20, 16, 15, True], [18, 15, 13, True], [16, 13, 12, True], [15, 12, 10, True], [13, 11, 9, True], [12, 9, 7, True], [10, 8, 6, True], [8, 6, 5, True], [7, 5, 4, True], [5, 4, 3, True], [3, 2, 2, True], [2, 1, 1, True],
			[13, 16, 15, True], [13, 15, 13, True], [12, 14, 13, True], [11, 13, 12, True], [10, 12, 11, True], [9, 11, 10, True], [8, 10, 9, True], [7, 9, 8, True], [6, 8, 7, True], [5, 7, 6, True], [4, 6, 5, True], [4, 5, 4, True], [3, 4, 3, True], [2, 3, 2, True], [1, 2, 1, True], [1, 1, 1, True],
			[31, 30, 3, True], [29, 27, 3, True], [27, 25, 2, True], [25, 22, 2, True], [23, 20, 2, True], [21, 18, 1, True], [19, 16, 1, True], [17, 14, 1, True], [15, 12, 1, True], [13, 10, 0, True], [11, 9, 0, True], [9, 7, 0, True], [7, 5, 0, True], [5, 4, 0, True], [3, 2, 0, True], [1, 1, 0, True],
			[0, 0, 31, True], [1, 1, 29, True], [2, 2, 27, True], [3, 3, 25, True], [4, 4, 23, True], [5, 5, 21, True], [6, 6, 19, True], [6, 6, 17, True], [6, 6, 15, True], [6, 6, 13, True], [6, 6, 12, True], [5, 5, 10, True], [4, 4, 8, True], [3, 3, 6, True], [2, 2, 4, True], [1, 1, 2, True],
			[5, 0, 0, True], [7, 0, 0, True], [9, 1, 0, True], [12, 1, 0, True], [13, 2, 0, True], [15, 3, 1, True], [18, 4, 1, True], [20, 5, 1, True], [22, 6, 2, True], [24, 9, 3, True], [25, 12, 5, True], [27, 15, 7, True], [28, 18, 10, True], [28, 21, 12, True], [29, 23, 14, True], [30, 26, 17, True],
			[20, 15, 7, True], [22, 19, 7, True], [24, 24, 7, True], [28, 28, 11, True], [15, 23, 31, True], [21, 28, 31, True], [26, 31, 31, True], [13, 0, 0, True], [17, 0, 0, True], [22, 0, 0, True], [26, 0, 0, True], [31, 0, 0, True], [31, 30, 18, True], [31, 30, 24, True], [31, 31, 31, True], [0, 0, 0, True]
		]

		#
		# skank.dat
		#

		print(lev_quakepalette[2][0])

		if name == "skank.dat" or name == "SKANK.DAT":

			dat = DatSkank.from_file(self.filepath)

			pixel = dat.BitmapEntryT

			for i, pixel in enumerate(dat.bitmaps):
				pixels = compute_texture(compute_palette(pixel, dat.bitmaps[i].bitmap, False), (dat.header.width, dat.header.height))
				write_png(f"bitmap.{i}", (dat.header.width, dat.header.height), True, pixels)

			return {'FINISHED'}

		#
		# duke nukem 3d (experimental)
		#

		if self.LevelFormat == "DUKE3D":

			lev = LevDuke.from_file(self.filepath)

			vertex = lev.VertexT
			plane = lev.PlaneT
			palette_entry = lev.PaletteEntryT

			lev_vertices = []
			lev_quads = []

			if self.bExtractSkyTextures:
				palette = compute_palette(palette_entry, lev.sky_data.palette, True)
				pixels = compute_texture_paletted(lev.sky_data.bitmap, (lev.sky_data.width, lev.sky_data.height), palette)

				write_png("sky", (lev.sky_data.width, lev.sky_data.height), True, pixels)

				if self.bExtractPalettes:
					palette_pixels = compute_texture(palette, (16, 16))
					write_png("skypalette", (16, 16), True, palette_pixels)

			for vertex in lev.vertices:
				lev_vertices.append([vertex.coords[0], vertex.coords[1], vertex.coords[2]])

			for plane in lev.planes:
				lev_quads.append([plane.vertex_indices[0], plane.vertex_indices[1], plane.vertex_indices[2], plane.vertex_indices[3]])

			mesh_lev = add_mesh(name, lev_vertices, [], lev_quads)
			obj_lev = add_object(name, mesh_lev)

			calc_object_rotation_scale(obj_lev)
			link_object(obj_lev)

		#
		# powerslave (experimental)
		#

		if self.LevelFormat == "POWERSLAVE":

			lev = LevPowerslave.from_file(self.filepath)

			lev_vertices = []
			lev_quads = []
			lev_vertex_colors = []

			vertex = lev.VertexT
			plane = lev.PlaneT

			if self.bExtractSkyTextures:
				skypalette = []
				skypixels = []

				skyimage = lev.skydata.skyimage

				for lev.PaletteentryT in lev.skydata.palette:
					entry = lev.PaletteentryT
					skypalette.append([(entry.r / 31), (entry.g / 31), (entry.b / 31), entry.a])

				for y in range(256): # sky texture height
					for x in range(512): # sky texture width
						pos = (y * 512) + x
						pixel = skypalette[skyimage[pos]]
						skypixels.append(pixel[0]) # red
						skypixels.append(pixel[1]) # green
						skypixels.append(pixel[2]) # blue
						skypixels.append(pixel[3]) # alpha

				output = bpy.data.images.new("Sky Texture", alpha=True, width=512, height=256)
				output.pixels = skypixels
				output.filepath_raw = self.filepath + ".sky.png"
				output.file_format = "PNG"
				output.update()
				output.save()

			for lev.VertexT in lev.vertices:
				vertex = lev.VertexT
				lev_vertices.append([vertex.coords[0], vertex.coords[1], vertex.coords[2]])
				lev_vertex_colors.append(vertex.lightlevel)

			for plane in lev.planes:
				if plane.quadoffsets[0] > -1 and plane.quadoffsets[1] < (lev.header.quadcount + 1):
					for i in range(plane.quadoffsets[1] - plane.quadoffsets[0] + 1):
						quad = lev.quads[plane.quadoffsets[0] + i]
						x = quad.indices[0] + plane.vertexoffsets[0]
						y = quad.indices[1] + plane.vertexoffsets[0]
						z = quad.indices[2] + plane.vertexoffsets[0]
						a = quad.indices[3] + plane.vertexoffsets[0]
						lev_quads.append([x, y, z, a])

			for lev.SectorT in lev.sectors:
				sector = lev.SectorT
				if sector.planes[0] > -1 and sector.planes[1] < (lev.header.planecount + 1):
					for i in range(sector.planes[1] - sector.planes[0] + 1):
						plane = lev.planes[sector.planes[0] + i]
						x = plane.vertices[0]
						y = plane.vertices[1]
						z = plane.vertices[2]
						a = plane.vertices[3]
						lev_quads.append([x, y, z, a])

			mesh_lev = bpy.data.meshes.new(name)
			mesh_lev.from_pydata(lev_verts, [], lev_quads)
			mesh_lev.vertex_colors.new()
			mesh_lev.update()

			obj_lev = bpy.data.objects.new(name, mesh_lev)

			generate_vertex_colors(mesh_lev, lev_saturncolors, lev_vertex_colors)

			if self.bFixRotation:
				obj_lev.scale = [-self.ImportScale, self.ImportScale, self.ImportScale]
				obj_lev.rotation_euler = [math.radians(90), 0, 0]
			else:
				obj_lev.scale = [self.ImportScale, self.ImportScale, self.ImportScale]

			scene.collection.objects.link(obj_lev)

		#
		# quake
		#

		if self.LevelFormat == "QUAKE":

			lev = LevQuake.from_file(self.filepath)

			lev_vertices = []
			lev_vertex_colors = []
			lev_quads = []
			lev_materials = []
			lev_entities = []

			vertex = lev.VertexT
			plane = lev.PlaneT
			node = lev.NodeT
			texture = lev.TextureT
			tile = lev.TileT
			palette_entry = lev.PaletteEntryT
			entity = lev.EntityT
			sound = lev.SoundT
			resource = lev.ResourceT

			for vertex in lev.verts:
				lev_vertices.append([vertex.coords[0], vertex.coords[1], vertex.coords[2]])
				lev_vertex_colors.append(vertex.color_lookup)

			for plane in lev.planes:
				if plane.tile_index < lev.header.num_tile_entries:
					tile = lev.tiles[plane.tile_index]
					X = Vector(lev_vertices[plane.vertex_indices[0]])
					Y = Vector(lev_vertices[plane.vertex_indices[1]])
					Z = Vector(lev_vertices[plane.vertex_indices[2]])
					A = Vector(lev_vertices[plane.vertex_indices[3]])

					def convert_int16_16_vector(v):
						return Vector((round(v[0]/65536.0), round(v[1]/65536.0), round(v[2]/65536.0)))

					width = tile.width
					height = tile.height

					base = tile.base_vector
					horizontal = tile.horizontal_vector
					vertical = tile.vertical_vector

					for tileY in range(height):
						for tileX in range(width):
							vc0 = [
								base[0] + tileX * horizontal[0] + tileY * vertical[0],
								base[1] + tileX * horizontal[1] + tileY * vertical[1],
								base[2] + tileX * horizontal[2] + tileY * vertical[2]
							]
							vc1 = [
								vc0[0] + horizontal[0],
								vc0[1] + horizontal[1],
								vc0[2] + horizontal[2]
							]
							vc2 = [
								vc0[0] + horizontal[0] + vertical[0],
								vc0[1] + horizontal[1] + vertical[1],
								vc0[2] + horizontal[2] + vertical[2]
							]
							vc3 = [
								vc0[0] + vertical[0],
								vc0[1] + vertical[1],
								vc0[2] + vertical[2]
							]

							vc0 = convert_int16_16_vector(vc0)
							vc1 = convert_int16_16_vector(vc1)
							vc2 = convert_int16_16_vector(vc2)
							vc3 = convert_int16_16_vector(vc3)

							points = tile.width + 1
							color_base = (tileY * points) + tileX

							vc0_color = tile.get_color_data[color_base]
							vc1_color = tile.get_color_data[color_base + 1]
							vc2_color = tile.get_color_data[color_base + 1 + points]
							vc3_color = tile.get_color_data[color_base + points]

							ofs = len(lev_vertices)

							lev_vertices.append(vc0)
							lev_vertices.append(vc1)
							lev_vertices.append(vc2)
							lev_vertices.append(vc3)

							lev_vertex_colors.append(vc0_color)
							lev_vertex_colors.append(vc1_color)
							lev_vertex_colors.append(vc2_color)
							lev_vertex_colors.append(vc3_color)

							lev_quads.append([ofs, ofs + 1, ofs + 2, ofs + 3])
				
			for plane in lev.planes:
				if plane.quad_start_index < lev.header.num_quads:
					for i in range(plane.quad_end_index - plane.quad_start_index + 1):
						quad = lev.quads[plane.quad_start_index + i]
						x = quad.vertex_indices[0] + plane.vert_start_index
						y = quad.vertex_indices[1] + plane.vert_start_index
						z = quad.vertex_indices[2] + plane.vert_start_index
						a = quad.vertex_indices[3] + plane.vert_start_index
						lev_quads.append([x, y, z, a])

			mesh_lev = add_mesh(name, lev_vertices, [], lev_quads)

			generate_vertex_colors(mesh_lev, lev_saturncolors, lev_vertex_colors)

			obj_lev = add_object(name, mesh_lev)

			if self.bExtractSounds or self.bExtractRawSounds:

				if not os.path.exists(resource_path):
					os.makedirs(resource_path)

				for i, sound in enumerate(lev.resources.sounds):
					num_channels = 1
					samples_per_second = 11025
					bytes_per_sample = sound.bits//8
					bytes_per_frame = num_channels*bytes_per_sample
					num_frames = sound.len_samples//bytes_per_frame

					if self.bExtractSounds:
						wav_path = f"{resource_path}sound{i:03d}.wav"

						if sound.bits==8:
							# For 8 bit data, the .wav format only supports unsigned samples, but we
							# have signed 8 bit samples! So we have to convert them:
							s8_samples = numpy.frombuffer(sound.samples, dtype='i1')
							u8_samples = (s8_samples+128).astype('u1')
							samples = u8_samples.tobytes()
						elif sound.bits==16:
							# For 16 bit data, the .wav format only supports little-endian samples,
							# but we have big-endian. So we have to convert them too!
							s16be_samples = numpy.frombuffer(sound.samples, dtype='>i2')
							s16le_samples = s16be_samples.astype('<i2')
							samples = s16le_samples.tobytes()
						else:
							raise ValueError("Expected 8 or 16 bit samples, but found something else!")

						with wave.open(wav_path, "wb") as w:
							w.setnchannels(num_channels)
							w.setsampwidth(bytes_per_sample)
							w.setframerate(samples_per_second)
							w.setnframes(num_frames)
							w.writeframes(samples)

					if self.bExtractRawSounds:
						raw_path = f"{resource_path}sound{i:03d}.raw"
						with open(raw_path, "wb") as f:
							f.write(sound.samples)

			if self.bExtractTextures:
				if self.bExtractPalettes:
					palette = compute_palette(palette_entry, lev.resources.palette, False)
					palette_pixels = compute_texture(palette, (16, 16))
					write_png("palette", (16, 16), True, palette_pixels)

				numTextures = 0

				for resource in lev.resources.resources:
					if resource.resource_type == 130:
						tex = resource.data
						palette = compute_palette(palette_entry, tex.palette, False)
						pixels = compute_texture_paletted(tex.bitmap, (64, 64), palette)
						write_png(f"texture{numTextures:04d}", (64, 64), True, pixels)

						if self.bExtractPalettes:
							palette_pixels = compute_texture(palette, (16, 1))
							write_png(f"texture{numTextures:04d}_palette", (16, 1), True, palette_pixels)

						numTextures += 1

				numTiles = 0

				for plane in lev.planes:
					if plane.tile_index < lev.header.num_tile_entries:
						tile = lev.tiles[plane.tile_index]
						width = tile.width
						height = tile.height

						for tileY in range(height):
							for tileX in range(width):
								tile_index = (tileY * width) + tileX
								tile_textureindex = tile.get_tile_texture_data[(tile_index * 2) + 1]

								if tile_textureindex not in lev_materials:
									mat = write_material(f"{name}-material-{tile_textureindex:04d}", tile_textureindex)
									obj_lev.data.materials.append(mat)
									lev_materials.append(tile_textureindex)

								obj_lev.data.polygons[numTiles].material_index = lev_materials.index(tile_textureindex)
								numTiles += 1

				numQuads = 0

				for plane in lev.planes:
					if plane.quad_start_index < lev.header.num_quads:
						for i in range(plane.quad_end_index - plane.quad_start_index + 1):
							quad = lev.quads[plane.quad_start_index + i]

							if quad.texture_index not in lev_materials:
								mat = write_material(f"{name}-material-{quad.texture_index:04d}", quad.texture_index)
								obj_lev.data.materials.append(mat)
								lev_materials.append(quad.texture_index)

							obj_lev.data.polygons[numTiles + numQuads].material_index = lev_materials.index(quad.texture_index)
							numQuads += 1

			if self.bExtractEntities:
				if self.bGenerateMapFile:
					entities_doc = open(self.filepath + ".map",'w')

				for entNum, entity in enumerate(lev.entities):
					ent_type = f"Entity {entNum}: {match_entity(entity.ent_type)}"

					if match_entity(entity.ent_type) != "misc_polymover" and entity.get_entity_data != None:
						if self.bFixRotation:
							entloc = [
								-entity.get_entity_data.coords[0] * self.ImportScale,
								-entity.get_entity_data.coords[2] * self.ImportScale,
								entity.get_entity_data.coords[1] * self.ImportScale
							]
						else:
							entloc = [
								entity.get_entity_data.coords[0] * self.ImportScale,
								entity.get_entity_data.coords[1] * self.ImportScale,
								entity.get_entity_data.coords[2] * self.ImportScale
							]
					else:
						entloc = [0, 0, 0]

					empty_ent = bpy.data.objects.new(ent_type, None)
					empty_ent.location = entloc
					empty_ent["classname"] = match_entity(entity.ent_type)
					empty_ent.empty_display_size = 2
					empty_ent.empty_display_type = "PLAIN_AXES"
					link_object(empty_ent)

					if self.bGenerateMapFile:
						entities_doc.write("{\n")
						entities_doc.write(f"\"classname\" \"" + match_entity(entity.ent_type) + "\"\n")
						entities_doc.write(f"\"origin\" \"{entloc[0]} {entloc[1]} {entloc[2]}\"\n")
						entities_doc.write("}\n")

			calc_object_rotation_scale(obj_lev)
			link_object(obj_lev)

		return {'FINISHED'}