import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
import seasampler as samp

#object = samp.SeaSampler('../src/input_files/SeaSampler', 'control depth', 'control_depth_V2')
#object = samp.SeaSampler('../src/input_files/SeaSampler', 'metadata', 'metadata_seasampler_V3')
object = samp.SeaSampler('../src/input_files/SeaSampler Tossa', 'plots', 'plots')
object.plot_depthvstemp('probatemp')