"""
QR Generation Module

This module contains utilities for generating QR codes from student data.
"""

from .create_qrcode import generate_qr_codes
from .import_qrcode import generate_simple_qr_codes

__all__ = ['generate_qr_codes', 'generate_simple_qr_codes']
