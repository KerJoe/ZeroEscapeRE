// ImHex pattern for .bm (simple model) files.
// Copyright (C) 2023 KerJoe.
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

struct Vector3f {
    float x, y, z;
};

struct Matrix44f {
    float row0[4];
    float row1[4];
    float row2[4];
    float row3[4];
};

struct Verts {
    Vector3f geom_vert;
    Vector3f norm_vert;
    Vector3f uv_vert;
};

struct VertsEntry {
    u32 vert_count;
    Verts verts[vert_count];
};

struct Indices {
    u16 p0, p1, p2;
};

struct IndicesEntry {
    u32 indc_count;
    Indices indcs[indc_count/3];
};

struct TextureName {
    u32 texture_name_size;
    char texture_name[texture_name_size];
    padding[12];
};

struct MeshEntry {
    padding[4];
    IndicesEntry indcs_entry [[single_color]];
    VertsEntry verts_entry [[single_color]];
    padding[52];
    bool has_texture;
    TextureName texture_name[has_texture] [[single_color]];
    padding[24];
};

u32 mesh_count @ $;
MeshEntry mesh_entries[mesh_count] @ $;