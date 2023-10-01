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
    padding[1]; // clone of joint_id0
    padding[1]; // clone of joint_id0
    float joint_weight0;
    float joint_weight1;
    padding[4]; // clone of joint_weight0
    padding[4]; // clone of joint_weight0
};

struct VertsEntry {
    u32 size;
    Verts verts[size];
};

struct Face {
    u16 p0, p1, p2;
};

struct FacesEntry {
    u32 size;
    Face faces[size/3];   
};

struct BonesIndexEntry {
    u32 size;
    u32 bones[size];
};

struct BoneName {
    u32 size_index_name;
    char index_name[size_index_name];
    u32 size_bone_name;
    char bone_name[size_bone_name];
    Matrix44f boneTransform; // 4*4 Joint transform ?
    float unk;
};

struct BonesNameEntry {
    u32 size;
    BoneName bones_names[size];
};

struct TextureName {
    u32 size;
    char name[size];
};


u32 mesh_count @ 0x00;

VertsEntry verts_entry @ $+12 [[single_color]];

FacesEntry faces_entry @ $+4 [[single_color]];

BonesIndexEntry bones_index_entry @ $ [[single_color]];

Matrix44f unk0 @ $; // Looks like a 4*4 matrix

TextureName texture_name @ $ + 53 [[single_color]];

BonesNameEntry bones_names_entry @ $ + 53 [[single_color]];


/*VertsEntry verts_entry2 @ $+8 [[single_color]];

FacesEntry faces_entry2 @ $+4 [[single_color]];

BonesIndexEntry bones_index_entry2 @ $ [[single_color]];

float unk02[4*4] @ $; // Looks like a 4*4 matrix

BonesNameEntry bones_names_entry2 @ $ + 94 [[single_color]];*/