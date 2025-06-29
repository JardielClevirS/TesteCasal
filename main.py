import os
import random
from PIL import Image, ImageOps, ImageDraw, ImageFont

LARGURA_LADRILHO = 250
ALTURA_LADRILHO = 450
TAMANHO_BORDA = 20
COR_BORDA = "black"

def criar_imagem_exemplo(caminho_arquivo="imagem_entrada.png", largura=1000, altura=900):
    if not os.path.exists(caminho_arquivo):
        print(f"Criando uma imagem de exemplo em '{caminho_arquivo}'...")
        img = Image.new('RGB', (largura, altura), color = 'white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        cols = largura // LARGURA_LADRILHO
        rows = altura // ALTURA_LADRILHO
        for i in range(rows):
            for j in range(cols):
                x0 = j * LARGURA_LADRILHO
                y0 = i * ALTURA_LADRILHO
                x1 = x0 + LARGURA_LADRILHO
                y1 = y0 + ALTURA_LADRILHO
                
                draw.rectangle([x0, y0, x1-1, y1-1], outline="lightgray")
                
                texto = str(i * cols + j)
                bbox = draw.textbbox((0,0), texto, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                pos_x = x0 + (LARGURA_LADRILHO - text_width) / 2
                pos_y = y0 + (ALTURA_LADRILHO - text_height) / 2
                draw.text((pos_x, pos_y), texto, fill="black", font=font)
        img.save(caminho_arquivo)

def processar_imagem(caminho_imagem_entrada, caminho_imagem_saida, caminho_chave):
    print(f"🖼️ Carregando a imagem de '{caminho_imagem_entrada}'...")
    try:
        img_original = Image.open(caminho_imagem_entrada)
    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{caminho_imagem_entrada}' não foi encontrado.")
        return

    largura_total, altura_total = img_original.size

    ladrilhos = []
    n_cols = largura_total // LARGURA_LADRILHO
    n_rows = altura_total // ALTURA_LADRILHO

    print(f"📏 A imagem será dividida em {n_rows} linhas e {n_cols} colunas.")
    
    for i in range(n_rows):
        for j in range(n_cols):
            box = (
                j * LARGURA_LADRILHO,
                i * ALTURA_LADRILHO,
                (j + 1) * LARGURA_LADRILHO,
                (i + 1) * ALTURA_LADRILHO,
            )
            ladrilho = img_original.crop(box)
            ladrilhos.append(ladrilho)
            
    if not ladrilhos:
        print("Erro: A imagem de entrada é menor que as dimensões do ladrilho. Nenhum ladrilho foi criado.")
        return

    n_ladrilhos = len(ladrilhos)
    indices_originais = list(range(n_ladrilhos))
    indices_embaralhados = indices_originais[:]
    random.shuffle(indices_embaralhados)

    with open(caminho_chave, "w") as f:
        f.write(",".join(map(str, indices_embaralhados)))
    print(f"🔑 Chave de embaralhamento salva em '{caminho_chave}'.")


    largura_ladrilho_com_borda = LARGURA_LADRILHO + (2 * TAMANHO_BORDA)
    altura_ladrilho_com_borda = ALTURA_LADRILHO + (2 * TAMANHO_BORDA)

    largura_final = n_cols * largura_ladrilho_com_borda
    altura_final = n_rows * altura_ladrilho_com_borda
    
    imagem_final = Image.new(img_original.mode, (largura_final, altura_final))
    print("🔄 Montando a imagem final embaralhada...")

    for idx_novo, idx_original in enumerate(indices_embaralhados):
        ladrilho_original = ladrilhos[idx_original]
        
        ladrilho_com_borda = ImageOps.expand(
            ladrilho_original, 
            border=TAMANHO_BORDA, 
            fill=COR_BORDA
        )
        
        nova_linha = idx_novo // n_cols
        nova_coluna = idx_novo % n_cols
        
        posicao_x = nova_coluna * largura_ladrilho_com_borda
        posicao_y = nova_linha * altura_ladrilho_com_borda
        
        imagem_final.paste(ladrilho_com_borda, (posicao_x, posicao_y))
        
    imagem_final.save(caminho_imagem_saida)
    print(f"✅ Processo concluído! Imagem final salva em '{caminho_imagem_saida}'.")

def reverter_processo(caminho_imagem_processada, caminho_chave, caminho_imagem_restaurada):
    print("\n--- Iniciando processo de reversão ---")
    
    try:
        img_processada = Image.open(caminho_imagem_processada)
        with open(caminho_chave, "r") as f:
            indices_embaralhados = list(map(int, f.read().split(',')))
    except FileNotFoundError:
        print("Erro: Imagem processada ou arquivo de chave não encontrado.")
        return

    largura_ladrilho_com_borda = LARGURA_LADRILHO + (2 * TAMANHO_BORDA)
    altura_ladrilho_com_borda = ALTURA_LADRILHO + (2 * TAMANHO_BORDA)
    
    n_cols = img_processada.width // largura_ladrilho_com_borda
    n_rows = img_processada.height // altura_ladrilho_com_borda

    n_ladrilhos = len(indices_embaralhados)
    mapa_reverso = [0] * n_ladrilhos
    for idx_novo, idx_original in enumerate(indices_embaralhados):
        mapa_reverso[idx_original] = idx_novo

    largura_restaurada = n_cols * LARGURA_LADRILHO
    altura_restaurada = n_rows * ALTURA_LADRILHO
    imagem_restaurada = Image.new(img_processada.mode, (largura_restaurada, altura_restaurada))
    print("🧩 Remontando a imagem original a partir da chave...")

    for idx_original in range(n_ladrilhos):
        idx_na_imagem_embaralhada = mapa_reverso[idx_original]
        
        linha_embaralhada = idx_na_imagem_embaralhada // n_cols
        coluna_embaralhada = idx_na_imagem_embaralhada % n_cols
        
        box_corte = (
            coluna_embaralhada * largura_ladrilho_com_borda,
            linha_embaralhada * altura_ladrilho_com_borda,
            (coluna_embaralhada + 1) * largura_ladrilho_com_borda,
            (linha_embaralhada + 1) * altura_ladrilho_com_borda
        )
        ladrilho_com_borda = img_processada.crop(box_corte)
        
        ladrilho_sem_borda = ladrilho_com_borda.crop(
            (TAMANHO_BORDA, TAMANHO_BORDA, 
             ladrilho_com_borda.width - TAMANHO_BORDA, 
             ladrilho_com_borda.height - TAMANHO_BORDA)
        )
        
        linha_original = idx_original // n_cols
        coluna_original = idx_original % n_cols
        posicao_x = coluna_original * LARGURA_LADRILHO
        posicao_y = linha_original * ALTURA_LADRILHO
        
        imagem_restaurada.paste(ladrilho_sem_borda, (posicao_x, posicao_y))
        
    imagem_restaurada.save(caminho_imagem_restaurada)
    print(f"✅ Imagem restaurada com sucesso em '{caminho_imagem_restaurada}'!")


if __name__ == '__main__':
    ARQUIVO_ENTRADA = "imagemDeENtrada.png"
    ARQUIVO_SAIDA = "imagemDeSaida.png"
    ARQUIVO_CHAVE = "chaveDeAessoParaCliente.txt"
    ARQUIVO_RESTAURADO = "imagemRestaurada.png"
    
    criar_imagem_exemplo(ARQUIVO_ENTRADA)

    processar_imagem(
        caminho_imagem_entrada=ARQUIVO_ENTRADA,
        caminho_imagem_saida=ARQUIVO_SAIDA,
        caminho_chave=ARQUIVO_CHAVE
    )
    
    reverter_processo(
        caminho_imagem_processada=ARQUIVO_SAIDA,
        caminho_chave=ARQUIVO_CHAVE,
        caminho_imagem_restaurada=ARQUIVO_RESTAURADO
    )