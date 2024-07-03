import individual_sensor as ins

sens = ins.SensorData("/home/marc/Projects/Mednet/tMednet/src/input_files/prueba_seascale.csv")
sens.plot_temperature_depth()