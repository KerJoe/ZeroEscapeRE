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
    u8 joint_id0;
    u8 joint_id1;
    u8 ; // clone of joint_id0
    u8; // clone of joint_id0
    float joint_weight0;
    float joint_weight1;
    float; // clone of joint_weight0
    float; // clone of joint_weight0
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

struct BonesIndexEntry {
    u32 bones_size;
    u32 bones[bones_size];
};

struct BoneName {
    u32 size_index_name;
    char index_name[size_index_name];
    u32 size_bone_name;
    char bone_name[size_bone_name];
    Matrix44f boneTransform; // 4*4 Joint transform ?
    float unk;
};

struct BoneHeir { // ?
    u32 children_size;
    u32 children[children_size];
};

struct BonesNameEntry {
    u32 bones_names_size;
    BoneName bones_names[bones_names_size];
    BoneHeir bone_heir[bones_names_size];
};


struct TextureName {
    u32 texture_name_size;
    char texture_name[texture_name_size];
};

struct AnimVertInds {
    u32 size;
    u16 inds[size];
};

struct AnimVertVals {
    u32 size;
    Vector3f verts[size];
};

struct AnimMesh {
    AnimVertInds anim_vert_inds [[single_color]];
    AnimVertVals anim_vert_vals [[single_color]];
};

struct Anim {
    u32 meshes_count;
    AnimMesh anim_meshes[meshes_count];
};

struct AnimName {
    u32 size;
    char name[size];
};

struct AnimNameEntry {
    u32 size;
    AnimName anim_names[size];
};

struct ExtraMeshEntry {
    padding[12];
    VertsEntry verts_entry [[single_color]];
    padding[4];
    FacesEntry faces_entry [[single_color]];
    BonesIndexEntry bones_index_entry [[single_color]];    
    Matrix44f [[single_color]];   
    padding[94]; 
};

struct MeshEntry {
    padding[12];
    VertsEntry verts_entry [[single_color]];
    padding[4];
    FacesEntry faces_entry [[single_color]];
    BonesIndexEntry bones_index_entry [[single_color]];    
    Matrix44f [[single_color]];
    padding[53];
    TextureName texture_name [[single_color]];
    padding[52];    
  
    bool extra_mesh;
    ExtraMeshEntry extra_mesh_entry[extra_mesh];
};

u32 mesh_count @ 0x00;
MeshEntry mesh_entries[mesh_count] @ $;

BonesNameEntry bones_names_entry @ $ [[single_color]];

u32 animation_count @ $ + 48;
Anim anims[animation_count] @ $;
AnimNameEntry anim_name_entry @ $ [[single_color]];
