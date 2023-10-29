// ImHex pattern for .bsn (3D scene) files.
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

#include <std/mem.pat>

struct TextureNameEntry {
    u32 texture_name_size;
    char texture_name[texture_name_size];
    u32 unk1[3];
};

struct TextureEntry {
    u32 unk0[13];
    bool has_texture;
    TextureNameEntry texture_name_entry[has_texture];
};

struct MeshEntry {
    u32 model_name_size;
    char model_name[model_name_size];
    u32 ;
    u32 texture_count;
    TextureEntry textures_entry[texture_count];
};

struct SceneEntry {
    char type[4];
    u32 name_size;
    char name[name_size];
    u32 ; // Always 0xFFFFFFFF
    float offset_x;
    float offset_y;
    float offset_z;
    float rotation_x;
    float rotation_y;
    float rotation_z;
    float size_x; // ?
    float size_y; // ?
    float size_z; // ?
    u32 ;
    u32 mesh_count;
    u32 ;
    u32 ;
    MeshEntry mesh_entry[mesh_count];
    u32 unk1[mesh_count == 0];
    u32 child_count;
} [[single_color]];

u32 scene_count @ $;
SceneEntry scene_entries[while(std::mem::size() != $)] @ $;