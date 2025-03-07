"""A collection of utility functions to work with PyMuPDF"""

from .fitzutils import (
    open_pdf,
    ToCEntry,
    dump_toc,
    pprint_toc,
    check_charset
)

__all__ = [
    'open_pdf',
    'ToCEntry',
    'dump_toc',
    'pprint_toc',
    'check_charset',
]
