"""Draw the app icon: python -m tools.make_icon

Writes src/ck_dps_solver/data/app_icon.png (the window icon) and packaging/icon.ico (the exe's icon, 16 to 256 px).
The icon is a rising bar chart on the sunset theme's orange-to-red gradient, readable down to 16 px.
"""
import os
import struct
import sys

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath  # noqa: E402

from tools import PACKAGE_DIR, REPO  # noqa: E402

SIZES = [16, 24, 32, 48, 64, 128, 256]
TOP, BOTTOM = QColor('#ffb347'), QColor('#d6453d') # Sunset orange to red
BARS = [0.38, 0.62, 0.86] # Bar heights, as a share of the drawing area


def draw(size):
    image = QImage(size, size, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    p = QPainter(image)
    p.setRenderHint(QPainter.Antialiasing)
    gradient = QLinearGradient(0, 0, 0, size)
    gradient.setColorAt(0, TOP)
    gradient.setColorAt(1, BOTTOM)
    background = QPainterPath()
    background.addRoundedRect(QRectF(0, 0, size, size), size * 0.22, size * 0.22)
    p.fillPath(background, gradient)
    # Three rising bars, white
    margin, gap = size * 0.2, size * 0.07
    width = (size - 2 * margin - 2 * gap) / 3
    floor = size - margin
    p.setPen(Qt.NoPen)
    p.setBrush(QColor('#fff8ef'))
    for i, height in enumerate(BARS):
        h = (size - 2 * margin) * height
        p.drawRoundedRect(QRectF(margin + i * (width + gap), floor - h, width, h), width * 0.18, width * 0.18)
    p.end()
    return image


def png_bytes(image):
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, 'PNG')
    return bytes(data)


def write_ico(path, images):
    """An .ico holding PNG images (supported since Windows Vista)"""
    pngs = [(size, png_bytes(image)) for size, image in images]
    header = struct.pack('<HHH', 0, 1, len(pngs))
    offset = 6 + 16 * len(pngs)
    entries, blobs = b'', b''
    for size, png in pngs:
        side = 0 if size >= 256 else size # 0 means 256
        entries += struct.pack('<BBBBHHII', side, side, 0, 0, 1, 32, len(png), offset)
        blobs += png
        offset += len(png)
    with open(path, 'wb') as file:
        file.write(header + entries + blobs)


def main():
    app = QGuiApplication(sys.argv[:1]) # noqa: F841 (needed for painting)
    images = [(size, draw(size)) for size in SIZES]
    draw(256).save(os.path.join(PACKAGE_DIR, 'data', 'app_icon.png'))
    write_ico(os.path.join(REPO, 'packaging', 'icon.ico'), images)
    print('Wrote data/app_icon.png and packaging/icon.ico')


if __name__ == '__main__':
    main()
