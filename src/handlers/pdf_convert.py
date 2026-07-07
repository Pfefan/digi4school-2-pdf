import glob
import os
import tqdm
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import cairosvg
from pypdf import PdfWriter
from slugify import slugify


class SVGtoPDFConverter:
    """
    A class to convert SVG files to PDF using cairo.
    """

    def __init__(self):
        pass

    def convert_single_svg_to_pdf(self, svg_file, svg_path, use_normal_mode=False):
        """
        Convert a single SVG file to PDF.

        Parameters:
        svg_file (str): The path to the SVG file.
        svg_path (str): The directory where the SVG file is located.
        use_normal_mode (bool): Whether to use the normal mode which lets the lib decide or not normal mode
        where the size is set manually
        doesn't have a defined size.

        Returns:
        str: The path to the generated PDF file.
        """
        pdf_filename = Path(svg_file).stem + '.pdf'
        pdf_file = Path(svg_path) / 'temp_pdf' / pdf_filename

        if use_normal_mode:
            cairosvg.svg2pdf(url=svg_file, write_to=str(pdf_file), unsafe=True)
        else:
            cairosvg.svg2pdf(url=svg_file, write_to=str(pdf_file), parent_width=923, parent_height=1312, unsafe=True)

        return pdf_file

    def convert_all_svgs_to_pdf(self, svg_path, filename, show_progress=False):
        """
        Convert all SVG files in a directory to PDF.

        Parameters:
        svg_path (str): The directory where the SVG files are located.
        filename (str): The name of the output PDF file.

        Returns:
        bool: The successful execution of the conversion
        str: The error code when the program fails
        """
        merger = None
        os.makedirs("output", exist_ok=True)
        os.makedirs(Path(svg_path) / "temp_pdf", exist_ok=True)

        svg_files = glob.glob(os.path.join(svg_path, '*.svg'))
        svg_files.sort(key=lambda x: int(Path(x).stem))
        total_pdfs = len(svg_files) if show_progress else None

        filename = slugify(filename) + ".pdf"
        output_pdf = Path("output") / filename

        use_normal_mode = self.check_valid_svgsize(svg_files[0])

        try:
            merger = PdfWriter()

            with ProcessPoolExecutor() as executor:
                future_to_pdf = {executor.submit(self.convert_single_svg_to_pdf, svg_file, svg_path, use_normal_mode): svg_file for svg_file in svg_files}

                pdf_files = []
                with tqdm.tqdm(total=total_pdfs, desc="Converting svgs to pdf", unit="pdf", disable=not show_progress) as pbar:
                    for future in as_completed(future_to_pdf):
                        pdf_file = future.result()
                        pdf_files.append(pdf_file)
                        pbar.update()

                pdf_files.sort(key=lambda f: int(Path(f).stem)) # sort the pdfs by their number

                for pdf_file in pdf_files:
                    merger.append(pdf_file)

            merger.write(output_pdf)
            if merger is not None:
                merger.close()
        except Exception as e:
            return False, str(e)

        if not use_normal_mode:
            return True, "missingsize"
        return True, ""

    def check_valid_svgsize(self, svg_file: str):
        tree = ET.parse(svg_file)
        root = tree.getroot()

        viewbox = root.get('viewBox')

        if viewbox is not None:
            return True
        else:
            return False
