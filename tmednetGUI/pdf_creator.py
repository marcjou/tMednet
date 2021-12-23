from fpdf import FPDF
import numpy as np

class PDF(FPDF):


    # Method for drawing a line on the pdf
    def lines(self):
        self.set_line_width(0.0)
        self.line(0, pdf_h / 2, 210, pdf_h / 2)

    # Method to add images to the pdf
    def imagex(self):
        self.set_xy(40.0, 25.0)
        self.image('../src/output_images/5_20210730-15_20211017-14 Hovmoller.png', link='', type='', w=170.0, h=95.5)

    # Method to set titles
    def titles(self):
        self.set_xy(0.0, 0.0)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(220, 50, 50)
        self.cell(w=210.0, h=40.0, align='C', txt="LORD OF THE PDFS", border=0)

# PDF dimensions on A4
pdf_w=210
pdf_h=297

pdf = PDF()

pdf.add_page()
pdf.lines()
pdf.imagex()
pdf.titles()
pdf.set_author('Marc Jou')
pdf.output('test.pdf', 'F')
