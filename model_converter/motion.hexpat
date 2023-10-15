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

struct DynamicEntry {
    u32 joint_name_size;
    char joint_name[joint_name_size];
    u32 ;
    u32 ;
    u32 ;
    float ;
    float ;
    float ;
    u32 ;
    u32 ;
    u32 ;
    float ;
    float ;
    float ;
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
    u32 ;
    u32 ;
    u32 ;
    u32 ;        
    u32 ;
};

struct MorphEntry {
    u32 model_name_size;
    char model_name[model_name_size];    
    u32 unk0_count;            
    u32 unk0[unk0_count];        
};

struct StaticEntry {
    u32 joint_name_size;
    char joint_name[joint_name_size];
    Matrix44f transform [[single_color]];
};

u32 dynamic_entry_count @ 0x20;
DynamicEntry dynamic_entries[dynamic_entry_count] @ $;
u32 morph_entry_count @ $;
MorphEntry morph_entries[morph_entry_count] @ $;
u32 static_entry_count @ $;
StaticEntry static_entries[static_entry_count] @ $;