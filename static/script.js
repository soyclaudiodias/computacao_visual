const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("fileInput");
const resultDiv = document.getElementById("result");
const changeImageBtn = document.getElementById("changeImageBtn");

// abrir seletor ao clicar na área
dropZone.addEventListener("click", () => {
  fileInput.click();
});

// highlight ao arrastar
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("hover");
});
dropZone.addEventListener("dragleave", () => {
  dropZone.classList.remove("hover");
});

// soltou arquivo na área
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("hover");

  const files = e.dataTransfer.files;
  if (files.length > 0) {
    handleNewImage(files[0]);
  }
});

// escolheu arquivo no input
fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (file) {
    handleNewImage(file);
  }
  fileInput.value = ""; // permite reenviar o mesmo depois
});

// botão "Trocar imagem"
changeImageBtn.addEventListener("click", () => {
  fileInput.click();
});

// fluxo quando chega imagem nova
function handleNewImage(file) {
  hideUploadArea();
  uploadFile(file);
  changeImageBtn.classList.remove("hidden");
}

// esconde a caixa de upload inicial
function hideUploadArea() {
  dropZone.classList.add("hidden");
}

// se quiser reexibir o upload (não usamos agora)
function showUploadArea() {
  dropZone.classList.remove("hidden");
}

// manda a imagem pro backend (/upload) e depois monta a UI
function uploadFile(file) {
  const formData = new FormData();
  formData.append("file", file);

  fetch("/upload", { method: "POST", body: formData })
    .then((res) => {
      if (!res.ok) throw new Error("Falha no upload");
      return res.json();
    })
    .then((data) => {
      if (data.error) {
        alert("Erro: " + data.error);
        showUploadArea();
        return;
      }

      const originalUrl = `/uploads/${data.original}`;
      renderResultLayout(originalUrl);
    })
    .catch((err) => {
      console.error(err);
      alert("Erro no upload");
      showUploadArea();
    });
}

// monta a interface dos dois blocos (CLAHE e Bilateral)
// mantendo MESMA estrutura pros dois blocos pra alinhar perfeito
function renderResultLayout(originalUrl) {
  resultDiv.innerHTML = `
    <div class="panel">

      <!-- BLOCO CLAHE -->
      <div class="row-block">

        <button id="btnClahe" class="action-btn">Aplicar CLAHE</button>

        <div class="result-row">

          <!-- Coluna imagem ORIGINAL -->
          <div class="result-col image-col">
            <div class="img-label">IMAGEM ORIGINAL</div>
            <div class="image-frame">
              <img
                id="imgOriginalClahe"
                class="preview-img"
                src="${originalUrl}"
                alt="Imagem Original para CLAHE"
              />
            </div>
          </div>

          <!-- Coluna imagem PROCESSADA -->
          <div class="result-col image-col">
            <div class="img-label">CLAHE</div>
            <div class="image-frame">
              <img
                id="imgClaheResult"
                class="result-img"
                alt="Resultado CLAHE"
              />
            </div>
          </div>

          <!-- Coluna BOTÃO DOWNLOAD -->
          <div class="result-col download-col" id="claheDownloadCol">
            <a id="claheDownloadLink"
               class="download-link"
               download="clahe_result.png">
               Baixar imagem CLAHE
            </a>
          </div>

        </div>
      </div>

      <!-- BLOCO BILATERAL -->
      <div class="row-block">

        <button id="btnBilateral" class="action-btn">Aplicar Filtro Bilateral</button>

        <div class="result-row">

          <!-- Coluna imagem ORIGINAL -->
          <div class="result-col image-col">
            <div class="img-label">IMAGEM ORIGINAL</div>
            <div class="image-frame">
              <img
                id="imgOriginalBilateral"
                class="preview-img"
                src="${originalUrl}"
                alt="Imagem Original para Bilateral"
              />
            </div>
          </div>

          <!-- Coluna imagem PROCESSADA -->
          <div class="result-col image-col">
            <div class="img-label">FILTRO BILATERAL</div>
            <div class="image-frame">
              <img
                id="imgBilateralResult"
                class="result-img"
                alt="Resultado Bilateral"
              />
            </div>
          </div>

          <!-- Coluna BOTÃO DOWNLOAD -->
          <div class="result-col download-col" id="bilateralDownloadCol">
            <a id="bilateralDownloadLink"
               class="download-link"
               download="bilateral_result.png">
               Baixar imagem Bilateral
            </a>
          </div>

        </div>
      </div>

    </div>
  `;

  // pega elementos criados
  const btnClahe = document.getElementById("btnClahe");
  const imgClaheRes = document.getElementById("imgClaheResult");
  const claheDownloadCol = document.getElementById("claheDownloadCol");
  const claheDownloadLink = document.getElementById("claheDownloadLink");

  const btnBilateral = document.getElementById("btnBilateral");
  const imgBilRes = document.getElementById("imgBilateralResult");
  const bilateralDownloadCol = document.getElementById("bilateralDownloadCol");
  const bilateralDownloadLink = document.getElementById(
    "bilateralDownloadLink"
  );

  // botão de download começa invisível
  claheDownloadCol.classList.remove("visible");
  bilateralDownloadCol.classList.remove("visible");

  // helper pra processar imagem no backend e receber URL de saída
  async function processImage(endpoint, extraParams = {}) {
    const res = await fetch(originalUrl);
    const blob = await res.blob();

    const form = new FormData();
    form.append("image", blob, "imagem.png");

    for (const [key, value] of Object.entries(extraParams)) {
      form.append(key, value);
    }

    const response = await fetch(endpoint, {
      method: "POST",
      body: form,
    });

    const json = await response.json();
    if (!response.ok || json.error) {
      alert("Erro ao processar imagem: " + (json.error || response.statusText));
      return null;
    }

    return json.output; // ex: "/uploads/arquivo_processado.png"
  }

  // clique: aplicar CLAHE
  btnClahe.addEventListener("click", async () => {
    const outUrl = await processImage("/api/clahe", {
      clipLimit: 2.0,
      tileGridSize: "8,8",
    });

    if (!outUrl) return;

    imgClaheRes.src = outUrl;
    imgClaheRes.classList.add("visible");

    claheDownloadLink.href = outUrl;
    claheDownloadCol.classList.add("visible");
  });

  // clique: aplicar Filtro Bilateral
  btnBilateral.addEventListener("click", async () => {
    const outUrl = await processImage("/api/denoise/bilateral", {
      d: 25,
      sigmaColor: 250,
      sigmaSpace: 250,
    });

    if (!outUrl) return;

    imgBilRes.src = outUrl;
    imgBilRes.classList.add("visible");

    bilateralDownloadLink.href = outUrl;
    bilateralDownloadCol.classList.add("visible");
  });
}
