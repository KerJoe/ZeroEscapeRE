// ImHex pattern for .bsm (rigged model) files.
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
    u8 bone0;
    u8 bone1;
    u8 ; // clone of bone0
    u8 ; // clone of bone0
    float bone0_weight;
    float bone1_weight;
    float ; // clone of bone0_weight
    float ; // clone of bone0_weight
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

struct BonesIndexEntry {
    u32 bone_count;
    u32 bones[bone_count];
};

struct Bone {
    u32 internal_bone_name_size;
    char internal_bone_name[internal_bone_name_size];
    u32 proper_bone_name_size;
    char proper_bone_name[proper_bone_name_size];
    Matrix44f bone_transform;
    float ;
};

struct BoneHeir {
    u32 child_count;
    u32 child[child_count];
};

struct BoneNamesEntry {
    u32 bone_name_count;
    Bone bone_names[bone_name_count];
    BoneHeir bone_heirs[bone_name_count];
};

struct TextureName {
    u32 texture_name_size;
    char texture_name[texture_name_size];
};

struct AnimIndcs {
    u32 indc_count;
    u16 indcs[indc_count];
};

struct AnimVerts {
    u32 vert_count;
    Vector3f verts[vert_count];
};

struct AnimMesh {
    AnimIndcs anim_indcs [[single_color]];
    AnimVerts anim_verts [[single_color]];
};

struct Anim {
    u32 anim_count;
    AnimMesh anims[anim_count];
};

struct AnimName {
    u32 anim_name_size;
    char anim_name[anim_name_size];
};

struct AnimNameEntry {
    u32 anim_entry_count;
    AnimName anim_entries[anim_entry_count];
};

struct ExtraMeshEntry {
    padding[12];
    VertsEntry vert_entries [[single_color]];
    padding[4];
    IndicesEntry indc_entries [[single_color]];
    BonesIndexEntry bone_index_entries [[single_color]];
    Matrix44f [[single_color]];
    padding[94];
};

struct MeshEntry {
    padding[12];
    VertsEntry vert_entries [[single_color]];
    padding[4];
    IndicesEntry indc_entries [[single_color]];
    BonesIndexEntry bone_index_entries [[single_color]];
    Matrix44f [[single_color]];
    padding[53];
    TextureName texture_name [[single_color]];
    padding[52];

    bool extra_mesh;
    ExtraMeshEntry extra_mesh_entry[extra_mesh];
};

u32 mesh_count @ $;
MeshEntry mesh_entries[mesh_count] @ $;

BoneNamesEntry bone_names_entry @ $ [[single_color]];

u32 animation_count @ $ + 48;
Anim anims[animation_count] @ $;
AnimNameEntry anim_name_entry @ $ [[single_color]];
