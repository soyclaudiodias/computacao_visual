from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import cv2
import os
import numpy as np

app = Flask(__name__)

# pasta de upload
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ----- FUNÇÕES DE PROCESSAMENTO -----

def denoise_bilateral(img_bgr, d=25, sigma_color=250, sigma_space=250, force_gray=False):
    """
    Aplica filtro bilateral.
    Se force_gray=True e a imagem for colorida, converte pra gray antes.
    """
    if force_gray and img_bgr.ndim == 3:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.bilateralFilter(img_bgr, d, sigma_color, sigma_space)

def apply_clahe_bgr(img_bgr, clip_limit=2.0, tile_grid_size=(8, 8)):
    """
    Aplica CLAHE no canal de luminância (L) em LAB e devolve imagem BGR melhorada.
    """
    if img_bgr is None or img_bgr.size == 0:
        raise ValueError("Imagem inválida ou vazia no apply_clahe_bgr")

    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    L, A, B = cv2.split(lab)

    clahe = cv2.createCLAHE(
        clipLimit=float(clip_limit),
        tileGridSize=tuple(tile_grid_size)
    )

    L_eq = clahe.apply(L)

    lab_eq = cv2.merge([L_eq, A, B])
    img_bgr_eq = cv2.cvtColor(lab_eq, cv2.COLOR_LAB2BGR)

    return img_bgr_eq

# ----- ROTAS BÁSICAS -----

@app.route('/')
def index():
    # carrega templates/index.html
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # recebe a imagem inicial do usuário e salva
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Arquivo vazio'}), 400

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # devolve só o nome da imagem salva pro front usar depois
    return jsonify({'original': file.filename})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # serve qualquer arquivo salvo em uploads/
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# ----- ROTA DENOISE BILATERAL -----

@app.post("/api/denoise/bilateral")
def api_denoise_bilateral():
    """
    Espera multipart/form-data com:
      - image (arquivo)
      - d, sigmaColor, sigmaSpace (opcionais)
    """
    file = request.files.get("image")
    if not file:
        return jsonify(error="Nenhuma imagem enviada (campo 'image')"), 400

    d = int(request.form.get("d", 9))
    sigma_color = float(request.form.get("sigmaColor", 75))
    sigma_space = float(request.form.get("sigmaSpace", 75))

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(file.filename or "img")
    ext = (ext.lower() or ".png") if ext else ".png"

    in_path  = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}{ext}")
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}_bilateral{ext}")

    # salva original
    file.save(in_path)

    img = cv2.imread(in_path, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify(error="Falha ao ler a imagem enviada"), 400

    # aplica filtro bilateral
    out = denoise_bilateral(img, d, sigma_color, sigma_space, force_gray=False)

    # salva resultado
    cv2.imwrite(out_path, out)

    return jsonify(
        message="ok",
        type="bilateral",
        params=dict(d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space),
        input=f"/uploads/{os.path.basename(in_path)}",
        output=f"/uploads/{os.path.basename(out_path)}"
    )

# ----- ROTA CLAHE -----

@app.post("/api/clahe")
def api_clahe():
    """
    Espera multipart/form-data com:
      - image (arquivo)
      - clipLimit (opcional)
      - tileGridSize (opcional no formato "8,8")
    """
    file = request.files.get("image")
    if not file:
        return jsonify(error="Nenhuma imagem enviada (campo 'image')"), 400

    clip_limit = float(request.form.get("clipLimit", 2.0))
    tile_raw = request.form.get("tileGridSize", "8,8")

    try:
        tx, ty = tile_raw.split(",")
        tile_grid_size = (int(tx), int(ty))
    except Exception:
        tile_grid_size = (8, 8)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(file.filename or "img")
    ext = (ext.lower() or ".png") if ext else ".png"

    in_path  = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}{ext}")
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}_clahe{ext}")

    # salva original
    file.save(in_path)

    # lê imagem
    img = cv2.imread(in_path, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify(error="Falha ao ler a imagem enviada"), 400

    # aplica CLAHE
    try:
        out = apply_clahe_bgr(
            img,
            clip_limit=clip_limit,
            tile_grid_size=tile_grid_size
        )
    except Exception as e:
        return jsonify(error=f"Erro ao aplicar CLAHE: {str(e)}"), 500

    # salva resultado
    cv2.imwrite(out_path, out)

    return jsonify(
        message="ok",
        type="clahe",
        params=dict(
            clipLimit=clip_limit,
            tileGridSize=list(tile_grid_size)
        ),
        input=f"/uploads/{os.path.basename(in_path)}",
        output=f"/uploads/{os.path.basename(out_path)}"
    )

# ----- MAIN -----

if __name__ == '__main__':
    app.run(debug=True)