# botcreare_ui.py
# ─────────────────────────────────────────────────────────────────────────────
# UI redesenhada para o BotCreare.
# Uso: substitua as classes janelaLogin e janelaPrincipal no arquivo original
# por este módulo, mantendo a classe PlayWrightBot intacta.
#
# No seu arquivo principal, troque:
#   class janelaLogin(QMainWindow): ...
#   class janelaPrincipal(QMainWindow): ...
# por:
#   from botcreare_ui import janelaLogin, janelaPrincipal, STYLESHEET
# ─────────────────────────────────────────────────────────────────────────────

from PySide6.QtWidgets import (
    QApplication, QCompleter, QMainWindow, QWidget, QDialog,
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit,
    QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QCheckBox, QFrame, QMessageBox,
)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import (
    QSettings, QStringListModel, QUrl, Qt, QMetaObject, QTimer, Signal,
)
from PySide6.QtGui import QFont, QIcon, QPixmap
import asyncio, os

# ── Paleta ────────────────────────────────────────────────────────────────────
BG0, BG1, BG2, BG3 = "#0d0f12", "#141720", "#1c2030", "#232840"
TEXT1, TEXT2, TEXT3 = "#e8eaf0", "#8b90a8", "#555a70"
ACCENT, GREEN, RED, AMBER = "#3b82f6", "#22c55e", "#ef4444", "#f59e0b"
MONO, SANS = "'IBM Plex Mono', 'Consolas', monospace", "'IBM Plex Sans', 'Segoe UI', sans-serif"

