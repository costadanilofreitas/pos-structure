# -*- coding: utf-8 -*-
from constants import *
import qrcode
from image import EscposImage
from PIL import Image, ImageChops


def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)


# im = Image.open("bord3.jpg")
# im = trim(im)
# im.show()


def image(img_source, high_density_vertical=True, high_density_horizontal=True, impl="bitImageRaster",
          fragment_height=1024):
    """ Print an image

    You can select whether the printer should print in high density or not. The default value is high density.
    When printing in low density, the image will be stretched.

    Esc/Pos supplies several commands for printing. This function supports three of them. Please try to vary the
    implementations if you have any problems. For example the printer `IT80-002` will have trouble aligning
    images that are not printed in Column-mode.

    The available printing implementations are:

        * `bitImageRaster`: prints with the `GS v 0`-command
        * `graphics`: prints with the `GS ( L`-command
        * `bitImageColumn`: prints with the `ESC *`-command

    :param img_source: PIL image or filename to load: `jpg`, `gif`, `png` or `bmp`
    :param high_density_vertical: print in high density in vertical direction *default:* True
    :param high_density_horizontal: print in high density in horizontal direction *default:* True
    :param impl: choose image printing mode between `bitImageRaster`, `graphics` or `bitImageColumn`
    :param fragment_height: Images larger than this will be split into multiple fragments *default:* 1024

    """
    # with open("\\\\.\\COM8", "w") as prnt:
    im = EscposImage(img_source)
    prnt = ""
    if im.height > fragment_height:
        fragments = im.split(fragment_height)
        for fragment in fragments:
            image(fragment,
                  high_density_vertical=high_density_vertical,
                  high_density_horizontal=high_density_horizontal,
                  impl=impl,
                  fragment_height=fragment_height)
        return

    if impl == "bitImageRaster":
        # GS v 0, raster format bit image
        density_byte = (0 if high_density_horizontal else 1) + (0 if high_density_vertical else 2)
        header = GS + b"v0" + six.int2byte(density_byte) + _int_low_high(im.width_bytes, 2) + _int_low_high(im.height,
                                                                                                            2)
        prnt += (header + im.to_raster_format())
        return prnt

    if impl == "bitImageColumn":
        # ESC *, column format bit image
        density_byte = (1 if high_density_horizontal else 0) + (32 if high_density_vertical else 0)
        header = ESC + b"*" + six.int2byte(density_byte) + _int_low_high(im.width, 2)
        outp = [ESC + b"3" + six.int2byte(16)]  # Adjust line-feed size
        for blob in im.to_column_format(high_density_vertical):
            outp.append(header + blob + b"\n")
        outp.append(ESC + b"2")  # Reset line-feed size
        return b''.join(outp)
        # prnt += (b''.join(outp))


