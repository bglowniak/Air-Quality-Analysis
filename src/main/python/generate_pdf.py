from fpdf import FPDF
import os
import csv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class ReportPDF(FPDF):
    def set_header(self, header_path):
        self.header_path = header_path

    def header(self):
        self.set_font('Times', 'B', 15)  # Times New Roman, Bold, 15
        # ATSDR Logo
        self.image(self.header_path, w=50,h=13.187)
        # adjust position to style the Title
        self.set_xy(x=60,y=10)
        self.cell(w=0,h=7.187, txt='Centers for Disease Control Prevention', border=0, ln=2)
        self.set_font('Times', '', 12)
        self.cell(w=0,h=6, txt='Agency for Toxic Substances and Disease Registry', border=0, ln=0)
        # Line break for position
        self.ln(5)

    # Page footer
    # def footer(self):
    #     self.set_font('Times', '', 10)
    #
    #     self.set_xy(-60, -20)
    #     self.cell(w=50, h=10, txt='Sample Footer Text')

def create_pdf(sensor_name, averaging_range, start_time, stop_time, process_start_time, file_dict, threshold_table, output_folder, header):
    """
    Creates the pdf and returns the full path to where the PDF was written to
    """
    # /////////
    # Setup PDF
    # /////////

    pdf = ReportPDF()
    pdf.set_header(header)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 11)

    # //////////////////////////////////
    # Details about the process that ran
    # //////////////////////////////////

    # Writing data to cells on the page using nifty new python fprint
    pdf.set_font('Times', '', 10)
    pdf.ln(8)
    pdf.cell(w=5,h=5, txt='Sensor: '+ sensor_name +' | Averaging Range: '+ averaging_range, border=0, ln=0, align='L')
    pdf.ln(8)
    pdf.cell(w=5,h=0, txt='Start Time: '+ start_time +' | Stop Time: '+ stop_time +' | Report Generated: '+ process_start_time, border=0, ln=0, align='L')
    pdf.ln(10)

    # /////////////
    # Details Table
    # /////////////

    # Page width
    page_width = pdf.w - 2*pdf.l_margin
    # Set column width to 1/9 of page width to distribute content
    # evenly across table and page
    col_width = page_width/9
    #import the csv dataset into array
    detail_file_path = file_dict['basic_stats']
    with open(detail_file_path, newline='') as csvfile:
        detail_data = list(csv.reader(csvfile))
    pdf.set_font('Times','',10.0)
    # 2*text height for increased padding
    text_height = pdf.font_size * 2
    # Construct table from detail_data
    for row in detail_data:
        for datum in row:
            pdf.cell(col_width, text_height, str(datum), border=1)
        pdf.ln(text_height)
    # add space
    pdf.ln(10)

    # //////////////////
    # Visualization pngs
    # //////////////////

    # get file paths for all the visualizations
    boxplot_file_path = file_dict['boxplot']
    threshold25_file_path = file_dict['PM25_thresh']
    threshold10_file_path = file_dict['PM10_thresh']
    humidity_file_path = file_dict['humidity_graph']
    files = [boxplot_file_path, threshold25_file_path, threshold10_file_path, humidity_file_path]
    # Create the image and spacing for each visualization
    for file_path in files:
        pdf.image(file_path, w=120,h=120)
        pdf.ln(5)

    # ///////////////
    # Threshold_table
    # ///////////////

    # Set column width to 1/6 of page width to distribute content
    # evenly across table and page
    col_width = page_width/6
    # Construct table from detail_data
    for row in threshold_table:
        for datum in row:
            pdf.cell(col_width, text_height, str(datum), border=1)
        pdf.ln(text_height)

    # Write to output file
    output_filename = os.path.join(output_folder, 'summary.pdf')
    pdf.output(output_filename, dest='F')
