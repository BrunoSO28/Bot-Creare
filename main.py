from PySide6.QtWidgets import QApplication, QCompleter, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar, QCheckBox, QDialog
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QSettings, QStringListModel, QUrl, Qt, QThread, Signal, QRect, QMetaObject
from PySide6.QtGui import QFont, QScreen, QIcon, QPixmap
from playwright.async_api import async_playwright
import sys
import asyncio
import os
import ctypes
from ctypes import wintypes


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

def aplicar_modo_escuro(hwnd):
    DWMWA_USE_IMMERSIVE_DARK_MODE = 20
    value = ctypes.c_int(1)
    ctypes.windll.dwmapi.DwmSetWindowAttribute(
        hwnd,
        DWMWA_USE_IMMERSIVE_DARK_MODE,
        ctypes.byref(value),
        ctypes.sizeof(value)
    )

#BOT do navegador
class PlayWrightBot(QThread):
    sinalInfo = Signal(str,str,str,str,str,str)
    sinalDownload = Signal(str, str, str)
    sinalTratativas = Signal(list)
    sinalPronto = Signal()
    sinalColunas = Signal(int)  # Novo sinal para enviar a quantidade de colunas
    sinalVideosCarregados = Signal()  # Novo sinal para quando todos os vídeos forem selecionados
    sinalLiberarVideo = Signal()
    sinalTabela = Signal(int, list)
    sinalSemAlertas = Signal(bool)
    sinalContador = Signal(int)
    sinalPedirCodigo = Signal()   # ← avisa a janela que precisa do código
    sinalLoginOk = Signal()       # ← avisa a janela que o login foi concluído
    sinalSessaoExpirada = Signal()
    sinalAlertas = Signal(int, int, int)
    sinalQrCode = Signal(bytes)
    sinalWhatsappConectado = Signal()


    def __init__(self, url):
        super().__init__()
        self.url = url
        self.loop = None
        self.pagina = None
        self.tratativas = None
        self.contador = 0
        self._video_liberado = asyncio.Event()
        self._tratativa_concluida = asyncio.Event()
        self._tratativa_concluida.set()  # começa liberado
        self._conta_recebida = asyncio.Event()
        self.email = ""
        self.senha = ""
        self.codigo = ""
        self._codigo_recebido = asyncio.Event()
        self.window_id = None
        self.cdp = None

    def receberConta(self):
        self.conta = janelaLogin()
        self.conta.sinalLogin.connect(self.iniciarConta)


    def iniciarConta(self, email, senha, codigo):
        self.email = email
        self.senha = senha
        self.codigo = codigo
        self._codigo_recebido.clear()
        if self.loop:
            self.loop.call_soon_threadsafe(self._conta_recebida.clear)
            self.loop.call_soon_threadsafe(self._conta_recebida.set)

    async def verificarSessao(self):
        try:
            campo = self.pagina.get_by_placeholder("Usuário")
            return await campo.count() > 0
        except:
            return False
    
    async def run_playwright(self):
        await self._conta_recebida.wait()  # Aguarda até que a conta seja recebida
        async with async_playwright() as pw:
            self.navegador = await pw.chromium.launch_persistent_context(
                user_data_dir="perfil_edge_bot",
                channel="msedge",
                headless=False,
                args=[
                "--window-position=-3000,0",#✅ joga a janela pra fora da tela
                "--window-size=1280,720"])

            #for pagina in self.navegador.pages:
             #   await pagina.close()

            self.pagina = await self.navegador.new_page()
            self.pagina.set_default_timeout(0)
            self.pagina2 = await self.navegador.new_page()
            self.pagina2.set_default_timeout(0)
            
            #Login na conta
            await self.pagina.goto(self.url, wait_until="commit", timeout=0)

            await self.pagina2.goto("https://web.whatsapp.com/", wait_until="commit", timeout=0)       
            
            await self.pagina2.bring_to_front()
            botaoNestaJanela = self.pagina2.get_by_role("button", name="Usar nesta janela")
            try:
                await botaoNestaJanela.wait_for(state="visible", timeout=5000)
                await botaoNestaJanela.click()
            except:
                pass
            
            qrCode = self.pagina2.get_by_role("img", name="Scan this QR code to link a")
            try:
                await qrCode.wait_for(state="visible", timeout=10000)
            except:
                pass
            if await qrCode.count() > 0:
                
                await self.pagina2.wait_for_selector(
                    'canvas[aria-label="Scan this QR code to link a device!"]',
                    state="visible",
                    timeout=30000
                )

                self.cdp = await self.navegador.new_cdp_session(self.pagina2)
                self.window_id = (await self.cdp.send("Browser.getWindowForTarget"))["windowId"]

                # Maximiza
                await self.cdp.send("Browser.setWindowBounds", {
                    "windowId": self.window_id,
                    "bounds": {"windowState": "maximized"}
                })

                await self.pagina2.bring_to_front()
                self.sinalQrCode.emit(b"")

                await qrCode.wait_for(state="hidden", timeout=120000)
                
                await self.cdp.send("Browser.setWindowBounds", {
                    "windowId": self.window_id,
                    "bounds": {"windowState": "normal", "left": -3000, "top": 0, "width": 1280, "height": 720}
                })

                self.sinalWhatsappConectado.emit()
            else:
                self.sinalWhatsappConectado.emit()
    
            await self.pagina.bring_to_front()
            # Aguarda o campo de usuário estar visível
            try:
                # Tenta múltiplas formas de localizar o campo de usuário
                campo_usuario = None

                # Método 1: Por placeholder ou label
                try:
                    campo_usuario = self.pagina.get_by_placeholder("Usuário")
                    await campo_usuario.wait_for(state="visible", timeout=5000)
                except:
                    pass
                
                # Método 2: Por role textbox
                if not campo_usuario:
                    try:
                        campo_usuario = self.pagina.get_by_role("textbox", name="Usuário")
                        await campo_usuario.wait_for(state="visible", timeout=5000)
                    except:
                        pass
                
                # Método 3: Por XPath (fallback)
                if not campo_usuario:
                    campo_usuario = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[1]')
                    await campo_usuario.wait_for(state="visible", timeout=5000)
                
                # Limpa o campo antes de preencher
                await campo_usuario.click()
                await campo_usuario.fill("")
                await self.pagina.wait_for_timeout(300)
                
                # Preenche o email
                await campo_usuario.fill(self.email)
                await self.pagina.wait_for_timeout(500)
                
                # Campo de senha
                campo_senha = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]')
                await campo_senha.click()
                await campo_senha.fill(self.senha)
                await self.pagina.wait_for_timeout(500)
                
            except Exception as e:
                print(f"Erro ao preencher campos de login: {e}")
                # Tenta método alternativo com type ao invés de fill
                try:
                    campo_usuario = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[1]')
                    await campo_usuario.click()
                    await campo_usuario.press_sequentially(self.email, delay=50)
                    
                    campo_senha = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]')
                    await campo_senha.click()
                    await campo_senha.press_sequentially(self.senha, delay=50)
                except Exception as e2:
                    print(f"Erro no método alternativo: {e2}")
            
            #await self.pagina.pause()
            await self.pagina.get_by_role("button", name="Entrar").click()
            await self.pagina.wait_for_timeout(1000)
            #await self.pagina.pause()

            campo_codigo = self.pagina.get_by_role("textbox", name="Código")
            if await campo_codigo.count() > 0:
                self.sinalPedirCodigo.emit()             # ← avisa a janela
                await self._codigo_recebido.wait()       # ← pausa até o usuário digitar
                await campo_codigo.fill(self.codigo)
                await self.pagina.get_by_role("button", name="Entrar").click()
                await self.pagina.wait_for_timeout(1000)

            self.sinalLoginOk.emit()  # ← login concluído, janela pode fechar


            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").click()

            await self.pagina.get_by_role("columnheader", name="Data do Alarme Activate to").click()
            #await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-header/div/div[2]/div/div[3]/p-checkbox/div/div[2]/span").click()
            #await self.pagina.pause()
                                 
            await asyncio.gather(
            self.monitorarSessao(),
            self.loopPrincipal()
        )
            await self.navegador.close()
        
    #Coletar informações do Alerta
    async def loopPrincipal(self):
        while not self.isInterruptionRequested():
            try:
                await self._tratativa_concluida.wait()
                try:
                    await self.pagina.wait_for_selector(
                        'xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-body/p-table/div/div/table/tbody/tr[1]/td[10]/span/button',
                        state="detached",  # ← espera o elemento ser removido do DOM
                        timeout=3000
                    )
                except:
                    pass                              
                try:
                    tratativa = self.pagina.locator('xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-body/p-table/div/div/table/tbody/tr[1]/td[10]/span/button')
                except:
                    pass
                if not tratativa:
                    try:
                        tratativa = self.pagina.get_by_role("button", name="Inserir Tratativa")
                    except:
                        pass
                if not tratativa:
                    tratativa = self.pagina.locator('button[ng-reflect-ngb-tooltip="Inserir Tratativa"]')
                
                quantidade = await tratativa.count()
                print(f">>> Quantidade de alertas: {quantidade}")  
                if quantidade == 0:
                    self.sinalSemAlertas.emit(True)
                    print(">>> Sem alertas, aguardando...")
                    await asyncio.sleep(5)
                    continue
                
                habilitado = await tratativa.is_enabled()
                print(f">>> Alerta habilitado: {habilitado}")
                
                if not habilitado:
                    await asyncio.sleep(2)
                    continue
                
                self._tratativa_concluida.clear()
                self.sinalSemAlertas.emit(False)
                self.dataHora = await self.pagina.locator('td[ng-reflect-ng-switch="datetime"] span[tooltipclass="diff"]').first.inner_text()
                await self.coletarQuantidadeAlertas()
                #await self.pagina.pause()
                await tratativa.click()
                
                self.alerta = await self.pagina.locator("step-infos label:has-text('Tipo de Alerta') + p-dropdown label.ui-dropdown-label").inner_text()

                self.placa = await self.pagina.locator("step-infos label:has-text('Placa / Prefixo') + p").inner_text()

                self.empresa = await self.pagina.locator("step-infos label:has-text('Empresa') + p").inner_text()

                self.filial = await self.pagina.locator("step-infos label:has-text('Filial') + p").inner_text()

                self.motorista = await self.pagina.locator("step-infos label:has-text('Motorista') + p").inner_text()

                print(self.alerta, self.placa, self.empresa, self.filial, self.motorista, self.dataHora)

                #Download do vídeo - usa .first para pegar o primeiro elemento quando há múltiplos
                await self.pagina.locator(".playMovie").first.dblclick()
                await self.pagina.wait_for_timeout(1000)

                video1 = self.pagina.locator("xpath=/html/body/dinamic-dialog/div/div/ng-component/div/ul/li[1]/div/div/app-download-button/button/i")

                video2 = self.pagina.locator("li:nth-child(2) > .video-wrapper > .download-container > app-download-button > .download-button")

                video5 = self.pagina.locator("li:nth-child(5) > .video-wrapper > .download-container > app-download-button > .download-button")

                self.diretoriofinal1 = ""
                self.diretoriofinal2 = ""
                self.diretoriofinal5 = ""

                if self.alerta == "Risco de colisão" or self.alerta == "Pedestre":
                    try:
                        if await video2.count() > 0:
                            async with self.pagina.expect_download() as downloadVideo2:
                                diretorio = os.getcwd()
                                await video2.click()
                                download2 = await downloadVideo2.value

                                self.diretoriofinal2 = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera2.mp4")

                                await download2.save_as(self.diretoriofinal2)
                                
                        else:
                            print(">>> Vídeo 2 não encontrado para download")
                    except Exception as e:
                        print(f">>> Vídeo não disponível para download: {e}")
                    self.sinalDownload.emit(self.diretoriofinal2,"","")
                else:
                    try:
                        if await video1.count() > 0:
                            async with self.pagina.expect_download() as downloadVideo1:
                                diretorio = os.getcwd()
                                await video1.click()
                                download1 = await downloadVideo1.value

                                self.diretoriofinal1 = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera1.mp4")

                                await download1.save_as(self.diretoriofinal1)
                        else:
                            print(">>> Vídeo 1 não encontrado para download")
                    except Exception as e:
                        print(f">>> Vídeo não disponível para download: {e}")

                    try:                
                        if await video5.count() > 0:
                            async with self.pagina.expect_download() as downloadVideo5:
                                diretorio = os.getcwd()
                                await video5.click()
                                download5 = await downloadVideo5.value

                                self.diretoriofinal5 = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera5.mp4")

                                await download5.save_as(self.diretoriofinal5)
                        else:
                            print(">>> Vídeo 5 não encontrado para download")
                    except Exception as e:
                        print(f">>> Vídeo não disponível para download: {e}")
                self.sinalDownload.emit(self.diretoriofinal1 or "", self.diretoriofinal5 or "","")

                self.sinalInfo.emit(self.alerta,self.placa,self.empresa,self.filial,self.motorista, self.dataHora)
                
                await self.pagina.mouse.click(400, 10)

                # Coleta os vídeos do alerta e clica em cada um
                videosAlerta = self.pagina.locator('ul[style="margin-bottom: 20px;"] li#itemToHistory')
                total = await videosAlerta.count()  # Adiciona await aqui
                print(f">>> Total de vídeos do alerta: {total}")
                
                for i in range(total):
                    await videosAlerta.nth(i).click()  # Adiciona await aqui também
                    await self.pagina.wait_for_timeout(300)  # Aguarda um pouco entre os cliques
                
                print(f">>> Todos os {total} vídeos foram selecionados")
                self.sinalVideosCarregados.emit()  # Emite sinal indicando que todos os vídeos foram carregados
                
                # Conta as linhas da tabela
                self.colunas = await self.pagina.locator('table:has(th:text("Tipo Alerta")) tbody tr').count()
                print(f">>> Quantidade de colunas: {self.colunas}")
                self.sinalColunas.emit(self.colunas)  # Emite o sinal com a quantidade de colunas

                self.tabelaHistorico = self.pagina.locator('table.alarm-history tbody tr.ng-star-inserted')
                self.total = await self.tabelaHistorico.count()
                print(f'>>> Total: {self.total}')

                dados_tabela = []
                for i in range(self.total):
                    self.linha = self.tabelaHistorico.nth(i)
                    self.col1 = await self.linha.locator("td:nth-child(1) span").inner_text()
                    self.col2 = await self.linha.locator("td:nth-child(2)").inner_text()
                    self.col3 = await self.linha.locator("td:nth-child(3)").inner_text()
                    dados_tabela.append((self.col1, self.col2, self.col3))
                    print(f'col1: {self.col1} - col2: {self.col2} - col3: {self.col3}')

                self.sinalTabela.emit(self.total, dados_tabela)

                await self.pagina.get_by_role("button", name="Aplicar gestão").click()
                await self.pagina.wait_for_timeout(500)
                await self.pagina.get_by_role("button", name="Aplicar gestão").click()
                #await self.pagina.pause()

                self.sinalPronto.emit()
                
                self.contador += 1
                self.sinalContador.emit(self.contador)
                # Aguarda um pouco antes de verificar o próximo alerta
                await asyncio.sleep(1)
                # Libera para próximo alerta
            except Exception as e:
                print(f">>> ERRO no loop principal: {e}")
                self._tratativa_concluida.set()  # nunca trava o loop
                await asyncio.sleep(2)
    
    async def monitorarSessao(self):
        """Roda em paralelo, detecta expiração em qualquer momento."""
        while not self.isInterruptionRequested():
            try:
                campo = self.pagina.get_by_placeholder("Usuário")
                if await campo.count() > 0:
                    print(">>> Sessão expirada detectada pelo monitor")
                    
                    # Pausa o loop principal
                    self._tratativa_concluida.clear()
                    self.sinalSessaoExpirada.emit()
                    
                    # Aguarda credenciais
                    self._conta_recebida.clear()
                    await self._conta_recebida.wait()
                    
                    # Faz o relogin
                    await self.pagina.get_by_placeholder("Usuário").fill(self.email)
                    campo_senha = self.pagina.locator(
                        'xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]'
                    )
                    await campo_senha.fill(self.senha)
                    await self.pagina.get_by_role("button", name="Entrar").click()
                    await self.pagina.wait_for_timeout(1000)

                    campo_codigo = self.pagina.get_by_role("textbox", name="Código")
                    if await campo_codigo.count() > 0:
                        self.sinalPedirCodigo.emit()
                        self._codigo_recebido.clear()
                        await self._codigo_recebido.wait()
                        await campo_codigo.fill(self.codigo)
                        await self.pagina.get_by_role("button", name="Entrar").click()
                        await self.pagina.wait_for_timeout(1000)

                    self.sinalLoginOk.emit()
                    print(">>> Relogin concluído pelo monitor")

                    try:
                        await self.pagina.wait_for_load_state("networkidle", timeout=10000)
                    except:
                        await self.pagina.wait_for_timeout(2000)

                    try:
                        toggle = self.pagina.locator(
                            ".theme-switch.ng-star-inserted > .switch > .slider"
                        )
                        await toggle.click()
                        await self.pagina.wait_for_timeout(500)
                        #await toggle.click()
                        #await self.pagina.wait_for_timeout(500)
                    except Exception as e:
                        print(f">>> ERRO ao clicar no toggle: {e}")

                    # Ordena pela data do alarme
                    try:
                        await self.pagina.get_by_role(
                            "columnheader", name="Data do Alarme Activate to"
                        ).click()
                        await self.pagina.wait_for_timeout(500)
                    except Exception as e:
                        print(f">>> ERRO ao clicar no cabeçalho: {e}")

                    # Libera o loop principal para recomeçar
                    self._tratativa_concluida.set()

            except Exception as e:
                print(f">>> ERRO monitorarSessao: {e}")

            await asyncio.sleep(2)  # verifica a cada 2 segundos
    
    #Rodando o navegador em segundo plano        
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_playwright())

    def clickSelecao(self, valor: str):
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.selecaoTratativa(valor), self.loop)

    async def coletarTratativas(self):
        try:
            await self.pagina.wait_for_selector(
                "treatment-step-three select",
                state="attached",
                timeout=10000
            )
            tratativas = await self.pagina.locator(
                "treatment-step-three select option"
            ).all_inner_texts()

            tratativas = [t.strip() for t in tratativas if t.strip() and t != "Selecione uma Tratativa"]
            print(">>> Opções encontradas:", tratativas)
            self.sinalTratativas.emit(tratativas)

        except Exception as e:
            print(">>> ERRO coletarTratativas:", e)

    def enviarCodigo(self, codigo: str):
        self.codigo = codigo
        if self.loop:
            self.loop.call_soon_threadsafe(self._codigo_recebido.set)

    async def selecaoTratativa(self, valor: str):
        print(">>> selecaoTratativa chamado com:", valor)
        try:
            # 1. Abre o dropdown visual
            await self.pagina.locator("treatment-step-three p-dropdown").click()
            await self.pagina.wait_for_timeout(500)

            # 2. Aguarda o painel flutuante aparecer
            await self.pagina.wait_for_selector(
                "p-dropdownpanel li, .ui-dropdown-item, .ui-dropdown-items li",
                state="visible",
                timeout=5000
            )
            
            # 3. Clica na opção selecionada na UI usando correspondência exata
            # Busca todos os itens e filtra pelo texto exato
            items = await self.pagina.locator(".ui-dropdown-item").all()
            for item in items:
                texto = await item.inner_text()
                if texto.strip() == valor:
                    await item.click()
                    print(f">>> Item clicado: {valor}")
                    break

            match valor:
                case "Rádio":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Condutor identificado utilizando rádio durante a condução em rodovia, ocasionando desvio de atenção e comprometendo a segurança viária. Reforçar a orientação para manter foco total na condução e utilizar o equipamento somente quando estritamente necessário e em condições seguras.")
                case "Bocejo Delay":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Condutor identificado bocejando de forma recorrente durante a condução, caracterizando indícios de sonolência.")
                case "Comer e Beber ao Volante":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Condutor identificado realizando alimentação durante a condução, o que compromete a atenção e o controle do veículo. Reforçar as diretrizes de segurança operacional")
                case "Sonolência Delay":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Motorista apresentando sonolência N1. Realizar a parada de 30 minutos.")
                case "Invalidar - Teste - Manutenção":
                    await self.pagina.locator("textarea").fill("Teste - Manuntenção.")
                case "N1 - Orientar Parada 30 min":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Motorista apresentando sonolência N1. Realizar a parada de 30 minutos.")
                case "Bocejo":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Condutor identificado bocejando de forma recorrente durante a condução, caracterizando indícios de sonolência.")
                case "N2 - Orientar Parada 60 min":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Motorista apresentando sonolência N2. Realizar a parada de 60 minutos.")
                case "Atenção":
                    await self.pagina.locator("textarea").fill("Reportado para a operação. Condutor demonstrando desatenção ao ambiente de condução, desviando o foco da direção. Reforçar orientação sobre direção defensiva e foco total na condução.")
            
            await self.pagina.wait_for_timeout(300)
            print(">>> Selecionado com sucesso:", valor)

        except Exception as e:
            print(">>> ERRO selecaoTratativa:", e)

    async def preencherTextoConduta(self, tipo_conduta: str):
        """Preenche o textarea com o texto específico da conduta"""
        print(f">>> preencherTextoConduta chamado com: {tipo_conduta}")
        try:
            texto = ""
            if tipo_conduta == "Cigarro":
                texto = "Reportado para a operação. Condutor identificado fumando durante a condução, comprometendo a segurança e contrariando as normas de conduta estabelecidas. Aplicar política de consequência conforme diretrizes da empresa e registrar pontos no sistema D-OLHO."
            elif tipo_conduta == "Celular":
                texto = "Reportado para a operação. Condutor identificado utilizando aparelho celular durante a condução, caracterizando grave infração de trânsito e comprometendo a segurança viária. Aplicar política de consequência conforme diretrizes da empresa e registrar pontos no sistema D-OLHO."
            elif tipo_conduta == "Câmera Manipulada":
                texto = "Reportado para a operação. Condutor identificado manipulando ou obstruindo a câmera de monitoramento durante a condução, caracterizando violação das normas de segurança e tentativa de burlar o sistema de monitoramento. Aplicar política de consequência conforme diretrizes da empresa e registrar pontos no sistema D-OLHO."
            
            await self.pagina.locator("textarea").fill(texto)
            await self.pagina.wait_for_timeout(300)
            print(f">>> Texto de conduta preenchido com sucesso: {tipo_conduta}")
        except Exception as e:
            print(f">>> ERRO preencherTextoConduta: {e}")

    async def preencherTextoAusencia(self, tipo_ausencia: str):
        """Preenche o textarea com o texto específico da ausência"""
        print(f">>> preencherTextoAusencia chamado com: {tipo_ausencia}")
        try:
            texto = ""
            if tipo_ausencia == "Câmera Desajustada":
                texto = "Solicitação de ajuste técnico. Câmera de monitoramento identificada com desalinhamento ou posicionamento inadequado, prejudicando a captura correta das imagens. Necessário ajuste pela equipe de Gestão de Equipamentos CCI para garantir o funcionamento adequado do sistema de monitoramento."
            elif tipo_ausencia == "Câmera Escura":
                texto = "Solicitação de ajuste técnico. Câmera de monitoramento apresentando imagens escuras ou com baixa luminosidade, impossibilitando a análise adequada. Necessário verificação e ajuste pela equipe de Gestão de Equipamentos CCI para correção do problema de iluminação."
            elif tipo_ausencia == "Câmera com Defeito":
                texto = "Solicitação de manutenção técnica. Câmera de monitoramento apresentando defeito técnico, impossibilitando o registro adequado das imagens. Necessário intervenção imediata da equipe de Gestão de Equipamentos CCI para reparo ou substituição do equipamento."
            
            await self.pagina.locator("textarea").fill(texto)
            await self.pagina.wait_for_timeout(300)
            print(f">>> Texto de ausência preenchido com sucesso: {tipo_ausencia}")
        except Exception as e:
            print(f">>> ERRO preencherTextoAusencia: {e}")

    def clickConduta(self, tipo_conduta: str):
        """Método chamado quando um botão de conduta é clicado"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.preencherTextoConduta(tipo_conduta), self.loop
            )

    def clickAusencia(self, tipo_ausencia: str):
        """Método chamado quando um botão de ausência é clicado"""
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.preencherTextoAusencia(tipo_ausencia), self.loop
            )
    async def alertaMonitorado(self):
        try:
            await self.pagina.get_by_role("button", name="Finalizar Tratativa").click()
            self._video_liberado.clear()
            self.sinalLiberarVideo.emit()
            await asyncio.wait_for(self._video_liberado.wait(), timeout=5.0)

            await self.pagina.wait_for_timeout(500)
            await self.pagina.mouse.click(400, 10)
            #await self.pagina.wait_for_timeout(500)
            #await self.pagina.get_by_role("button", name="Concluir").click()
            #await self.pagina.wait_for_timeout(500)

            await self.pagina.bring_to_front()
            await self.pagina.wait_for_timeout(500)
            await self.pagina.keyboard.press("Enter")
            await self.pagina.mouse.click(400, 10)
            await self.pagina.wait_for_timeout(500)
            botaoConcluir = self.pagina.get_by_role("button", name="Concluir")
            if await botaoConcluir.count() > 0 :
                await botaoConcluir.click()
            #await self.pagina.wait_for_timeout(300)
            #pyautogui.hotkey('Enter')
            await self.pagina.wait_for_timeout(500)
            await self.pagina.keyboard.press("Enter")

            await self.pagina.wait_for_timeout(3000)
            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()
            await self.pagina.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            print(f">>>ERRO {e}")
        finally:
            self._tratativa_concluida.set()
        
        print(">>> Tratativa Monitorada")

    async def subirVideoZap(self):
        try:
            await self.pagina2.bring_to_front()
            await self.pagina2.wait_for_timeout(1000)
            try:
                anexar = self.pagina2.get_by_role("button", name="Anexar")
                await anexar.wait_for(state="visible", timeout=5000)
            except:
                pass
            if not anexar:
                try:
                    anexar = self.pagina2.locator('xpath=//*[@id="main"]/footer/div[1]/div/span/div/div/div/div[1]/div/span/button/div/div/div[1]/span')
                    await anexar.wait_for(state="visible", timeout=5000)
                except:
                    pass
            try:
                await anexar.scroll_into_view_if_needed()
                await anexar.wait_for(state="visible", timeout=3000)
                await anexar.click()
            except:
                pass
            await self.pagina2.wait_for_timeout(1000)
            async with self.pagina2.expect_file_chooser() as fc_info:
                await self.pagina2.click('button[aria-label="Fotos e vídeos"]')
            
            file_chooser = await fc_info.value
            await file_chooser.set_files(self.diretoriofinal1)

            await self.pagina2.wait_for_timeout(1000)            
            await self.pagina2.get_by_test_id("media-caption-input-container").get_by_role("paragraph").fill(self.reportOperacao)
            await self.pagina2.wait_for_timeout(500)
            await self.pagina2.get_by_role("button", name="Enviar 1 item selecionado").click()
            await self.pagina2.wait_for_timeout(1000)
            await self.pagina2.keyboard.press("Escape")
            '''await self.pagina2.get_by_role("button", name="End icon button").click()
            await self.pagina2.wait_for_timeout(1000)
            await self.pagina2.get_by_text("Alerta de Fadiga - África").click()
            await self.pagina2.wait_for_timeout(1000)'''
        except Exception as e:
            import traceback
            print(f">>> ERRO subirVideoZap: {e}")
            traceback.print_exc()
        
    async def reportarOperacao(self):
        try:
            await self.pagina.get_by_role("button", name="Finalizar Tratativa").click()
            self._video_liberado.clear()
            self.sinalLiberarVideo.emit()
            await asyncio.wait_for(self._video_liberado.wait(), timeout=5.0)

            await self.pagina2.bring_to_front()
            botaoNestaJanela = self.pagina2.get_by_role("button", name="Usar nesta janela")
            try:
                await botaoNestaJanela.wait_for(state="visible", timeout=5000)
                await botaoNestaJanela.click()
            except:
                pass

            await self.pagina.wait_for_timeout(300)
            self.reportOperacao = await self.pagina.locator('div[style="width: 100%;"]').inner_text()

            print(self.reportOperacao)

            match self.filial: 
                case "Distribuição":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - distribuição")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_text("Alerta de Fadiga - Distribui").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "Costa Rica" | "Costa Rica Leves":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - costa rica")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_test_id("cell-frame-container").get_by_text("Alerta de Fadiga - Cost").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "Alto Taquari":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - alto taquari")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_test_id("cell-frame-container").get_by_text("Alerta de Fadiga - Alto").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "Cenibra NE" | "Cenibra BO" | "Cenibra SB Agregados":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - cenibra")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_text("Alerta de Fadiga - Cenibra").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "Catalão":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - cmoc")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_text("Alerta de Fadiga - CMOC").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "Químico 1 Felipe" | "Automotivo Fabiano" | "Automotivo Felipe" | "Automotivo Alvaro" | "Químico 2 Fabiano" | "Automotivo Kamilla":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - rodoviario")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_test_id("cell-frame-container").get_by_text("Alerta de Fadiga - Rodoviário").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "Transporte de Madeira - Expresso/RS":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - cmpc")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_text("Alerta de Fadiga - CMPC").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()
                case "GRID 1" | "GRID 2" | "GRID 3":
                    await self.pagina2.get_by_role("textbox", name="Pesquisar ou começar uma nova").fill("alerta de fadiga - bracell")
                    await self.pagina2.wait_for_timeout(500)
                    await self.pagina2.get_by_text("Alerta de Fadiga - Bracell").click()
                    await self.pagina2.wait_for_timeout(500)
                    await self.subirVideoZap()

            await self.pagina.bring_to_front()
            await self.pagina.wait_for_timeout(500)
            await self.pagina.mouse.click(400, 10)
            await self.pagina.wait_for_timeout(500)
            await self.pagina.mouse.click(400, 10)
            botaoConcluir = self.pagina.get_by_role("button", name="Concluir")
            if await botaoConcluir.count > 0:
                await self.pagina.wait_for_timeout(300)
                await botaoConcluir.click()
             
            print(">>> Aguardando tabela atualizar...")
            await self.pagina.wait_for_timeout(3000)
            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()
            await self.pagina.wait_for_load_state("networkidle", timeout=5000)
        except Exception as e:
            print(f">>> ERRO {e}")
        finally:
            self._tratativa_concluida.set()

    def clickMonitorado(self):
        if self.loop:
            
            asyncio.run_coroutine_threadsafe(self.alertaMonitorado(), self.loop)

    def clickReportarOperacao(self):
        if self.loop:
            
            asyncio.run_coroutine_threadsafe(self.reportarOperacao(), self.loop)

    async def invalidarAlerta(self):
        """Invalida o alerta atual voltando e selecionando 'Alerta invalidado'"""
        if self._tratativa_concluida.is_set():
            print("Invalidação ignorada, nada sendo processado")
            return
        try:
            print(">>> Iniciando invalidação do alerta")
              # Bloqueia o loop principal
            
            self._video_liberado.clear()
            self.sinalLiberarVideo.emit()
            await asyncio.wait_for(self._video_liberado.wait(), timeout=5.0)
            # Primeiro clique no botão Voltar
            botao_voltar = self.pagina.get_by_role("button", name="Voltar")
            await botao_voltar.click()
            await self.pagina.wait_for_timeout(100)
            print(">>> Primeiro 'Voltar' clicado")
            
            # Segundo clique no botão Voltar
            await botao_voltar.click()
            await self.pagina.wait_for_timeout(300)
            print(">>> Segundo 'Voltar' clicado")
            
            # Aguarda a página carregar
            await self.pagina.wait_for_timeout(300)
            
            # Seleciona o dropdown que NÃO está desabilitado
            dropdown_selector = ".ui-dropdown:not(.ui-state-disabled)"
            await self.pagina.wait_for_selector(dropdown_selector, state="visible", timeout=5000)
            
            # Clica no dropdown correto
            await self.pagina.locator(dropdown_selector).first.click()
            await self.pagina.wait_for_timeout(300)
            print(">>> Dropdown aberto")
            
            # Aguarda as opções do dropdown aparecerem
            await self.pagina.wait_for_selector(
                "p-dropdownpanel li, .ui-dropdown-item, .ui-dropdown-items li",
                state="visible",
                timeout=5000
            )
            
            # Seleciona "Alerta invalidado"
            await self.pagina.locator("li:has-text('Alerta invalidado')").click()
            await self.pagina.wait_for_timeout(300)
            print(">>> 'Alerta invalidado' selecionado")

            await self.pagina.get_by_role("button", name="Ok").click()
            await self.pagina.wait_for_timeout(300)

            await self.pagina.get_by_role("button", name="Finalizar").click()
            await self.pagina.wait_for_timeout(300)

            await self.pagina.get_by_role("button", name="Finalizar").nth(1).click()
            await self.pagina.wait_for_timeout(500)

            await self.pagina.bring_to_front()
            await self.pagina.mouse.click(400,10)
            await self.pagina.wait_for_timeout(700)
            await self.pagina.mouse.click(400,10)
            await self.pagina.wait_for_timeout(700)
            await self.pagina.mouse.click(400,10)
            await self.pagina.wait_for_timeout(700)
            await self.pagina.keyboard.press("Enter")
            await self.pagina.wait_for_timeout(700)
            
            print(">>> Aguardando tabela atualizar...")
    
            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()
            await self.pagina.wait_for_load_state("networkidle", timeout=5000)           
            
            # Emite sinal de tratativa finalizada para apagar o vídeo
            print(">>> Invalidação concluída com sucesso - Vídeo será apagado")
            
        except Exception as e:
            print(f">>> ERRO invalidarAlerta: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Sempre libera a flag, mesmo em caso de erro
            self._tratativa_concluida.set()
            print(">>> Flag processando_alerta liberada")

    def clickInvalidar(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.invalidarAlerta(), self.loop)

    def receberCheck(self):
        self.check = janelaPrincipal()
        self.check.sinalCheck.connect(self.escolherCheck)
    
    def clickCheck(self, valores):
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.escolherCheck(valores), self.loop
            )
    async def escolherCheck(self, estados: dict):
        seletores = {
            "Alto":  self.pagina.locator('.box-risk-chart[title="Filtrar Alertas de Alto Risco"] .fa.no-filter-icon'),
            "Médio": self.pagina.locator('.box-risk-chart[title="Filtrar Alertas de Médio Risco"] .fa.no-filter-icon'),
            "Baixo": self.pagina.locator('.box-risk-chart[title="Filtrar Alertas de Baixo Risco"] .fa.no-filter-icon'),
        }

        for nivel, deve_estar_marcado in estados.items():
            try:
                el = seletores[nivel]
                if await el.count() == 0:
                    print(f">>> Seletor '{nivel}' não encontrado na página")
                    continue

                classe = await el.get_attribute("class") or ""
                esta_marcado = "fa-check-square-o" in classe

                if deve_estar_marcado and not esta_marcado:
                    if el.is_visible():
                        await el.click()
                    print(f">>> {nivel} marcado")
                elif not deve_estar_marcado and esta_marcado:
                    if el.is_visible():
                        await el.click()
                    print(f">>> {nivel} desmarcado")
                else:
                    print(f">>> {nivel} já está no estado correto")

            except Exception as e:
                print(f">>> ERRO escolherCheck [{nivel}]: {e}")
            
    async def coletarQuantidadeAlertas(self):
        try:
            alto  = await self.pagina.locator('.box-risk-chart[title="Filtrar Alertas de Alto Risco"] focus-donut-chart').get_attribute("ng-reflect-value")
            medio = await self.pagina.locator('.box-risk-chart[title="Filtrar Alertas de Médio Risco"] focus-donut-chart').get_attribute("ng-reflect-value")
            baixo = await self.pagina.locator('.box-risk-chart[title="Filtrar Alertas de Baixo Risco"] focus-donut-chart').get_attribute("ng-reflect-value")

            print(f">>> Alto: {alto} | Médio: {medio} | Baixo: {baixo}")
            self.sinalAlertas.emit(int(alto or 0), int(medio or 0), int(baixo or 0))
        except Exception as e:
            print(f">>> ERRO coletarQuantidadeAlertas: {e}")        

class janelaLogin(QMainWindow):
    sinalLogin = Signal(str, str, str)
    sinalCodigo = Signal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - BotCreare")
        self.setWindowIcon(QIcon(resource_path("icone_creare.ico")))
        janelaPrincipal.ajustarJanelaAoMonitor(self, largura_pct=30, altura_pct=40)

        self.settings = QSettings("MinhaApp", "RevisaoVideo")

        self.caixaLogin = QWidget()
        self.setCentralWidget(self.caixaLogin)
        raiz = QVBoxLayout(self.caixaLogin)

        info = QWidget()
        layoutInfo = QVBoxLayout(info)
        layoutInfo.setContentsMargins(14, 40, 14, 10)
        layoutInfo.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        self.labelConta = QLabel("Entre com sua conta CREARE")
        self.labelConta.setFont(QFont("Average Sans", 12, QFont.Bold))
        self.labelConta.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        login = QWidget()
        layoutLogin = QVBoxLayout(login)
        layoutLogin.setContentsMargins(14, 10, 10, 10)
        layoutLogin.setSpacing(20)
        layoutLogin.setAlignment(Qt.AlignCenter | Qt.AlignTop)

        self.inputEmail = QLineEdit()
        self.inputEmail.setFixedSize(300, 25)
        self.inputEmail.setAlignment(Qt.AlignCenter)
        self.inputEmail.setPlaceholderText("Digite seu email")

        self.inputSenha = QLineEdit()
        self.inputSenha.setFixedSize(300, 25)
        self.inputSenha.setAlignment(Qt.AlignCenter)
        self.inputSenha.setPlaceholderText("Digite sua senha")
        self.inputSenha.setEchoMode(QLineEdit.Password)

        self.labelCodigo = QLabel("Código de autenticação recebido no email:")
        self.labelCodigo.setAlignment(Qt.AlignCenter)
        self.labelCodigo.hide()

        self.inputCodigo = QLineEdit()
        self.inputCodigo.setFixedSize(300, 25)
        self.inputCodigo.setAlignment(Qt.AlignCenter)
        self.inputCodigo.setPlaceholderText("Digite o código de autenticação")
        self.inputCodigo.hide()

        self.btnEntrar = QPushButton("Entrar")
        self.btnEntrar.setFixedSize(300, 25)
        self.btnEntrar.clicked.connect(self.submitLogin)

        self.labelCR = QLabel("Desenvolvido por Bruno Oliveira")
        self.labelCR.setAlignment(Qt.AlignCenter)
        self.labelCR.setFont(QFont("Average Sans"))
        self.labelCR.setStyleSheet("color: gray;")

        layoutInfo.addWidget(self.labelConta)
        layoutLogin.addWidget(self.inputEmail)
        layoutLogin.addWidget(self.inputSenha)
        layoutLogin.addWidget(self.labelCodigo)
        layoutLogin.addWidget(self.inputCodigo)
        layoutLogin.addWidget(self.btnEntrar)
        layoutLogin.addWidget(self.labelCR)

        raiz.addWidget(info)
        raiz.addWidget(login)

        self.configurarAutocomplete()
        self.carregarUltimoLogin()

    def mostrarCampoCodigo(self):   # ← deve estar aqui, dentro da classe
        self.labelCodigo.show()
        self.inputCodigo.show()
        self.inputCodigo.setEnabled(True)
        self.btnEntrar.setEnabled(True)
        self.btnEntrar.setText("Confirmar código")
        self.btnEntrar.clicked.disconnect()
        self.btnEntrar.clicked.connect(self.submitCodigo)
        self.inputCodigo.setFocus()

    def submitCodigo(self):
        codigo = self.inputCodigo.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Erro", "Por favor, digite o código de autenticação.")
            return
        # Envia o código para o bot continuar
        self.sinalCodigo.emit(codigo)
        self.btnEntrar.setEnabled(True)
        self.btnEntrar.setText("Aguardando...")

    def submitLogin(self):
        email = self.inputEmail.text().strip()
        senha = self.inputSenha.text().strip()

        if not email or not senha:
            QMessageBox.warning(self, "Erro de Login", "Por favor, preencha email e senha.")
            return

        self.salvarConta(email, senha)
        self.sinalLogin.emit(email, senha, "")
        self.btnEntrar.setEnabled(False)
        self.btnEntrar.setText("Entrando...")  # feedback visual enquanto aguarda
    
    def configurarAutocomplete(self):
        contas = self.settings.value("contas", {}) or {}

        self.modelo = QStringListModel(list(contas.keys()))
        self.completer = QCompleter(self.modelo, self)
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)  # filtra em qualquer parte do email
        self.inputEmail.setCompleter(self.completer)

        # Ao ativar uma sugestão, preenche a senha automaticamente
        self.completer.activated.connect(self.preencherSenhaPorEmail)
        # Ao sair do campo também tenta preencher
        self.inputEmail.editingFinished.connect(
            lambda: self.preencherSenhaPorEmail(self.inputEmail.text())
        )

    def preencherSenhaPorEmail(self, email: str):
        contas = self.settings.value("contas", {}) or {}
        if email in contas:
            self.inputSenha.setText(contas[email])

    def carregarUltimoLogin(self):
        ultimo = self.settings.value("ultimo_login", "")
        if ultimo:
            self.inputEmail.setText(ultimo)
            self.preencherSenhaPorEmail(ultimo)

    def salvarConta(self, email: str, senha: str):
        contas = self.settings.value("contas", {}) or {}
        contas[email] = senha
        self.settings.setValue("contas", contas)
        self.settings.setValue("ultimo_login", email)

        # Atualiza o autocomplete com o novo email
        self.modelo.setStringList(list(contas.keys()))


class janelaPrincipal(QMainWindow):
    sinalCheck = Signal(str)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BotCreare")
        self.setWindowIcon(QIcon(resource_path("icone_creare.ico")))
        self.video_atual = None
        self.videos = {}
        self.janelaQr = None

        # Janela mais alta e menos larga: 70% largura, 90% altura
        self.ajustarJanelaAoMonitor(largura_pct=70, altura_pct=90)
        
        # ── Widget central ──────────────────────────────────────────────────
        central = QWidget()
        self.setCentralWidget(central)

        raiz = QHBoxLayout(central)
        raiz.setContentsMargins(12, 12, 12, 12)
        raiz.setSpacing(12)

        # ── COLUNA ESQUERDA  (espaço para tabela futura) ────────────────────
        self.painelTabela = QWidget()
        self.painelTabela.setObjectName("painelTabela")
        self.painelTabela.setStyleSheet(
            "#painelTabela { border: 1px dashed #444; border-radius: 6px; }"
        )
        self.painelTabela.setMinimumWidth(260)
        self.painelTabela.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.labelTabela = QLabel("Histórico de Alertas", self.painelTabela)
        self.labelTabela.setAlignment(Qt.AlignCenter)
        self.labelTabela.setStyleSheet("font-size: 13px;")

        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Tipo Alerta", "Quando", "Tratativa"])
        # Cabeçalho estica para preencher o espaço
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Não permite edição pelo usuário
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

        # Seleciona a linha inteira ao clicar
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)

        self.layoutTabela = QVBoxLayout(self.painelTabela)
        self.layoutTabela.addWidget(self.labelTabela)
        self.layoutTabela.addWidget(self.tabela)

        raiz.addWidget(self.painelTabela, stretch=3)

        # ── COLUNA CENTRAL  (vídeo + controles + ações) ─────────────────────
        colCentro = QWidget()
        layoutCentro = QVBoxLayout(colCentro)
        layoutCentro.setContentsMargins(0, 0, 0, 0)
        layoutCentro.setSpacing(8)
        layoutCentro.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Status
        self.loadingBar = QProgressBar()
        self.loadingBar.setFixedHeight(12)  
        self.loadingBar.setRange(0, 0)  # modo indeterminado = animação infinita
        self.loadingBar.setTextVisible(False)
        self.loadingBar.setFixedHeight(4)
        self.loadingBar.hide()
        layoutCentro.addWidget(self.loadingBar)

        self.loadingWidget = QLabel("Aguardando alertas...")
        self.loadingWidget.setAlignment(Qt.AlignCenter)
        self.loadingWidget.setFont(QFont("Arial", 11))
        self.loadingWidget.setStyleSheet("color: #888; padding: 8px;")
        self.loadingWidget.hide()
        layoutCentro.addWidget(self.loadingWidget)  

        # Seletor de vídeos
        self.seletorVideo = QComboBox()
        self.seletorVideo.addItem("Câmera 1")
        self.seletorVideo.addItem("Câmera 2")
        self.seletorVideo.addItem("Câmera 3")
        self.seletorVideo.currentTextChanged.connect(self.trocarVideo)
        layoutCentro.addWidget(self.seletorVideo)

        # Vídeo – maior e proporcional
        self.caixaVideo = QVideoWidget()
        self.caixaVideo.setMinimumSize(520, 400)
        self.caixaVideo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layoutCentro.addWidget(self.caixaVideo, stretch=1)

        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.caixaVideo)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)

        # Contador de visualizações
        self.labelColunas = QLabel()
        self.labelColunas.setAlignment(Qt.AlignCenter)
        self.labelColunas.setFont(QFont("Arial", 10, QFont.Bold))
        self.labelColunas.setStyleSheet("color: #0088ff; padding: 2px;")
        layoutCentro.addWidget(self.labelColunas)

        # Controles de reprodução
        self.layoutControles = QHBoxLayout()
        self.layoutControles.setSpacing(6)
        self.layoutControles.setAlignment(Qt.AlignHCenter)

        fonte_p = QFont("Arial", 9)
        btnPlay  = QPushButton("▶️")
        btnPause = QPushButton("⏸️")
        btnNormalSpeed = QPushButton("1X")
        btnSpeed = QPushButton("2X")

        for btn in [btnPlay, btnPause, btnNormalSpeed, btnSpeed]:
            btn.setFont(fonte_p)
            btn.setFixedSize(34, 30)
        
        btnNormalSpeed.clicked.connect(lambda: self.player.setPlaybackRate(1.0))
        btnSpeed.clicked.connect(lambda: self.player.setPlaybackRate(2.0))
        btnPlay.clicked.connect(self.player.play)
        btnPause.clicked.connect(self.player.pause)

        self.layoutControles.addWidget(btnPlay)
        self.layoutControles.addWidget(btnPause)
        self.layoutControles.addWidget(btnNormalSpeed)
        self.layoutControles.addWidget(btnSpeed)
        layoutCentro.addLayout(self.layoutControles)

        # Botões Válido / Inválido
        acoes = QHBoxLayout()
        acoes.setSpacing(16)
        acoes.setAlignment(Qt.AlignHCenter)

        self.btnValido = QPushButton("Válido")
        self.btnValido.clicked.connect(self.abrirTratativa)
        self.btnValido.setStyleSheet("QPushButton {background-color: #2a7d2a; color: white;} QPushButton:hover{background-color: #9fdf9f}")
        

        self.btnInvalido = QPushButton("Inválido")
        self.btnInvalido.clicked.connect(self.clickInvalidar)
        self.btnInvalido.setStyleSheet("QPushButton {background-color: #990000; color: white;} QPushButton:hover{background-color: #ff8080}")

        for btn in [self.btnValido, self.btnInvalido]:
            btn.setFont(fonte_p)
            btn.setFixedSize(130, 40)

        acoes.addWidget(self.btnValido)
        acoes.addWidget(self.btnInvalido)
        layoutCentro.addLayout(acoes)

        raiz.addWidget(colCentro, stretch=4)

        # ── COLUNA DIREITA  (informações + tratativa + report) ───────────────
        self.colunaDireita = QWidget()
        self.colunaDireita.setObjectName("colDireita")
        self.colunaDireita.setStyleSheet(
            "#colDireita { border: 1px dashed #444; border-radius: 6px; }"
        )
        self.colunaDireita.setMinimumWidth(300)
        self.colunaDireita.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layoutDireita = QVBoxLayout(self.colunaDireita)
        layoutDireita.setContentsMargins(14, 10, 10, 10)
        layoutDireita.setSpacing(10)
        layoutDireita.setAlignment(Qt.AlignTop)

        fonte_info = QFont("Arial", 11, QFont.Bold)

        # Informações do alerta
        self.infoAlerta = QLabel()
        self.infoAlerta.setAlignment(Qt.AlignCenter)
        self.infoAlerta.setFont(fonte_info)
        self.infoAlerta.setObjectName("infoAlerta")
        self.infoAlerta.setStyleSheet(
            "#infoAlerta { border-bottom: 1px solid #444; padding-bottom: 8px; }"
        )
        self.infoAlerta.setWordWrap(True)
        layoutDireita.addWidget(self.infoAlerta)

        self.infoPlaca = QLabel()
        self.infoPlaca.setAlignment(Qt.AlignCenter)
        self.infoPlaca.setFont(fonte_info)
        self.infoPlaca.setWordWrap(True)
        layoutDireita.addWidget(self.infoPlaca)

        self.infoEmpresa = QLabel()
        self.infoEmpresa.setAlignment(Qt.AlignCenter)
        self.infoEmpresa.setFont(fonte_info)
        self.infoEmpresa.setWordWrap(True)
        layoutDireita.addWidget(self.infoEmpresa)

        self.infoFilial = QLabel()
        self.infoFilial.setAlignment(Qt.AlignCenter)
        self.infoFilial.setFont(fonte_info)
        self.infoFilial.setWordWrap(True)
        layoutDireita.addWidget(self.infoFilial)

        self.infoMotorista = QLabel()
        self.infoMotorista.setAlignment(Qt.AlignCenter)
        self.infoMotorista.setFont(fonte_info)
        self.infoMotorista.setWordWrap(True)
        layoutDireita.addWidget(self.infoMotorista)

        self.infoDataHora = QLabel()
        self.infoDataHora.setAlignment(Qt.AlignCenter)
        self.infoDataHora.setFont(fonte_info)
        self.infoDataHora.setWordWrap(True)
        layoutDireita.addWidget(self.infoDataHora)

        # Separador visual
        separador = QLabel()
        separador.setFixedHeight(1)
        separador.setStyleSheet("background: #444; margin: 6px 0;")
        layoutDireita.addWidget(separador)

        # ── Seção de Tratativa (oculta até clicar Válido) ──
        self.containerT = QWidget()
        self.containerT.hide()
        layoutT = QVBoxLayout(self.containerT)
        layoutT.setContentsMargins(0, 0, 0, 0)
        layoutT.setSpacing(8)

        self.tratativas = QComboBox(self)
        self.tratativas.setPlaceholderText("Selecione sua tratativa")
        self.tratativas.currentTextChanged.connect(self.sincronizarSelecao)
        layoutT.addWidget(self.tratativas)

        # Botões de conduta
        self.escolhaConduta = QHBoxLayout()
        self.escolhaConduta.setSpacing(6)

        self.cigarro = QPushButton("Cigarro")
        self.cigarro.clicked.connect(lambda: self.bot.clickConduta("Cigarro"))
        self.cigarro.hide()

        self.celular = QPushButton("Celular")
        self.celular.clicked.connect(lambda: self.bot.clickConduta("Celular"))
        self.celular.hide()

        self.cameraManipulada = QPushButton("Câmera Manipulada")
        self.cameraManipulada.clicked.connect(lambda: self.bot.clickConduta("Câmera Manipulada"))
        self.cameraManipulada.hide()

        self.escolhaConduta.addWidget(self.cigarro)
        self.escolhaConduta.addWidget(self.celular)
        self.escolhaConduta.addWidget(self.cameraManipulada)
        layoutT.addLayout(self.escolhaConduta)

        # Botões de ausência
        self.escolhaAusencia = QHBoxLayout()
        self.escolhaAusencia.setSpacing(6)

        self.cameraDesajustada = QPushButton("Câmera Desajustada")
        self.cameraDesajustada.clicked.connect(lambda: self.bot.clickAusencia("Câmera Desajustada"))
        self.cameraDesajustada.hide()

        self.cameraEscura = QPushButton("Câmera Escura")
        self.cameraEscura.clicked.connect(lambda: self.bot.clickAusencia("Câmera Escura"))
        self.cameraEscura.hide()

        self.cameraDefeito = QPushButton("Câmera com Defeito")
        self.cameraDefeito.clicked.connect(lambda: self.bot.clickAusencia("Câmera com Defeito"))
        self.cameraDefeito.hide()

        self.escolhaAusencia.addWidget(self.cameraDesajustada)
        self.escolhaAusencia.addWidget(self.cameraEscura)
        self.escolhaAusencia.addWidget(self.cameraDefeito)
        layoutT.addLayout(self.escolhaAusencia)

        layoutDireita.addWidget(self.containerT)

        # ── Seção de Report (oculta até clicar Válido) ──
        self.containerR = QWidget()
        self.containerR.hide()
        layoutR = QHBoxLayout(self.containerR)
        layoutR.setContentsMargins(0, 0, 0, 0)
        layoutR.setSpacing(8)

        self.reportado = QPushButton("Monitorado")
        self.reportado.clicked.connect(lambda: self.bot.clickMonitorado())
        self.reportado.setFixedHeight(32)

        self.operacao = QPushButton("Reportar para a Operação")
        self.operacao.clicked.connect(lambda: self.bot.clickReportarOperacao())
        self.operacao.setFixedHeight(32)

        layoutR.addWidget(self.reportado)
        layoutR.addWidget(self.operacao)
        layoutDireita.addWidget(self.containerR)

        self.labelContador = QLabel()
        self.labelContador.setAlignment(Qt.AlignCenter)
        self.labelContador.setFont(QFont("Arial", 10, QFont.Bold))
        self.labelContador.setStyleSheet("color: #0088ff; padding: 2px;")
        layoutDireita.addWidget(self.labelContador)

        layoutDireita.addStretch()
        
        # ALTO RISCO
        layoutAltoRisco = QHBoxLayout()
        layoutAltoRisco.setAlignment(Qt.AlignRight)
        self.labelAltoRisco = QLabel("ALTO RISCO")
        self.labelAltoRisco.setAlignment(Qt.AlignCenter)
        self.labelAltoRisco.setFont(QFont("Average Sans", 12, QFont.Bold))
        self.labelAltoRisco.setStyleSheet("color: #ff5b5b; padding: 2px;")
        self.checkAltoRisco = QCheckBox()
        layoutAltoRisco.addWidget(self.labelAltoRisco)
        layoutAltoRisco.addWidget(self.checkAltoRisco)
        self.checkAltoRisco.stateChanged.connect(self.validarRisco)
        layoutDireita.addLayout(layoutAltoRisco)

        # MÉDIO RISCO
        layoutMedioRisco = QHBoxLayout()
        layoutMedioRisco.setAlignment(Qt.AlignRight)
        self.labelMedioRisco = QLabel("MÉDIO RISCO")
        self.labelMedioRisco.setAlignment(Qt.AlignCenter)
        self.labelMedioRisco.setFont(QFont("Average Sans", 12, QFont.Bold))
        self.labelMedioRisco.setStyleSheet("color: #fbb630; padding: 2px;")
        self.checkMedioRisco = QCheckBox()
        layoutMedioRisco.addWidget(self.labelMedioRisco)
        layoutMedioRisco.addWidget(self.checkMedioRisco)
        self.checkMedioRisco.stateChanged.connect(self.validarRisco)
        layoutDireita.addLayout(layoutMedioRisco)

        # BAIXO RISCO
        layoutBaixoRisco = QHBoxLayout()
        layoutBaixoRisco.setAlignment(Qt.AlignRight)
        self.labelBaixoRisco = QLabel("BAIXO RISCO")
        self.labelBaixoRisco.setAlignment(Qt.AlignCenter)
        self.labelBaixoRisco.setFont(QFont("Average Sans", 12, QFont.Bold))
        self.labelBaixoRisco.setStyleSheet("color: #2e57a5; padding: 2px;")
        self.checkBaixoRisco = QCheckBox()
        layoutBaixoRisco.addWidget(self.labelBaixoRisco)
        layoutBaixoRisco.addWidget(self.checkBaixoRisco)
        self.checkBaixoRisco.stateChanged.connect(self.validarRisco)
        layoutDireita.addLayout(layoutBaixoRisco)  
  
        raiz.addWidget(self.colunaDireita, stretch=3)

        self.aplicarModoEscuro()
        self.iniciarThread()

    # ── Métodos de controle ──────────────────────────────────────────────────

    def iniciarThread(self):
        self.bot = PlayWrightBot("https://login.goawakecloud.com.br/pt-br/goawake?cc=true")
        self.bot.sinalInfo.connect(self.coletarInfo)
        self.bot.sinalDownload.connect(self.downloadConcluido)
        self.bot.sinalTratativas.connect(self.listarTratativas)
        self.bot.sinalColunas.connect(self.atualizarColunas)
        self.bot.sinalVideosCarregados.connect(self.habilitarBotaoInvalidar)
        self.bot.sinalLiberarVideo.connect(self.liberarVideoAtual)
        self.bot.sinalTabela.connect(self.atualizarTabela)
        self.bot.sinalSemAlertas.connect(self.toggleLoading)
        self.bot.sinalContador.connect(self.atualizarContador)
        self.bot.sinalSessaoExpirada.connect(self.reabrirLogin)
        self.bot.sinalAlertas.connect(self.atualizarQuantidadeAlertas)
        self.bot.sinalQrCode.connect(self.qrCode)
        self.bot.sinalWhatsappConectado.connect(self.fecharQrSeAberto, Qt.QueuedConnection)
        self.bot.start()

    def coletarInfo(self, alerta, placa, filial, empresa, motorista, dataHora):
        self.infoAlerta.setText(alerta)
        self.infoPlaca.setText(placa)
        self.infoFilial.setText(filial)
        self.infoEmpresa.setText(empresa)
        self.infoMotorista.setText(motorista)
        self.infoDataHora.setText(f'Data do ocorrido: {dataHora}')

        self.btnValido.setEnabled(False)
        self.btnInvalido.setEnabled(False)
        print(">>> Botões desabilitados, aguardando carregamento dos vídeos...")
        self.habilitarBotoesAcao()

        if hasattr(self, '_tratativaAberta'):
            delattr(self, '_tratativaAberta')

        # Oculta seções de tratativa/report ao carregar novo alerta
        self.containerT.hide()
        self.containerR.hide()
        self.pedirTratativas()

    def habilitarBotaoInvalidar(self):
        self.btnValido.setEnabled(True)
        self.btnInvalido.setEnabled(True)
        print(">>> Botões Válido e Inválido habilitados")

    def atualizarColunas(self, quantidade):
        self.labelColunas.setText(f"Alerta já foi visto {quantidade} vezes")
        print(f">>> Label atualizado: {quantidade} alertas monitorados")

    def atualizarContador(self, contador):
        self.labelContador.setText(f"Alertas tratados hoje: {contador}")

    def atualizarTabela(self, linhas, dados):
        print(f'>>> dados: {dados}')
        if hasattr(self, 'noHistoricoLabel'):
                self.noHistoricoLabel.deleteLater()
                del self.noHistoricoLabel       
        if linhas == 0:
            self.tabela.hide()
            self.noHistoricoLabel = QLabel("Nenhum alerta anterior encontrado")
            self.noHistoricoLabel.setAlignment(Qt.AlignCenter)
            self.layoutTabela.addWidget(self.noHistoricoLabel)

        else:
            self.tabela.show()
            self.tabela.setRowCount(linhas)
            for i, (tipo, quando, tratativa) in enumerate(dados):
                self.tabela.setItem(i, 0, QTableWidgetItem(tipo))
                self.tabela.setItem(i, 1, QTableWidgetItem(quando))
                self.tabela.setItem(i, 2, QTableWidgetItem(tratativa))
            print(f">>> Tabela atualizada com {linhas} linhas")

    def downloadConcluido(self, video1, video2, video3):
        self.videos = {
            "Câmera 1": video1,
            "Câmera 2": video2,
            "Câmera 3": video3,
        }
        self.trocarVideo(self.seletorVideo.currentText())
    
    def trocarVideo(self, nome: str):
        caminho = self.videos.get(nome)
        if caminho and os.path.exists(caminho):
            self.video_atual = caminho
            self.player.setSource(QUrl.fromLocalFile(caminho))
            self.player.play()

    def liberarVideoAtual(self):
        try:
            self.player.stop()
            self.player.setSource(QUrl())
            pasta = os.path.join(os.getcwd(), "perfil_edege_bot", "Downloads")
            if os.path.exists(pasta):
                import time
                for arquivo in os.listdir(pasta):
                    if arquivo.endswith(".mp4"):
                        caminho = os.path.join(pasta, arquivo)
                        for tentativa in range(3):
                            try:
                                os.remove(caminho)
                                print(f">>> Vídeo {caminho} apagado")
                                break
                            except PermissionError:
                                print(f">>> Tentativa {tentativa + 1}/3 falhou, aguardando...")
                                time.sleep(0.3)
            self.video_atual = None
            self.videos = {}

        except Exception as e:
            print(f">>> ERRO ao liberar vídeo: {e}")
        finally:
            asyncio.run_coroutine_threadsafe(self._marcarVideoLiberado(), self.bot.loop)

    async def _marcarVideoLiberado(self):
        self.bot._video_liberado.set()

    def abrirTratativa(self):
        if hasattr(self, '_tratativaAberta'):
            return
        self._tratativaAberta = True
        self.desabilitarBotoesAcao()
        self.containerT.show()
        self.containerR.show()

    def clickInvalidar(self):
        self.desabilitarBotoesAcao()
        if self.bot:
            self.bot.clickInvalidar()

    def desabilitarBotoesAcao(self):
        self.btnValido.setEnabled(False)
        self.btnInvalido.setEnabled(False)

    def habilitarBotoesAcao(self):
        self.btnValido.setEnabled(True)
        self.btnInvalido.setEnabled(True)

    def sincronizarSelecao(self, valor: str):
        print(">>> sincronizarSelecao chamado:", valor)
        self.ocultarTodosBotoes()
        if valor == "Conduta - Política de Consequência + Pontos no D-OLHO":
            self.mostrarConduta()
        elif valor == "Ausência - Solicitar ajuste - Gestão de Equipamentos CCI":
            self.mostrarAusencia()
        if self.bot:
            self.bot.clickSelecao(valor, )

    def listarTratativas(self, opcoes: list):
        if self.tratativas is None:
            self._tratativas_pendentes = opcoes
            return
        self.tratativas.blockSignals(True)
        self.tratativas.clear()
        self.tratativas.addItems(opcoes)
        self.tratativas.blockSignals(False)

    def pedirTratativas(self):
        asyncio.run_coroutine_threadsafe(self.bot.coletarTratativas(), self.bot.loop)

    def mostrarConduta(self):
        self.cameraDesajustada.hide()
        self.cameraEscura.hide()
        self.cameraDefeito.hide()
        self.celular.show()
        self.cigarro.show()
        self.cameraManipulada.show()

    def mostrarAusencia(self):
        self.celular.hide()
        self.cigarro.hide()
        self.cameraManipulada.hide()
        self.cameraDesajustada.show()
        self.cameraEscura.show()
        self.cameraDefeito.show()

    def ocultarTodosBotoes(self):
        self.celular.hide()
        self.cigarro.hide()
        self.cameraManipulada.hide()
        self.cameraDesajustada.hide()
        self.cameraEscura.hide()
        self.cameraDefeito.hide()

    def toggleLoading(self, sem_alertas: bool):
        if not self.loadingWidget or not self.caixaVideo:
            return
        # Centro
        self.loadingWidget.setVisible(sem_alertas)
        self.loadingBar.setVisible(sem_alertas)
        self.caixaVideo.setVisible(not sem_alertas)
        self.seletorVideo.setVisible(not sem_alertas)
        self.labelColunas.setVisible(not sem_alertas)
        self.btnValido.setVisible(not sem_alertas)
        self.btnInvalido.setVisible(not sem_alertas)
        for i in range(self.layoutControles.count()):
            widget = self.layoutControles.itemAt(i).widget()
            if widget:
                widget.setVisible(not sem_alertas)

        # Direita
        self.colunaDireita.setVisible(not sem_alertas)

        # Esquerda
        self.painelTabela.setVisible(not sem_alertas)

    def reabrirLogin(self):
        self.janelaLogin = janelaLogin()
        self.janelaLogin.bot = self.bot
        self.janelaLogin.sinalLogin.connect(self.bot.iniciarConta)
        self.janelaLogin.sinalCodigo.connect(self.bot.enviarCodigo)
        self.bot.sinalPedirCodigo.connect(self.janelaLogin.mostrarCampoCodigo)
        self.bot.sinalLoginOk.connect(self.janelaLogin.close)
        self.janelaLogin.show()
    
    def validarRisco(self):
        checks = [self.checkAltoRisco, self.checkMedioRisco, self.checkBaixoRisco]
        marcados = [c for c in checks if c.isChecked()]

        if len(marcados) == 3:
            for c in checks:
                c.blockSignals(True)
                c.setChecked(False)
                c.blockSignals(False)
            self.bot.clickCheck({"Alto": False, "Médio": False, "Baixo": False})
            return

        self.bot.clickCheck({
            "Alto":  self.checkAltoRisco.isChecked(),
            "Médio": self.checkMedioRisco.isChecked(),
            "Baixo": self.checkBaixoRisco.isChecked(),
        })

    def atualizarQuantidadeAlertas(self, alto, medio, baixo):
        self.labelAltoRisco.setText(f"{alto} {'Alerta' if alto == 1 else 'Alertas'} - ALTO RISCO")
        self.labelMedioRisco.setText(f"{medio} {'Alerta' if medio == 1 else 'Alertas'} - MÉDIO RISCO")
        self.labelBaixoRisco.setText(f"{baixo} {'Alerta' if baixo == 1 else 'Alertas'} - BAIXO RISCO")


    def aplicarModoEscuro(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QPushButton {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:disabled {
                background-color: #252525;
                color: #555;
                border-color: #333;
            }
            QComboBox {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 3px 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2d2d2d;
                color: #e0e0e0;
                selection-background-color: #0055aa;
            }
            QComboBox::drop-down {
                border: none;
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #e0e0e0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 3px 8px;
            }
            QTableWidget {
                background-color: #252525;
                color: #e0e0e0;
                gridline-color: #3a3a3a;
                border: none;
            }
            QTableWidget::item:selected {
                background-color: #0055aa;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #2d2d2d;
                color: #aaaaaa;
                border: 1px solid #3a3a3a;
                padding: 4px;
            }
            QScrollBar:vertical {
                background: #1e1e1e;
                width: 8px;
            }
            QScrollBar::handle:vertical {
                background: #444;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0;
            }
            QProgressBar {
                background-color: #2d2d2d;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #0055aa;
                border-radius: 2px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #555;
                border-radius: 3px;
                background-color: #2d2d2d;
            }
            QCheckBox::indicator:checked {
                background-color: #0055aa;
                border-color: #0055aa;
            }
            QMessageBox {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
        """)

    def qrCode(self, dados: bytes):
        if self.janelaQr is not None:  # já aberta, atualiza ao invés de criar nova
            return

        self.janelaQr = QDialog(self)
        self.janelaQr.setWindowTitle("Conectar WhatsApp")
        self.janelaQr.setModal(False)
        self.janelaQr.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")

        layout = QVBoxLayout(self.janelaQr)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)

        instrucao = QLabel("O navegador foi aberto com o QR Code.\nEscaneie pelo WhatsApp no celular.")
        instrucao.setAlignment(Qt.AlignCenter)
        instrucao.setFont(QFont("Arial", 11))
        layout.addWidget(instrucao)

        labelQr = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(dados)
        pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        labelQr.setPixmap(pixmap)
        labelQr.setAlignment(Qt.AlignCenter)
        layout.addWidget(labelQr)

        aviso = QLabel("A janela fechará automaticamente\nquando o WhatsApp conectar")
        aviso.setAlignment(Qt.AlignCenter)
        aviso.setStyleSheet("color: #888; font-size: 10px;")
        layout.addWidget(aviso)

        self.janelaQr.adjustSize()
        self.janelaQr.show()

    def fecharQrSeAberto(self):
        if hasattr(self, 'janelaQr') and self.janelaQr is not None:
            QMetaObject.invokeMethod(self.janelaQr, "close", Qt.QueuedConnection)
            self.janelaQr = None


    def ajustarJanelaAoMonitor(self, largura_pct=70, altura_pct=90):
        """Ajusta o tamanho da janela como percentual da tela disponível."""
        tela = QApplication.primaryScreen()
        if tela:
            geo = tela.availableGeometry()
            largura = int(geo.width() * largura_pct / 100)
            altura  = int(geo.height() * altura_pct / 100)
            x = geo.x() + (geo.width()  - largura) // 2
            y = geo.y() + (geo.height() - altura)  // 2
            self.setGeometry(x, y, largura, altura)
            print(f"Janela: {largura}x{altura} em ({x}, {y})")
        else:
            print("Não foi possível detectar a tela")


# ── Execução ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)
    janela = janelaPrincipal()
    janela.show()
    hwnd = int(janela.winId())
    aplicar_modo_escuro(hwnd)

    janela2 = janelaLogin()
    janela2.bot = janela.bot  # ← referência para enviarCodigo()
    janela2.sinalLogin.connect(janela.bot.iniciarConta)
    janela2.sinalCodigo.connect(janela.bot.enviarCodigo)
    janela.bot.sinalPedirCodigo.connect(janela2.mostrarCampoCodigo)  # ← mostra campo de código
    janela.bot.sinalLoginOk.connect(janela2.close)                   # ← fecha só quando logado
    janela2.show()

    sys.exit(app.exec())