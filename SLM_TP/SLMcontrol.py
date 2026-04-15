# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 16:14:18 2026

@author: Théo MAHIEU
"""

import threading
import time
import numpy as np
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QDesktopWidget, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal
#from SLM_radtopix import pixel_slm_radverspix_holoeyenir015_manip4

class SLMController(QObject):
    """Contrôleur central pour gérer l'affichage SLM"""
    update_signal = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.app = QApplication(sys.argv)
        self.slm_window = SLMWindow(screen_index=1, is_control_window=False)
        self.control_window = SLMWindow(screen_index=0, is_control_window=True)
        self.update_signal.connect(self.update_display)
        
    def update_display(self, image_data):
        """Mettre à jour l'affichage avec de nouvelles données"""
        self.slm_window.update_display(image_data)
        self.control_window.update_display(image_data)
        
    def show(self):
        """Afficher les fenêtres"""
        self.slm_window.show()
        self.control_window.show()
        
    def run(self):
        """Démarrer l'application"""
        self.show()
        self.app.exec_()

class SLMWindow(QMainWindow):
    def __init__(self, screen_index=1, is_control_window=False):
        super().__init__()
        self.screen_index = screen_index
        self.is_control_window = is_control_window
        self.initUI()
        
    def initUI(self):
        screens = QDesktopWidget().screenCount()
        
        if self.screen_index < screens:
            screen_geometry = QDesktopWidget().screenGeometry(self.screen_index)
            
            if self.is_control_window:
                self.setGeometry(10, 600, 480, 270)
                self.setWindowTitle('SLM Control Panel')
            else:
                self.setGeometry(screen_geometry)
                self.setWindowTitle('SLM Display - Full Screen')
                self.showFullScreen()
                
            width, height = screen_geometry.width(), screen_geometry.height()
            self.image_data = np.zeros((height, width), dtype=np.uint8)
            
            self.label = QLabel(self)
            self.setCentralWidget(self.label)
            self.update_display()
            
    def update_display(self, image_data=None):
        if image_data is not None:
            self.image_data = image_data
            
        height, width = self.image_data.shape
        qimage = QImage(self.image_data.data, width, height, width, QImage.Format_Grayscale8)
        pixmap = QPixmap.fromImage(qimage)
        
        if self.is_control_window:
            pixmap = pixmap.scaled(480, 270, Qt.KeepAspectRatio)
            
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)

# Variable globale pour le contrôleur
slm_controller = None

def init_slm_display():
    """Initialiser l'affichage SLM dans le thread principal"""
    global slm_controller
    slm_controller = SLMController()
    slm_controller.show()
    return slm_controller

def update_slm_image(image_data):
    """Mettre à jour l'image SLM (thread-safe)"""
    if slm_controller:
        slm_controller.update_signal.emit(image_data)

def main(test_image2):
    # Initialiser l'affichage SLM
    controller = init_slm_display()
    
    # Démarrer l'application Qt dans un thread séparé
    qt_thread = threading.Thread(target=controller.run, daemon=True)
    qt_thread.start()
        
    # Mettre à jour l'affichage SLM
    update_slm_image(test_image2)