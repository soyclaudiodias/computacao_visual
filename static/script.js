const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('fileInput');
const resultDiv = document.getElementById('result');

// Clique na área = abre seletor
dropZone.addEventListener('click', () => fileInput.click());

// Efeito visual ao arrastar
dropZone.addEventListener('dragover', e => {
  e.preventDefault();
  dropZone.classList.add('hover');
});
dropZone.addEventListener('dragleave', () => dropZone.classList.remove('hover'));

// Soltou arquivo na área
dropZone.addEventListener('drop', e => {
  e.preventDefault();
  dropZone.classList.remove('hover');
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    hideUploadArea();
    uploadFile(files[0]);
  }
});

// Selecionou via diálogo
fileInput.addEventListener('change', e => {
  const file = e.target.files[0];
  if (file) {
    hideUploadArea();
    uploadFile(file);
  }
  fileInput.value = ''; // permite escolher o mesmo arquivo de novo depois
});

function hideUploadArea() { dropZone.classList.add('hidden'); }
function showUploadArea() { dropZone.classList.remove('hidden'); }

function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  fetch('/upload', { method: 'POST', body: formData })
    .then(res => {
      if (!res.ok) throw new Error('Falha no upload');
      return res.json();
    })
    .then(data => {
      if (data.error) {
        alert('Erro: ' + data.error);
        showUploadArea();
      } else {
        // Mostra a imagem enviada
        resultDiv.innerHTML = `
          <h3>Imagem enviada:</h3>
          <div class="image-container">
            <img id="originalImage" src="/uploads/${data.original}" alt="Imagem Original" />
            <img id="bilateralImage" class="hidden" alt="Imagem Filtrada" />
          </div>
          <br>
          <button id="toggleBtn">Aplicar Filtro Bilateral</button>
        `;

        // evento do botão
        const btn = document.getElementById('toggleBtn');
        const imgOrig = document.getElementById('originalImage');
        const imgBilat = document.getElementById('bilateralImage');
        let originalSrc = imgOrig.src;
        let bilateralSrc = null;
        let showingBilateral = false;

        // botão que alterna entre imagem original e filtrada
        btn.addEventListener('click', async () => {
          // Envia e salva a imagem
          if (!bilateralSrc) {
            const form = new FormData();
            const res = await fetch(originalSrc);
            const blob = await res.blob();
            form.append('image', blob, 'imagem.png');
            form.append('d', 25);
            form.append('sigmaColor', 250);
            form.append('sigmaSpace', 250);
            // envia a imagem para aplicar o filtro bilateral
            const response = await fetch('/api/denoise/bilateral', {
              method: 'POST',
              body: form
            });
            const json = await response.json();
            bilateralSrc = json.output;
            imgBilat.src = bilateralSrc;
          }

          // Alterna visual entre original e bilateral
          showingBilateral = !showingBilateral;

          if (showingBilateral) {
            imgBilat.classList.remove('hidden');
            imgOrig.classList.add('move-left');
            btn.textContent = 'Mostrar Original';
          } else {
            imgBilat.classList.add('hidden');
            imgOrig.classList.remove('move-left');
            btn.textContent = 'Aplicar Filtro Bilateral';
          }
        });
      }
    })
    .catch(err => {
      console.error(err);
      alert('Erro no upload');
      showUploadArea();
    });
}
