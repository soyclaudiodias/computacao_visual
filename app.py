from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import cv2
import os
import numpy as np
import io

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")

# Aplica filtro bilateral pra remover ruído e converte para cinza se a imagem for colorida
def denoise_bilateral(img_bgr, d=25, sigma_color=250, sigma_space=250, force_gray=False):
    if force_gray and img_bgr.ndim == 3:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.bilateralFilter(img_bgr, d, sigma_color, sigma_space)

# Onde os uploads vão ficar
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Renderiza o HTML principal (templates/index.html)
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # Validações básicas do upload
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Arquivo vazio'})
    
    # Salva o arquivo e devolve o nome pro front
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Retornar apenas o nome do arquivo, não o caminho absoluto
    return jsonify({'original': file.filename})

# Rota para servir os arquivos da pasta uploads
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# nova rota para aplicar filtragem bilateral via API
@app.post("/api/denoise/bilateral")
def api_denoise_bilateral():
    file = request.files.get("image")
    if not file:
        return jsonify(error="Nenhuma imagem enviada (campo 'image')"), 400

    d = int(request.form.get("d", 9))
    sigma_color = float(request.form.get("sigmaColor", 75))
    sigma_space = float(request.form.get("sigmaSpace", 75))

    # Criação de nomes únicos para os arquivos
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(file.filename or "img")
    ext = ext.lower() or ".png"
    in_path  = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}{ext}")
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}_bilateral{ext}")

     # Salva o arquivo enviado
    file.save(in_path)
    img = cv2.imread(in_path, cv2.IMREAD_COLOR)
    if img is None:
        return jsonify(error="Falha ao ler a imagem enviada"), 400

    # Aplica e salva o filtro bilateral
    out = denoise_bilateral(img, d, sigma_color, sigma_space, force_gray=False)
    cv2.imwrite(out_path, out)

    return jsonify(
        message="ok",
        params=dict(d=d, sigmaColor=sigma_color, sigmaSpace=sigma_space),
        input=f"/uploads/{os.path.basename(in_path)}",
        output=f"/uploads/{os.path.basename(out_path)}"
    )

# Executa a função principal
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import cv2
import os

from CLAHE import apply_clahe_bgr  # importa sua função CLAHE

app = Flask(__name__)

# define e garante a pasta de uploads UMA vez só
UPLOAD_FOLDER = os.path.join(app.root_path, "uploads")
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


def denoise_bilateral(img_bgr, d=25, sigma_color=250, sigma_space=250, force_gray=True):
    if force_gray and img_bgr.ndim == 3:
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    return cv2.bilateralFilter(img_bgr, d, sigma_color, sigma_space)


@app.route('/')
def index():
    # Renderiza o HTML principal (templates/index.html)
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_file():
    # Validações básicas do upload
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Arquivo vazio'})

    # Salva o arquivo original com o próprio nome enviado
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    # Retorna apenas o nome pro front
    return jsonify({'original': file.filename})


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Serve os arquivos salvos em uploads/
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.post("/api/denoise/bilateral")
def api_denoise_bilateral():
    """
    Espera multipart/form-data com:
      - image (arquivo)
      - d, sigmaColor, sigmaSpace (opcionais)
    Retorna JSON com URLs da imagem original e da filtrada.
    """
    file = request.files.get("image")
    if not file:
        return jsonify(error="Nenhuma imagem enviada (campo 'image')"), 400

    d = int(request.form.get("d", 9))
    sigma_color = float(request.form.get("sigmaColor", 75))
    sigma_space = float(request.form.get("sigmaSpace", 75))

    # nomes únicos pros arquivos de entrada/saída
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(file.filename or "img")
    ext = (ext.lower() or ".png") if ext else ".png"

    in_path  = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}{ext}")
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}_bilateral{ext}")

    # salva imagem original
    file.save(in_path)

    # lê imagem como BGR
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


@app.post("/api/clahe")
def api_clahe():
    """
    Espera multipart/form-data com:
      - image (arquivo)
      - clipLimit (opcional)
      - tileGridSize (opcional no formato "8,8")
    Retorna JSON com URLs da imagem original e da equalizada.
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

    # nomes únicos pros arquivos
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base, ext = os.path.splitext(file.filename or "img")
    ext = (ext.lower() or ".png") if ext else ".png"

    in_path  = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}{ext}")
    out_path = os.path.join(app.config["UPLOAD_FOLDER"], f"{base}_{ts}_clahe{ext}")

    # salva imagem original
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

    # salva saída
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


if __name__ == '__main__':
    app.run(debug=True)
