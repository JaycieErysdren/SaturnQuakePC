meta:
  id: lev_quake
  file-extension: lev
  endian: be
  bit-endian: be

seq:
  - id: sky_data
    size: 131104
    type: sky_data_t
  - id: header
    type: header_t
  - id: nodes
    type: node_t
    repeat: expr
    repeat-expr: header.num_nodes
  - id: planes
    type: plane_t
    repeat: expr
    repeat-expr: header.num_planes
  - id: tiles
    type: tile_t
    repeat: expr
    repeat-expr: header.num_tile_entries
  - id: verts
    type: vertex_t
    repeat: expr
    repeat-expr: header.num_vertices
  - id: quads
    type: quad_t
    repeat: expr
    repeat-expr: header.num_quads
  - id: entities
    type: entity_t(_index)
    repeat: expr
    repeat-expr: header.num_entities
  - id: entity_polylinks
    type: entity_polylink_t
    repeat: expr
    repeat-expr: header.num_entity_polylinks
  - id: entity_polylink_data1
    type: entity_polylink_data1_t
    size: header.num_entity_polylink_data1_segments * 2
  - id: entity_polylink_data2
    type: entity_polylink_data2_t
    size: header.num_entity_polylink_data2_segments * 4
  - id: entity_data
    type: entity_data_t
    size: header.len_entity_data
  - id: tile_texture_data
    type: tile_texture_data_t
    size: header.len_tile_texture_data
  - id: tile_color_data
    type: tile_color_data_t
    size: header.len_tile_color_data
  - id: unknown
    size: 128
    repeat: expr
    repeat-expr: header.num_unknown
  - id: resources
    type: resources_t
  - id: unknown0
    type: len_and_unknown_t
  - id: level_name
    type: str
    size: 32
    encoding: ASCII
  - id: unknown1
    type: u4
    repeat: expr
    repeat-expr: 9
  - id: unknown2
    type: len_and_unknown_t
  - id: unknown3
    type: len_and_unknown_t

