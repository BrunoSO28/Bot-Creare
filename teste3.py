from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox, QSizePolicy
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt, QThread, Signal, QRect
from PySide6.QtGui import QFont, QScreen
from playwright.async_api import async_playwright
import sys
import asyncio
import os
import pyautogui

#BOT do navegador
class PlayWrightBot(QThread):
    sinalInfo = Signal(str,str,str,str,str)
    sinalDownload = Signal(str)
    sinalTratativas = Signal(list)
    sinalPronto = Signal()
    sinalColunas = Signal(int)
    sinalVideosCarregados = Signal()
    sinalLiberarVideo = Signal()

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.loop = None
        self.pagina = None
        self.tratativas = None
        self.processando_alerta = False
        self._video_liberado = asyncio.Event()

    async def run_playwright(self):
        async with async_playwright() as pw:
            self.navegador = await pw.chromium.launch_persistent_context(
                user_data_dir="perfil_edge_bot",
                channel="msedge", 
                headless=False)
            self.pagina = await self.navegador.new_page()
            self.pagina2 = await self.navegador.new_page()
            await self.pagina.goto(self.url, wait_until="commit", timeout=0)
            await self.pagina2.goto("https://web.whatsapp.com/", wait_until="commit", timeout=0)
            
            try:
                campo_usuario = None
                try:
                    campo_usuario = self.pagina.get_by_placeholder("Usuário")
                    await campo_usuario.wait_for(state="visible", timeout=5000)
                except:
                    pass
                if not campo_usuario:
                    try:
                        campo_usuario = self.pagina.get_by_role("textbox", name="Usuário")
                        await campo_usuario.wait_for(state="visible", timeout=5000)
                    except:
                        pass
                if not campo_usuario:
                    campo_usuario = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[1]')
                    await campo_usuario.wait_for(state="visible", timeout=5000)
                await campo_usuario.click()
                await campo_usuario.fill("")
                await self.pagina.wait_for_timeout(300)
                await campo_usuario.fill("brunooliveira@expressonepomuceno.com.br")
                await self.pagina.wait_for_timeout(500)
                campo_senha = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]')
                await campo_senha.click()
                await campo_senha.fill("Bruno.2025")
                await self.pagina.wait_for_timeout(500)
            except Exception as e:
                print(f"Erro ao preencher campos de login: {e}")
                try:
                    campo_usuario = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[1]')
                    await campo_usuario.click()
                    await campo_usuario.press_sequentially("brunooliveira@expressonepomuceno.com.br", delay=50)
                    campo_senha = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]')
                    await campo_senha.click()
                    await campo_senha.press_sequentially("Bruno.2025", delay=50)
                except Exception as e2:
                    print(f"Erro no método alternativo: {e2}")
            
            await self.pagina.get_by_role("button", name="Entrar").click()
            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").click()
            tratativa = self.pagina.locator('xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-body/p-table/div/div/table/tbody/tr[1]/td[10]/span/button/img')
            await self.pagina.pause()

            while not self.isInterruptionRequested():
                while self.processando_alerta:
                    await asyncio.sleep(0.5)
                    print(">>> Aguardando processamento manual...")

                quantidade = await tratativa.count()
                print(f">>> Quantidade de alertas: {quantidade}")
                if quantidade == 0:
                    print(">>> Sem alertas, aguardando...")
                    await asyncio.sleep(5)
                    continue
                habilitado = await tratativa.is_enabled()
                print(f">>> Alerta habilitado: {habilitado}")
                if not habilitado:
                    await asyncio.sleep(2)
                    continue
                self.processando_alerta = True
                await self.pagina.wait_for_timeout(1000)
                await tratativa.click()
                self.alerta = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[1]/p-dropdown/div/label").inner_text()
                self.placa = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[2]/p").inner_text()
                self.filial = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[4]/p").inner_text()
                self.empresa = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[3]").inner_text()
                self.motorista = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[5]/p").inner_text()
                await self.pagina.locator(".playMovie").first.dblclick()
                await self.pagina.wait_for_timeout(1000)
                videoDl = self.pagina.locator("xpath=/html/body/dinamic-dialog/div/div/ng-component/div/ul/li[1]/div/div/app-download-button/button/i")
                self._video_liberado.clear()
                self.sinalLiberarVideo.emit()
                await asyncio.wait_for(self._video_liberado.wait(), timeout=5.0)
                async with self.pagina.expect_download() as downloadVideo:
                    await videoDl.click()
                    download = await downloadVideo.value
                    diretorio = os.getcwd()
                    self.diretoriofinal = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera.mp4")
                    await download.save_as(self.diretoriofinal)
                    self.sinalDownload.emit(self.diretoriofinal)
                self.sinalInfo.emit(self.alerta,self.placa,self.empresa,self.filial,self.motorista)
                await self.pagina.mouse.click(400, 10)
                videosAlerta = self.pagina.locator('ul[style="margin-bottom: 20px;"] li#itemToHistory')
                total = await videosAlerta.count()
                print(f">>> Total de vídeos do alerta: {total}")
                for i in range(total):
                    await videosAlerta.nth(i).click()
                    await self.pagina.wait_for_timeout(300)
                print(f">>> Todos os {total} vídeos foram selecionados")
                self.sinalVideosCarregados.emit()
                self.colunas = await self.pagina.locator('table:has(th:text("Tipo Alerta")) tbody tr').count()
                print(f">>> Quantidade de colunas: {self.colunas}")
                self.sinalColunas.emit(self.colunas)
                await self.pagina.get_by_role("button", name="Aplicar gestão").click()
                await self.pagina.get_by_role("button", name="Aplicar gestão").click()
                self.sinalPronto.emit()
                await asyncio.sleep(1)
                self.processando_alerta = False

            while not self.isInterruptionRequested():
                await asyncio.sleep(0.1)                      
            await self.pagina.wait_for_timeout(10000)
            await self.navegador.close()

    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_playwright())

    def clickSelecao(self, valor: str, janela_callback=None):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.selecaoTratativa(valor), self.loop)

    async def coletarTratativas(self):
        try:
            await self.pagina.wait_for_selector("treatment-step-three select", state="attached", timeout=10000)
            tratativas = await self.pagina.locator("treatment-step-three select option").all_inner_texts()
            tratativas = [t.strip() for t in tratativas if t.strip() and t != "Selecione uma Tratativa"]
            print(">>> Opções encontradas:", tratativas)
            self.sinalTratativas.emit(tratativas)
        except Exception as e:
            print(">>> ERRO coletarTratativas:", e)

    async def selecaoTratativa(self, valor: str):
        print(">>> selecaoTratativa chamado com:", valor)
        try:
            await self.pagina.locator("treatment-step-three p-dropdown").click()
            await self.pagina.wait_for_timeout(500)
            await self.pagina.wait_for_selector("p-dropdownpanel li, .ui-dropdown-item, .ui-dropdown-items li", state="visible", timeout=5000)
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
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.preencherTextoConduta(tipo_conduta), self.loop)

    def clickAusencia(self, tipo_ausencia: str):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.preencherTextoAusencia(tipo_ausencia), self.loop)

    async def alertaMonitorado(self):
        await self.pagina.get_by_role("button", name="Finalizar Tratativa").click()
        await self.pagina.wait_for_timeout(300)
        await self.pagina.get_by_role("button", name="Concluir").click()
        print(">>> Aguardando tabela atualizar...")
        await self.pagina.wait_for_timeout(3000)
        await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()
        print(">>> Tratativa Monitorada")

    async def subirVideoZap(self):
        await self.pagina2.get_by_role("button", name="Anexar").click()
        await self.pagina2.wait_for_timeout(500)
        await self.pagina2.click('button[aria-label="Fotos e vídeos"]')
        await self.pagina2.wait_for_timeout(500)
        await self.pagina2.locator('input[accept="image/*,video/mp4,video/3gpp,video/quicktime,video/webm,video/x-matroska"]').set_input_files(self.diretoriofinal)
        await self.pagina2.wait_for_timeout(500)
        pyautogui.hotkey('alt', 'F4')
        await self.pagina2.wait_for_timeout(500)
        await self.pagina2.get_by_test_id("media-caption-input-container").get_by_role("paragraph").fill(self.reportOperacao)
        await self.pagina2.wait_for_timeout(500)
        await self.pagina2.get_by_role("button", name="Enviar 1 item selecionado").click()
        await self.pagina2.wait_for_timeout(1000)
        await self.pagina2.get_by_role("button", name="End icon button").click()
        await self.pagina2.wait_for_timeout(500)
        await self.pagina2.get_by_text("Alerta de Fadiga - África").click()
        await self.pagina2.wait_for_timeout(100)

    async def reportarOperacao(self):
        await self.pagina.get_by_role("button", name="Finalizar Tratativa").click()
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
            case "Químico 1 Felipe" | "Automotivo Fabiano" | "Automotivo Felipe" | "Automotivo Alvaro" | "Químico 2 Fabiano":
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
            
        await self.pagina.get_by_role("button", name="Concluir").click()
        print(">>> Aguardando tabela atualizar...")
        await self.pagina.wait_for_timeout(3000)
        await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()

    def clickMonitorado(self):
        if self.loop:
            self.processando_alerta = True
            asyncio.run_coroutine_threadsafe(self.alertaMonitorado(), self.loop)

    def clickReportarOperacao(self):
        if self.loop:
            self.processando_alerta = True
            asyncio.run_coroutine_threadsafe(self.reportarOperacao(), self.loop)

    async def invalidarAlerta(self):
        try:
            print(">>> Iniciando invalidação do alerta")
            self.processando_alerta = True
            botao_voltar = self.pagina.get_by_role("button", name="Voltar")
            await botao_voltar.click()
            await self.pagina.wait_for_timeout(100)
            print(">>> Primeiro 'Voltar' clicado")
            await botao_voltar.click()
            await self.pagina.wait_for_timeout(300)
            print(">>> Segundo 'Voltar' clicado")
            await self.pagina.wait_for_timeout(300)
            dropdown_selector = ".ui-dropdown:not(.ui-state-disabled)"
            await self.pagina.wait_for_selector(dropdown_selector, state="visible", timeout=5000)
            await self.pagina.locator(dropdown_selector).first.click()
            await self.pagina.wait_for_timeout(300)
            print(">>> Dropdown aberto")
            await self.pagina.wait_for_selector("p-dropdownpanel li, .ui-dropdown-item, .ui-dropdown-items li", state="visible", timeout=5000)
            await self.pagina.locator("li:has-text('Alerta invalidado')").click()
            await self.pagina.wait_for_timeout(300)
            print(">>> 'Alerta invalidado' selecionado")
            await self.pagina.get_by_role("button", name="Ok").click()
            await self.pagina.wait_for_timeout(300)
            await self.pagina.get_by_role("button", name="Finalizar").click()
            await self.pagina.wait_for_timeout(300)
            await self.pagina.get_by_role("button", name="Finalizar").nth(1).click()
            await self.pagina.wait_for_timeout(300)
            await self.pagina.get_by_role("button", name="Ok").click()
            print(">>> Aguardando tabela atualizar...")
            await self.pagina.wait_for_timeout(3000)
            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()            
            print(">>> Invalidação concluída com sucesso - Vídeo será apagado")
        except Exception as e:
            print(f">>> ERRO invalidarAlerta: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.processando_alerta = False
            print(">>> Flag processando_alerta liberada")

    def clickInvalidar(self):
        if self.loop:
            self.processando_alerta = True
            asyncio.run_coroutine_threadsafe(self.invalidarAlerta(), self.loop)


class janelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Revisão de Vídeo")
        self.video_atual = None

        # Janela mais alta e menos larga: 70% largura, 90% altura
        self.ajustarJanelaAoMonitor(largura_pct=70, altura_pct=90)

        self.iniciarThread()

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

        labelTabela = QLabel("Tabela\n(em breve)", self.painelTabela)
        labelTabela.setAlignment(Qt.AlignCenter)
        labelTabela.setStyleSheet("color: #555; font-size: 13px;")
        layoutTabela = QVBoxLayout(self.painelTabela)
        layoutTabela.addWidget(labelTabela)

        raiz.addWidget(self.painelTabela, stretch=3)

        # ── COLUNA CENTRAL  (vídeo + controles + ações) ─────────────────────
        colCentro = QWidget()
        layoutCentro = QVBoxLayout(colCentro)
        layoutCentro.setContentsMargins(0, 0, 0, 0)
        layoutCentro.setSpacing(8)
        layoutCentro.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Status
        self.status_label = QLabel("Carregando Vídeo...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 11, QFont.Bold))
        layoutCentro.addWidget(self.status_label)

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
        controles = QHBoxLayout()
        controles.setSpacing(6)
        controles.setAlignment(Qt.AlignHCenter)

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

        controles.addWidget(btnPlay)
        controles.addWidget(btnPause)
        controles.addWidget(btnNormalSpeed)
        controles.addWidget(btnSpeed)
        layoutCentro.addLayout(controles)

        # Botões Válido / Inválido
        acoes = QHBoxLayout()
        acoes.setSpacing(16)
        acoes.setAlignment(Qt.AlignHCenter)

        self.btnValido = QPushButton("Válido")
        self.btnValido.clicked.connect(self.abrirTratativa)
        self.btnValido.setStyleSheet("background-color: #2a7d2a; color: white; font-weight: bold;")

        self.btnInvalido = QPushButton("Inválido")
        self.btnInvalido.clicked.connect(self.clickInvalidar)
        self.btnInvalido.setStyleSheet("background-color: #990000; color: white; font-weight: bold;")

        for btn in [self.btnValido, self.btnInvalido]:
            btn.setFont(fonte_p)
            btn.setFixedSize(130, 40)

        acoes.addWidget(self.btnValido)
        acoes.addWidget(self.btnInvalido)
        layoutCentro.addLayout(acoes)

        raiz.addWidget(colCentro, stretch=4)

        # ── COLUNA DIREITA  (informações + tratativa + report) ───────────────
        colDireita = QWidget()
        colDireita.setObjectName("colDireita")
        colDireita.setStyleSheet(
            "#colDireita { border-left: 1px solid #444; }"
        )
        colDireita.setMinimumWidth(300)
        colDireita.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layoutDireita = QVBoxLayout(colDireita)
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

        # Empurra tudo para cima
        layoutDireita.addStretch()

        raiz.addWidget(colDireita, stretch=3)

    # ── Métodos de controle ──────────────────────────────────────────────────

    def iniciarThread(self):
        self.bot = PlayWrightBot("https://login.goawakecloud.com.br/pt-br/goawake?cc=true")
        self.bot.sinalInfo.connect(self.coletarInfo)
        self.bot.sinalDownload.connect(self.downloadConcluido)
        self.bot.sinalTratativas.connect(self.listarTratativas)
        self.bot.sinalColunas.connect(self.atualizarColunas)
        self.bot.sinalVideosCarregados.connect(self.habilitarBotaoInvalidar)
        self.bot.sinalLiberarVideo.connect(self.liberarVideoAtual)
        self.bot.start()

    def coletarInfo(self, alerta, placa, filial, empresa, motorista):
        self.infoAlerta.setText(alerta)
        self.infoPlaca.setText(placa)
        self.infoFilial.setText(filial)
        self.infoEmpresa.setText(empresa)
        self.infoMotorista.setText(motorista)

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

    def downloadConcluido(self, diretorioFinal):
        self.video_atual = diretorioFinal
        self.player.setSource(QUrl.fromLocalFile(diretorioFinal))
        self.player.play()

    def liberarVideoAtual(self):
        try:
            self.player.stop()
            self.player.setSource(QUrl())
            if self.video_atual and os.path.exists(self.video_atual):
                import time
                for tentativa in range(5):
                    try:
                        os.remove(self.video_atual)
                        print(f">>> Vídeo anterior apagado: {self.video_atual}")
                        break
                    except PermissionError:
                        print(f">>> Tentativa {tentativa + 1}/5 falhou, aguardando...")
                        time.sleep(0.3)
                self.video_atual = None
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
            self.bot.clickSelecao(valor, janela_callback=self)

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
    sys.exit(app.exec())