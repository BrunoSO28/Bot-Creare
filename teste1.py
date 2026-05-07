import sys
import asyncio
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout,
    QWidget, QPushButton, QTextEdit
)
from playwright.async_api import async_playwright


class PlaywrightWorker(QThread):
    finished_signal = Signal(str)
    log_signal = Signal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._loop = None
        self._page = None

    # ── Método público chamado pela UI ──────────────────────────────────────
    def click_element(self, selector: str):
        """Agenda um clique no seletor a partir da thread principal."""
        if self._loop and self._page:
            asyncio.run_coroutine_threadsafe(
                self._do_click(selector), self._loop
            )

    async def _do_click(self, selector: str):
        try:
            await self._page.click(selector)
            self.log_signal.emit(f"Clicou em: {selector}")
        except Exception as e:
            self.log_signal.emit(f"Erro ao clicar: {e}")

    # ── Loop principal do Playwright ────────────────────────────────────────
    async def run_playwright(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            self._page = await browser.new_page()

            await self._page.goto(self.url)
            title = await self._page.title()
            self.log_signal.emit(f"Página carregada: {title}")

            # Mantém o browser aberto até a thread ser interrompida
            while not self.isInterruptionRequested():
                await asyncio.sleep(0.1)

            await browser.close()

    def run(self):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self.run_playwright())
        self.finished_signal.emit("Browser fechado.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySide6 + Playwright")
        self.worker = None

        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)

        self.btn_open = QPushButton("Abrir Google")
        self.btn_open.clicked.connect(self.start_browser)

        # Botão da UI que clica no botão "Pesquisa Google"
        self.btn_click = QPushButton('Clicar em "Pesquisa Google"')
        self.btn_click.clicked.connect(self.click_search_button)
        self.btn_click.setEnabled(False)

        self.btn_close = QPushButton("Fechar Browser")
        self.btn_close.clicked.connect(self.close_browser)
        self.btn_close.setEnabled(False)

        layout.addWidget(self.text_area)
        layout.addWidget(self.btn_open)
        layout.addWidget(self.btn_click)
        layout.addWidget(self.btn_close)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_browser(self):
        self.btn_open.setEnabled(False)
        self.btn_click.setEnabled(True)
        self.btn_close.setEnabled(True)

        self.worker = PlaywrightWorker("https://www.google.com")
        self.worker.log_signal.connect(self.log)
        self.worker.finished_signal.connect(self.on_finished)
        self.worker.start()

    def click_search_button(self):
        if self.worker:
            # Seletor CSS do botão "Pesquisa Google"
            self.worker.click_element('input[name="btnK"]')

    def close_browser(self):
        if self.worker:
            self.worker.requestInterruption()
            self.btn_click.setEnabled(False)
            self.btn_close.setEnabled(False)

    def on_finished(self, msg):
        self.log(msg)
        self.btn_open.setEnabled(True)

    def log(self, msg):
        self.text_area.append(msg)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())