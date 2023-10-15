struct TextureNameEntry {
    u32 texture_name_size;
    char texture_name[texture_name_size];     
    u32 u1[3];
};

struct TextureEntry {
    u32 u0[13];
    bool has_texture;
    TextureNameEntry texture_name_entry[has_texture];
};

struct MeshEntry {
    u32 model_name_size;
    char model_name[model_name_size];
    u32 ;
    u32 texture_count;
    TextureEntry texture_entry[texture_count];
};

struct SceneEntry {
    u32;
    char type[4];
    u32 name_size;
    char name[name_size];
    float ;
    float u0[9];
    u32 ;
    u32 mesh_count;
    u32 ;
    u32 ;
    MeshEntry mesh_entry[mesh_count];
    u32 u1[mesh_count == 0];    
} [[single_color]];

SceneEntry scene_entries[101] @ $;
//SceneEntry scene_entries[1] @ 0x1AB9;