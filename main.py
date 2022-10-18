import struct
from PIL import Image
import TextureImport

if __name__ == '__main__':
    texPath = r"C:\Users\Darkness\Desktop\Mod Tools FQ\re_chunk_000\natives\x64\streaming\character\player\pl0300_vergil\pl0300_body\pl0300_coat_nrmr.tex.11"
    rawImage = TextureImport.TEX(texPath, 'RGBA')

    image = Image.frombuffer('RGBA', (rawImage.__w, rawImage.__h), rawImage.__buffer)
    image.show()