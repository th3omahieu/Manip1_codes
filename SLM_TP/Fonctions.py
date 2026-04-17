# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 09:56:36 2026

@author: Théo MAHIEU
"""

import numpy as np

# def calculCentreContour(cx, dx, cy, dy, h, m):
#     """
#     Insère un motif H dans une matrice M à une position donnée, 
#     avec un redimensionnement par blocs (Kronecker).
#     """
#     # Récupération des dimensions du motif H
#     n, n2 = h.shape

#     # Si le motif n'a pas la taille du ROI, on le redimensionne par blocs
#     if n2 != dx or n != dy:
#         # On s'assure que dx et dy sont des multiples de n et n2
#         dx = dx - (dx % n2)
#         dy = dy - (dy % n)
        
#         px = dx // n2
#         py = dy // n
        
#         # Équivalent de kron(H, ones(Py, Px))
#         h = np.kron(h, np.ones((py, px)))

#     # Calcul des indices (on s'assure d'avoir des entiers pour le slicing)
#     # Note : En Python, les indices de fin sont exclus, donc le -1 du Matlab disparaît
#     y_start = int(cy - dy / 2)
#     y_end = int(cy + dy / 2)
#     x_start = int(cx - dx / 2)
#     x_end = int(cx + dx / 2)

#     # Insertion du motif H dans la matrice M
#     # On fait une copie pour ne pas modifier la matrice M d'origine (optionnel)
#     m_out = m.copy()
#     m_out[y_start:y_end, x_start:x_end] = h

#     return m_out

def corr2(A, B):
    """
    Coefficient de corrélation 2D (équivalent exact de MATLAB).
    A et B doivent avoir la même taille.
    """
    # Conversion en flottant pour éviter les erreurs d'arrondi/overflow
    A = np.asanyarray(A).astype(float)
    B = np.asanyarray(B).astype(float)

    # Vérification de la taille (comme narginchk et validateattributes)
    if A.shape != B.shape:
        raise ValueError("Les matrices A et B doivent avoir la même taille.")

    # Soustraction de la moyenne (mean2)
    a_shifted = A - np.mean(A)
    b_shifted = B - np.mean(B)

    # Calcul du coefficient R
    num = np.sum(a_shifted * b_shifted)
    den = np.sqrt(np.sum(a_shifted**2) * np.sum(b_shifted**2))

    # Gestion du cas où le dénominateur est nul (images uniformes)
    if den == 0:
        return 0.0

    return num / den

def calculCentreContour(Cx, Dx, Cy, Dy, H, M):
    N, N2 = H.shape
    
    Px = Dx // N2
    Py = Dy // N
    
    H_ext = np.kron(H, np.ones((Py, Px)))
    
    new_Dy, new_Dx = H_ext.shape
    
    y_start = int(Cy - new_Dy // 2)
    y_end   = y_start + new_Dy
    x_start = int(Cx - new_Dx // 2)
    x_end   = x_start + new_Dx

    M[y_start:y_end, x_start:x_end] = H_ext.astype(np.uint8)

    return M

def PixelSLM_pixversrad_Holoeyenir80(xphi, x2pi_val, a1, a2):
    xphi = np.array(xphi) % x2pi_val
    px1, py1 = 0, 0
    px2, py2 = x2pi_val, 2 * np.pi
    
    pente = (py2 - py1) / (px2 - px1)
    intercept = py1 - pente * px1
    
    phi = (xphi - px1) * (xphi - px2) * (a1 * xphi + a2) + (pente * xphi + intercept)
    return phi 

def PixelSLM_radverspix_Holoeyenir80(phi, x2pi_val, b1, b2):
    two_pi = 2 * np.pi
    phi = np.array(phi) % two_pi
    
    px1_inv, py1_inv = 0, 0
    px2_inv, py2_inv = two_pi, x2pi_val
    
    pente_inv = (py2_inv - py1_inv) / (px2_inv - px1_inv)
    intercept_inv = py1_inv - pente_inv * px1_inv
    
    pix = (phi - px1_inv) * (phi - px2_inv) * (b1 * phi + b2) + (pente_inv * phi + intercept_inv)
    
    return np.clip(pix, 0, 255)