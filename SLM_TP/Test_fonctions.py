# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 09:38:21 2026

@author: Théo MAHIEU
"""

#%% Imports

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat  # Pour charger les fichiers .mat
import sys
import PySpin
import flir_tools
import flir_video
import flir_image
import SLMcontrol
import Fonctions
import time
from scipy.ndimage import zoom
import threading
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDesktopWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal

#%% Camera initilization
sys, clist, cam = flir_tools.connect_cam()
DXmax = 1280;     # Maximum width of the frame (pixels)
DYmax = 1024;     # Maximum height of the frame (pixels)
Xinmax = 0;       # Horizontal offset (starting X-coordinate)
Yinmax = 0;       # Vertical offset (starting Y-coordinate)

#%% Test FLIR camera

tempsexp = 23
flir_video.live_view(cam, tempsexp)

#%% Take image

image = flir_image.capture(cam, tempsexp) 

plt.figure()  
plt.imshow(image, cmap='turbo')
plt.colorbar()
plt.title('Image')
plt.show()

#%% Camera ROI

# Caution: Dx, Dy must be multiple of 16; Xinf Yinff of 8

data = flir_image.capture(cam, tempsexp, DXmax, DYmax, Xinmax, Yinmax)

if data is not None:
    h = plt.figure()
    plt.imshow(data, cmap='turbo')
    plt.title("Click on ROI center")
    pts = plt.ginput(1) 
    plt.close(h)
    
    if pts:
        xcenter, ycenter = pts[0]
        DXff, DYff = 624, 624
        Xinff = int(np.floor(xcenter) - np.floor(DXff / 2))
        Yinff = int(np.floor(ycenter) - np.floor(DYff / 2))
        Xinff = max(0, min(Xinff, DXmax - DXff))
        Yinff = max(0, min(Yinff, DYmax - DYff))
        Xinff = 8 * (Xinff // 8)
        Yinff = 8 * (Yinff // 8)
        tempsexp = flir_video.live_view(cam, tempsexp, DXff, DYff, Xinff, Yinff)
        
#%% SLM initialization

controller = SLMcontrol.init_slm_display()
slm_width = controller.slm_window.width()
slm_height = controller.slm_window.height()

A0 = np.zeros((slm_height, slm_width), dtype=np.uint8)

#%% SLM tets

width = 5  
h = controller.slm_window.height()
w = controller.slm_window.width()

x = np.arange(w)
y = np.arange(h)
pattern = ((x // width) % 2 == 0) * 255
patterny = ((y // width) % 2 == 0) * 255

M = (patterny[:, None] ^ pattern[None, :]).astype(np.uint8)

SLMcontrol.update_slm_image(M)

#%% SLM ROI

controller = SLMcontrol.init_slm_display()

Cxslm = 300
Dxslm = 500
Cyslm = 400
Dyslm = 500

Nrand = 50
SLMrand = np.floor(np.random.rand(Nrand, Nrand) + 0.5).astype(np.uint8)

SLMrand = Fonctions.calculCentreContour(Cxslm, Dxslm, Cyslm, Dyslm, SLMrand, A0)
SLMrand = (SLMrand.astype(np.uint16) * 100) 
SLMrand = np.clip(SLMrand, 0, 255).astype(np.uint8) 

SLMcontrol.update_slm_image(SLMrand)
time.sleep(0.2)

#%%----------------------------------------------------------------------------------

# 1. SLM Calibration

#------------------------------------------------------------------------------------
#%% SLM calibration

controller = SLMcontrol.init_slm_display()
reference_data = flir_image.capture(cam, tempsexp)
time.sleep(0.2)

#%%
reference = flir_image.capture(cam, tempsexp)

#%%

data = flir_image.capture(cam, tempsexp)

#%%
print(Fonctions.corr2(data, reference))

#%%

h = controller.slm_window.height()
w = controller.slm_window.width()

# 1. Générer une matrice de nombres aléatoires entre 0 et 1
random_matrix = np.random.rand(h, w)

#%%
# 2. Créer un masque binaire : True si > 0.5 (environ 50% des pixels)
# On multiplie par 255 pour le niveau de gris du SLM
M = (random_matrix > 0.5).astype(np.uint8) * 255

# 3. Envoi au SLM
SLMcontrol.update_slm_image(M)

#%%

h, w = 20, 30
random_matrix = np.random.rand(h, w)
M0 = (random_matrix > 0.5).astype(np.uint8)

#%% 
M = Fonctions.calculCentreContour(960, 1900, 540, 1060, M0, A0)*230
SLMcontrol.update_slm_image(M)


#%% SLM Calibration

controller = SLMcontrol.init_slm_display()
reference_data = flir_image.capture(cam, tempsexp)

#%%

vec = np.arange(0,255,10)

h,w = 20, 20
random_matrix = np.random.rand(h,w)
M0 = (random_matrix > 0.5).astype(np.uint8)
M_display = A0.copy()
M = Fonctions.calculCentreContour(960, 1900, 540, 1060, M0, M_display)
C = []

#%%
C = []

for k in range(len(vec)):
    M1 = M*vec[k]
    SLMcontrol.update_slm_image(M1)
    QApplication.processEvents()
    time.sleep(0.2)
    data = flir_image.capture(cam, tempsexp)
    C.append(Fonctions.corr2(data, reference_data))
    
plt.figure()
plt.plot(vec, C, 'r+') # 'r+-' : rouge, points en croix, reliés
plt.xlabel('Valeur vec[k]')
plt.ylabel('Corrélation')
plt.title('Corrélation')
plt.grid(True)
plt.show()






