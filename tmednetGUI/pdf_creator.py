from fpdf import FPDF

# PDF dimensions on A4
pdf_w = 210
pdf_h = 297


class PDF(FPDF):


    # Method for drawing a line on the pdf
    def lines(self):
        self.set_line_width(0.0)
        self.line(0, pdf_h / 2, 210, pdf_h / 2)

    # Method to add images to the pdf
    def imagex(self, image, afterTitle=False):
        if afterTitle:
            self.set_xy(self.get_x(), self.get_y() + 14)
        else:
            self.set_xy(self.get_x(), self.get_y() + 5)
        self.image(image, link='', type='', w=170.0, h=95.5)

    # Method to set titles
    def titles(self, title):
        self.set_xy(self.get_x(), self.get_y() + 5)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(220, 50, 50)
        self.cell(w=210.0, h=20.0, align='C', txt=title, border=0)

    # Method to set text
    def text(self, text, afterTitle=False, color='Black'):
        if afterTitle:
            self.set_y(self.get_y() + 14)
        self.set_font('Arial', '', 12)
        if color == 'Black':
            self.set_text_color(0, 0, 0)
        elif color == 'White':
            self.set_text_color(250,250,250)
        self.write(10, text)


def pdf_starter():
    pdf = PDF()
    pdf.add_page()
    return pdf



'''
pdf.titles()
pdf.text('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec dapibus mi auctor egestas aliquet. Aliquam erat volutpat. Donec luctus, arcu posuere commodo iaculis, tortor dui rhoncus velit, at ultricies augue dolor vitae risus. Curabitur pellentesque, quam fermentum luctus pulvinar, nisl massa vestibulum libero, id lacinia elit urna nec purus. Proin ut dignissim nunc. Duis vitae eleifend diam. Quisque vel mi nec orci lacinia accumsan at sed justo. Pellentesque ac ligula sed quam pretium mattis. Cras a euismod purus, et ultricies nunc. Nunc sit amet dolor neque. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia curae; Nunc consectetur facilisis est a pretium. Donec nec finibus ligula. Curabitur eu neque vitae velit tempus tempor sed ac sapien. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. ')
pdf.text('\ncacatua 27')
pdf.set_author('Marc Jou')
pdf.output('test.pdf', 'F')
'''