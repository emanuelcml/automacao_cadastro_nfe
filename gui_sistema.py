from tkinter import *
from tkinter.filedialog import askopenfilename
from tkinter import messagebox
from fornecedor import Fornecedor
from sistema_nota_legal import SistemaNotaLegal
from threading import Thread

class SistemaGUI:
    def __init__(self, master=None):
        self._handle_sis_nota_legal = None

        self.layout_janela(master)

        master.mainloop()

    def layout_janela(self, master=None):
        master.title('Automação de cadastro de notas')

        _fonte_padrao = ('Arial', '11')

        # estrutura de containers
        _frame_login = Frame(master)
        _frame_login.grid(row=0, column=0, padx=3)

        _frame_fornecedor = Frame(master)
        _frame_fornecedor.grid(row=0, column=1, padx=3)

        _frame_arquivo = Frame(master)
        _frame_arquivo.grid(row=1, columnspan=2, pady=3)

        _frame_cadastro = Frame(master)
        _frame_cadastro.grid(row=2, columnspan=2, pady=7)

        # ----- componentes dos containers
        # -- frame_login
        _titulo = Label(_frame_login, text='Dados do usuário')
        _titulo['font'] = ('Arial', '10', 'bold')
        _titulo.grid(row=0, columnspan=2)

        _login_label = Label(_frame_login, text='Login:', font=_fonte_padrao)
        _login_label.grid(row=1, column=0, sticky=E)

        self._login = Entry(_frame_login)
        self._login['width'] = 30
        self._login['font'] = _fonte_padrao
        self._login.focus()
        self._login.grid(row=1, column=1)

        _senha_label = Label(_frame_login, text='Senha:', font=_fonte_padrao)
        _senha_label.grid(row=2, column=0, sticky=E)

        self._senha = Entry(_frame_login)
        self._senha['width'] = 30
        self._senha['font'] = _fonte_padrao
        self._senha['show'] = '*'
        self._senha.grid(row=2, column=1)

        # -- frame_fornecedor
        _fornecedor_label = Label(_frame_fornecedor, text='Escolha o tipo de arquivo')
        _fornecedor_label['font'] = ('Arial', '10', 'bold')
        _fornecedor_label.grid(row=0)

        fornecedores = Fornecedor()
        ids_fornecedores = fornecedores.get_ids_fornecedores()
        self._tipo_fornecedor = StringVar(_frame_fornecedor, '1')
        _rb_fornecedor1 = Radiobutton(_frame_fornecedor,
                                      text=fornecedores.fornecedor[ids_fornecedores[0]]['fonte'],
                                      variable=self._tipo_fornecedor,
                                      value=ids_fornecedores[0])
        _rb_fornecedor1.grid(row=1, sticky=W)
        _rb_fornecedor2 = Radiobutton(_frame_fornecedor,
                                      text=fornecedores.fornecedor[ids_fornecedores[1]]['fonte'],
                                      variable=self._tipo_fornecedor,
                                      value=ids_fornecedores[1])
        _rb_fornecedor2.grid(row=2, sticky=W)
        _rb_fornecedor3 = Radiobutton(_frame_fornecedor,
                                      text=fornecedores.fornecedor[ids_fornecedores[2]]['fonte'],
                                      variable=self._tipo_fornecedor,
                                      value=ids_fornecedores[2])
        _rb_fornecedor3.grid(row=3, sticky=W)

        # -- frame_arquivo
        _lbl_selecao_arquivo = Label(_frame_arquivo, text='Escolha o arquivo')
        _lbl_selecao_arquivo['font'] = ('Arial', '10', 'bold')
        _lbl_selecao_arquivo.grid(row=0, columnspan=2)

        _btn_selecionar_arquivo = Button(_frame_arquivo)
        _btn_selecionar_arquivo['text'] = 'Selecionar arquivo'
        _btn_selecionar_arquivo['font'] = ('Calibri', '9')
        _btn_selecionar_arquivo['command'] = self._selecionar_arquivo
        _btn_selecionar_arquivo.grid(row=1, column=0, padx=3)

        self._path_arquivo = StringVar()
        self._lbl_nome_arquivo = Entry(_frame_arquivo, textvariable=self._path_arquivo, state='readonly')
        self._lbl_nome_arquivo['width'] = 45
        self._lbl_nome_arquivo['font'] = _fonte_padrao
        self._lbl_nome_arquivo.grid(row=1, column=1, padx=4)

        _lbl_id_inicio = Label(_frame_arquivo, text='Ordem de inicio:')
        _lbl_id_inicio['font'] = _fonte_padrao
        _lbl_id_inicio.grid(row=2, column=0)

        self._inp_id_inicio = Entry(_frame_arquivo)
        self._inp_id_inicio['width'] = 10
        self._inp_id_inicio['font'] = _fonte_padrao
        self._inp_id_inicio.grid(row=2, column=1, padx=4, sticky=W)

        # -- frame_cadastro
        _btn_iniciar_cadastro = Button(_frame_cadastro)
        _btn_iniciar_cadastro['text'] = 'Iniciar cadastro'
        _btn_iniciar_cadastro['font'] = ('Calibri', '9')
        _btn_iniciar_cadastro['command'] = self._iniciar_cadastro
        _btn_iniciar_cadastro.grid()

        self._lbl_status = Label(_frame_cadastro)
        self._lbl_status['text'] = ''
        self._lbl_status.grid()

        master.after(500,
                     lambda: self._lbl_status.config(text=self._handle_sis_nota_legal.status)
                     if self._handle_sis_nota_legal is not None else self._lbl_status.config(text='...'))

    def _iniciar_cadastro(self):

        id_inicio = self._inp_id_inicio.get().strip()
        if id_inicio.isnumeric():
            id_inicio = int(id_inicio)
        else:
            id_inicio = 0

        self._lbl_status.config(text='Iniciando o processo de cadastro')

        thread_cadastro = Thread(target=self._executa_cadastro, args=(id_inicio,))
        thread_cadastro.start()

    def _executa_cadastro(self, id_inicio):
        try:
            self._handle_sis_nota_legal = SistemaNotaLegal(self._lbl_nome_arquivo.get(),
                                                           int(self._tipo_fornecedor.get()),
                                                           id_inicio)

            self._handle_sis_nota_legal.inicia(self._login.get().strip(), self._senha.get().strip())

        except FileNotFoundError as fne:
            self._lbl_status.config(text='Arquivo nao encontrado')
        except ValueError as ve:
            self._lbl_status.config(text='Erro nos campos preenchidos')
        except:
            self._lbl_status.config(text=f'-- Falha interna --\n {self._handle_sis_nota_legal.cont_notas_cadastradas_sucesso} notas cadastradas.')
        else:
            self._lbl_status.config(text=f'Processo encerrado. {self._handle_sis_nota_legal.cont_notas_cadastradas_sucesso} notas cadastradas.')

    def _selecionar_arquivo(self):
        filename = askopenfilename()
        self._path_arquivo.set(filename)
        self._lbl_nome_arquivo.xview_moveto(1)


if __name__ == '__main__':
    janela = Tk()
    SistemaGUI(janela)
