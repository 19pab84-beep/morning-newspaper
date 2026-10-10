#!/usr/bin/env python3
"""Experimental, independent PDF -> Brother HBP stream test.

Stream layout follows the public brlaser driver implementation by Peter De Wachter
(GPLv2+): https://github.com/pdewacht/brlaser . This educational test adapter
is distributed under GPL-2.0-or-later as a derivative interpretation of that code.
Requires Ghostscript (gs), no Windows/CUPS runtime. Tested structurally only;
HL-1210WE physical compatibility MUST be verified by user.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def pbm_read(path):
    data = path.read_bytes()
    ptr = 0
    def get_token():
        nonlocal ptr
        while ptr < len(data):
            if data[ptr] in b' \t\r\n':
                ptr += 1
            elif data[ptr] == 35:
                ptr = data.find(b'\n', ptr) + 1
            else:
                break
        start = ptr
        while ptr < len(data) and data[ptr] not in b' \t\r\n#':
            ptr += 1
        return data[start:ptr]
    if get_token() != b'P4':
        raise ValueError(f'{path}: expected binary PBM (P4)')
    width = int(get_token())
    height = int(get_token())
    if data[ptr:ptr+2] == b'\r\n':
        ptr += 2
    else:
        assert data[ptr:ptr+1] in (b' ', b'\t', b'\n', b'\r'), 'Invalid PBM header separator'
        ptr += 1
    stride = (width + 7) // 8
    pixels = memoryview(data)[ptr:]
    if len(pixels) != stride * height:
        raise ValueError(f'{path}: incorrect raster size {len(pixels)}, expected {stride*height}')
    return width, height, stride, pixels


def overflow(n):
    if n < 0:
        return b''
    return bytes([255]) * (n // 255) + bytes([n % 255])


def substitute(offset, contents):
    assert 0 <= offset < 10000
    n = len(contents) - 1
    assert n >= 0
    return (bytes([(min(offset, 15) << 3) | min(n, 7)])
            + overflow(offset - 15) + overflow(n - 7) + contents)


def encode_line(line, reference=None):
    # PBM P4 has black=1, white=0, which is brlaser raster polarity.
    if not any(line):
        return b'\xff'
    if reference is None:
        return b'\x01' + substitute(0, line)
    assert len(reference) == len(line)
    start = 0
    while start < len(line) and line[start] == reference[start]:
        start += 1
    if start == len(line):
        return b'\x00'
    end = len(line)
    while end > start and line[end-1] == reference[end-1]:
        end -= 1
    # One substitution command is sufficient and valid for our smoke test.
    return b'\x01' + substitute(start, line[start:end])


def page_header():
    return (b'\x1b%-12345X@PJL\n'
        b'@PJL SET RAS1200MODE = FALSE\n'
        b'@PJL SET RESOLUTION = 600\n'
        b'@PJL SET ECONOMODE = OFF\n'
        b'@PJL SET SOURCETRAY = AUTO\n'
        b'@PJL SET MEDIATYPE = PLAIN\n'
        b'@PJL SET PAPER = A4\n'
        b'@PJL SET PAGEPROTECT = AUTO\n'
        b'@PJL SET ORIENTATION = PORTRAIT\n'
        b'@PJL ENTER LANGUAGE = PCL\n'
        b'\x1bE\x1b&l1X')


def page_stream(width, height, stride, pixels):
    # Blank remainder bits on right edge, following P4 raster semantics.
    mask = 0xff << (8-(width % 8)) & 0xff if width % 8 else 0xff
    output = bytearray(page_header())
    output += b'\x1b*b1030m'
    lines = []
    block_bytes = 0
    previous = None
    def flush():
        nonlocal block_bytes
        if not lines:
            return
        output.extend(f'{block_bytes + 2}w'.encode('ascii'))
        output.extend(bytes((0, len(lines))))
        for e in lines:
            output.extend(e)
        lines.clear()
        block_bytes = 0
    for i in range(height):
        data = pixels[i*stride:(i+1)*stride].tobytes()
        if mask != 0xff:
            data = data[:-1] + bytes((data[-1] & mask,))
        if i % 64 == 0:
            flush()
            encoded = encode_line(data)
        else:
            encoded = encode_line(data, previous)
            if block_bytes + len(encoded) >= 16350:
                flush()
                encoded = encode_line(data)
        lines.append(encoded)
        block_bytes += len(encoded)
        previous = data
    flush()
    output.extend(b'1030M\x0c')
    return output


def build(pdf: Path, prn: Path):
    if not shutil.which('gs'):
        raise RuntimeError('Ghostscript (gs) must be installed in your Linux runtime')
    with tempfile.TemporaryDirectory() as tmp:
        template = str(Path(tmp) / 'page-%03d.pbm')
        subprocess.run(['gs', '-q', '-dSAFER', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pbmraw',
                        '-r600', '-dFIXEDMEDIA', '-sPAPERSIZE=a4', '-dPDFFitPage',
                        f'-sOutputFile={template}', str(pdf)], check=True)
        sheets = sorted(Path(tmp).glob('page-*.pbm'))
        if not sheets:
            raise RuntimeError('Ghostscript returned no pages')
        name = b'PORANNA PRASA - DAILY EDITION'
        job = bytearray(b'\0' * 128)
        job += b'\x1b%-12345X@PJL\n@PJL JOB NAME="' + name + b'"\n'
        for sheet in sheets:
            w, h, stride, pixels = pbm_read(sheet)
            print(f'{sheet.name}: {w} x {h} at 600 DPI, line={stride} bytes')
            job += page_stream(w, h, stride, pixels)
        job += b'\x1b%-12345X@PJL\n@PJL EOJ NAME="' + name + b'"\n\x1b%-12345X\n'
        prn.write_bytes(job)
        print(f'OUTPUT {prn} ({len(job):,} bytes, {len(sheets)} pages)')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Experimental Brother HL-1200 series HBP encoder')
    parser.add_argument('input_pdf', type=Path)
    parser.add_argument('output_prn', type=Path)
    a = parser.parse_args()
    build(a.input_pdf, a.output_prn)
