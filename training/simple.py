import re
import os
import sys
import argparse

import numpy as np
from scipy import misc

from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Activation, Dense
from keras.optimizers import SGD

from sklearn.cross_validation import train_test_split

from common import (command_mapping,
                    command_rev_mapping,
                    load_mapping,
                    command_readable_mapping)

import os, json
from glob import glob
import numpy as np
from scipy import misc, ndimage
from scipy.ndimage.interpolation import zoom

from keras import backend as K
from keras.models import Sequential
from keras.layers.core import Flatten, Dense, Dropout, Lambda, Merge
from keras.optimizers import Adam
from keras.preprocessing.image import ImageDataGenerator

