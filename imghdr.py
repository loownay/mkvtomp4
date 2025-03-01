"""Recognize image file formats based on their first few bytes."""

__all__ = ["what"]

def what(file, h=None):
    """Recognize image file formats based on their first few bytes."""
    if h is None:
        if isinstance(file, str):
            with open(file, 'rb') as f:
                h = f.read(32)
        else:
            location = file.tell()
            h = file.read(32)
            file.seek(location)
            if not h:
                return None

    for tf in tests:
        res = tf(h, file)
        if res:
            return res
    return None


# ---------------------------------#
# Recognize image headers

def test_jpeg(h, f):
    """JPEG data in JFIF or Exif format"""
    if h[0:2] == b'\xff\xd8':
        return 'jpeg'

def test_png(h, f):
    """PNG data"""
    if h[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'

def test_gif(h, f):
    """GIF ('87 and '89 variants)"""
    if h[:6] in (b'GIF87a', b'GIF89a'):
        return 'gif'

def test_tiff(h, f):
    """TIFF (can be in Motorola or Intel byte order)"""
    if h[:2] in (b'MM', b'II'):
        return 'tiff'

def test_rgb(h, f):
    """SGI image library"""
    if h[:2] == b'\x01\xda':
        return 'rgb'

def test_pbm(h, f):
    """PBM (portable bitmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'14' and h[2] in b' \t\n\r':
        return 'pbm'

def test_pgm(h, f):
    """PGM (portable graymap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'25' and h[2] in b' \t\n\r':
        return 'pgm'

def test_ppm(h, f):
    """PPM (portable pixmap)"""
    if len(h) >= 3 and \
        h[0] == ord(b'P') and h[1] in b'36' and h[2] in b' \t\n\r':
        return 'ppm'

def test_rast(h, f):
    """Sun raster file"""
    if h[:4] == b'\x59\xa6\x6a\x95':
        return 'rast'

def test_xbm(h, f):
    """X bitmap (X10 or X11)"""
    if h[:7] == b'#define':
        return 'xbm'

def test_bmp(h, f):
    """BMP file"""
    if h[:2] == b'BM':
        return 'bmp'

def test_webp(h, f):
    """WebP file"""
    if h[:4] == b'RIFF' and h[8:12] == b'WEBP':
        return 'webp'

def test_exr(h, f):
    """OpenEXR file"""
    if h[:4] == b'\x76\x2f\x31\x01':
        return 'exr'

tests = [
    test_jpeg,
    test_png,
    test_gif,
    test_tiff,
    test_rgb,
    test_pbm,
    test_pgm,
    test_ppm,
    test_rast,
    test_xbm,
    test_bmp,
    test_webp,
    test_exr
] 