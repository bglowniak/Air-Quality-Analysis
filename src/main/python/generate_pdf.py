from fpdf import FPDF, HTMLMixin
import os


FONT_FAMILY = 'Times'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ReportPDF(FPDF, HTMLMixin):
    def header(self):
        self.set_font('Times', 'B', 15)  # Times New Roman, Bold, 15

        self.cell(w=10)
        self.image(os.path.join(BASE_DIR, 'resources', 'base', 'image.png'))

        # Move to the right, and print title
        self.cell(w=70)
        self.cell(w=60, h=10, txt='Example Title', align='C', border=1, ln=0, link='C')

        # Line break
        self.ln(5)

    # Page footer
    def footer(self):
        self.set_font('Times', '', 10)

        self.set_xy(-60, -20)
        self.cell(w=50, h=10, txt='Sample Footer Text')


if __name__ == '__main__':
    # Setup PDF
    pdf = ReportPDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 11)

    pdf.cell(w=0, h=10, txt='Hello', border=0, ln=0)

    # Write to output file
    output_filename = os.path.join('', 'output.pdf')
    pdf.output(output_filename, dest='F')

    # Uncomment below to open the file (only works on macOS)
    os.system('open %s' % output_filename)
