# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 15:33:45 2026

@author: Théo MAHIEU
"""

import PySpin

def capture(cam, tempsexp, DXmax=1280, DYmax=1024, Xinmax=0, Yinmax=0):
    """
    Prend une image unique (Snapshot).
    Equivalent de flir_image.m
    """
    # 1. Configuration de l'exposition (ms -> µs)
    if cam.ExposureAuto.GetAccessMode() == PySpin.RW:
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)

    cam.ExposureTime.SetValue(tempsexp * 1000)
    if cam.IspEnable.GetAccessMode() == PySpin.RW:
        cam.IspEnable.SetValue(False)

    # 2. Configuration du ROI (Region of Interest)
    # Note: En PySpin, il faut parfois désactiver l'auto-centrage pour changer le ROI
    if cam.Width.GetAccessMode() == PySpin.RW:
        if hasattr(cam, 'OffsetAutoCenter') and cam.OffsetAutoCenter.GetAccessMode() == PySpin.RW:
            cam.OffsetAutoCenter.SetValue(False)
        cam.OffsetX.SetValue(0)
        cam.OffsetY.SetValue(0)
        cam.Width.SetValue(DXmax)
        cam.Height.SetValue(DYmax)
        cam.OffsetX.SetValue(Xinmax)
        cam.OffsetY.SetValue(Yinmax)
        
    s_node_map = cam.GetTLStreamNodeMap()
    handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode("StreamBufferHandlingMode"))
    if PySpin.IsAvailable(handling_mode) and PySpin.IsWritable(handling_mode):
        handling_mode.SetIntValue(handling_mode.GetEntryByName("NewestOnly").GetValue())

    # 3. Capture unique
    cam.BeginAcquisition()
    
    data = None
    try:
        # On récupère une seule frame
        image_result = cam.GetNextImage(1000)
        
        if not image_result.IsIncomplete():
            # On extrait le tableau NumPy
            data = image_result.GetNDArray().copy() # .copy() pour garder les données en mémoire
            # converted_image = image_result.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
            # data = converted_image.GetNDArray().copy()
        image_result.Release()
        
    except Exception as e:
        print(f"Erreur lors de la capture : {e}")
        
    finally:
        cam.EndAcquisition()
        
    return data