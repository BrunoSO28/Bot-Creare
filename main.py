from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextEdit, QLineEdit, QComboBox
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl, Qt, QThread, Signal, QRect
from PySide6.QtGui import QFont, QScreen
from playwright.async_api import async_playwright
import sys
import asyncio
import os

#BOT do navegador
class PlayWrightBot(QThread):
    sinalInfo = Signal(str,str,str,str,str)
    sinalDownload = Signal(str)
    sinalGestao = Signal(str)
    sinalTratativas = Signal(list)
    sinalPronto = Signal()

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.loop = None
        self.pagina = None
        self.tratativas = None

    async def run_playwright(self):
        async with async_playwright() as pw:
            navegador = await pw.chromium.launch_persistent_context(
                user_data_dir="perfil_edge_bot",
                channel="msedge", 
                headless=False)
            self.pagina = await navegador.new_page()

            #Login na conta
            await self.pagina.goto(self.url, wait_until="commit", timeout=0)
            
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
                await campo_usuario.fill("brunooliveira@expressonepomuceno.com.br")
                await self.pagina.wait_for_timeout(500)
                
                # Campo de senha
                campo_senha = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]')
                await campo_senha.click()
                await campo_senha.fill("Bruno.2025")
                await self.pagina.wait_for_timeout(500)
                
            except Exception as e:
                print(f"Erro ao preencher campos de login: {e}")
                # Tenta método alternativo com type ao invés de fill
                try:
                    campo_usuario = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[1]')
                    await campo_usuario.click()
                    await campo_usuario.press_sequentially("brunooliveira@expressonepomuceno.com.br", delay=50)
                    
                    campo_senha = self.pagina.locator('xpath=//*[@id="__next"]/div[4]/div[2]/div[1]/form/input[2]')
                    await campo_senha.click()
                    await campo_senha.press_sequentially("Bruno.2025", delay=50)
                except Exception as e2:
                    print(f"Erro no método alternativo: {e2}")
            
            #await self.pagina.pause()
            await self.pagina.get_by_role("button", name="Entrar").click()
            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").click()
            await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-header/div/div[2]/div/div[3]/p-checkbox/div/div[2]/span").click()
            #await self.pagina.pause()
            tratativa = self.pagina.locator('xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-body/p-table/div/div/table/tbody/tr[1]/td[10]/span/button/img')

            #Coletar informações do Alerta
            while await tratativa.is_enabled():
                await tratativa.click()
                alerta = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[1]/p-dropdown/div/label").inner_text()

                placa = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[2]/p").inner_text()

                filial = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[4]/p").inner_text()

                empresa = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[3]").inner_text()
                
                motorista = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[5]/p").inner_text()
                
                #Download do vídeo
                await self.pagina.locator(".playMovie").dblclick()
                await self.pagina.wait_for_timeout(1000)
                videoDl = self.pagina.locator("xpath=/html/body/dinamic-dialog/div/div/ng-component/div/ul/li[1]/div/div/app-download-button/button/i")
                async with self.pagina.expect_download() as downloadVideo:
                    await videoDl.click()
                    download = await downloadVideo.value

                    diretorio = os.getcwd()

                    diretorioFinal = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera.mp4")

                    await download.save_as(diretorioFinal)

                    self.sinalDownload.emit(diretorioFinal)

                self.sinalInfo.emit(alerta,placa,empresa,filial,motorista)
                
                await self.pagina.mouse.click(400, 10)

                self.sinalPronto.emit()

            while not self.isInterruptionRequested():
                await asyncio.sleep(0.1)                      
 
            await self.pagina.wait_for_timeout(10000)
            await navegador.close()

    #Rodando o navegador em segundo plano        
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_playwright())

    def clickNavegador(self, locator: str):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.acaoClick(locator), self.loop)

    async def acaoClick(self, locator: str):
        if self.pagina is None:
            print("ERRO: pagina = None")
            return
        try:
            await self.pagina.locator(locator).click()
            self.sinalGestao.emit(locator)
        except Exception as e:
            print(f"Erro ao clicar em {locator}: {e}")

    def clickSelecao(self, valor: str):
        if self.loop:
            asyncio.run_coroutine_threadsafe(
                self.selecaoTratativa(valor), self.loop
            )

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

    async def selecaoTratativa(self, valor: str):
        try:
            # Clica no dropdown visual para abrir
            await self.pagina.locator("treatment-step-three p-dropdown").click()
            await self.pagina.wait_for_timeout(500)
            
            # Clica na opção pelo texto dentro do painel que abre
            await self.pagina.locator(
                "p-dropdownitem li"
            ).filter(has_text=valor).click()
            
            await self.pagina.wait_for_timeout(300)
            self.sinalGestao.emit(valor)
            print(">>> Selecionado com sucesso:", valor)
        except Exception as e:
            print(">>> ERRO selecaoTratativa:", e)

