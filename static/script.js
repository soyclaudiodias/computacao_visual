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
          <img src="/uploads/${data.original}" alt="Imagem" />
        `;
      }
    })
    .catch(err => {
      console.error(err);
      alert('Erro no upload');
      showUploadArea();
    });
}