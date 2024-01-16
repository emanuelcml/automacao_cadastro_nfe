import time
import os
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from dados_nota import DadosNota


class SistemaNotaLegal:
    def __init__(self, filename, num_fornecedor, inicio_lista_notas=0):
        load_dotenv()

        self._driver = self._configura_driver()

        self._handle_dados = DadosNota(filename, num_fornecedor, inicio_lista_notas)

        self._aguarda_carregar()
        self._qtde_notas = self._handle_dados.get_total_notas()

        self._status = 'Iniciando sistema'

        self._cont_notas = 0
        self.cont_notas_cadastradas_sucesso = 0

    @property
    def status(self):
        return self._status

    def _possui_dados_login(self, usuario, senha):
        if usuario == '' or senha == '':
            raise ValueError('Usuário/senha são de preenchimento obrigatórios!')
        else:
            return True

    def inicia(self, usuario, senha):
        if not self._possui_dados_login(usuario, senha):
            return False

        self._driver.get(os.getenv('SITE'))
        time.sleep(5)

        if not self._logar(usuario, senha):
            return False

        self._acessar_area_notas_cadastradas()

        try:
            while True:
                print(self._info_total_notas_cadastradas(), end='')
                self._cadastrar_nota(self._handle_dados.proxima_nota())
                time.sleep(1)
                self._verificar_cadastro()
                print(self._status)

                if self._eh_pagina_erro_sistema_maximo_cadastro():
                    self._driver.back()
                    time.sleep(2)
                    self._driver.refresh()

        except StopIteration:
            print('Sem mais notas para cadastrar')

        self._encerrar_sessao()

    def _configura_driver(self):
        options = webdriver.FirefoxOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        ua = UserAgent()
        options.add_argument(f'user-agent={ua.random}')

        driver = webdriver.Firefox(options=options)

        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        driver.maximize_window()

        return driver

    def _aguarda_carregar(self):
        self._driver.implicitly_wait(4.0)

    def _eh_pagina_erro_sistema_maximo_cadastro(self):
        try:
            msg_erro = self._driver.find_element(By.XPATH, '/html/body/div/div[1]/div[3]/table/tbody/tr/td/div/div[2]/table[1]/tbody/tr[1]/td[2]/span')
            return True
        except NoSuchElementException:
            return False

    def _logar(self, usuario, senha):
        print('Logando no sistema')
        perfil_entidade = self._carrega_elemento('//*[@id="frmLogin:j_id11:5"]')
        perfil_entidade.click()

        login = self._carrega_elemento('//*[@id="frmLogin:txtLogin"]')
        login.send_keys(usuario)
        password = self._carrega_elemento(
            '//*[@id="frmLogin:pnlLogin_body"]/table[1]/tbody/tr/td[3]/table/tbody/tr[2]/td[2]/input')
        password.send_keys(senha)

        btn_acessar = self._carrega_elemento('//*[@id="frmLogin:btAcessar"]')
        btn_acessar.click()

        try:
            # verifica se encontra o menu para acessar notas cadastradas, indicando sucesso ao logar no sistema
            menu_notas_cadastradas = self._carrega_elemento('//*[@id="iconj_id19:RL_CONU014"]')
            return True

        except NoSuchElementException:
            print('Falha ao logar no sistema. Verifique suas credenciais.')
            return False

    def _acessar_area_notas_cadastradas(self):
        menu_notas_cadastradas = self._carrega_elemento('//*[@id="iconj_id19:RL_CONU014"]')
        menu_notas_cadastradas.click()

    def _carrega_elemento(self, xpath):
        try:
            return WebDriverWait(self._driver, 15).until(
                ec.element_to_be_clickable((By.XPATH, xpath))
            )
        except TimeoutException:
            if self._eh_pagina_erro_sistema_maximo_cadastro():
                self._driver.refresh()
                time.sleep(2)
                self._driver.back()
            else:
                raise NoSuchElementException('Limite de tempo excedido')

    def _cadastrar_nota(self, chave_nota):
        # selecionar o tipo da opção 5, Nota Fiscal ao Consumidor Eletronico NFCE
        tipo_nota = Select(
            self._carrega_elemento('//*[@id="form1:pnlTipoNota"]/tbody/tr/td[2]/select')
        )
        tipo_nota.select_by_value('5')

        chave = self._carrega_elemento('//*[@id="form1:pnlTipoNota"]/tbody/tr[2]/td[2]/input')
        chave.send_keys(chave_nota)
        print(chave_nota)
        chave.send_keys(Keys.TAB)

        time.sleep(1)

        btn_cadastrar = self._carrega_elemento('//*[@id="form1:j_id97"]')
        btn_cadastrar.click()

        self._cont_notas += 1

    def _nota_ja_cadastrada(self):
        time.sleep(1)
        try:
            message_error_cadastro = self._carrega_elemento('//*[@id="form1:msgs"]/div')
            return True
        except NoSuchElementException:
            return False

    def _verificar_cadastro(self):
        if self._nota_ja_cadastrada():
            # caso a nota já esteja cadastrada, limpa o campo da chave para inserir nova chave
            chave = self._carrega_elemento('//*[@id="form1:pnlTipoNota"]/tbody/tr[2]/td[2]/input')
            chave.clear()
            self._status = 'Falha - Nota indisponível para cadastro'

        else:
            self.cont_notas_cadastradas_sucesso += 1
            # codigo para ir para a próxima nota, após sucesso do cadastro
            # apertar botão de voltar e acessar area de cadastro no menu
            btn_voltar_sucesso = self._carrega_elemento('//*[@id="pnlLogin_body"]/table[2]/tbody/tr[1]/td/input')
            btn_voltar_sucesso.click()

            self._acessar_area_notas_cadastradas()

            self._status = 'Sucesso - Nota cadastrada no sistema'

    def _info_total_notas_cadastradas(self):
        return "Cadastrando nota {} de {} - ".format(self._handle_dados.get_ordem_nota_atual() + 1, self._qtde_notas)

    def _encerrar_sessao(self):
        print('Foram cadastradas {} notas com sucesso'.format(self.cont_notas_cadastradas_sucesso))
        self._driver.quit()


if __name__ == '__main__':
    d = SistemaNotaLegal('NFCE MES 12 2023.pdf', 2,1200)
    d.inicia(os.getenv('LOGIN'), os.getenv('PASSWORD'))
