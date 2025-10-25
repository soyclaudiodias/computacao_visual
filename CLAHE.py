import cv2
import numpy as np

# Aplica CLAHE apenas no canal de luminância (L) no espaço LAB.
# Retorna uma imagem BGR melhorada em contraste.
def apply_clahe_bgr(img_bgr, clip_limit=2.0, tile_grid_size=(8, 8)):
    
    # Garantir que recebemos uma imagem válida tipo uint8
    if img_bgr is None or img_bgr.size == 0:
        raise ValueError("Imagem inválida ou vazia no apply_clahe_bgr")

    # Converte BGR -> LAB
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)

    # Cria o objeto CLAHE
    clahe = cv2.createCLAHE(clipLimit=float(clip_limit),
                            tileGridSize=tuple(tile_grid_size))

    # Aplica CLAHE só no canal L (luminância)
    L_eq = clahe.apply(L)

    # Junta canais de volta e retorna em BGR
    lab_eq = cv2.merge([L_eq, A, B])
    img_bgr_eq = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)

    return img_bgr_eq

# Versão para imagem já em escala de cinza

def apply_clahe_gray(img_gray, clip_limit=2.0, tile_grid_size=(8, 8)):
    
    if img_gray is None or img_gray.size == 0:
        raise ValueError("Imagem inválida ou vazia no apply_clahe_gray")

    if len(img_gray.shape) != 2:
        raise ValueError("apply_clahe_gray recebeu imagem não-grayscale")

    clahe = cv2.createCLAHE(clipLimit=float(clip_limit),
                            tileGridSize=tuple(tile_grid_size))

    eq = clahe.apply(img_gray)
    return eq
