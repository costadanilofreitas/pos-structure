from typing import Any  # noqa
import qrcode


class QrCodeGenerator(object):
    @staticmethod
    def generate_qr_code(content):
        # type: (unicode) -> Any
        qr_code = qrcode.QRCode(version=2,
                                box_size=6,
                                border=1,
                                error_correction=qrcode.constants.ERROR_CORRECT_L)
        qr_code.add_data(content)
        qr_code.make(fit=True)

        return qr_code.make_image().convert("RGB")
