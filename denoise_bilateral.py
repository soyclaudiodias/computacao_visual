import argparse
import os
import cv2

def bilateral_denoise(img, d=9, sigma_color=75, sigma_space=75, force_gray=False):
    # Aplica tons de cinza quando imagem colorida
    if force_gray and img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)

def main():
    # Configura os argumentos de linha de comando
    ap = argparse.ArgumentParser(description="Denoise Bilateral (OpenCV).")
    ap.add_argument("input", help="Caminho da imagem de entrada")
    ap.add_argument("-o", "--output", help="Saída (default: <nome>_bilateral.<ext>)")
    ap.add_argument("--d", type=int, default=9, help="Diâmetro da vizinhança (ex.: 5, 9, 15)")
    ap.add_argument("--sigmaColor", type=float, default=75.0, help="Sigma no domínio de cor")
    ap.add_argument("--sigmaSpace", type=float, default=75.0, help="Sigma no domínio espacial")
    ap.add_argument("--gray", action="store_true", help="Forçar grayscale")
    ap.add_argument("--show", action="store_true", help="Mostrar antes/depois")
    args = ap.parse_args()

    # Verifica o arquivo entrada
    if not os.path.exists(args.input):
        raise FileNotFoundError(f"Arquivo não encontrado: {args.input}")

    # Lê imagem
    img = cv2.imread(args.input, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Falha ao ler a imagem. Verifique o caminho/arquivo.")

    # Aplica o filtro bilateral
    out = bilateral_denoise(
        img,
        d=args.d,
        sigma_color=args.sigmaColor,
        sigma_space=args.sigmaSpace,
        force_gray=args.gray,
    )

    # Aplica o nome do arquivo saída
    if not args.output:
        base, ext = os.path.splitext(args.input)
        args.output = f"{base}_bilateral{'.png' if out.ndim==2 else ext}"

    # Salva a imagem
    ok = cv2.imwrite(args.output, out)
    if not ok:
        raise IOError(f"Não foi possível salvar em: {args.output}")
    
    # Salvamento com sucesso
    print(f"✔ Denoise Bilateral salvo em: {args.output}")

    # Exibe a imagem original e com o ruido bilateral aplicado
    if args.show:
        cv2.imshow("Antes", img)
        cv2.imshow("Depois (Bilateral)", out)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
## Executa a função principal
if __name__ == "__main__":
    main()
