import ctypes
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import fitz  # PyMuPDF

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-Monitor DPI Aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

def selecionar_e_comprimir():
    # Abre janela para escolher o PDF
    caminho_entrada = filedialog.askopenfilename(
        title="Selecione o PDF escaneado",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if not caminho_entrada:
        return

    # Define o nome do arquivo de saída na mesma pasta
    pasta, nome_arquivo = os.path.split(caminho_entrada)
    nome_base, extensao = os.path.splitext(nome_arquivo)
    caminho_saida = os.path.join(pasta, f"{nome_base}_leve{extensao}")

    # Pega as opções escolhidas na tela
    dpi_escolhido = int(var_dpi.get())
    qualidade_escolhida = int(var_qualidade.get())
    usar_pb = var_pb.get()

    btn_selecionar.config(state="disabled", text="Comprimindo...")
    janela.update()

    try:
        doc = fitz.open(caminho_entrada)
        doc.rewrite_images(
            dpi_threshold=dpi_escolhido + 1,
            dpi_target=dpi_escolhido,
            quality=qualidade_escolhida,
            set_to_gray=usar_pb
        )
        doc.save(caminho_saida, garbage=4, deflate=True, clean=True)
        doc.close()

        # Calcula tamanho antes e depois
        antes = os.path.getsize(caminho_entrada) / (1024 * 1024)
        depois = os.path.getsize(caminho_saida) / (1024 * 1024)
        economia = (1 - (depois / antes)) * 100

        lbl_status.config(
            text=f"Salvo como: {nome_base}_leve.pdf\n"
                 f"Antes: {antes:.2f} MB  ➔  Depois: {depois:.2f} MB (-{economia:.1f}%)",
            fg="green"
        )
        messagebox.showinfo("Concluído", f"PDF comprimido com sucesso!\nRedução de {economia:.1f}%.")

    except Exception as e:
        lbl_status.config(text="Erro ao comprimir o arquivo.", fg="red")
        messagebox.showerror("Erro", f"Ocorreu um problema:\n{e}")

    finally:
        btn_selecionar.config(state="normal", text="Selecionar PDF e Comprimir")

# --- Configuração da Janela ---
janela = tk.Tk()
janela.title("Compressor de PDF Escaneado")
#janela.geometry("500x340")
janela.resizable(False, False)

# Título
tk.Label(janela, text="Compressor de Escaneamentos", font=("Arial", 13, "bold")).pack(pady=10)

# Frame de Opções
frame_opcoes = tk.Frame(janela)
frame_opcoes.pack(pady=5)

# Opção DPI
tk.Label(frame_opcoes, text="Resolução (DPI):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
var_dpi = tk.StringVar(value="150")
tk.OptionMenu(frame_opcoes, var_dpi, "50", "75", "100", "150", "200", "300").grid(row=0, column=1, sticky="w")

# Opção Qualidade JPG
tk.Label(frame_opcoes, text="Qualidade (1-100):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
var_qualidade = tk.StringVar(value="75")
tk.Spinbox(frame_opcoes, from_=30, to=95, textvariable=var_qualidade, width=5).grid(row=1, column=1, sticky="w")

# Opção Preto e Branco
var_pb = tk.BooleanVar(value=False)
tk.Checkbutton(
    janela,
    text="Converter para Preto e Branco (reduz muito mais)",
    variable=var_pb
).pack(pady=8)

# Botão Principal
btn_selecionar = tk.Button(
    janela,
    text="Selecionar PDF e Comprimir",
    font=("Arial", 11, "bold"),
    bg="#0066cc",
    fg="white",
    padx=15,
    pady=8,
    command=selecionar_e_comprimir
)
btn_selecionar.pack(pady=10)

# Texto de Status
lbl_status = tk.Label(janela, text="Nenhum arquivo processado ainda.", font=("Arial", 9), fg="#555")
lbl_status.pack(pady=5)

janela.mainloop()
