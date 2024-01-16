import pandas as pd
import re
from arquivo_nota_pdf import ArquivoNotaPDF
from fornecedor import Fornecedor

class DadosNota:
    def __init__(self, file, num_fornecedor, id_nota_inicio=0):
        if file == '':
            # implementar validação de caminho de arquivo posteriormente
            raise FileNotFoundError('Caminho do arquivo incorreto ou não encontrado!')

        # carrega as configurações de estrutura do arquivo de notas dependendo do fornecedor
        self._fornecedor = Fornecedor()

        self._contador_nota = 0

        # _dados pode ser uma Series pandas, uma lista, um iterável de chaves no formato string
        self._dados = self._carrega_dados(file, self._fornecedor.fornecedor[num_fornecedor], id_nota_inicio)

        # iterador para acessar uma nota a cada cadastro
        self._ch_nota = self._get_nota()

    def _carrega_dados(self, filename, fornecedor, id_nota_inicio=0):
        tipo_arquivo = filename.split('.')[-1]

        lista_chaves = []

        if tipo_arquivo.lower() == 'csv':
            self._ler_dados_csv(filename, fornecedor['id_chave'])
            lista_chaves = self._pre_processa_raw_dados_csv(fornecedor['id_chave'])

        elif tipo_arquivo.lower() == 'pdf':
            arquivo = ArquivoNotaPDF(filename, fornecedor)
            lista_chaves = arquivo.get_lista_notas()

        return lista_chaves[id_nota_inicio:]

    def _ler_dados_csv(self, filename, col):
        self._dados = pd.read_csv(filename, usecols=[col])

    def _pre_processa_raw_dados_csv(self, col):
        pattern = r'\=([0-9]*)\|'
        return self._dados[col].apply(lambda x:
                                      re.search(pattern, x).group().
                                      removeprefix('=').removesuffix('|'))

    def _get_nota(self):
        for ch in self._dados:
            self._contador_nota += 1
            yield ch

    def proxima_nota(self):
        return next(self._ch_nota)

    def get_total_notas(self):
        return len(self._dados)

    def get_ordem_nota_atual(self):
        return self._contador_nota