def qr(content, ec=QR_ECLEVEL_L, size=3, model=QR_MODEL_2, native=False):
    """ Print QR Code for the provided string

    :param content: The content of the code. Numeric data will be more efficiently compacted.
    :param ec: Error-correction level to use. One of QR_ECLEVEL_L (default), QR_ECLEVEL_M, QR_ECLEVEL_Q or
        QR_ECLEVEL_H.
        Higher error correction results in a less compact code.
    :param size: Pixel size to use. Must be 1-16 (default 3)
    :param model: QR code model to use. Must be one of QR_MODEL_1, QR_MODEL_2 (default) or QR_MICRO (not supported
        by all printers).
    :param native: True to render the code on the printer, False to render the code as an image and send it to the
        printer (Default)
    """
    # Basic validation
    if ec not in [QR_ECLEVEL_L, QR_ECLEVEL_M, QR_ECLEVEL_H, QR_ECLEVEL_Q]:
        raise ValueError("Invalid error correction level")
    if not 1 <= size <= 16:
        raise ValueError("Invalid block size (must be 1-16)")
    if model not in [QR_MODEL_1, QR_MODEL_2, QR_MICRO]:
        raise ValueError("Invalid QR model (must be one of QR_MODEL_1, QR_MODEL_2, QR_MICRO)")
    if content == "":
        # Handle edge case by printing nothing.
        return
    if not native:
        # Map ESC/POS error correction levels to python 'qrcode' library constant and render to an image
        if model != QR_MODEL_2:
            raise ValueError("Invalid QR model for qrlib rendering (must be QR_MODEL_2)")
        python_qr_ec = {
            QR_ECLEVEL_H: qrcode.constants.ERROR_CORRECT_H,
            QR_ECLEVEL_L: qrcode.constants.ERROR_CORRECT_L,
            QR_ECLEVEL_M: qrcode.constants.ERROR_CORRECT_M,
            QR_ECLEVEL_Q: qrcode.constants.ERROR_CORRECT_Q
        }
        qr_code = qrcode.QRCode(version=None, box_size=size, border=1, error_correction=python_qr_ec[ec])
        qr_code.add_data(content)
        qr_code.make(fit=True)
        qr_img = qr_code.make_image()
        with qr_img._img.convert("RGB") as im:
            # Convert the RGB image in printable image
            return image(im)
        # Native 2D code printing
        # cn = b'1'  # Code type for QR code
        # # Select model: 1, 2 or micro.
        # _send_2d_code_data(six.int2byte(65), cn, six.int2byte(48 + model) + six.int2byte(0))
        # # Set dot size.
        # _send_2d_code_data(six.int2byte(67), cn, six.int2byte(size))
        # # Set error correction level: L, M, Q, or H
        # _send_2d_code_data(six.int2byte(69), cn, six.int2byte(48 + ec))
        # # Send content & print
        # _send_2d_code_data(six.int2byte(80), cn, content.encode('utf-8'), b'0')
        # _send_2d_code_data(six.int2byte(81), cn, b'', b'0')


def insert_space(string, length):
    return ' '.join(string[i:i + length] for i in xrange(0, len(string), length))


def barcode(code, one_line=True):
    import barcode
    from PIL import Image
    from barcode.writer import ImageWriter
    wrt = ImageWriter(print_text=False)

    if not one_line:
        # Return barcode in two lines
        code128_1 = barcode.Code128(code[:22], writer=wrt)
        code128_1.save('imagem')
        code128_2 = barcode.Code128(code[22:], writer=wrt)
        code128_2.save('imagem2')

        with Image.open('imagem.png') as img1:
            with Image.open('imagem2.png') as img2:
                with img1.resize((img1.width, int(img1.height * 0.33))) as img3:
                    with img2.resize((img2.width, int(img2.height * 0.33))) as img4:
                        with img3.convert("RGB") as pilimg1:
                            with img4.convert("RGB") as pilimg2:
                                return image(pilimg1), image(pilimg2)
    else:
        # Return barcode in one line
        code128_1 = barcode.Code128(code[:], writer=wrt)
        code128_1.save('imagem')
        with Image.open('imagem.png') as img1:
            with trim(img1) as img2:  # Trim image borders
                with img2.resize((int(img2.width * 0.78), int(img2.height * 0.5))) as img3: # Magic numbers so that image fits in Epson TMT-T88IV using a total of 56 characters
                    with img3.convert("RGB") as pilimg1:
                        return image(pilimg1), ""


def _int_low_high(inp_number, out_bytes):
    """ Generate multiple bytes for a number: In lower and higher parts, or more parts as needed.

    :param inp_number: Input number
    :param out_bytes: The number of bytes to output (1 - 4).
    """
    max_input = (256 << (out_bytes * 8) - 1)
    if not 1 <= out_bytes <= 4:
        raise ValueError("Can only output 1-4 byes")
    if not 0 <= inp_number <= max_input:
        raise ValueError("Number too large. Can only output up to {0} in {1} byes".format(max_input, out_bytes))
    outp = b''
    for _ in range(0, out_bytes):
        outp += six.int2byte(inp_number % 256)
        inp_number //= 256
    return outp


if __name__ == '__main__':
    pass
