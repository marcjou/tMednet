import write_tmednet_log as wtl

lg = wtl.LogWriter()
lg.modify_log('01', ['Esta prueba es nueva sip', 'Mirame soy una segunda prueba'])
lg.insert_data('02', ['De los creadores', 'De un idiota en el insti', 'Llega', 'Un idiota en la uni'])
lg.difference_and_filter('../src/input_files/Database_T_06_Medes_200207-202210.txt')
lg.write_file()
print(lg.get_path())