import os
import random
from PIL import Image, ImageOps, ImageDraw, ImageFont

# --- Configurações Iniciais ---
# Conforme o enunciado do problema
LARGURA_LADRILHO = 250
ALTURA_LADRILHO = 450
TAMANHO_BORDA = 20
COR_BORDA = "black" # A cor da borda pode ser alterada aqui

def criar_imagem_exemplo(caminho_arquivo="imagem_entrada.png", largura=1000, altura=900):
    """Cria uma imagem de exemplo caso nenhuma seja fornecida."""
    if not os.path.exists(caminho_arquivo):
        print(f"Criando uma imagem de exemplo em '{caminho_arquivo}'...")
        img = Image.new('RGB', (largura, altura), color = 'white')
        draw = ImageDraw.Draw(img)
        try:
            # Tenta usar uma fonte comum
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            # Usa a fonte padrão se a outra não for encontrada
            font = ImageFont.load_default()

        # Desenha uma grade e números para visualizar os ladrilhos originais
        cols = largura // LARGURA_LADRILHO
        rows = altura // ALTURA_LADRILHO
        for i in range(rows):
            for j in range(cols):
                x0 = j * LARGURA_LADRILHO
                y0 = i * ALTURA_LADRILHO
                x1 = x0 + LARGURA_LADRILHO
                y1 = y0 + ALTURA_LADRILHO
                
                # Desenha o retângulo do ladrilho
                draw.rectangle([x0, y0, x1-1, y1-1], outline="lightgray")
                
                # Escreve o número do ladrilho no centro
                texto = str(i * cols + j)
                bbox = draw.textbbox((0,0), texto, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                pos_x = x0 + (LARGURA_LADRILHO - text_width) / 2
                pos_y = y0 + (ALTURA_LADRILHO - text_height) / 2
                draw.text((pos_x, pos_y), texto, fill="black", font=font)
        img.save(caminho_arquivo)

def processar_imagem(caminho_imagem_entrada, caminho_imagem_saida, caminho_chave):
    """
    Executa o fluxo principal: fatiar, adicionar bordas, embaralhar e montar.
    
    Args:
        caminho_imagem_entrada (str): Caminho para a imagem original.
        caminho_imagem_saida (str): Caminho onde a imagem processada será salva.
        caminho_chave (str): Caminho para salvar o arquivo com a ordem de embaralhamento.
    """
    print(f"🖼️  Carregando a imagem de '{caminho_imagem_entrada}'...")
    try:
        img_original = Image.open(caminho_imagem_entrada)
    except FileNotFoundError:
        print(f"Erro: O arquivo de entrada '{caminho_imagem_entrada}' não foi encontrado.")
        return

    largura_total, altura_total = img_original.size

    # 1. DIVIDIR A IMAGEM EM LADRILHOS (SESSÕES)
    ladrilhos = []
    # Calcula quantas colunas e linhas de ladrilhos teremos
    n_cols = largura_total // LARGURA_LADRILHO
    n_rows = altura_total // ALTURA_LADRILHO

    print(f"📏 A imagem será dividida em {n_rows} linhas e {n_cols} colunas.")
    
    for i in range(n_rows):
        for j in range(n_cols):
            # Define a caixa de corte (esquerda, cima, direita, baixo)
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

    # 2. CRIAR A ORDEM DE EMBARALHAMENTO (A "CHAVE")
    # O segredo para a reversibilidade é salvar a ordem dos ladrilhos.
    n_ladrilhos = len(ladrilhos)
    indices_originais = list(range(n_ladrilhos))
    indices_embaralhados = indices_originais[:] # Cria uma cópia para embaralhar
    random.shuffle(indices_embaralhados)

    # Salva a chave em um arquivo de texto. Ex: "3,1,0,2,..."
    with open(caminho_chave, "w") as f:
        f.write(",".join(map(str, indices_embaralhados)))
    print(f"🔑 Chave de embaralhamento salva em '{caminho_chave}'.")


    # 3. ADICIONAR BORDAS, EMBARALHAR E MONTAR A IMAGEM FINAL
    largura_ladrilho_com_borda = LARGURA_LADRILHO + (2 * TAMANHO_BORDA)
    altura_ladrilho_com_borda = ALTURA_LADRILHO + (2 * TAMANHO_BORDA)

    # Calcula o tamanho da imagem final
    largura_final = n_cols * largura_ladrilho_com_borda
    altura_final = n_rows * altura_ladrilho_com_borda
    
    # Cria a tela em branco para a imagem final
    imagem_final = Image.new(img_original.mode, (largura_final, altura_final))
    print("🔄 Montando a imagem final embaralhada...")

    # Itera sobre os índices embaralhados para montar a nova imagem
    for idx_novo, idx_original in enumerate(indices_embaralhados):
        ladrilho_original = ladrilhos[idx_original]
        
        # Adiciona a borda ao ladrilho
        ladrilho_com_borda = ImageOps.expand(
            ladrilho_original, 
            border=TAMANHO_BORDA, 
            fill=COR_BORDA
        )
        
        # Calcula a posição para colar o ladrilho na imagem final
        nova_linha = idx_novo // n_cols
        nova_coluna = idx_novo % n_cols
        
        posicao_x = nova_coluna * largura_ladrilho_com_borda
        posicao_y = nova_linha * altura_ladrilho_com_borda
        
        imagem_final.paste(ladrilho_com_borda, (posicao_x, posicao_y))
        
    # 4. SALVAR A IMAGEM FINAL
    imagem_final.save(caminho_imagem_saida)
    print(f"✅ Processo concluído! Imagem final salva em '{caminho_imagem_saida}'.")

def reverter_processo(caminho_imagem_processada, caminho_chave, caminho_imagem_restaurada):
    """
    Função bônus para demonstrar a reversibilidade do processo.
    """
    print("\n--- Iniciando processo de reversão ---")
    
    try:
        img_processada = Image.open(caminho_imagem_processada)
        with open(caminho_chave, "r") as f:
            indices_embaralhados = list(map(int, f.read().split(',')))
    except FileNotFoundError:
        print("Erro: Imagem processada ou arquivo de chave não encontrado.")
        return

    # Calcula as dimensões com base na imagem processada
    largura_ladrilho_com_borda = LARGURA_LADRILHO + (2 * TAMANHO_BORDA)
    altura_ladrilho_com_borda = ALTURA_LADRILHO + (2 * TAMANHO_BORDA)
    
    n_cols = img_processada.width // largura_ladrilho_com_borda
    n_rows = img_processada.height // altura_ladrilho_com_borda

    # Cria o mapa reverso para facilitar a restauração
    # mapa_reverso[idx_original] = idx_novo
    n_ladrilhos = len(indices_embaralhados)
    mapa_reverso = [0] * n_ladrilhos
    for idx_novo, idx_original in enumerate(indices_embaralhados):
        mapa_reverso[idx_original] = idx_novo

    # Cria a tela para a imagem restaurada
    largura_restaurada = n_cols * LARGURA_LADRILHO
    altura_restaurada = n_rows * ALTURA_LADRILHO
    imagem_restaurada = Image.new(img_processada.mode, (largura_restaurada, altura_restaurada))
    print("🧩 Remontando a imagem original a partir da chave...")

    for idx_original in range(n_ladrilhos):
        # Onde este ladrilho está na imagem embaralhada?
        idx_na_imagem_embaralhada = mapa_reverso[idx_original]
        
        # Pega a posição e extrai o ladrilho com borda
        linha_embaralhada = idx_na_imagem_embaralhada // n_cols
        coluna_embaralhada = idx_na_imagem_embaralhada % n_cols
        
        box_corte = (
            coluna_embaralhada * largura_ladrilho_com_borda,
            linha_embaralhada * altura_ladrilho_com_borda,
            (coluna_embaralhada + 1) * largura_ladrilho_com_borda,
            (linha_embaralhada + 1) * altura_ladrilho_com_borda
        )
        ladrilho_com_borda = img_processada.crop(box_corte)
        
        # Remove a borda
        ladrilho_sem_borda = ladrilho_com_borda.crop(
            (TAMANHO_BORDA, TAMANHO_BORDA, 
             ladrilho_com_borda.width - TAMANHO_BORDA, 
             ladrilho_com_borda.height - TAMANHO_BORDA)
        )
        
        # Calcula a posição correta para colar na imagem restaurada
        linha_original = idx_original // n_cols
        coluna_original = idx_original % n_cols
        posicao_x = coluna_original * LARGURA_LADRILHO
        posicao_y = linha_original * ALTURA_LADRILHO
        
        imagem_restaurada.paste(ladrilho_sem_borda, (posicao_x, posicao_y))
        
    imagem_restaurada.save(caminho_imagem_restaurada)
    print(f"✅ Imagem restaurada com sucesso em '{caminho_imagem_restaurada}'!")


if __name__ == '__main__':
    # Nomes dos arquivos
    ARQUIVO_ENTRADA = "imagemDeENtrada.png"
    ARQUIVO_SAIDA = "imagemDeSaida.png"
    ARQUIVO_CHAVE = "chaveDeAessoParaCliente.txt"
    ARQUIVO_RESTAURADO = "imagemRestaurada.png"
    
    # Garante que uma imagem de entrada exista para o script rodar
    criar_imagem_exemplo(ARQUIVO_ENTRADA)

    # --- Execução do Processo Principal ---
    processar_imagem(
        caminho_imagem_entrada=ARQUIVO_ENTRADA,
        caminho_imagem_saida=ARQUIVO_SAIDA,
        caminho_chave=ARQUIVO_CHAVE
    )
    
    # --- Execução do Processo de Reversão (para demonstrar) ---
    # O cliente executaria uma função similar a esta usando a imagem e a chave.
    reverter_processo(
        caminho_imagem_processada=ARQUIVO_SAIDA,
        caminho_chave=ARQUIVO_CHAVE,
        caminho_imagem_restaurada=ARQUIVO_RESTAURADO
    )