from _EscPosImage import EscPosImage
from _QrCodeGenerator import QrCodeGenerator
import six


GS = b'\x1d'


class EscPosQrCodeGenerator(object):
    @staticmethod
    def generate_qr_code(content):
        # type: (unicode) -> str
        img = QrCodeGenerator.generate_qr_code(content)
        return EscPosQrCodeGenerator._print_image(EscPosImage(img))

    @staticmethod
    def _print_image(esc_pos_image):
        # type: (EscPosImage) -> str
        density_byte = 0
        header = GS + \
                 b"v0" + \
                 six.int2byte(density_byte) + \
                 EscPosQrCodeGenerator._int_low_high(esc_pos_image.width_bytes, 2) + \
                 EscPosQrCodeGenerator._int_low_high(esc_pos_image.height, 2)
        return header + esc_pos_image.to_raster_format()

    @staticmethod
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
