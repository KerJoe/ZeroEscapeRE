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
    Vector3f geometry_vert;
    Vector3f;
    Vector3f uv_vert;
};

struct VertsEntry {
    u32 verts_size;
    Verts verts[verts_size];
};

struct Face {
    u16 p0, p1, p2;
};

struct FacesEntry {
    u32 faces_size;
    Face faces[faces_size/3];   
};


struct TextureName {
    u32 texture_name_size;
    char texture_name[texture_name_size];
};

struct MeshEntry {
    padding[4];
    FacesEntry faces_entry [[single_color]];
    VertsEntry verts_entry [[single_color]];
    padding[53];
    TextureName texture_name [[single_color]];
    padding[36];
};

u32 mesh_count @ 0x00;
MeshEntry mesh_entries[2] @ $;