# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 10:49:00 2026

@author: Théo MAHIEU
"""

import PySpin

def connect_cam():
    """Initialise la caméra et la renvoie. À faire UNE SEULE FOIS."""
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    if cam_list.GetSize() == 0:
        cam_list.Clear()
        system.ReleaseInstance()
        return None, None, None
    cam = cam_list[0]
    cam.Init()
    return system, cam_list, cam

def disconnect_cam(system, cam_list, cam):
    """Libère la caméra proprement."""
    if cam:
        if cam.IsStreaming():
            cam.EndAcquisition()
        cam.DeInit()
        del cam
    if cam_list:
        cam_list.Clear()
    if system:
        system.ReleaseInstance()