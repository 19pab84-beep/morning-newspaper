"""Local 600 dpi HBP candidate. No socket, HTTP, Tasker or printer access.

Reuses the existing src.build_prn encoder read-only (GPL-2.0-or-later;
brlaser interpretation by Peter De Wachter). PyMuPDF provides the raster,
so this offline path does not depend on a system Ghostscript executable.
Physical HL-1210WE compatibility still requires a user print test.
"""
from pathlib import Path
import fitz
from PIL import Image
from src.build_prn import page_stream


def build(pdf, path):
    name=b'PORANNA PRASA - V3 REVIEW ONLY'
    job=bytearray(b'\0'*128)
    job+=b'\x1b%-12345X@PJL\n@PJL JOB NAME="'+name+b'"\n'
    with fitz.open(pdf) as doc:
        if len(doc)!=4:
            raise ValueError('PRN wymaga czterech stron')
        for page in doc:
            pix=page.get_pixmap(dpi=600,colorspace=fitz.csGRAY,alpha=False)
            if pix.width<4960 or pix.height<7015:
                raise ValueError('PRN wymaga A4 / 600 dpi')
            image=Image.frombytes('L',(pix.width,pix.height),pix.samples)
            mono=image.convert('1',dither=Image.Dither.FLOYDSTEINBERG)
            # Pillow one-bit: white=1. HBP/P4 stream: black=1.
            raster=mono.tobytes().translate(bytes(v^255 for v in range(256)))
            stride=(pix.width+7)//8
            job+=page_stream(pix.width,pix.height,stride,memoryview(raster))
    job+=b'\x1b%-12345X@PJL\n@PJL EOJ NAME="'+name+b'"\n\x1b%-12345X\n'
    Path(path).write_bytes(job)
