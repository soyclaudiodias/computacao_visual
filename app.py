from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
