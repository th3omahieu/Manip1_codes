# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 10:53:38 2026

@author: Théo MAHIEU
"""

import PySpin
import matplotlib.pyplot as plt
import numpy as np
import sys

def live_view(cam, tempsexp, DXmax=1280, DYmax=1024, Xinmax=0, Yinmax=0):
    """
    Flux live permanent. 
    L'utilisateur DOIT fermer la fenêtre pour sortir.
    La fermeture INTERROMPT tout le script (sys.exit).
    """
    # 1. Configuration (Exposition et ROI)
    if cam.ExposureAuto.GetAccessMode() == PySpin.RW:
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
    cam.ExposureTime.SetValue(tempsexp * 1000)
    if cam.IsStreaming():
        cam.EndAcquisition()
    
    cam.OffsetX.SetValue(0); cam.OffsetY.SetValue(0)
    cam.Width.SetValue(int(DXmax)); cam.Height.SetValue(int(DYmax))
    cam.OffsetX.SetValue(int(Xinmax)); cam.OffsetY.SetValue(int(Yinmax))

    # 2. Setup fenêtrage
    plt.ion()
    fig, ax = plt.subplots()
    fig.canvas.manager.set_window_title('LIVE - FERMER POUR INTERROMPRE LE SCRIPT')
    display_handle = None

    cam.BeginAcquisition()
    print(">>> LIVE en cours... Fermez la fenêtre pour ARRETER le processus.")

    try:
        # Boucle infinie tant que la fenêtre existe
        while plt.fignum_exists(fig.number):
            image_result = cam.GetNextImage(1000)
            
            if not image_result.IsIncomplete():
                data = image_result.GetNDArray()
                
                if display_handle is None:
                    display_handle = ax.imshow(data, cmap='turbo')
                    plt.show()
                else:
                    display_handle.set_data(data)
                    display_handle.set_clim(np.min(data), np.max(data))
                
                fig.canvas.draw_idle()
                fig.canvas.flush_events()
            
            image_result.Release()
            plt.pause(0.01)

    except Exception as e:
        print(f"Erreur : {e}")
    finally:
        # 3. Sortie de boucle : La fenêtre a été fermée
        print("\n[!] Fenêtre fermée. Interruption volontaire du script.")
        if cam.IsStreaming():
            cam.EndAcquisition()
        
        # Action radicale : on stoppe tout
        plt.close('all')
        sys.exit("Script stoppé par l'utilisateur.") 

    # Note : Le 'return' ne sera jamais atteint à cause du sys.exit
    return tempsexp