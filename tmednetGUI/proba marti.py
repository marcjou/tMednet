import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import seasampler as samp

#object = samp.SeaSampler('../src/input_files/Boreas', 'control depth', 'control_depth_Boreas')
#object = samp.SeaSampler('../src/input_files/SeaSampler', 'metadata', 'metadata_seasampler_V4')
object = samp.SeaSampler('../src/input_files/SeaSampler Tossa', 'plots', 'plots')
object.add_data_list('../src/input_files/SeaSampler Boreas')
object.add_data_list('../src/input_files/SeaSampler Medes')
object.add_data_list('../src/input_files/SeaSampler Ullastres')
object.radar_plot()