types:
  # 131104 bytes
  sky_data_t:
    seq:
      - id: palette
        type: palette_entry_t
        repeat: expr
        repeat-expr: 16
      - id: bitmaps
        type: sky_bitmap_t
        repeat: expr
        repeat-expr: 64

  palette_entry_t:
    seq:
      - id: a
        type: b1
      - id: b
        type: b5
      - id: g
        type: b5
      - id: r
        type: b5

  sky_bitmap_t:
    seq:
      - id: image
        size: 2048

  # 60 bytes
  header_t:
    seq:
      - id: unknown_01
        type: u4
      - id: unknown_02
        type: u4
      - id: num_nodes
        type: u4
      - id: num_planes
        type: u4
      - id: num_vertices
        type: u4
      - id: num_quads
        type: u4
      - id: len_tile_texture_data
        type: u4
      - id: num_tile_entries
        type: u4
      - id: len_tile_color_data
        type: u4
      - id: num_entities
        type: u4
      - id: len_entity_data
        type: u4
      - id: num_entity_polylinks
        type: u4
      - id: num_entity_polylink_data1_segments
        type: u4
      - id: num_entity_polylink_data2_segments
        type: u4
      - id: num_unknown
        type: u4

  # 28 bytes each
  node_t:
    seq:
      - id: reserved
        type: u2
        repeat: expr
        repeat-expr: 2
      - id: position
        type: u2
        repeat: expr
        repeat-expr: 3
      - id: distance
        type: u2
      - id: first_plane
        type: u2
      - id: last_plane
        type: u2
      - id: unknown
        type: u2
        repeat: expr
        repeat-expr: 6

  # 40 bytes each
  plane_t:
    seq:
      - id: vertex_indices
        type: u2
        repeat: expr
        repeat-expr: 4
      - id: node_index
        type: u2
      - id: flags
        type: u2
      - id: collision_flags
        type: u2
      - id: tile_index
        type: u2
      - id: unknown_index
        type: u2
      - id: quad_start_index
        type: u2
      - id: quad_end_index
        type: u2
      - id: vert_start_index
        type: u2
      - id: vert_end_index
        type: u2
      - id: normal
        type: s2
        repeat: expr
        repeat-expr: 3
      - id: distance
        type: s2
      - id: angle
        type: s2
      - id: reserved
        type: u2
        repeat: expr
        repeat-expr: 2

  # 44 bytes each
  tile_t:
    seq:
      - id: ofs_texture_data
        type: u2
      - id: width
        type: u1
      - id: height
        type: u1
      - id: ofs_color_data
        type: u2
      - id: unknown
        type: u2
      - id: horizontal_vector
        type: s4
        repeat: expr
        repeat-expr: 3
      - id: vertical_vector
        type: s4
        repeat: expr
        repeat-expr: 3
      - id: base_vector
        type: s4
        repeat: expr
        repeat-expr: 3
    instances:
      get_color_data:
        io: _root.tile_color_data._io
        pos: ofs_color_data
        type: u1
        repeat: expr
        repeat-expr: (width + 1) * (height + 1)
      get_tile_texture_data:
        io: _root.tile_texture_data._io
        pos: ofs_texture_data
        type: u1
        repeat: expr
        repeat-expr: (height * width) * 2

  tile_color_data_t:
    seq:
      - id: data
        size: _parent.header.len_tile_color_data

  tile_texture_data_t:
    seq:
      - id: data
        size: _parent.header.len_tile_texture_data

  # 8 bytes each
  vertex_t:
    seq:
      - id: coords
        type: s2
        repeat: expr
        repeat-expr: 3
      - id: color_lookup
        type: u1
      - id: reserved
        type: u1

  # 5 bytes each
  quad_t:
    seq:
      - id: vertex_indices
        type: u1
        repeat: expr
        repeat-expr: 4
      - id: texture_index
        type: u1

  # 4 bytes each
  entity_t:
    params:
      - id: index
        type: s4
    seq:
      - id: ent_type
        type: u2
      - id: ofs_entity_data
        type: u2
    instances:
      get_entity_data:
        io: _root.entity_data._io
        pos: ofs_entity_data
        if: ofs_entity_data < _root.header.len_entity_data
        type:
            switch-on: ent_type
            cases:
              0x92: entity_polymover_t
              _: entity_generic_t

  entity_generic_t:
    seq:
      - id: start
        type: s2
      - id: coords
        type: s2
        repeat: expr
        repeat-expr: 3

  entity_polymover_t:
    seq:
      - id: polylink_id
        type: s2
      - id: data
        type: s2
        repeat: expr
        repeat-expr: 20

  entity_data_t:
    seq:
      - id: data
        size: _parent.header.len_entity_data

  entity_polylink_data1_t:
    seq:
      - id: data
        type: u1
        repeat: eos

  entity_polylink_data2_t:
    seq:
      - id: data
        type: u1
        repeat: eos

  # 18 bytes each
  entity_polylink_t:
    seq:
      - id: lead
        type: u2
      - id: ofs_entity_polylink_data1
        type: u2
        repeat: expr
        repeat-expr: 2
      - id: ofs_entity_polylink_data2
        type: u2
        repeat: expr
        repeat-expr: 2
      - id: unknown
        type: u2
      - id: reserved
        type: u2
        repeat: expr
        repeat-expr: 3
    instances:
      getdata1:
        io: _root.entity_polylink_data1._io
        pos: ofs_entity_polylink_data1[0] * 2
        type: u1
        repeat: expr
        repeat-expr: (ofs_entity_polylink_data1[1] - ofs_entity_polylink_data1[0] + 1) * 2
      getdata2:
        io: _root.entity_polylink_data2._io
        pos: ofs_entity_polylink_data2[0] * 4
        type: u1
        repeat: expr
        repeat-expr: (ofs_entity_polylink_data2[1] - ofs_entity_polylink_data2[0] + 1) * 4

  resources_t:
    seq:
      - id: prefix
        type: resources_prefix_t
      - id: num_sounds
        type: u4
      - id: sounds
        type: sound_t
        repeat: expr
        repeat-expr: num_sounds
      - id: len_palette
        type: u4
      - id: palette
        type: palette_entry_t
        repeat: expr
        repeat-expr: len_palette / 2
      - id: num_resources
        type: u4
      - id: resources
        type: resource_t
        repeat: expr
        repeat-expr: num_resources

  resources_prefix_t:
    seq:
      - id: num_values
        type: u4
      - id: values
        type: s2
        repeat: expr
        repeat-expr: num_values

  sound_t:
    seq:
      - id: len_samples
        type: s4
      - id: maybe_pitch_adjust
        type: s4
        doc: |
          from comparing the extracted sounds with the sounds in the game
          (see https://www.youtube.com/watch?v=Wse8iFMM-jg&t=207s and E1L1.LEV
          sound 0), i think this is a speed/pitch adjust. 0x7000 seems to be
          the nominal value, with sounds with that value sounding the same. but
          notably door and elevator sound pitches sound different in game, and
          they have a different value here. however, i havent managed to find
          a consistent correlation between these values and the pitch change.
          -- vfig
      - id: bits
        type: s4
        doc: bits per sample; 8 or 16.
      - id: loop_point
        type: s4
        doc: |
          index of sample (or possibly byte offset; with 8 bit sounds its the
          same) from which to loop after reaching the end of the sound the
          first time. 0 means the entire sample loops; -1 means no loop.
      - id: samples       # signed, mono, 11025 Hz PCM
        size: len_samples

  resource_t:
    seq:
      - id: flags
        type: u1
      - id: resource_type
        type: u1
      - id: data
        type:
          switch-on: resource_type
          cases:
            0x82: texture_t # 130
            0x34: resource_0x34_t # 52
            0x6a: resource_0x6a_t # 106
            0x6c: resource_0x6c_t # 108

  texture_t:
    seq:
      - id: palette
        type: palette_entry_t
        repeat: expr
        repeat-expr: 16
      - id: bitmap
        type: b4
        repeat: expr
        repeat-expr: 64 * 64

  resource_0x34_t:
    seq:
      - id: unknown0
        type: u2
      #- id: unknown1
      #  size: 0x400
      - id: unknown1
        type: palette_entry_t
        repeat: expr
        repeat-expr: 512

  resource_0x6a_t:
    seq:
      - id: unknown0
        type: u2
      - id: len_data
        type: u2
      - id: data
        size: len_data

  resource_0x6c_t:
    seq:
      - id: unknown0
        type: u2
      - id: len_data
        type: u2
      - id: data
        size: len_data

  len_and_unknown_t:
    seq:
    - id: len_data
      type: u4
    - id: data
      size: len_data
