#!/usr/bin/env python3
"""
Conversor de AVI para MP4
Uso: python converter_avi_mp4.py [arquivo.avi ou pasta]
"""
 
import subprocess
import sys
import os
from pathlib import Path
 
 
def converter_arquivo(entrada: Path, saida: Path = None) -> bool:
    """Converte um único arquivo AVI para MP4."""
    if saida is None:
        saida = entrada.with_suffix(".mp4")
 
    print(f"Convertendo: {entrada.name} → {saida.name}")
 
    comando = [
        "ffmpeg",
        "-i", str(entrada),
        "-c:v", "libx264",      # codec de vídeo H.264
        "-c:a", "aac",          # codec de áudio AAC
        "-crf", "23",           # qualidade (0=melhor, 51=pior; 23 é padrão)
        "-preset", "medium",    # velocidade de codificação
        "-movflags", "+faststart",  # otimiza para streaming web
        "-y",                   # sobrescreve sem perguntar
        str(saida),
    ]
 
    try:
        resultado = subprocess.run(
            comando,
            capture_output=True,
            text=True,
        )
        if resultado.returncode == 0:
            tamanho_orig = entrada.stat().st_size / (1024 * 1024)
            tamanho_novo = saida.stat().st_size / (1024 * 1024)
            print(f"  ✓ Concluído! {tamanho_orig:.1f} MB → {tamanho_novo:.1f} MB")
            return True
        else:
            print(f"  ✗ Erro ao converter {entrada.name}:")
            print(resultado.stderr[-500:])  # últimas 500 chars do erro
            return False
    except FileNotFoundError:
        print("Erro: ffmpeg não encontrado. Instale com:")
        print("  Ubuntu/Debian: sudo apt install ffmpeg")
        print("  macOS:         brew install ffmpeg")
        print("  Windows:       https://ffmpeg.org/download.html")
        sys.exit(1)
 
 
def converter_pasta(pasta: Path) -> None:
    """Converte todos os arquivos AVI de uma pasta."""
    arquivos = list(pasta.glob("*.avi")) + list(pasta.glob("*.AVI"))
 
    if not arquivos:
        print(f"Nenhum arquivo .avi encontrado em: {pasta}")
        return
 
    print(f"Encontrados {len(arquivos)} arquivo(s) AVI\n")
    sucessos, falhas = 0, 0
 
    for arquivo in sorted(arquivos):
        ok = converter_arquivo(arquivo)
        if ok:
            sucessos += 1
        else:
            falhas += 1
 
    print(f"\nResumo: {sucessos} convertido(s), {falhas} com erro(s)")
 
 
def main():
    if len(sys.argv) < 2:
        # Sem argumento: converte todos os AVI da pasta atual
        converter_pasta(Path("."))
        return
 
    caminho = Path(sys.argv[1])
 
    if not caminho.exists():
        print(f"Erro: '{caminho}' não encontrado.")
        sys.exit(1)
 
    if caminho.is_dir():
        converter_pasta(caminho)
    elif caminho.suffix.lower() == ".avi":
        # Destino opcional como segundo argumento
        saida = Path(sys.argv[2]) if len(sys.argv) > 2 else None
        ok = converter_arquivo(caminho, saida)
        sys.exit(0 if ok else 1)
    else:
        print(f"Erro: '{caminho.name}' não é um arquivo .avi nem uma pasta.")
        sys.exit(1)
 
 
if __name__ == "__main__":
    main()