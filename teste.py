import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QComboBox

def funcao1():
    label.setText("Botão Pressionado")
    label.adjustSize()

def funcao2():
    valorLido = caixaTexto.text()
    label.setText(valorLido)
    label.adjustSize()

def funcao3():
    valor = combo.currentText()
    label.setText(valor)
    label.adjustSize()


app = QApplication(sys.argv)

janela = QWidget()
janela.resize(800,600)
janela.setWindowTitle("Primeira Janela")

btn = QPushButton("Botão 1", janela)
btn.setGeometry(100, 100, 150, 80)
btn.setStyleSheet("background-color:white; color:black")
btn.clicked.connect(funcao1)

btn2 = QPushButton("Botão 2", janela)
btn2.setGeometry(100, 300, 150, 80)
btn2.setStyleSheet("background-color:white; color:black")
btn2.clicked.connect(funcao2)

btn3 = QPushButton("Botão 3", janela)
btn3.setGeometry(100, 500, 150, 80)
btn3.setStyleSheet("background-color:white; color:black")
btn3.clicked.connect(funcao3)

caixaTexto = QLineEdit("", janela)
caixaTexto.setGeometry(500, 300, 150, 30)

combo = QComboBox(janela)
combo.addItem("Selecione uma opção")
combo.addItem("Masculino")
combo.addItem("Feminino")
combo.addItem("Outro")
combo.move(300,30)

label = QLabel("Texto", janela)
label.move(150,80)
label.setStyleSheet("font-family: Times New Roman, Times, serif; font-size:20px")

janela.show()

app.exec()