#UI 
class janelaPrincipal (QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Revisão de Vídeo")
        
        # Ajusta a janela considerando o DPI scaling do Windows
        self.ajustarJanelaAoMonitor(85)
        
        self.iniciarThread()

        #Layout do App
        central = QWidget()
        self.setCentralWidget(central)

        self.layoutHorizontal = QHBoxLayout(central)
        self.layoutHorizontal.setContentsMargins(20,20,20,20)
        self.layoutHorizontal.setSpacing(20)
        
        self.esquerdo = QWidget()
        self.layoutEsquerdo = QVBoxLayout(self.esquerdo)

        container = QWidget()
        # Remove tamanho fixo para ser responsivo
        container.setMinimumSize(500, 400)
        container.setObjectName("container")
        container.setStyleSheet("#container { border-bottom: 1px solid #a6a6a6; } ")
        
        layoutContainer = QVBoxLayout(container)
        layoutContainer.setContentsMargins(10, 10, 10, 10)
        layoutContainer.setSpacing(6)
        
        self.layoutEsquerdo.addWidget(container, alignment=Qt.AlignTop | Qt.AlignLeft)     
        
        self.status_label = QLabel("Carregando Vídeo...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setFont(QFont("Arial", 12, QFont.Bold))
        layoutContainer.addWidget(self.status_label)

        # Local onde o vídeo vai aparecer
        self.caixaVideo = QVideoWidget()
        layoutContainer.addWidget(self.caixaVideo, stretch=1)
        self.player = QMediaPlayer(self)
        self.player.setVideoOutput(self.caixaVideo)
        

        #Controles 
        controles = QHBoxLayout()
        controles.setSpacing(6)  # espaço menor entre botões

        btnPlay = QPushButton("▶️")
        btnPause = QPushButton("⏸️")
        btnNormalSpeed = QPushButton("1X")
        btnSpeed = QPushButton("2X")

        fonte_pequena = QFont("Arial", 9)

        for btn in [btnPlay, btnPause, btnNormalSpeed, btnSpeed]:
            btn.setFont(fonte_pequena)
            btn.setFixedHeight(30)          
            btn.setFixedWidth(30)           

        btnNormalSpeed.clicked.connect(lambda: self.player.setPlaybackRate(1.0))
        btnSpeed.clicked.connect(lambda: self.player.setPlaybackRate(2.0))
        btnPlay.clicked.connect(self.player.play)
        btnPause.clicked.connect(self.player.pause)

        controles.addWidget(btnPlay)
        controles.addWidget(btnPause)
        controles.addWidget(btnNormalSpeed)
        controles.addWidget(btnSpeed)
        controles.addStretch()  # empurra os botões para a esquerda
        layoutContainer.addLayout(controles)
        
        #Ações
        acoes = QHBoxLayout()
        acoes.setSpacing(10)

        btnValido = QPushButton("Válido")
        btnValido.clicked.connect(self.abrirTratativa)
        btnValido.clicked.connect(self.aplicarGestao)
        btnValido.setStyleSheet("background-color: green;")

        btnInvalido = QPushButton("Inválido")
        btnInvalido.setStyleSheet("background-color:#990000;")
        
        for btn in [btnValido, btnInvalido]:
            btn.setFont(fonte_pequena)
            btn.setFixedHeight(38)         
            btn.setFixedWidth(120)

        acoes.addWidget(btnValido)
        acoes.addWidget(btnInvalido)
        layoutContainer.addLayout(acoes)

        #Informações na UI
        direito = QWidget()
        layoutDireito = QVBoxLayout(direito)
        
        container2 = QWidget()
        # Remove tamanho fixo para ser responsivo
        container2.setMinimumSize(500, 400)
        container2.setObjectName("container2")
        container2.setStyleSheet("#container2 { border-left: 1px solid #a6a6a6; } ")
        
        layoutContainer2 = QVBoxLayout(container2)
        layoutContainer2.setContentsMargins(10, 10, 10, 10)
        layoutContainer2.setSpacing(6)
        
        layoutDireito.addWidget(container2, alignment=Qt.AlignTop | Qt.AlignRight)

        self.infoAlerta = QLabel()
        self.infoAlerta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoAlerta.setFont(QFont("Arial", 12, QFont.Bold))
        self.infoAlerta.setObjectName("infoAlerta")
        self.infoAlerta.setStyleSheet("#infoAlerta {border-bottom: 1px solid #a6a6a6; padding: 10px;}")
        self.infoAlerta.setWordWrap(True)  # Permite quebra de linha
        layoutContainer2.addWidget(self.infoAlerta)
        
        self.infoPlaca = QLabel()
        self.infoPlaca.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoPlaca.setFont(QFont("Arial", 12, QFont.Bold))
        self.infoPlaca.setWordWrap(True)
        layoutContainer2.addWidget(self.infoPlaca)
        
        self.infoFilial = QLabel()
        self.infoFilial.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoFilial.setFont(QFont("Arial", 12, QFont.Bold))
        self.infoFilial.setWordWrap(True)
        layoutContainer2.addWidget(self.infoFilial)
        
        self.infoEmpresa = QLabel()
        self.infoEmpresa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoEmpresa.setFont(QFont("Arial", 12, QFont.Bold))
        self.infoEmpresa.setWordWrap(True)
        layoutContainer2.addWidget(self.infoEmpresa)
        
        self.infoMotorista = QLabel()
        self.infoMotorista.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.infoMotorista.setFont(QFont("Arial", 12, QFont.Bold))
        self.infoMotorista.setWordWrap(True)
        layoutContainer2.addWidget(self.infoMotorista)

        self.layoutHorizontal.addWidget(self.esquerdo)
        self.layoutHorizontal.addWidget(direito)

        self.containerT = QWidget()
        self.containerT.setMinimumSize(500, 300)
        self.containerT.setObjectName("containerT")
        self.containerT.hide()  # ← oculto até clicar em Válido
        
        layoutTratativa = QVBoxLayout(self.containerT)
        
        self.tratativas = QComboBox(self)
        self.tratativas.setFixedWidth(400)
        self.tratativas.setPlaceholderText("Selecione sua tratativa")
        self.tratativas.currentTextChanged.connect(self.sincronizarSelecao)
        
        report = QHBoxLayout()
        reportado = QPushButton("Monitorado")
        reportado.setFixedHeight(30)
        operacao = QPushButton("Reportar para a Operação")
        operacao.setFixedHeight(30)
        report.addWidget(reportado)
        report.addWidget(operacao)
        
        layoutTratativa.addWidget(self.tratativas, alignment=Qt.AlignCenter | Qt.AlignTop)
        layoutTratativa.addStretch()
        layoutTratativa.addLayout(report)
        layoutTratativa.addStretch()
        
        self.layoutEsquerdo.addWidget(self.containerT)

    #Iniciar a thread para abrir o site
    def iniciarThread(self):
        self.bot = PlayWrightBot("https://login.goawakecloud.com.br/pt-br/goawake?cc=true")
        self.bot.sinalInfo.connect(self.coletarInfo)
        self.bot.sinalDownload.connect(self.downloadConcluido)
        self.bot.sinalGestao.connect(self.aplicarGestao)
        self.bot.sinalTratativas.connect(self.listarTratativas)
        self.bot.start()

    #Coletar as informações do site
    def coletarInfo(self, alerta, placa,filial, empresa, motorista):
        self.infoAlerta.setText(alerta)
        self.infoPlaca.setText(placa)
        self.infoFilial.setText(filial)
        self.infoEmpresa.setText(empresa)
        self.infoMotorista.setText(motorista)
        self.pedirTratativas()

    #Inicia o vídeo assim que ele é baixado
    def downloadConcluido(self, diretorioFinal):
        self.player.setSource(QUrl.fromLocalFile(diretorioFinal))
        self.player.play()

    #Tratativas do alerta quando o botão de válidar é apertado
    def abrirTratativa(self):
        if hasattr(self, '_tratativaAberta'):
            return
        self._tratativaAberta = True
        
        self.containerT.show()  # ← apenas exibe, já foi criado no __init__

    def aplicarGestao(self):
        if self.bot:
            self.bot.clickNavegador(".playMovie")
            self.bot.clickNavegador("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[2]/treatment-step-one/div/div/div[3]/div[3]/button")
            self.bot.clickNavegador("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[2]/treatment-step-two/div/div/div[2]/div[3]/button")

    def sincronizarSelecao(self, valor: str):
        print(">>> sincronizarSelecao chamado:", valor)
        if self.bot:
            self.bot.clickSelecao(valor)

    def listarTratativas(self, opcoes: list):
        if self.tratativas is None:
            self._tratativas_pendentes = opcoes  # guarda para usar depois
            return
        
        self.tratativas.blockSignals(True)
        self.tratativas.clear()
        self.tratativas.addItems(opcoes)
        self.tratativas.blockSignals(False) # ← confirme que essa linha executa
        print(">>> sinais bloqueados?", self.tratativas.signalsBlocked())
        print(">>> combo tem itens:", self.tratativas.count())

    def pedirTratativas(self):
        asyncio.run_coroutine_threadsafe(
        self.bot.coletarTratativas(), self.bot.loop
    )

    def ajustarJanelaAoMonitor(self, percentual=80):
        """
        Ajusta o tamanho da janela baseado no tamanho do monitor.
        Considera o DPI scaling do Windows (125%, 150%, etc.)
        
        Args:
            percentual (int): Percentual do tamanho da tela a ser usado (padrão: 80%)
        """
        # Obtém a tela onde a janela está localizada
        tela = QApplication.primaryScreen()
        
        if tela:
            # Obtém a geometria disponível da tela (excluindo barras de tarefas)
            geometria_disponivel = tela.availableGeometry()
            
            # Obtém o fator de escala DPI
            dpi_scale = tela.devicePixelRatio()
            
            # Calcula o tamanho baseado no percentual
            largura = int(geometria_disponivel.width() * percentual / 100)
            altura = int(geometria_disponivel.height() * percentual / 100)
            
            # Calcula a posição para centralizar a janela
            x = geometria_disponivel.x() + (geometria_disponivel.width() - largura) // 2
            y = geometria_disponivel.y() + (geometria_disponivel.height() - altura) // 2
            
            # Define a geometria da janela
            self.setGeometry(x, y, largura, altura)
            
            print(f"Janela ajustada para: {largura}x{altura} na posição ({x}, {y})")
            print(f"DPI Scale Factor: {dpi_scale}")
            print(f"Resolução da tela: {geometria_disponivel.width()}x{geometria_disponivel.height()}")
        else:
            print("Não foi possível detectar a tela")
    
    def maximizarJanela(self):
        """Maximiza a janela para ocupar toda a tela disponível"""
        self.showMaximized()
    
    def ajustarJanelaPersonalizado(self, largura, altura, centralizar=True):
        """
        Ajusta a janela para um tamanho personalizado.
        
        Args:
            largura (int): Largura desejada em pixels
            altura (int): Altura desejada em pixels
            centralizar (bool): Se True, centraliza a janela na tela
        """
        self.resize(largura, altura)
        
        if centralizar:
            tela = QApplication.primaryScreen()
            if tela:
                geometria_disponivel = tela.availableGeometry()
                x = geometria_disponivel.x() + (geometria_disponivel.width() - largura) // 2
                y = geometria_disponivel.y() + (geometria_disponivel.height() - altura) // 2
                self.move(x, y)

#Executa o App
if __name__ == "__main__":
    # Habilita suporte a High DPI antes de criar a aplicação
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    janela = janelaPrincipal()
    janela.show()
    sys.exit(app.exec())