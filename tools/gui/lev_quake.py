# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 9):
    raise Exception("Incompatible Kaitai Struct Python API: 0.9 or later is required, but you have %s" % (kaitaistruct.__version__))

class LevQuake(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self._raw_sky_data = self._io.read_bytes(131104)
        _io__raw_sky_data = KaitaiStream(BytesIO(self._raw_sky_data))
        self.sky_data = LevQuake.SkyDataT(_io__raw_sky_data, self, self._root)
        self.header = LevQuake.HeaderT(self._io, self, self._root)
        self.nodes = []
        for i in range(self.header.num_nodes):
            self.nodes.append(LevQuake.NodeT(self._io, self, self._root))

        self.planes = []
        for i in range(self.header.num_planes):
            self.planes.append(LevQuake.PlaneT(self._io, self, self._root))

        self.tiles = []
        for i in range(self.header.num_tile_entries):
            self.tiles.append(LevQuake.TileT(self._io, self, self._root))

        self.verts = []
        for i in range(self.header.num_vertices):
            self.verts.append(LevQuake.VertexT(self._io, self, self._root))

        self.quads = []
        for i in range(self.header.num_quads):
            self.quads.append(LevQuake.QuadT(self._io, self, self._root))

        self.entities = []
        for i in range(self.header.num_entities):
            self.entities.append(LevQuake.EntityT(i, self._io, self, self._root))

        self.entity_polylinks = []
        for i in range(self.header.num_entity_polylinks):
            self.entity_polylinks.append(LevQuake.EntityPolylinkT(self._io, self, self._root))

        self._raw_entity_polylink_data1 = self._io.read_bytes((self.header.num_entity_polylink_data1_segments * 2))
        _io__raw_entity_polylink_data1 = KaitaiStream(BytesIO(self._raw_entity_polylink_data1))
        self.entity_polylink_data1 = LevQuake.EntityPolylinkData1T(_io__raw_entity_polylink_data1, self, self._root)
        self._raw_entity_polylink_data2 = self._io.read_bytes((self.header.num_entity_polylink_data2_segments * 4))
        _io__raw_entity_polylink_data2 = KaitaiStream(BytesIO(self._raw_entity_polylink_data2))
        self.entity_polylink_data2 = LevQuake.EntityPolylinkData2T(_io__raw_entity_polylink_data2, self, self._root)
        self._raw_entity_data = self._io.read_bytes(self.header.len_entity_data)
        _io__raw_entity_data = KaitaiStream(BytesIO(self._raw_entity_data))
        self.entity_data = LevQuake.EntityDataT(_io__raw_entity_data, self, self._root)
        self._raw_tile_texture_data = self._io.read_bytes(self.header.len_tile_texture_data)
        _io__raw_tile_texture_data = KaitaiStream(BytesIO(self._raw_tile_texture_data))
        self.tile_texture_data = LevQuake.TileTextureDataT(_io__raw_tile_texture_data, self, self._root)
        self._raw_tile_color_data = self._io.read_bytes(self.header.len_tile_color_data)
        _io__raw_tile_color_data = KaitaiStream(BytesIO(self._raw_tile_color_data))
        self.tile_color_data = LevQuake.TileColorDataT(_io__raw_tile_color_data, self, self._root)
        self.unknown = []
        for i in range(self.header.num_unknown):
            self.unknown.append(self._io.read_bytes(128))

        self.resources = LevQuake.ResourcesT(self._io, self, self._root)
        self.unknown0 = LevQuake.LenAndUnknownT(self._io, self, self._root)
        self.level_name = (self._io.read_bytes(32)).decode(u"ASCII")
        self.unknown1 = []
        for i in range(9):
            self.unknown1.append(self._io.read_u4be())

        self.unknown2 = LevQuake.LenAndUnknownT(self._io, self, self._root)
        self.unknown3 = LevQuake.LenAndUnknownT(self._io, self, self._root)

    class TileTextureDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(self._parent.header.len_tile_texture_data)


    class EntityDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(self._parent.header.len_entity_data)


    class Resource0x6cT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown0 = self._io.read_u2be()
            self.len_data = self._io.read_u2be()
            self.data = self._io.read_bytes(self.len_data)


    class ResourcesPrefixT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.num_values = self._io.read_u4be()
            self.values = []
            for i in range(self.num_values):
                self.values.append(self._io.read_s2be())



    class SoundT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_samples = self._io.read_s4be()
            self.attribute_02 = self._io.read_s4be()
            self.bits = self._io.read_s4be()
            self.attribute_04 = self._io.read_s4be()
            self.samples = self._io.read_bytes(self.len_samples)


    class EntityT(KaitaiStruct):
        def __init__(self, index, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self.index = index
            self._read()

        def _read(self):
            self.ent_type = self._io.read_u2be()
            self.ofs_entity_data = self._io.read_u2be()

        @property
        def get_entity_data(self):
            if hasattr(self, '_m_get_entity_data'):
                return self._m_get_entity_data

            if self.ofs_entity_data < self._root.header.len_entity_data:
                io = self._root.entity_data._io
                _pos = io.pos()
                io.seek(self.ofs_entity_data)
                _on = self.ent_type
                if _on == 146:
                    self._m_get_entity_data = LevQuake.EntityPolymoverT(io, self, self._root)
                else:
                    self._m_get_entity_data = LevQuake.EntityGenericT(io, self, self._root)
                io.seek(_pos)

            return getattr(self, '_m_get_entity_data', None)


    class ResourcesT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.prefix = LevQuake.ResourcesPrefixT(self._io, self, self._root)
            self.num_sounds = self._io.read_u4be()
            self.sounds = []
            for i in range(self.num_sounds):
                self.sounds.append(LevQuake.SoundT(self._io, self, self._root))

            self.len_palette = self._io.read_u4be()
            self.palette = []
            for i in range(self.len_palette // 2):
                self.palette.append(LevQuake.PaletteEntryT(self._io, self, self._root))

            self.num_resources = self._io.read_u4be()
            self.resources = []
            for i in range(self.num_resources):
                self.resources.append(LevQuake.ResourceT(self._io, self, self._root))



    class VertexT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.coords = []
            for i in range(3):
                self.coords.append(self._io.read_s2be())

            self.color_lookup = self._io.read_u1()
            self.reserved = self._io.read_u1()


    class HeaderT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown_01 = self._io.read_u4be()
            self.unknown_02 = self._io.read_u4be()
            self.num_nodes = self._io.read_u4be()
            self.num_planes = self._io.read_u4be()
            self.num_vertices = self._io.read_u4be()
            self.num_quads = self._io.read_u4be()
            self.len_tile_texture_data = self._io.read_u4be()
            self.num_tile_entries = self._io.read_u4be()
            self.len_tile_color_data = self._io.read_u4be()
            self.num_entities = self._io.read_u4be()
            self.len_entity_data = self._io.read_u4be()
            self.num_entity_polylinks = self._io.read_u4be()
            self.num_entity_polylink_data1_segments = self._io.read_u4be()
            self.num_entity_polylink_data2_segments = self._io.read_u4be()
            self.num_unknown = self._io.read_u4be()


    class Resource0x34T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown0 = self._io.read_u2be()
            self.unknown1 = []
            for i in range(512):
                self.unknown1.append(LevQuake.PaletteEntryT(self._io, self, self._root))



    class EntityPolymoverT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.polylink_id = self._io.read_s2be()
            self.data = []
            for i in range(20):
                self.data.append(self._io.read_s2be())



    class LenAndUnknownT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.len_data = self._io.read_u4be()
            self.data = self._io.read_bytes(self.len_data)


    class QuadT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex_indices = []
            for i in range(4):
                self.vertex_indices.append(self._io.read_u1())

            self.texture_index = self._io.read_u1()


    class TextureT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.palette = []
            for i in range(16):
                self.palette.append(LevQuake.PaletteEntryT(self._io, self, self._root))

            self.bitmap = []
            for i in range((64 * 64)):
                self.bitmap.append(self._io.read_bits_int_be(4))



    class PaletteEntryT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.a = self._io.read_bits_int_be(1) != 0
            self.b = self._io.read_bits_int_be(5)
            self.g = self._io.read_bits_int_be(5)
            self.r = self._io.read_bits_int_be(5)


    class EntityPolylinkData1T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            i = 0
            while not self._io.is_eof():
                self.data.append(self._io.read_u1())
                i += 1



    class EntityPolylinkData2T(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = []
            i = 0
            while not self._io.is_eof():
                self.data.append(self._io.read_u1())
                i += 1



    class ResourceT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.flags = self._io.read_u1()
            self.resource_type = self._io.read_u1()
            _on = self.resource_type
            if _on == 130:
                self.data = LevQuake.TextureT(self._io, self, self._root)
            elif _on == 52:
                self.data = LevQuake.Resource0x34T(self._io, self, self._root)
            elif _on == 106:
                self.data = LevQuake.Resource0x6aT(self._io, self, self._root)
            elif _on == 108:
                self.data = LevQuake.Resource0x6cT(self._io, self, self._root)


    class TileT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.ofs_texture_data = self._io.read_u2be()
            self.width = self._io.read_u1()
            self.height = self._io.read_u1()
            self.ofs_color_data = self._io.read_u2be()
            self.unknown = self._io.read_u2be()
            self.horizontal_vector = []
            for i in range(3):
                self.horizontal_vector.append(self._io.read_s4be())

            self.vertical_vector = []
            for i in range(3):
                self.vertical_vector.append(self._io.read_s4be())

            self.base_vector = []
            for i in range(3):
                self.base_vector.append(self._io.read_s4be())


        @property
        def get_color_data(self):
            if hasattr(self, '_m_get_color_data'):
                return self._m_get_color_data

            io = self._root.tile_color_data._io
            _pos = io.pos()
            io.seek(self.ofs_color_data)
            self._m_get_color_data = []
            for i in range(((self.width + 1) * (self.height + 1))):
                self._m_get_color_data.append(io.read_u1())

            io.seek(_pos)
            return getattr(self, '_m_get_color_data', None)

        @property
        def get_tile_texture_data(self):
            if hasattr(self, '_m_get_tile_texture_data'):
                return self._m_get_tile_texture_data

            io = self._root.tile_texture_data._io
            _pos = io.pos()
            io.seek(self.ofs_texture_data)
            self._m_get_tile_texture_data = []
            for i in range(((self.height * self.width) * 2)):
                self._m_get_tile_texture_data.append(io.read_u1())

            io.seek(_pos)
            return getattr(self, '_m_get_tile_texture_data', None)


    class EntityPolylinkT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.lead = self._io.read_u2be()
            self.ofs_entity_polylink_data1 = []
            for i in range(2):
                self.ofs_entity_polylink_data1.append(self._io.read_u2be())

            self.ofs_entity_polylink_data2 = []
            for i in range(2):
                self.ofs_entity_polylink_data2.append(self._io.read_u2be())

            self.unknown = self._io.read_u2be()
            self.reserved = []
            for i in range(3):
                self.reserved.append(self._io.read_u2be())


        @property
        def getdata1(self):
            if hasattr(self, '_m_getdata1'):
                return self._m_getdata1

            io = self._root.entity_polylink_data1._io
            _pos = io.pos()
            io.seek((self.ofs_entity_polylink_data1[0] * 2))
            self._m_getdata1 = []
            for i in range((((self.ofs_entity_polylink_data1[1] - self.ofs_entity_polylink_data1[0]) + 1) * 2)):
                self._m_getdata1.append(io.read_u1())

            io.seek(_pos)
            return getattr(self, '_m_getdata1', None)

        @property
        def getdata2(self):
            if hasattr(self, '_m_getdata2'):
                return self._m_getdata2

            io = self._root.entity_polylink_data2._io
            _pos = io.pos()
            io.seek((self.ofs_entity_polylink_data2[0] * 4))
            self._m_getdata2 = []
            for i in range((((self.ofs_entity_polylink_data2[1] - self.ofs_entity_polylink_data2[0]) + 1) * 4)):
                self._m_getdata2.append(io.read_u1())

            io.seek(_pos)
            return getattr(self, '_m_getdata2', None)


    class NodeT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.reserved = []
            for i in range(2):
                self.reserved.append(self._io.read_u2be())

            self.position = []
            for i in range(3):
                self.position.append(self._io.read_u2be())

            self.distance = self._io.read_u2be()
            self.first_plane = self._io.read_u2be()
            self.last_plane = self._io.read_u2be()
            self.unknown = []
            for i in range(6):
                self.unknown.append(self._io.read_u2be())



    class PlaneT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.vertex_indices = []
            for i in range(4):
                self.vertex_indices.append(self._io.read_u2be())

            self.node_index = self._io.read_u2be()
            self.flags = self._io.read_u2be()
            self.collision_flags = self._io.read_u2be()
            self.tile_index = self._io.read_u2be()
            self.unknown_index = self._io.read_u2be()
            self.quad_start_index = self._io.read_u2be()
            self.quad_end_index = self._io.read_u2be()
            self.vert_start_index = self._io.read_u2be()
            self.vert_end_index = self._io.read_u2be()
            self.normal = []
            for i in range(3):
                self.normal.append(self._io.read_s2be())

            self.distance = self._io.read_s2be()
            self.angle = self._io.read_s2be()
            self.reserved = []
            for i in range(2):
                self.reserved.append(self._io.read_u2be())



    class SkyBitmapT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.image = self._io.read_bytes(2048)


    class EntityGenericT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.start = self._io.read_s2be()
            self.coords = []
            for i in range(3):
                self.coords.append(self._io.read_s2be())



    class Resource0x6aT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.unknown0 = self._io.read_u2be()
            self.len_data = self._io.read_u2be()
            self.data = self._io.read_bytes(self.len_data)


    class SkyDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.palette = []
            for i in range(16):
                self.palette.append(LevQuake.PaletteEntryT(self._io, self, self._root))

            self.bitmaps = []
            for i in range(64):
                self.bitmaps.append(LevQuake.SkyBitmapT(self._io, self, self._root))



    class TileColorDataT(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = self._io.read_bytes(self._parent.header.len_tile_color_data)



