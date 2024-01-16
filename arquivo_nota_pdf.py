from pypdf import PdfReader


class ArquivoNotaPDF:
    def __init__(self, filename, fornecedor):
        self.arquivo = PdfReader(filename)
        # para ser um fornecedor precisa fornecer um dicionário pelo menos com
        # os campos: id_chave, id_fim_cabecalho, id_inicio_rodape, id_rodape_ultima_pagina
        self._fornecedor = fornecedor

    def get_lista_notas(self):
        conteudo = self._seleciona_conteudo(self.arquivo)
        return self._seleciona_chaves(conteudo)

    def _converte_em_chave_apenas_numeros(self, chave):
        for v in ['-', '.', '/']:
            chave = chave.replace(v, '')
        return chave

    def _seleciona_conteudo(self, pdf):
        conteudo_interesse_paginas = []
        for pagina in pdf.pages[:-1]:
            conteudo_interesse_paginas.extend(
                self._corpo_pagina(pagina.extract_text(),
                                   self._fornecedor['id_fim_cabecalho'],
                                   self._fornecedor['id_inicio_rodape']))
        # ultima página
        pagina = pdf.pages[-1]
        conteudo_interesse_paginas.extend(
            # elimina as duas ultimas linhas
            self._corpo_pagina(pagina.extract_text(),
                               self._fornecedor['id_fim_cabecalho'],
                               self._fornecedor['id_rodape_ultima_pagina']))
        return conteudo_interesse_paginas

    def _corpo_pagina(self, txt, inicio, fim):
        return txt.splitlines()[inicio:fim]

    def _seleciona_chaves(self, texto_corpo):
        chave_nota = []
        for linha in texto_corpo:
            chave = linha.split()
            chave_nota.append(self._converte_em_chave_apenas_numeros(
                chave[self._fornecedor['id_chave']]))
        chave_notas = list(set(chave_nota))

        return chave_notas
