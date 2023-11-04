// ImHex pattern for .motion (skeletal animation) files.
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

struct ExtraEntry {
    u32 unk0_count;
    float unk0[unk0_count];
    u32 unk1_count;
    float unk1[unk1_count];
    u32 unk2_count;
    u32 unk2[unk2_count];
    u32 ;
    u32 ;
    u32 ;
    u32 unk3_count;
    float unk3[unk3_count];
    u32 unk4_count;
    float unk4[unk4_count];
};

struct AngleEntry {
    u32 ;
    u32 ;
    u32 ;
    float rotation_x;
    float rotation_y;
    float rotation_z;
};

struct AngleExtraEntry {
    u32 unk0_count;
    u32 unk0[unk0_count];
    u32 unk1_count;
    float unk1[unk1_count];
};

struct DynamicEntry {
    u32 bone_name_count;
    char bone_name[bone_name_count];
    u32 ;
    u32 unk3;
    u32 ;
    float offset_x;
    float offset_y;
    float offset_z;
    AngleEntry angle_entry[unk3>1];
    AngleExtraEntry angle_extra_entry[unk3>2];
    u32 ;
    u32 ;
    u32 animation_entry_count;
    u32 ;
    u32 ;
    u32 timestamp_count;
    float timestamps[timestamp_count];
    u32 movement_count;
    float movements[movement_count];
    ExtraEntry extra_entry[animation_entry_count - 1];
    u32 unk0_count;
    u32 unk0[unk0_count];
    u32 unk1_count;
    u32 unk1[unk1_count];
    u32 unk2_count;
    u32 unk2[unk2_count];
    u32 ;
};

struct MorphEntry {
    u32 model_name_size;
    char model_name[model_name_size];
    u32 animation_count;
    float animation_progress[animation_count];
};

struct StaticEntry {
    u32 bone_name_size;
    char bone_names[bone_name_size];
    Matrix44f transform [[single_color]];
};

u32 dynamic_entry_count @ $ + 0x20;
DynamicEntry dynamic_entries[dynamic_entry_count] @ $;
u32 morph_entry_count @ $;
MorphEntry morph_entries[morph_entry_count] @ $;
u32 static_entry_count @ $;
StaticEntry static_entries[static_entry_count] @ $;
