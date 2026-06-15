class DadosPacientes:
    def __init__(self, numero, cor):
        self.numero = numero
        self.cor = cor
        self.proximo = None

class Pacientes:
    def __init__(self, nodos=None):
        self.head = None
        if nodos is not None:
            nodo = DadosPacientes(dado=nodos.pop(0))
            self.head = nodo
            for elem in nodos:
                nodo.proximo = DadosPacientes(dado=elem)
                nodo = nodo.proximo

    def inserirSemPrioridade(self, nodo):
        if self.head == None:
            self.head = nodo
            return
        nodo_atual = self.head
        while nodo_atual.proximo != None:
            nodo_atual = nodo_atual.proximo

        nodo_atual.proximo = nodo
        return
    
    def inserirComPrioridade(self, nodo):
        if self.head == None:
            self.head = nodo
            return



while True: 
  print('1 - Adicionar pacientes na fila')
  print('2 - Mostrar pacientes na fila')
  print('3 - Chamar paciente')
  print('4 - Sair')

  op = int(input("Escolha uma opção: ")) 
  if op == 1: 
    cor = input('Informe a cor do cartão (A / V): ')
    numero = input('Informe a número do cartão: ')

  #if op == 2: 
    
  elif op == 3: 
    print()

  elif op == 4:
    print('Encerrando...')
    break

  else: 
    print("Selecione outra opção!\n")