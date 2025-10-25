from flask import Flask, render_template, request, jsonify, send_from_directory
from datetime import datetime
import cv2
import os
import numpy as np
import io

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")

# Aplica filtro bilateral pra remover ruído e converte para cinza se a imagem for colorida
def denoise_bilateral(img_bgr, d=25, sigma_color=250, sigma_space=250, force_gray=True):
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
    out = denoise_bilateral(img, d, sigma_color, sigma_space)
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
