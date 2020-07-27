"""The executable of pdftocio"""

import argparse
import sys
import os.path

from argparse import Namespace
from fitzutils import open_pdf, dump_toc, pprint_toc
from .tocparser import parse_toc
from .tocio import write_toc, read_toc
from textwrap import dedent


def getargs() -> Namespace:
    """parse commandline arguments"""

    app_desc = dedent("""
    pdftocio: manipulate the table of contents of a pdf file.

    This command can operate in two ways: it can either be used to extract the
    table of contents of a pdf, or add table of contents to a pdf using the
    output of pdftocgen.

    1. To extract the table of contents of a pdf for modification, only supply
    a input file:

        $ pdftocio in.pdf

    or if you want to print it in a readable format, use the -H flag:

        $ pdftocio -H in.pdf

    2. To write a new table of contents to a pdf using the toc file from
    pdftocgen, use input redirection,

        $ pdftocio in.pdf < toc

    pipes,

        $ pdftocgen -r recipe.toml in.pdf | pdftocio in.pdf

    or the -t flag

        $ pdftocio -t toc in.pdf

    to supply the toc file. If you want to specify an output file name, use
    the -o option

        $ pdftocio -t toc -o out.pdf in.pdf
    """)
    parser = argparse.ArgumentParser(
        description=app_desc,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('input',
                        metavar='in.pdf',
                        help="path to the input pdf document")
    parser.add_argument('-o', '--out',
                        metavar='out.pdf',
                        help="""path to the output pdf document.
                        if not given, the default is {input}_out.pdf""")
    toc_help = """
    path to the table of contents generated by pdftocgen.
    if this option is not given, the default is stdin, but
    if no input is piped or redirected to stdin, this program
    will instead print the existing ToC of the pdf file
    """
    parser.add_argument('-t', '--toc',
                        metavar='toc',
                        type=argparse.FileType('r'),
                        default='-',
                        help=toc_help)
    parser.add_argument('-H', '--human-readable',
                        action='store_true',
                        help="""print the toc in a readable format, only
                        effective when -t is not set and stdin is not piped or
                        redirected""")
    parser.add_argument('-g', '--debug',
                        action='store_true',
                        help="enable debug mode")

    return parser.parse_args()


def main():
    args = getargs()
    try:
        with open_pdf(args.input) as doc:
            if args.toc.isatty():
                # no input from user, switch to output mode and extract the toc
                # of pdf
                toc = read_toc(doc)
                if len(toc) == 0:
                    print("error: no table of contents found", file=args.out)
                    sys.exit(1)

                if args.human_readable:
                    print(pprint_toc(toc))
                else:
                    print(dump_toc(toc), end="")
                sys.exit(0)

            # an input is given, so switch to input mode
            toc = parse_toc(args.toc)
            write_toc(doc, toc)

            if args.out is None:
                # add suffix to input name as output
                pfx, ext = os.path.splitext(args.input)
                args.out = f"{pfx}_out{ext}"
            doc.save(args.out)
    except ValueError as e:
        if args.debug:
            raise e
        print("error:", e)
        sys.exit(1)
    except IOError as e:
        if args.debug:
            raise e
        print("error: unable to open file", file=sys.stderr)
        print(e, file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt as e:
        if args.debug:
            raise e
        print("error: interrupted", file=sys.stderr)
        sys.exit(1)
