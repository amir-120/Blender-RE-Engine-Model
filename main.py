from enum import IntEnum

class MaterialFlags(IntEnum):
    BaseTwoSideEnable = 0x01 << 0
    BaseAlphaTestEnable = 0x01 << 1
    ShadowCastDisable = 0x01 << 2
    VertexShaderUsed = 0x01 << 3
    EmissiveUsed = 0x01 < 4
    TessellationEnable = 0x01 << 5
    EnableIgnoreDepth = 0x01 << 6
    AlphaMaskUsed = 0x01 << 7
    ForcedTwoSideEnable = 0x01 << 8
    TwoSideEnable = 0x01 << 9
    TessFactor = 0x01 << 10
    PhongFactor = 0x01 << 16
    RoughTransparentEnable = 0x01 << 24
    ForcedAlphaTestEnable = 0x01 << 25
    AlphaTestEnable = 0x01 << 26
    SSSProfileUsed = 0x01 << 27
    EnableStencilPriority = 0x01 << 28
    RequireDualQuaternion = 0x01 << 29
    PixelDepthOffsetUsed = 0x01 << 30
    NoRayTracing = 0x01 << 31

if __name__ == '__main__':
    #texPath = r"C:\Users\Darkness\Desktop\Mod Tools FQ\re_chunk_000\natives\x64\character\player\pl0300_vergil\pl0300_body\pl0300_coat_nrmr.tex.11"
    #rawImage = TEX(texPath)
    #image = Image.frombytes('RGBA', (rawImage.w, rawImage.h), bytes(rawImage.data))
    #image.save(r"C:\Users\Darkness\Desktop\test.png", bitmap_format="png")
    #image.show()
    print([x.value for x in MaterialFlags])