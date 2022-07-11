import pprint
from fpdf import FPDF
from create_table import PDF

pdf = PDF('P', 'mm', 'Letter')
pdf.alias_nb_pages()


pdf.set_font('helvetica', '', 10)
pdf.add_page()
pdf.cell(0, 6, 'Date: ', border=0, ln=1)
pdf.cell(0, 6, 'Specified Strength (MPa): ', border=0, ln=1)
pdf.cell(0, 6, 'Batch Number: ', border=0, ln=1)
pdf.cell(0, 6, 'Client: ', border=0, ln=1)
pdf.cell(0, 6, 'Site Address: ', border=0, ln=1)
pdf.cell(0, 6, 'Subclient/Contractor: ', border=0, ln=1)

pdf.image('tof.png', 145, 47, 60)

data_as_dict = {"Lab No",
                "Casting Date",
                "Receiving Date",
                "Curing**",
                "Age",
                "Testing Date",
                "Diameter (mm)",
                "Mass of Cylinder (g)",
                "Density (kg/m3)",
                "Compressive Strength (MPa)",
                "Type of Fracture*"
}

data_as_dict = {k: [] for k in data_as_dict}




data_as_dict = {"Lab No": ["22-0600003A-7D-1","Mary","Carlson","Lucas", 'x', 'x'],
                "Casting Date": ["25-05-2022","Ramos","Banks","Cimon",  'x', 'x'],
                "Receiving Date": ['26-05-2022','19','31',              'x', 'x'],
                "Curing**": ['Moisture Room','19','31',                 'x', 'x'],
                "Age": ['52-D','19','31',                               'x', 'x'],
                "Testing Date": ['01-06-2022','19','31',                'x', 'x'],
                "Diameter (mm)": ['101.0','19','31',                    'x', 'x'],
                "Mass of Cylinder (g)": ['3710','19','31',              'x', 'x'],
                "Density (kg/m3)": ['2292','19','31',                   'x', 'x'],
                "Compressive Strength (MPa)": ['35.4','19','31',        'x', 'x'],
                "Type of Fracture*": ['2','19','31',                    'x', 'x']
            }

pdf.ln(5)
pdf.create_table(table_data = data_as_dict, align_header='C', align_data='C', data_size=8, cell_width=[27,20,20,15,9,20,18,18,15,19,14], title_size=40)
pdf.ln(5)

# 97.95 - 62.5 = 35.45

notes = 'This is an example paragraph for the max number of words I can use in the notes section of the final report. I am at 108 characters as of the end of the last sentence but I need 200. Twenty letters now'

pdf.cell(50, 7, 'Mix ID: ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Cylinders Cast at PLT: ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Ticket ID: ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Concrete Supplier: ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Specified Slump (mm): ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Specified Air (%): ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Measured Slump (mm): ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Measured Air (%): ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Load No.: ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Truck No.: ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Concrete Temperature (°C): ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Type of Mould: ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Ambient Temperature (°C): ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Casting Time: ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Initial Curing Temperature (°C): ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Time of Charge: ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Casted By: ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Nominal Size of Aggregate (mm): ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'Location: ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Initial Curing Temperature (Minimum °C): ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.cell(50, 7, 'PLT #: ', border=0)
pdf.cell(47.95, 7, 'ANS ', border=0)
pdf.cell(62.5, 7, 'Initial Curing Temperature (Maximum °C): ', border=0)
pdf.cell(35.45, 7, 'ANS ', border=0, ln=1)

pdf.ln(5)

pdf.cell(15, 7, 'Signature: ', border=0)

pdf.ln(2)

pdf.cell(17, 7, '', border=0)
pdf.set_font('helvetica', 'U', 10)
sig_x = pdf.get_x()
sig_y = pdf.get_y()

print(sig_x)
print(sig_y)

pdf.image('signature.png', sig_x + 6, sig_y - 5, 18)
pdf.cell(15, 7, '                                ', ln=1)
pdf.set_font('helvetica', '', 9)
pdf.cell(19, 4, '', border=0)
pdf.cell(15, 4, 'Fawad Khan', ln=1)
pdf.cell(19, 4, '', border=0)
pdf.cell(15, 4, 'Lab Manager')

pdf.output('pdf_1.pdf')