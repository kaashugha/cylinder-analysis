from datetime import datetime
from fpdf import FPDF
from create_table import PDF

def create_pdf(data_as_dict, batch_data):
    pdf = PDF('P', 'mm', 'Letter')
    pdf.alias_nb_pages()

    pdf.set_font('helvetica', '', 10)
    pdf.add_page()
    today = str(datetime.today())[:-16]
    pdf.cell(0, 6, 'Date: ' + today, border=0, ln=1) # ADD TODAYS DATE STAMP
    pdf.cell(0, 6, 'Specified Strength (MPa): ' + batch_data['spec_str'], border=0, ln=1)
    pdf.cell(0, 6, 'Batch Number: ' + batch_data['_batch_id'], border=0, ln=1)
    pdf.cell(0, 6, 'Client: ' + batch_data['client_name'], border=0, ln=1)
    pdf.cell(0, 6, 'Site Address: ' + batch_data['site_add'], border=0, ln=1)
    pdf.cell(0, 6, 'Subclient/Contractor: ' + batch_data['subclient_cont'], border=0, ln=1)

    pdf.image('tof.png', 145, 47, 60)

    pdf.ln(5)
    pdf.create_table(table_data = data_as_dict, align_header='C', align_data='C', data_size=8, cell_width=[27,20,20,15,9,20,18,18,15,19,14], title_size=40)
    pdf.ln(5)

    # 97.95 - 62.5 = 35.45

    notes = 'This is an example paragraph for the max number of words I can use in the notes section of the final report. I am at 108 characters as of the end of the last sentence but I need 200. Twenty letters now'

    pdf.cell(50, 7, 'Mix ID: ', border=0)
    pdf.cell(47.95, 7, batch_data['mix_id'], border=0)
    pdf.cell(62.5, 7, 'Concrete Supplier: ', border=0)
    pdf.cell(35.45, 7, batch_data['conc_supp'], border=0, ln=1)

    pdf.cell(50, 7, 'Ticket ID: ', border=0)
    pdf.cell(47.95, 7, batch_data['ticket_no'], border=0)
    pdf.cell(62.5, 7, 'Specified Air (%): ', border=0)
    pdf.cell(35.45, 7, batch_data['spec_air'], border=0, ln=1)

    pdf.cell(50, 7, 'Specified Slump (mm): ', border=0)
    pdf.cell(47.95, 7, batch_data['spec_slump'], border=0)
    pdf.cell(62.5, 7, 'Measured Air (%): ', border=0)
    pdf.cell(35.45, 7, batch_data['meas_air'], border=0, ln=1)

    pdf.cell(50, 7, 'Measured Slump (mm): ', border=0)
    pdf.cell(47.95, 7, str(batch_data['meas_slump']), border=0)
    pdf.cell(62.5, 7, 'Truck No.: ', border=0)
    pdf.cell(35.45, 7, str(batch_data['truck_no']), border=0, ln=1)

    pdf.cell(50, 7, 'Load No.: ', border=0)
    pdf.cell(47.95, 7, str(batch_data['load_no']), border=0)
    pdf.cell(62.5, 7, 'Type of Mould: ', border=0)
    pdf.cell(35.45, 7, batch_data['mould_type'], border=0, ln=1)

    pdf.cell(50, 7, 'Concrete Temperature (°C): ', border=0)
    pdf.cell(47.95, 7, str(batch_data['conc_temp']), border=0)
    pdf.cell(62.5, 7, 'Casting Time (24 hr): ', border=0)
    pdf.cell(35.45, 7, str(batch_data['cast_time']), border=0, ln=1)

    pdf.cell(50, 7, 'Ambient Temperature (°C): ', border=0)
    pdf.cell(47.95, 7, str(batch_data['amb_temp']), border=0)
    pdf.cell(62.5, 7, 'Time of Charge (24 hr): ', border=0)
    pdf.cell(35.45, 7, str(batch_data['charge_time']), border=0, ln=1)

    pdf.cell(50, 7, 'Casted By: ', border=0)
    pdf.cell(47.95, 7, batch_data['cast_by'], border=0)
    pdf.cell(62.5, 7, 'Nominal Size of Aggregate (mm): ', border=0)
    pdf.cell(35.45, 7, str(batch_data['agg_size']), border=0, ln=1)

    pdf.cell(50, 7, 'Location: ', border=0)
    pdf.cell(47.95, 7, batch_data['struct_grid'], border=0)
    pdf.cell(62.5, 7, 'Initial Curing Temperature (Minimum °C): ', border=0)
    pdf.cell(35.45, 7, str(batch_data['temp_min']), border=0, ln=1)

    pdf.cell(50, 7, 'PLT #: ', border=0)
    pdf.cell(47.95, 7, batch_data['plt'], border=0)
    pdf.cell(62.5, 7, 'Initial Curing Temperature (Maximum °C): ', border=0)
    pdf.cell(35.45, 7, str(batch_data['temp_max']), border=0, ln=1)

    pdf.cell(50, 7, 'Cylinders Cast at PLT: ', border=0)
    pdf.cell(47.95, 7, batch_data['cast_plt'], border=0, ln=1)

    pdf.ln(5)

    pdf.cell(15, 7, 'Signature: ', border=0)

    pdf.ln(2)

    pdf.cell(17, 7, '', border=0)
    pdf.set_font('helvetica', 'U', 10)
    sig_x = pdf.get_x()
    sig_y = pdf.get_y()

    pdf.image('signature.png', sig_x + 6, sig_y - 5, 18)
    pdf.cell(15, 7, '                                ', ln=1)
    pdf.set_font('helvetica', '', 9)
    pdf.cell(19, 4, '', border=0)
    pdf.cell(15, 4, 'Fawad Khan', ln=1)
    pdf.cell(19, 4, '', border=0)
    pdf.cell(15, 4, 'Lab Manager')

    pdf.output(batch_data['_batch_id'] + '.pdf')