import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time

class ControleBraco:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle do Braço Robótico")
        self.root.geometry("480x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")

        self.ser = None
        self.conectado = False
        self.enviando = False

        # Cores
        self.bg = "#1e1e2e"
        self.fg = "#cdd6f4"
        self.accent = "#89b4fa"
        self.slider_bg = "#313244"

        self.criar_interface()
        self.atualizar_portas()

    def criar_interface(self):
        # Título
        titulo = tk.Label(self.root, text="Controle do Braço Robótico", 
                          font=("Segoe UI", 16, "bold"), bg=self.bg, fg=self.accent)
        titulo.pack(pady=(20, 10))

        # Frame da porta serial
        frame_porta = tk.Frame(self.root, bg=self.bg)
        frame_porta.pack(pady=10)

        tk.Label(frame_porta, text="Porta:", bg=self.bg, fg=self.fg, font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)

        self.combo_porta = ttk.Combobox(frame_porta, width=15, state="readonly")
        self.combo_porta.pack(side=tk.LEFT, padx=5)

        self.btn_atualizar = tk.Button(frame_porta, text="⟳", command=self.atualizar_portas,
                                       bg="#45475a", fg=self.fg, relief="flat", width=3)
        self.btn_atualizar.pack(side=tk.LEFT, padx=5)

        self.btn_conectar = tk.Button(frame_porta, text="Conectar", command=self.conectar,
                                      bg="#a6e3a1", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                                      relief="flat", width=12)
        self.btn_conectar.pack(side=tk.LEFT, padx=10)

        # Status
        self.lbl_status = tk.Label(self.root, text="● Desconectado", bg=self.bg, fg="#f38ba8",
                                   font=("Segoe UI", 10))
        self.lbl_status.pack(pady=5)

        # Separador
        ttk.Separator(self.root, orient="horizontal").pack(fill="x", padx=30, pady=15)

        # Frame dos sliders
        frame_sliders = tk.Frame(self.root, bg=self.bg)
        frame_sliders.pack(pady=5, padx=30, fill="x")

        # Variáveis dos sliders
        self.var_base = tk.IntVar(value=90)
        self.var_braco = tk.IntVar(value=90)
        self.var_antebraco = tk.IntVar(value=90)
        self.var_garra = tk.IntVar(value=90)

        # Criar os 4 sliders
        self.criar_slider(frame_sliders, "Base", self.var_base, 0)
        self.criar_slider(frame_sliders, "Braço", self.var_braco, 1)
        self.criar_slider(frame_sliders, "Antebraço", self.var_antebraco, 2)
        self.criar_slider(frame_sliders, "Garra", self.var_garra, 3)

        # Botão de posição central
        btn_centro = tk.Button(self.root, text="Posição Central (90°)", command=self.posicao_central,
                               bg="#89b4fa", fg="#1e1e2e", font=("Segoe UI", 10, "bold"),
                               relief="flat", width=25)
        btn_centro.pack(pady=20)

        # Rodapé
        tk.Label(self.root, text="Arraste os sliders para controlar o braço",
                 bg=self.bg, fg="#6c7086", font=("Segoe UI", 9)).pack(side=tk.BOTTOM, pady=10)

    def criar_slider(self, parent, nome, variavel, linha):
        frame = tk.Frame(parent, bg=self.bg)
        frame.pack(fill="x", pady=8)

        # Nome + valor
        frame_topo = tk.Frame(frame, bg=self.bg)
        frame_topo.pack(fill="x")

        tk.Label(frame_topo, text=nome, bg=self.bg, fg=self.fg,
                 font=("Segoe UI", 11, "bold"), width=12, anchor="w").pack(side=tk.LEFT)

        lbl_valor = tk.Label(frame_topo, textvariable=variavel, bg=self.bg, fg=self.accent,
                             font=("Segoe UI", 11, "bold"), width=4)
        lbl_valor.pack(side=tk.RIGHT)

        # Slider
        scale = tk.Scale(frame, from_=0, to=180, orient="horizontal",
                         variable=variavel, showvalue=False,
                         bg=self.slider_bg, fg=self.fg, troughcolor="#45475a",
                         highlightthickness=0, length=380,
                         activebackground=self.accent, sliderrelief="flat")
        scale.pack(fill="x")

        # Atualiza o valor quando mexe
        scale.configure(command=lambda v: self.ao_mover())

    def atualizar_portas(self):
        portas = [porta.device for porta in serial.tools.list_ports.comports()]
        self.combo_porta["values"] = portas
        if portas:
            self.combo_porta.current(0)

    def conectar(self):
        if self.conectado:
            self.desconectar()
            return

        porta = self.combo_porta.get()
        if not porta:
            messagebox.showerror("Erro", "Nenhuma porta selecionada!")
            return

        try:
            self.ser = serial.Serial(porta, 9600, timeout=1)
            time.sleep(2)  # Espera o Arduino resetar
            self.conectado = True
            self.lbl_status.config(text="● Conectado", fg="#a6e3a1")
            self.btn_conectar.config(text="Desconectar", bg="#f38ba8")
            self.iniciar_envio()
            print(f"Conectado em {porta}")
        except Exception as e:
            messagebox.showerror("Erro de conexão", str(e))

    def desconectar(self):
        self.enviando = False
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.conectado = False
        self.lbl_status.config(text="● Desconectado", fg="#f38ba8")
        self.btn_conectar.config(text="Conectar", bg="#a6e3a1")

    def iniciar_envio(self):
        self.enviando = True
        threading.Thread(target=self.loop_envio, daemon=True).start()

    def loop_envio(self):
        while self.enviando and self.conectado:
            try:
                comando = f"{self.var_base.get()},{self.var_braco.get()},{self.var_antebraco.get()},{self.var_garra.get()}\n"
                self.ser.write(comando.encode())
            except:
                self.root.after(0, self.desconectar)
                break
            time.sleep(0.05)  # Envia a cada 50ms (bem suave)

    def ao_mover(self):
        # Só para forçar atualização visual (o loop já envia)
        pass

    def posicao_central(self):
        self.var_base.set(90)
        self.var_braco.set(90)
        self.var_antebraco.set(90)
        self.var_garra.set(90)

    def on_closing(self):
        self.desconectar()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ControleBraco(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()