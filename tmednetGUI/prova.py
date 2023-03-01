import write_tmednet_log as wtl

lg = wtl.LogWriter(1, ['Esta prueba es nueva sip', 'Mirame soy una segunda prueba'])
lg.insert_data(2, ['De los creadores', 'De un idiota en el insti', 'Llega', 'Un idiota en la uni'])
lg.write_file()
print(lg.get_path())
print(lg.get_data()[1])