STYLESHEET = f"""
* {{ font-family: {SANS}; }}
QMainWindow, QWidget {{ background: {BG0}; color: {TEXT1}; }}

/* ── Topbar ── */
#topbar {{ background: {BG1}; border-bottom: 1px solid rgba(255,255,255,.07); }}
#logoLabel {{ font-family: {MONO}; font-size: 12px; font-weight: 600; color: {ACCENT}; }}
#clockLabel {{ font-family: {MONO}; font-size: 11px; color: {TEXT2}; }}
#sessionLabel {{ font-family: {MONO}; font-size: 11px; color: {GREEN}; }}
#topPill {{ font-family: {MONO}; font-size: 10px; font-weight: 600;
            border-radius: 3px; padding: 2px 8px; }}

/* ── Panels ── */
#panelLeft, #panelRight {{ background: {BG1}; border: 1px solid rgba(255,255,255,.07); }}
#panelHeader {{ background: {BG1}; border-bottom: 1px solid rgba(255,255,255,.07); }}
#panelHeaderLabel {{ font-family: {MONO}; font-size: 10px; font-weight: 600;
                     color: {TEXT3}; letter-spacing: 2px; }}

/* ── Centre ── */
#panelCenter {{ background: {BG0}; }}
#camTabBar {{ background: {BG1}; border-bottom: 1px solid rgba(255,255,255,.07); }}
#camTab {{ background: transparent; color: {TEXT3}; border: none;
           border-right: 1px solid rgba(255,255,255,.07);
           font-family: {MONO}; font-size: 11px; padding: 6px 16px; min-width: 60px; }}
#camTab:hover {{ color: {TEXT2}; background: {BG2}; }}
#camTab[active="true"] {{ color: {ACCENT}; background: {BG0};
                           border-bottom: 2px solid {ACCENT}; }}
#videoArea {{ background: #060810; }}

/* ── Controls bar ── */
#controlsBar {{ background: {BG1}; border-top: 1px solid rgba(255,255,255,.07); padding: 5px 8px; }}
#ctrlBtn {{ background: {BG2}; color: {TEXT1};
            border: 1px solid rgba(255,255,255,.1); border-radius: 4px;
            font-family: {MONO}; font-size: 11px;
            min-width: 30px; max-width: 36px; min-height: 28px; max-height: 28px; }}
#ctrlBtn:hover {{ background: {BG3}; border-color: {ACCENT}; }}
#viewCountLabel {{ font-family: {MONO}; font-size: 10px; color: {ACCENT};
                   background: rgba(59,130,246,.08);
                   border: 1px solid rgba(59,130,246,.2); border-radius: 3px; padding: 3px 8px; }}

/* ── Actions bar ── */
#actionsBar {{ background: {BG1}; border-top: 1px solid rgba(255,255,255,.07); padding: 8px 10px; }}
#btnValido  {{ background: rgba(34,197,94,.13); color: #4ade80;
               border: 1px solid rgba(34,197,94,.28); border-radius: 5px;
               font-size: 12px; font-weight: 600; min-height: 36px; }}
#btnValido:hover  {{ background: rgba(34,197,94,.22); }}
#btnValido:disabled  {{ background: rgba(34,197,94,.04); color: rgba(74,222,128,.25);
                        border-color: rgba(34,197,94,.08); }}
#btnInvalido {{ background: rgba(239,68,68,.10); color: #f87171;
                border: 1px solid rgba(239,68,68,.22); border-radius: 5px;
                font-size: 12px; font-weight: 600; min-height: 36px; }}
#btnInvalido:hover {{ background: rgba(239,68,68,.20); }}
#btnInvalido:disabled {{ background: rgba(239,68,68,.04); color: rgba(248,113,113,.25);
                          border-color: rgba(239,68,68,.08); }}

/* ── Alert card ── */
#alertCard {{ background: {BG2}; border: 1px solid rgba(255,255,255,.10); border-radius: 6px; margin: 8px; }}
#alertTypeLabel {{ font-size: 13px; font-weight: 700; color: {AMBER}; padding: 8px 10px 4px; }}
#infoLabel {{ font-family: {MONO}; font-size: 9px; font-weight: 600;
              color: {TEXT3}; letter-spacing: 2px; padding: 0; }}
#infoVal   {{ font-size: 11px; font-weight: 500; color: {TEXT1}; padding: 0 0 4px; }}

/* ── Counter ── */
#counterBox {{ background: rgba(59,130,246,.06); border: 1px solid rgba(59,130,246,.15);
               border-radius: 4px; margin: 2px 8px 4px; padding: 5px 10px; }}
#counterLabel {{ font-family: {MONO}; font-size: 10px; color: {TEXT2}; }}
#counterVal   {{ font-family: {MONO}; font-size: 15px; font-weight: 600; color: {ACCENT}; }}

/* ── Tratativa ── */
#secLabel {{ font-family: {MONO}; font-size: 9px; font-weight: 600;
             color: {TEXT3}; letter-spacing: 2px; padding: 4px 0 3px; }}
QComboBox {{ background: {BG2}; color: {TEXT1};
             border: 1px solid rgba(255,255,255,.10); border-radius: 4px;
             padding: 5px 8px; font-size: 11px; min-height: 28px; }}
QComboBox:focus {{ border-color: {ACCENT}; }}
QComboBox::drop-down {{ border: none; width: 18px; }}
QComboBox QAbstractItemView {{ background: {BG2}; color: {TEXT1};
    border: 1px solid rgba(255,255,255,.10);
    selection-background-color: rgba(59,130,246,.25); outline: none; }}
#subBtn {{ background: {BG2}; color: {TEXT2};
           border: 1px solid rgba(255,255,255,.08); border-radius: 4px;
           font-size: 10px; padding: 5px 4px; min-height: 26px; }}
#subBtn:hover {{ background: {BG3}; color: {TEXT1}; border-color: {ACCENT}; }}
#btnMonitor {{ background: rgba(59,130,246,.10); color: #93c5fd;
               border: 1px solid rgba(59,130,246,.22); border-radius: 4px;
               font-size: 10px; font-weight: 600; min-height: 30px; }}
#btnMonitor:hover {{ background: rgba(59,130,246,.20); }}
#btnReport  {{ background: rgba(245,158,11,.10); color: #fcd34d;
               border: 1px solid rgba(245,158,11,.22); border-radius: 4px;
               font-size: 10px; font-weight: 600; min-height: 30px; }}
#btnReport:hover {{ background: rgba(245,158,11,.20); }}

/* ── Risk filters ── */
#riskFiltersBox {{ border-top: 1px solid rgba(255,255,255,.07); padding: 6px 8px; }}
QCheckBox {{ background: transparent; }}
QCheckBox::indicator {{ width: 14px; height: 14px;
    border: 1px solid rgba(255,255,255,.2); border-radius: 3px; background: {BG2}; }}
QCheckBox::indicator:checked {{ background: {ACCENT}; border-color: {ACCENT}; }}

/* ── History table ── */
QTableWidget {{ background: transparent; color: {TEXT1};
                gridline-color: rgba(255,255,255,.04); border: none; font-size: 11px; }}
QTableWidget::item {{ padding: 5px 6px; border-bottom: 1px solid rgba(255,255,255,.04); }}
QTableWidget::item:selected {{ background: rgba(59,130,246,.15); color: {TEXT1}; }}
QHeaderView::section {{ background: {BG2}; color: {TEXT3};
    font-family: {MONO}; font-size: 9px; font-weight: 600; letter-spacing: 1px;
    border: none; border-bottom: 1px solid rgba(255,255,255,.07); padding: 5px 6px; }}
QScrollBar:vertical {{ background: transparent; width: 4px; }}
QScrollBar::handle:vertical {{ background: rgba(255,255,255,.15); border-radius: 2px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

/* ── Loading ── */
#loadingLabel {{ color: {TEXT3}; font-family: {MONO}; font-size: 12px; padding: 12px; }}
QProgressBar {{ background: {BG2}; border: none; border-radius: 2px; max-height: 3px; }}
QProgressBar::chunk {{ background: {ACCENT}; border-radius: 2px; }}

/* ── Login ── */
#loginTitle {{ font-size: 13px; font-weight: 700; color: {TEXT1}; padding: 8px 0; }}
QLineEdit {{ background: {BG2}; color: {TEXT1};
             border: 1px solid rgba(255,255,255,.10); border-radius: 4px;
             padding: 6px 10px; font-size: 12px; min-height: 30px; }}
QLineEdit:focus {{ border-color: {ACCENT}; }}
#btnEntrar {{ background: {ACCENT}; color: white; border: none; border-radius: 4px;
              font-size: 12px; font-weight: 600; min-height: 34px; }}
#btnEntrar:hover {{ background: #2563eb; }}
#btnEntrar:disabled {{ background: rgba(59,130,246,.3); color: rgba(255,255,255,.4); }}

/* ── Dialogs ── */
QDialog    {{ background: {BG1}; color: {TEXT1}; }}
QMessageBox {{ background: {BG1}; color: {TEXT1}; }}
QMessageBox QPushButton {{ background: {BG2}; color: {TEXT1};
    border: 1px solid rgba(255,255,255,.1); border-radius: 4px;
    padding: 4px 16px; min-height: 28px; }}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────
def _sep_h():
    """Linha separadora horizontal."""
    f = QFrame()
    f.setFrameShape(QFrame.HLine)
    f.setStyleSheet("background: rgba(255,255,255,.06); max-height:1px; border:none;")
    return f

def _sep_v():
    """Linha separadora vertical (topbar)."""
    f = QFrame()
    f.setFrameShape(QFrame.VLine)
    f.setFixedWidth(1)
    f.setStyleSheet("background: rgba(255,255,255,.1); border:none;")
    return f

def _ajustar_janela(win, largura_pct=75, altura_pct=90):
    """Redimensiona qualquer QMainWindow como % da tela disponível."""
    tela = QApplication.primaryScreen()
    if tela:
        geo = tela.availableGeometry()
        w = int(geo.width() * largura_pct / 100)
        h = int(geo.height() * altura_pct / 100)
        x = geo.x() + (geo.width() - w) // 2
        y = geo.y() + (geo.height() - h) // 2
        win.setGeometry(x, y, w, h)

def resource_path(relative_path):
    import sys
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


# ── Janela de Login ───────────────────────────────────────────────────────────
class janelaLogin(QMainWindow):
    sinalLogin  = Signal(str, str, str)
    sinalCodigo = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BotCreare — Login")
        self.setWindowIcon(QIcon(resource_path("icone_creare.ico")))
        self.setStyleSheet(STYLESHEET)
        _ajustar_janela(self, largura_pct=28, altura_pct=42)

        self.settings = QSettings("MinhaApp", "RevisaoVideo")

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Mini topbar
        tb = QWidget(); tb.setObjectName("topbar"); tb.setFixedHeight(36)
        tbl = QHBoxLayout(tb); tbl.setContentsMargins(14, 0, 14, 0)
        logo = QLabel("⬡  BOTCREARE — ACESSO"); logo.setObjectName("logoLabel")
        tbl.addWidget(logo)
        root.addWidget(tb)

        # Form
        fw = QWidget()
        fl = QVBoxLayout(fw)
        fl.setContentsMargins(32, 28, 32, 28); fl.setSpacing(12); fl.setAlignment(Qt.AlignTop)

        title = QLabel("Entre com sua conta CREARE")
        title.setObjectName("loginTitle"); title.setAlignment(Qt.AlignCenter)
        fl.addWidget(title); fl.addSpacing(6)

        self.inputEmail = QLineEdit(); self.inputEmail.setPlaceholderText("E-mail")
        self.inputSenha = QLineEdit(); self.inputSenha.setPlaceholderText("Senha")
        self.inputSenha.setEchoMode(QLineEdit.Password)
        fl.addWidget(self.inputEmail); fl.addWidget(self.inputSenha)

        self.labelCodigo = QLabel("Código de autenticação (e-mail):")
        self.labelCodigo.setStyleSheet(f"color:{TEXT2}; font-size:11px; background:transparent;")
        self.labelCodigo.hide()
        self.inputCodigo = QLineEdit(); self.inputCodigo.setPlaceholderText("Código"); self.inputCodigo.hide()
        fl.addWidget(self.labelCodigo); fl.addWidget(self.inputCodigo)

        self.btnEntrar = QPushButton("Entrar"); self.btnEntrar.setObjectName("btnEntrar")
        self.btnEntrar.clicked.connect(self.submitLogin)
        fl.addWidget(self.btnEntrar)
        root.addWidget(fw)

        self._setup_autocomplete()
        self._load_last_login()

    # ── slots ──
    def mostrarCampoCodigo(self):
        self.labelCodigo.show(); self.inputCodigo.show()
        self.inputCodigo.setEnabled(True); self.btnEntrar.setEnabled(True)
        self.btnEntrar.setText("Confirmar código")
        self.btnEntrar.clicked.disconnect(); self.btnEntrar.clicked.connect(self.submitCodigo)
        self.inputCodigo.setFocus()

    def submitCodigo(self):
        codigo = self.inputCodigo.text().strip()
        if not codigo:
            QMessageBox.warning(self, "Erro", "Digite o código de autenticação."); return
        self.sinalCodigo.emit(codigo)
        self.btnEntrar.setText("Aguardando...")

    def submitLogin(self):
        email = self.inputEmail.text().strip(); senha = self.inputSenha.text().strip()
        if not email or not senha:
            QMessageBox.warning(self, "Erro", "Preencha e-mail e senha."); return
        self._save_account(email, senha)
        self.sinalLogin.emit(email, senha, "")
        self.btnEntrar.setEnabled(False); self.btnEntrar.setText("Entrando...")

    def _setup_autocomplete(self):
        contas = self.settings.value("contas", {}) or {}
        self._model = QStringListModel(list(contas.keys()))
        comp = QCompleter(self._model, self)
        comp.setCaseSensitivity(Qt.CaseInsensitive); comp.setFilterMode(Qt.MatchContains)
        self.inputEmail.setCompleter(comp)
        comp.activated.connect(self._fill_password)
        self.inputEmail.editingFinished.connect(lambda: self._fill_password(self.inputEmail.text()))

    def _fill_password(self, email):
        contas = self.settings.value("contas", {}) or {}
        if email in contas: self.inputSenha.setText(contas[email])

    def _load_last_login(self):
        last = self.settings.value("ultimo_login", "")
        if last: self.inputEmail.setText(last); self._fill_password(last)

    def _save_account(self, email, senha):
        contas = self.settings.value("contas", {}) or {}
        contas[email] = senha
        self.settings.setValue("contas", contas); self.settings.setValue("ultimo_login", email)
        self._model.setStringList(list(contas.keys()))


# ── Janela Principal ──────────────────────────────────────────────────────────
class janelaPrincipal(QMainWindow):
    sinalCheck = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BotCreare")
        self.setWindowIcon(QIcon(resource_path("icone_creare.ico")))
        self.setStyleSheet(STYLESHEET)
        self.video_atual = None
        self.videos = {}
        self.janelaQr = None
        self.ajustarJanelaAoMonitor(largura_pct=75, altura_pct=90)

        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setContentsMargins(0,0,0,0); root.setSpacing(0)

        self._build_topbar(root)

        body = QWidget(); bl = QHBoxLayout(body); bl.setContentsMargins(0,0,0,0); bl.setSpacing(0)
        self._build_left(bl)
        self._build_center(bl)
        self._build_right(bl)
        root.addWidget(body, stretch=1)

        self._iniciarThread()

        self._clock = QTimer(self); self._clock.timeout.connect(self._tick); self._clock.start(1000)
        self._tick()

    # ── TOPBAR ────────────────────────────────────────────────────────────────
    def _build_topbar(self, root):
        tb = QWidget(); tb.setObjectName("topbar"); tb.setFixedHeight(36)
        l = QHBoxLayout(tb); l.setContentsMargins(14,0,14,0); l.setSpacing(14)

        logo = QLabel("⬡  BOTCREARE — FADIGA"); logo.setObjectName("logoLabel"); l.addWidget(logo)
        l.addWidget(_sep_v())
        self.clockLabel = QLabel("00:00:00"); self.clockLabel.setObjectName("clockLabel"); l.addWidget(self.clockLabel)
        l.addWidget(_sep_v())
        sess = QLabel("● SESSÃO ATIVA"); sess.setObjectName("sessionLabel"); l.addWidget(sess)
        l.addStretch()

        # mini risk pills (topbar)
        self._pill_alto  = self._make_pill("0 alto",  "rgba(239,68,68,.13)",  "#fca5a5", "rgba(239,68,68,.28)")
        self._pill_medio = self._make_pill("0 médio", "rgba(245,158,11,.13)", "#fcd34d", "rgba(245,158,11,.28)")
        self._pill_baixo = self._make_pill("1 baixo", "rgba(59,130,246,.13)", "#93c5fd", "rgba(59,130,246,.28)")
        for p in [self._pill_alto, self._pill_medio, self._pill_baixo]: l.addWidget(p)
        root.addWidget(tb)

    def _make_pill(self, text, bg, fg, border):
        lbl = QLabel(text); lbl.setObjectName("topPill")
        lbl.setStyleSheet(f"background:{bg}; color:{fg}; border:1px solid {border}; border-radius:3px; padding:2px 8px; font-family:{MONO}; font-size:10px; font-weight:600;")
        return lbl

    def _tick(self):
        from datetime import datetime
        self.clockLabel.setText(datetime.now().strftime("%H:%M:%S"))

    # ── LEFT PANEL ────────────────────────────────────────────────────────────
    def _build_left(self, parent):
        p = QWidget(); p.setObjectName("panelLeft")
        p.setMinimumWidth(190); p.setMaximumWidth(250)
        p.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        l = QVBoxLayout(p); l.setContentsMargins(0,0,0,0); l.setSpacing(0)

        hdr = QWidget(); hdr.setObjectName("panelHeader"); hdr.setFixedHeight(32)
        hl = QHBoxLayout(hdr); hl.setContentsMargins(10,0,10,0)
        hl.addWidget(self._panel_label("HISTÓRICO DE ALERTAS"))
        l.addWidget(hdr)

        self._no_hist = QLabel("Nenhum alerta anterior")
        self._no_hist.setObjectName("loadingLabel"); self._no_hist.setAlignment(Qt.AlignCenter)
        l.addWidget(self._no_hist)

        self.tabela = QTableWidget(0, 3)
        self.tabela.setHorizontalHeaderLabels(["Tipo Alerta", "Quando", "Tratativa"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.verticalHeader().setVisible(False)
        self.tabela.setShowGrid(False)
        self.tabela.hide()
        l.addWidget(self.tabela)

        # Keep reference for atualizarTabela
        self.layoutTabela = l
        parent.addWidget(p, stretch=3)

    # ── CENTER PANEL ──────────────────────────────────────────────────────────
    def _build_center(self, parent):
        p = QWidget(); p.setObjectName("panelCenter")
        p.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        l = QVBoxLayout(p); l.setContentsMargins(0,0,0,0); l.setSpacing(0)

        # Cam tabs
        cam_bar = QWidget(); cam_bar.setObjectName("camTabBar"); cam_bar.setFixedHeight(32)
        cbl = QHBoxLayout(cam_bar); cbl.setContentsMargins(0,0,0,0); cbl.setSpacing(0)
        self._cam_tabs = []
        for name in ["CH1", "CH2", "CH5"]:
            btn = QPushButton(name); btn.setObjectName("camTab"); btn.setCheckable(True)
            btn.clicked.connect(lambda _, n=name: self._switch_cam(n))
            cbl.addWidget(btn); self._cam_tabs.append((name, btn))
        cbl.addStretch()
        self._cam_tabs[0][1].setChecked(True); self._cam_tabs[0][1].setProperty("active","true")
        l.addWidget(cam_bar)

        # Loading bar
        self.loadingBar = QProgressBar(); self.loadingBar.setRange(0,0)
        self.loadingBar.setTextVisible(False); self.loadingBar.setFixedHeight(3); self.loadingBar.hide()
        l.addWidget(self.loadingBar)

        # Loading label
        self.loadingWidget = QLabel("⬡  Aguardando alertas...")
        self.loadingWidget.setObjectName("loadingLabel"); self.loadingWidget.setAlignment(Qt.AlignCenter); self.loadingWidget.hide()
        l.addWidget(self.loadingWidget)

        # Video
        self.caixaVideo = QVideoWidget(); self.caixaVideo.setObjectName("videoArea")
        self.caixaVideo.setMinimumSize(460, 320)
        self.caixaVideo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        l.addWidget(self.caixaVideo, stretch=1)
        self.player = QMediaPlayer(self); self.player.setVideoOutput(self.caixaVideo)
        self.player.setLoops(QMediaPlayer.Loops.Infinite)

        # Controls bar
        cb = QWidget(); cb.setObjectName("controlsBar"); cb.setFixedHeight(38)
        cbl2 = QHBoxLayout(cb); cbl2.setContentsMargins(8,4,8,4); cbl2.setSpacing(5)
        for sym, fn in [("▶", self.player.play), ("⏸", self.player.pause),
                        ("1×", lambda: self.player.setPlaybackRate(1.0)),
                        ("2×", lambda: self.player.setPlaybackRate(2.0))]:
            b = QPushButton(sym); b.setObjectName("ctrlBtn"); b.clicked.connect(fn); cbl2.addWidget(b)
        cbl2.addStretch()
        self.labelColunas = QLabel(); self.labelColunas.setObjectName("viewCountLabel"); cbl2.addWidget(self.labelColunas)
        l.addWidget(cb)

        # Actions bar
        ab = QWidget(); ab.setObjectName("actionsBar"); ab.setFixedHeight(52)
        abl = QHBoxLayout(ab); abl.setContentsMargins(10,8,10,8); abl.setSpacing(8)
        self.btnValido = QPushButton("✓  Válido"); self.btnValido.setObjectName("btnValido")
        self.btnValido.clicked.connect(self.abrirTratativa)
        self.btnInvalido = QPushButton("✕  Inválido"); self.btnInvalido.setObjectName("btnInvalido")
        self.btnInvalido.clicked.connect(self.clickInvalidar)
        abl.addWidget(self.btnValido); abl.addWidget(self.btnInvalido)
        l.addWidget(ab)

        parent.addWidget(p, stretch=5)

    def _switch_cam(self, name):
        for n, btn in self._cam_tabs:
            active = (n == name)
            btn.setChecked(active); btn.setProperty("active", "true" if active else "false")
            btn.style().unpolish(btn); btn.style().polish(btn)
        self.trocarVideo({"CH1":"Câmera 1","CH2":"Câmera 2","CH5":"Câmera 3"}.get(name,"Câmera 1"))

    # ── RIGHT PANEL ───────────────────────────────────────────────────────────
    def _build_right(self, parent):
        p = QWidget(); p.setObjectName("panelRight")
        p.setMinimumWidth(220); p.setMaximumWidth(270)
        p.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        l = QVBoxLayout(p); l.setContentsMargins(0,0,0,0); l.setSpacing(0)

        # Header
        hdr = QWidget(); hdr.setObjectName("panelHeader"); hdr.setFixedHeight(32)
        hl = QHBoxLayout(hdr); hl.setContentsMargins(10,0,10,0)
        hl.addWidget(self._panel_label("ALERTA ATUAL"))
        l.addWidget(hdr)

        # Alert card
        card = QWidget(); card.setObjectName("alertCard")
        cl = QVBoxLayout(card); cl.setContentsMargins(10,6,10,8); cl.setSpacing(0)
        self.infoAlerta = QLabel("—"); self.infoAlerta.setObjectName("alertTypeLabel"); cl.addWidget(self.infoAlerta)
        cl.addWidget(_sep_h())
        for label_txt, attr in [("PLACA / PREFIXO","infoPlaca"),("EMPRESA","infoEmpresa"),
                                  ("FILIAL","infoFilial"),("MOTORISTA","infoMotorista"),("DATA DO OCORRIDO","infoDataHora")]:
            lbl = QLabel(label_txt); lbl.setObjectName("infoLabel")
            val = QLabel("—"); val.setObjectName("infoVal"); val.setWordWrap(True)
            setattr(self, attr, val)
            cl.addWidget(lbl); cl.addWidget(val); cl.addWidget(_sep_h())
        l.addWidget(card)

        # Counter
        ctr = QWidget(); ctr.setObjectName("counterBox")
        ctl = QHBoxLayout(ctr); ctl.setContentsMargins(10,4,10,4)
        lbl_c = QLabel("Alertas tratados hoje"); lbl_c.setObjectName("counterLabel")
        self.labelContador = QLabel("0"); self.labelContador.setObjectName("counterVal")
        ctl.addWidget(lbl_c); ctl.addStretch(); ctl.addWidget(self.labelContador)
        l.addWidget(ctr)

        # Tratativa container (hidden)
        self.containerT = QWidget(); self.containerT.hide()
        ctl2 = QVBoxLayout(self.containerT); ctl2.setContentsMargins(8,4,8,4); ctl2.setSpacing(5)
        ctl2.addWidget(self._sec_label("TRATATIVA"))
        self.tratativas = QComboBox(); self.tratativas.setPlaceholderText("Selecione a tratativa...")
        self.tratativas.currentTextChanged.connect(self.sincronizarSelecao)
        ctl2.addWidget(self.tratativas)

        ctl2.addWidget(self._sec_label("CONDUTA"))
        cond = QHBoxLayout(); cond.setSpacing(5)
        self.cigarro          = self._sub_btn("Cigarro",        lambda: self.bot.clickConduta("Cigarro"))
        self.celular          = self._sub_btn("Celular",        lambda: self.bot.clickConduta("Celular"))
        self.cameraManipulada = self._sub_btn("Cam. Manipulada",lambda: self.bot.clickConduta("Câmera Manipulada"))
        for b in [self.cigarro, self.celular, self.cameraManipulada]:
            cond.addWidget(b); b.hide()
        ctl2.addLayout(cond)

        ctl2.addWidget(self._sec_label("AUSÊNCIA"))
        aus = QHBoxLayout(); aus.setSpacing(5)
        self.cameraDesajustada = self._sub_btn("Desajustada", lambda: self.bot.clickAusencia("Câmera Desajustada"))
        self.cameraEscura      = self._sub_btn("Escura",      lambda: self.bot.clickAusencia("Câmera Escura"))
        self.cameraDefeito     = self._sub_btn("Com Defeito", lambda: self.bot.clickAusencia("Câmera com Defeito"))
        for b in [self.cameraDesajustada, self.cameraEscura, self.cameraDefeito]:
            aus.addWidget(b); b.hide()
        ctl2.addLayout(aus)
        l.addWidget(self.containerT)

        # Report container (hidden)
        self.containerR = QWidget(); self.containerR.hide()
        crl = QVBoxLayout(self.containerR); crl.setContentsMargins(8,2,8,4); crl.setSpacing(5)
        crl.addWidget(self._sec_label("AÇÃO"))
        rep = QHBoxLayout(); rep.setSpacing(5)
        self.reportado = QPushButton("Monitorado");       self.reportado.setObjectName("btnMonitor")
        self.operacao  = QPushButton("Reportar Op.");     self.operacao.setObjectName("btnReport")
        self.reportado.clicked.connect(lambda: self.bot.clickMonitorado())
        self.operacao.clicked.connect(lambda: self.bot.clickReportarOperacao())
        rep.addWidget(self.reportado); rep.addWidget(self.operacao); crl.addLayout(rep)
        l.addWidget(self.containerR)

        l.addStretch()

        # Risk filters
        rf = QWidget(); rf.setObjectName("riskFiltersBox")
        rfl = QVBoxLayout(rf); rfl.setContentsMargins(0,4,0,4); rfl.setSpacing(2)
        rfl.addWidget(self._sec_label("FILTRO DE RISCO"))
        risk_data = [
            ("riskAltoLabel",  "#fca5a5", "0 Alertas — ALTO RISCO",  "checkAltoRisco"),
            ("riskMedioLabel", "#fcd34d", "0 Alertas — MÉDIO RISCO", "checkMedioRisco"),
            ("riskBaixoLabel", "#93c5fd", "1 Alerta  — BAIXO RISCO", "checkBaixoRisco"),
        ]
        for obj, color, text, chk_attr in risk_data:
            row = QHBoxLayout(); row.setSpacing(6)
            dot = QLabel("●"); dot.setStyleSheet(f"color:{color}; font-size:9px; background:transparent;")
            lbl = QLabel(text); lbl.setStyleSheet(f"color:{color}; font-size:11px; font-weight:600; background:transparent;")
            setattr(self, obj, lbl)
            chk = QCheckBox(); setattr(self, chk_attr, chk)
            chk.stateChanged.connect(self.validarRisco)
            row.addWidget(dot); row.addWidget(lbl, stretch=1); row.addWidget(chk)
            rfl.addLayout(row)
        l.addWidget(rf)

        parent.addWidget(p, stretch=3)

    # ── Utility builders ──────────────────────────────────────────────────────
    def _panel_label(self, text):
        lbl = QLabel(text); lbl.setObjectName("panelHeaderLabel"); return lbl

    def _sec_label(self, text):
        lbl = QLabel(text); lbl.setObjectName("secLabel"); return lbl

    def _sub_btn(self, text, slot):
        btn = QPushButton(text); btn.setObjectName("subBtn"); btn.clicked.connect(slot); return btn

    # ── Thread + signal wiring ────────────────────────────────────────────────
    def _iniciarThread(self):
        # Import bot from original file at runtime to avoid circular import
        try:
            from __main__ import PlayWrightBot
        except ImportError:
            from botcreare import PlayWrightBot  # fallback if used as module

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

    # ── Slots (mesma lógica do original) ─────────────────────────────────────
    def coletarInfo(self, alerta, placa, filial, empresa, motorista, dataHora):
        self.infoAlerta.setText(alerta)
        self.infoPlaca.setText(placa); self.infoFilial.setText(filial)
        self.infoEmpresa.setText(empresa); self.infoMotorista.setText(motorista)
        self.infoDataHora.setText(dataHora)
        self.btnValido.setEnabled(False); self.btnInvalido.setEnabled(False)
        self.habilitarBotoesAcao()
        if hasattr(self, '_tratativaAberta'): delattr(self, '_tratativaAberta')
        self.containerT.hide(); self.containerR.hide()
        self.pedirTratativas()

    def habilitarBotaoInvalidar(self):
        self.btnValido.setEnabled(True); self.btnInvalido.setEnabled(True)

    def atualizarColunas(self, n):
        self.labelColunas.setText(f"  visto {n}× neste turno  ")

    def atualizarContador(self, n):
        self.labelContador.setText(str(n))

    def atualizarTabela(self, linhas, dados):
        if linhas == 0:
            self.tabela.hide(); self._no_hist.show()
        else:
            self._no_hist.hide(); self.tabela.show(); self.tabela.setRowCount(linhas)
            for i, (tipo, quando, trat) in enumerate(dados):
                self.tabela.setItem(i, 0, QTableWidgetItem(tipo))
                self.tabela.setItem(i, 1, QTableWidgetItem(quando))
                self.tabela.setItem(i, 2, QTableWidgetItem(trat))

    def downloadConcluido(self, v1, v2, v3):
        self.videos = {"Câmera 1": v1, "Câmera 2": v2, "Câmera 3": v3}
        active = next((n for n, btn in self._cam_tabs if btn.isChecked()), "CH1")
        self.trocarVideo({"CH1":"Câmera 1","CH2":"Câmera 2","CH5":"Câmera 3"}.get(active,"Câmera 1"))

    def trocarVideo(self, nome):
        caminho = self.videos.get(nome)
        if caminho and os.path.exists(caminho):
            self.video_atual = caminho
            self.player.setSource(QUrl.fromLocalFile(caminho)); self.player.play()

    def liberarVideoAtual(self):
        try:
            self.player.stop(); self.player.setSource(QUrl())
            pasta = os.path.join(os.getcwd(), "perfil_edge_bot", "Downloads")
            if os.path.exists(pasta):
                import time
                for arq in os.listdir(pasta):
                    if arq.endswith(".mp4"):
                        path = os.path.join(pasta, arq)
                        for _ in range(3):
                            try: os.remove(path); break
                            except PermissionError: time.sleep(0.3)
            self.video_atual = None; self.videos = {}
        except Exception as e:
            print(f">>> ERRO ao liberar vídeo: {e}")
        finally:
            asyncio.run_coroutine_threadsafe(self._marcarVideoLiberado(), self.bot.loop)

    async def _marcarVideoLiberado(self):
        self.bot._video_liberado.set()

    def abrirTratativa(self):
        if hasattr(self, '_tratativaAberta'): return
        self._tratativaAberta = True
        self.desabilitarBotoesAcao(); self.containerT.show(); self.containerR.show()

    def clickInvalidar(self):
        self.desabilitarBotoesAcao()
        if self.bot: self.bot.clickInvalidar()

    def desabilitarBotoesAcao(self):
        self.btnValido.setEnabled(False); self.btnInvalido.setEnabled(False)

    def habilitarBotoesAcao(self):
        self.btnValido.setEnabled(True); self.btnInvalido.setEnabled(True)

    def sincronizarSelecao(self, valor):
        self.ocultarTodosBotoes()
        if valor == "Conduta - Política de Consequência + Pontos no D-OLHO": self.mostrarConduta()
        elif valor == "Ausência - Solicitar ajuste - Gestão de Equipamentos CCI": self.mostrarAusencia()
        if self.bot: self.bot.clickSelecao(valor)

    def listarTratativas(self, opcoes):
        self.tratativas.blockSignals(True); self.tratativas.clear()
        self.tratativas.addItems(opcoes); self.tratativas.blockSignals(False)

    def pedirTratativas(self):
        asyncio.run_coroutine_threadsafe(self.bot.coletarTratativas(), self.bot.loop)

    def mostrarConduta(self):
        for b in [self.cameraDesajustada, self.cameraEscura, self.cameraDefeito]: b.hide()
        for b in [self.cigarro, self.celular, self.cameraManipulada]: b.show()

    def mostrarAusencia(self):
        for b in [self.cigarro, self.celular, self.cameraManipulada]: b.hide()
        for b in [self.cameraDesajustada, self.cameraEscura, self.cameraDefeito]: b.show()

    def ocultarTodosBotoes(self):
        for b in [self.cigarro, self.celular, self.cameraManipulada,
                  self.cameraDesajustada, self.cameraEscura, self.cameraDefeito]: b.hide()

    def toggleLoading(self, sem_alertas):
        self.loadingWidget.setVisible(sem_alertas); self.loadingBar.setVisible(sem_alertas)
        self.caixaVideo.setVisible(not sem_alertas); self.labelColunas.setVisible(not sem_alertas)
        self.btnValido.setVisible(not sem_alertas); self.btnInvalido.setVisible(not sem_alertas)

    def reabrirLogin(self):
        self.janelaLogin2 = janelaLogin()
        self.janelaLogin2.sinalLogin.connect(self.bot.iniciarConta)
        self.janelaLogin2.sinalCodigo.connect(self.bot.enviarCodigo)
        self.bot.sinalPedirCodigo.connect(self.janelaLogin2.mostrarCampoCodigo)
        self.bot.sinalLoginOk.connect(self.janelaLogin2.close)
        self.janelaLogin2.show()

    def validarRisco(self):
        checks = [self.checkAltoRisco, self.checkMedioRisco, self.checkBaixoRisco]
        if sum(c.isChecked() for c in checks) == 3:
            for c in checks: c.blockSignals(True); c.setChecked(False); c.blockSignals(False)
            self.bot.clickCheck({"Alto":False,"Médio":False,"Baixo":False}); return
        self.bot.clickCheck({"Alto":self.checkAltoRisco.isChecked(),
                              "Médio":self.checkMedioRisco.isChecked(),
                              "Baixo":self.checkBaixoRisco.isChecked()})

    def atualizarQuantidadeAlertas(self, alto, medio, baixo):
        def _n(v, t): return f"{v} {'Alerta' if v==1 else 'Alertas'} — {t} RISCO"
        self.riskAltoLabel.setText(_n(alto,"ALTO")); self.riskMedioLabel.setText(_n(medio,"MÉDIO")); self.riskBaixoLabel.setText(_n(baixo,"BAIXO"))
        self._pill_alto.setText(f"{alto} alto"); self._pill_medio.setText(f"{medio} médio"); self._pill_baixo.setText(f"{baixo} baixo")

    def qrCode(self, dados):
        if self.janelaQr: return
        self.janelaQr = QDialog(self); self.janelaQr.setWindowTitle("Conectar WhatsApp")
        self.janelaQr.setModal(False); self.janelaQr.setStyleSheet(f"background:{BG1}; color:{TEXT1};")
        dl = QVBoxLayout(self.janelaQr); dl.setContentsMargins(30,30,30,30); dl.setSpacing(12)
        instr = QLabel("O navegador foi aberto com o QR Code.\nEscaneie pelo WhatsApp no celular.")
        instr.setAlignment(Qt.AlignCenter); instr.setFont(QFont("Segoe UI",11)); dl.addWidget(instr)
        lbl_qr = QLabel(); px = QPixmap(); px.loadFromData(dados)
        px = px.scaled(300,300,Qt.KeepAspectRatio,Qt.SmoothTransformation)
        lbl_qr.setPixmap(px); lbl_qr.setAlignment(Qt.AlignCenter); dl.addWidget(lbl_qr)
        aviso = QLabel("Fecha automaticamente quando conectar.")
        aviso.setAlignment(Qt.AlignCenter); aviso.setStyleSheet(f"color:{TEXT3}; font-size:10px;"); dl.addWidget(aviso)
        self.janelaQr.adjustSize(); self.janelaQr.show()

    def fecharQrSeAberto(self):
        if self.janelaQr:
            QMetaObject.invokeMethod(self.janelaQr, "close", Qt.QueuedConnection)
            self.janelaQr = None

    def ajustarJanelaAoMonitor(self, largura_pct=75, altura_pct=90):
        _ajustar_janela(self, largura_pct=largura_pct, altura_pct=altura_pct)
