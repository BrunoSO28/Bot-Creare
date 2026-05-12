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
    sinalTratativas = Signal(list)
    sinalPronto = Signal()
    sinalTrativativaFinalizada = Signal()  # Novo sinal para quando a tratativa for finalizada
    sinalColunas = Signal(int)  # Novo sinal para enviar a quantidade de colunas
    sinalVideosCarregados = Signal()  # Novo sinal para quando todos os vídeos forem selecionados

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.loop = None
        self.pagina = None
        self.tratativas = None
        self.processando_alerta = False  # Flag para controlar o processamento

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
            #await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-header/div/div[2]/div/div[3]/p-checkbox/div/div[2]/span").click()
            tratativa = self.pagina.locator('xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[2]/div[1]/nb-card/nb-card-body/p-table/div/div/table/tbody/tr[1]/td[10]/span/button/img')
            #await self.pagina.pause()

            #Coletar informações do Alerta
            while await tratativa.is_enabled():
                # Aguarda se estiver processando manualmente (invalidando, etc)
                while self.processando_alerta:
                    await asyncio.sleep(0.5)
                    print(">>> Aguardando processamento manual...")
                
                self.processando_alerta = True  # Marca que está processando
                
                await tratativa.click()
                alerta = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[1]/p-dropdown/div/label").inner_text()

                placa = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[2]/p").inner_text()

                filial = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[4]/p").inner_text()

                empresa = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[3]").inner_text()
                
                motorista = await self.pagina.locator("xpath=/html/body/ngx-app/ngx-pages/ngx-sample-layout/nb-layout/div/div/div/div/div/nb-layout-column/filters-outlet/ngx-fatigue-v2/div/div/div[3]/div/div/treatment-flow/div/div/div[3]/div[1]/div/step-infos/div[1]/div[5]/p").inner_text()
                
                #Download do vídeo - usa .first para pegar o primeiro elemento quando há múltiplos
                await self.pagina.locator(".playMovie").first.dblclick()
                await self.pagina.wait_for_timeout(1000)
                videoDl = self.pagina.locator("xpath=/html/body/dinamic-dialog/div/div/ng-component/div/ul/li[1]/div/div/app-download-button/button/i")
                async with self.pagina.expect_download() as downloadVideo:
                    await videoDl.click()
                    download = await downloadVideo.value

                    diretorio = os.getcwd()
                    diretorioFinal = os.path.join(diretorio, "perfil_edge_bot\\Downloads\\Camera.mp4")

                    # Apaga o vídeo anterior se existir para evitar erro de permissão
                    if os.path.exists(diretorioFinal):
                        try:
                            os.remove(diretorioFinal)
                            print(f">>> Vídeo anterior apagado antes do download")
                        except Exception as e:
                            print(f">>> Erro ao apagar vídeo anterior: {e}")
                            # Aguarda um pouco e tenta novamente
                            await self.pagina.wait_for_timeout(1000)
                            try:
                                os.remove(diretorioFinal)
                                print(f">>> Vídeo anterior apagado na segunda tentativa")
                            except Exception as e2:
                                print(f">>> Erro na segunda tentativa: {e2}")

                    await download.save_as(diretorioFinal)

                    self.sinalDownload.emit(diretorioFinal)

                self.sinalInfo.emit(alerta,placa,empresa,filial,motorista)
                
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
                
                await self.pagina.get_by_role("button", name="Aplicar gestão").click()
                await self.pagina.get_by_role("button", name="Aplicar gestão").click()

                self.sinalPronto.emit()
                
                # Aguarda um pouco antes de verificar o próximo alerta
                await asyncio.sleep(1)
                self.processando_alerta = False  # Libera para próximo alerta

            while not self.isInterruptionRequested():
                await asyncio.sleep(0.1)                      
 
            await self.pagina.wait_for_timeout(10000)
            await navegador.close()

    #Rodando o navegador em segundo plano        
    def run(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.run_playwright())

    def clickSelecao(self, valor: str, janela_callback=None):
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
        #await self.pagina.locator("textarea").fill("Monitorado")
        await self.pagina.get_by_role("button", name="Finalizar Tratativa").click()
        await self.pagina.wait_for_timeout(300)
        await self.pagina.get_by_role("button", name="Concluir").click()
        await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()
        await self.pagina.wait_for_timeout(300)
        self.sinalTrativativaFinalizada.emit()  # Notifica que a tratativa foi finalizada
        print(">>> Tratativa 'Monitorado' finalizada")

    def clickMonitorado(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.alertaMonitorado(), self.loop)

    async def invalidarAlerta(self):
        """Invalida o alerta atual voltando e selecionando 'Alerta invalidado'"""
        try:
            print(">>> Iniciando invalidação do alerta")
            self.processando_alerta = True  # Bloqueia o loop principal
            
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
            await self.pagina.wait_for_timeout(300)

            await self.pagina.get_by_role("button", name="Ok").click()
            await self.pagina.wait_for_timeout(300)

            await self.pagina.locator(".theme-switch.ng-star-inserted > .switch > .slider").dblclick()
            await self.pagina.wait_for_timeout(300)
            

            # Emite sinal de tratativa finalizada para apagar o vídeo
            self.sinalTrativativaFinalizada.emit()
            print(">>> Invalidação concluída com sucesso - Vídeo será apagado")
            
        except Exception as e:
            print(f">>> ERRO invalidarAlerta: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Sempre libera a flag, mesmo em caso de erro
            self.processando_alerta = False
            print(">>> Flag processando_alerta liberada")

    def clickInvalidar(self):
        if self.loop:
            asyncio.run_coroutine_threadsafe(self.invalidarAlerta(), self.loop)



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
        
        # Configura o vídeo para repetir em loop
        self.player.setLoops(QMediaPlayer.Loops.Infinite)

        # Label para mostrar a quantidade de alertas já monitorados
        self.labelColunas = QLabel()
        self.labelColunas.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelColunas.setFont(QFont("Arial", 10, QFont.Bold))
        self.labelColunas.setStyleSheet("color: #0066cc; padding: 5px;")
        layoutContainer.addWidget(self.labelColunas)
        
        # Armazena o caminho do vídeo atual para poder apagá-lo depois
        self.video_atual = None
        

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

        self.btnValido = QPushButton("Válido")
        self.btnValido.clicked.connect(self.abrirTratativa)
        self.btnValido.setStyleSheet("background-color: green;")

        self.btnInvalido = QPushButton("Inválido")
        self.btnInvalido.clicked.connect(self.clickInvalidar)
        self.btnInvalido.setStyleSheet("background-color:#990000;")
        
        for btn in [self.btnValido, self.btnInvalido]:
            btn.setFont(fonte_pequena)
            btn.setFixedHeight(38)         
            btn.setFixedWidth(120)

        acoes.addWidget(self.btnValido)
        acoes.addWidget(self.btnInvalido)
        layoutContainer.addLayout(acoes)

        #Informações na UI
        self.direito = QWidget()
        self.layoutDireito = QVBoxLayout(self.direito)
        
        container2 = QWidget()
        # Remove tamanho fixo para ser responsivo
        container2.setMinimumSize(500, 400)
        container2.setObjectName("container2")
        container2.setStyleSheet("#container2 { border-left: 1px solid #a6a6a6; } ")
        
        layoutContainer2 = QVBoxLayout(container2)
        layoutContainer2.setContentsMargins(10, 10, 10, 10)
        layoutContainer2.setSpacing(6)
        
        self.layoutDireito.addWidget(container2, alignment=Qt.AlignTop | Qt.AlignRight)

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
        self.layoutHorizontal.addWidget(self.direito)

        self.containerT = QWidget()
        self.containerT.setMinimumSize(500, 300)
        self.containerT.setObjectName("containerT")
        self.containerT.hide()  # ← oculto até clicar em Válido
        
        layoutTratativa = QVBoxLayout(self.containerT)
        layoutTratativa.setContentsMargins(10, 10, 10, 10)
        layoutTratativa.setSpacing(2)
        layoutTratativa.setAlignment(Qt.AlignTop)
        
        self.tratativas = QComboBox(self)
        self.tratativas.setFixedWidth(400)
        self.tratativas.setPlaceholderText("Selecione sua tratativa")
        self.tratativas.currentTextChanged.connect(self.sincronizarSelecao)        
        
        layoutTratativa.addWidget(self.tratativas)
        layoutTratativa.addStretch()

        self.escolhaConduta = QHBoxLayout()
        self.escolhaConduta.setAlignment(Qt.AlignLeft)
        self.cigarro = QPushButton("Cigarro")
        self.cigarro.clicked.connect(lambda: self.bot.clickConduta("Cigarro"))
        self.cigarro.hide()
        self.cigarro.setFixedWidth(150)
        self.celular = QPushButton("Celular")
        self.celular.clicked.connect(lambda: self.bot.clickConduta("Celular"))
        self.celular.setFixedWidth(150)
        self.celular.hide()
        self.cameraManipulada = QPushButton("Câmera Manipulada")
        self.cameraManipulada.clicked.connect(lambda: self.bot.clickConduta("Câmera Manipulada"))
        self.cameraManipulada.setFixedWidth(150)
        self.cameraManipulada.hide()
        self.escolhaConduta.addWidget(self.cigarro)
        self.escolhaConduta.addWidget(self.celular)
        self.escolhaConduta.addWidget(self.cameraManipulada)

        layoutTratativa.addLayout(self.escolhaConduta)

        self.escolhaAusencia = QHBoxLayout()
        self.escolhaAusencia.setAlignment(Qt.AlignLeft)
        self.cameraDesajustada = QPushButton("Câmera Desajustada")
        self.cameraDesajustada.clicked.connect(lambda: self.bot.clickAusencia("Câmera Desajustada"))
        self.cameraDesajustada.hide()
        self.cameraDesajustada.setFixedWidth(200)
        self.cameraEscura = QPushButton("Câmera Escura")
        self.cameraEscura.clicked.connect(lambda: self.bot.clickAusencia("Câmera Escura"))
        self.cameraEscura.hide()
        self.cameraEscura.setFixedWidth(200)
        self.cameraDefeito = QPushButton("Câmera com Defeito")
        self.cameraDefeito.clicked.connect(lambda: self.bot.clickAusencia("Câmera com Defeito"))
        self.cameraDefeito.hide()
        self.cameraDefeito.setFixedWidth(200)
        self.escolhaAusencia.addWidget(self.cameraDesajustada)
        self.escolhaAusencia.addWidget(self.cameraEscura)
        self.escolhaAusencia.addWidget(self.cameraDefeito)

        layoutTratativa.addLayout(self.escolhaAusencia)
        layoutTratativa.addStretch() 

        self.layoutEsquerdo.addWidget(self.containerT)

        self.containerR = QWidget()
        self.containerR.setMinimumSize(500, 300)
        self.containerR.setObjectName("containerR")
        self.containerR.hide()

        layoutReport = QVBoxLayout(self.containerR)

        self.report = QHBoxLayout()
        self.reportado = QPushButton("Monitorado")
        self.reportado.clicked.connect(lambda: self.bot.clickMonitorado())
        self.reportado.setFixedHeight(30)
        self.operacao = QPushButton("Reportar para a Operação")
        self.operacao.setFixedHeight(30)
        self.report.addWidget(self.reportado)
        self.report.addWidget(self.operacao)
        
        layoutReport.addLayout(self.report)

        self.layoutDireito.addWidget(self.containerR)


    #Iniciar a thread para abrir o site
    def iniciarThread(self):
        self.bot = PlayWrightBot("https://login.goawakecloud.com.br/pt-br/goawake?cc=true")
        self.bot.sinalInfo.connect(self.coletarInfo)
        self.bot.sinalDownload.connect(self.downloadConcluido)
        self.bot.sinalTratativas.connect(self.listarTratativas)
        self.bot.sinalTrativativaFinalizada.connect(self.apagarVideo)  # Conecta o sinal para apagar o vídeo
        self.bot.sinalColunas.connect(self.atualizarColunas)  # Conecta o sinal para atualizar a contagem
        self.bot.sinalVideosCarregados.connect(self.habilitarBotaoInvalidar)  # Conecta o sinal para habilitar botão Inválido
        self.bot.start()

    #Coletar as informações do site
    def coletarInfo(self, alerta, placa,filial, empresa, motorista):
        self.infoAlerta.setText(alerta)
        self.infoPlaca.setText(placa)
        self.infoFilial.setText(filial)
        self.infoEmpresa.setText(empresa)
        self.infoMotorista.setText(motorista)
        
        # Desabilita ambos os botões inicialmente
        # Serão habilitados apenas após todos os vídeos serem carregados
        self.btnValido.setEnabled(False)
        self.btnInvalido.setEnabled(False)
        print(">>> Botões desabilitados, aguardando carregamento dos vídeos...")
        
        # Reseta a flag de tratativa aberta
        if hasattr(self, '_tratativaAberta'):
            delattr(self, '_tratativaAberta')
        
        self.pedirTratativas()
    
    def habilitarBotaoInvalidar(self):
        """Habilita ambos os botões após todos os vídeos serem carregados"""
        self.btnValido.setEnabled(True)
        self.btnInvalido.setEnabled(True)
        print(">>> Botões Válido e Inválido habilitados - Todos os vídeos foram carregados")

    #Atualiza o label com a quantidade de alertas já monitorados
    def atualizarColunas(self, quantidade):
        """Atualiza o label com a quantidade de alertas já monitorados"""
        self.labelColunas.setText(f"Alerta já foi visto {quantidade} vezes ")
        print(f">>> Label atualizado: {quantidade} alertas monitorados")

    #Inicia o vídeo assim que ele é baixado
    def downloadConcluido(self, diretorioFinal):
        # Armazena o caminho do vídeo atual
        self.video_atual = diretorioFinal
        self.player.setSource(QUrl.fromLocalFile(diretorioFinal))
        self.player.play()

    #Apaga o vídeo quando a tratativa é finalizada
    def apagarVideo(self):
        """Apaga o vídeo atual para liberar espaço para o próximo"""
        try:
            if self.video_atual and os.path.exists(self.video_atual):
                print(f">>> Iniciando processo de exclusão do vídeo: {self.video_atual}")
                
                # Para o player antes de apagar
                self.player.stop()
                self.player.setSource(QUrl())
                
                # Força a coleta de lixo para liberar recursos
                import gc
                gc.collect()
                
                # Usa QTimer para aguardar e tentar apagar
                from PySide6.QtCore import QTimer
                QTimer.singleShot(1000, lambda: self._tentarApagarVideo(self.video_atual))
                
                # Limpa a referência
                self.video_atual = None
                
                # Atualiza o status
                self.status_label.setText("Aguardando próximo vídeo...")
            else:
                print(">>> Nenhum vídeo para apagar")
        except Exception as e:
            print(f">>> ERRO ao apagar vídeo: {e}")
            import traceback
            traceback.print_exc()
    
    def _tentarApagarVideo(self, caminho_video):
        """Tenta apagar o vídeo com múltiplas tentativas"""
        max_tentativas = 5
        for tentativa in range(max_tentativas):
            try:
                if os.path.exists(caminho_video):
                    os.remove(caminho_video)
                    print(f">>> Vídeo apagado com sucesso: {caminho_video}")
                    return
                else:
                    print(f">>> Vídeo já não existe: {caminho_video}")
                    return
            except PermissionError as e:
                print(f">>> Tentativa {tentativa + 1}/{max_tentativas} falhou: {e}")
                if tentativa < max_tentativas - 1:
                    import time
                    time.sleep(0.5)
                else:
                    print(f">>> ERRO: Não foi possível apagar o vídeo após {max_tentativas} tentativas")
            except Exception as e:
                print(f">>> ERRO inesperado ao apagar vídeo: {e}")
                break

    #Tratativas do alerta quando o botão de válidar é apertado
    def abrirTratativa(self):
        if hasattr(self, '_tratativaAberta'):
            return
        self._tratativaAberta = True
        
        # Desabilita os botões após clicar
        self.desabilitarBotoesAcao()
        
        self.containerT.show()
        self.containerR.show()
    
    def clickInvalidar(self):
        """Método chamado quando o botão Inválido é clicado"""
        # Desabilita os botões imediatamente
        self.desabilitarBotoesAcao()
        
        # Chama o método do bot
        if self.bot:
            self.bot.clickInvalidar()
    
    def desabilitarBotoesAcao(self):
        """Desabilita os botões Válido e Inválido"""
        self.btnValido.setEnabled(False)
        self.btnInvalido.setEnabled(False)
        print(">>> Botões de ação desabilitados")
    
    def habilitarBotoesAcao(self):
        """Habilita os botões Válido e Inválido"""
        self.btnValido.setEnabled(True)
        self.btnInvalido.setEnabled(True)
        print(">>> Botões de ação habilitados")  

    def sincronizarSelecao(self, valor: str):
        print(">>> sincronizarSelecao chamado:", valor)
        
        # Primeiro oculta todos os botões
        self.ocultarTodosBotoes()
        
        # Depois mostra os botões apropriados baseado na seleção
        if valor == "Conduta - Política de Consequência + Pontos no D-OLHO":
            self.mostrarConduta()
        elif valor == "Ausência - Solicitar ajuste - Gestão de Equipamentos CCI":
            self.mostrarAusencia()
        
        # Sincroniza com o bot
        if self.bot:
            self.bot.clickSelecao(valor, janela_callback=self)
        
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

    def mostrarConduta(self):
        # Oculta botões de ausência primeiro
        self.cameraDesajustada.hide()
        self.cameraEscura.hide()
        self.cameraDefeito.hide()
        # Mostra botões de conduta
        self.celular.show()
        self.cigarro.show()
        self.cameraManipulada.show()
        print(">>> Botões de conduta exibidos")

    def mostrarAusencia(self):
        # Oculta botões de conduta primeiro
        self.celular.hide()
        self.cigarro.hide()
        self.cameraManipulada.hide()
        # Mostra botões de ausência
        self.cameraDesajustada.show()
        self.cameraEscura.show()
        self.cameraDefeito.show()
        print(">>> Botões de ausência exibidos")
    
    def ocultarTodosBotoes(self):
        # Oculta todos os botões de escolha
        self.celular.hide()
        self.cigarro.hide()
        self.cameraManipulada.hide()
        self.cameraDesajustada.hide()
        self.cameraEscura.hide()
        self.cameraDefeito.hide()

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