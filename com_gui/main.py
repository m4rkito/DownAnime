import sys
from PySide2.QtWidgets import QMainWindow, QApplication, QLabel, QProgressBar, QMessageBox
from PySide2.QtGui import QIcon
from PySide2.QtCore import QFile, Slot, QTimer, QThread, SIGNAL
from inter_downanime import Ui_MainWindow
from downanime import DownAnime
import _thread
from threading import Thread, Event
from platform import system

#instancia do DownAnime
down = DownAnime()

sistema = system()

class Label(QLabel):

	def __init__(self, **kwargs):
		
		super(Label, self).__init__(**kwargs)

		self.setStyleSheet("""
				color: white;
				background-color: #606060;
				""")
		self.marcar = True
		self.clicado = False

	def mostra_anime_ep(self, obj):
		"""
		Esta função envia o index do anime escolhido para o DownAnime pesquisa pelos episódios
		"""
		global down
		global janela
		
		down.escolha_anime = self.escolha
		down.episodios()
		janela.episodios()

	def baixar(self, obj):
		"""
		chama a função para baixar os episódios
		"""
		
		global janela
		
		if not self.clicado:

			self.setStyleSheet("""
					background-color: rgb(255, 255, 255);
					color:black;
					""")
			janela.baixar_ep(self.link, "adicionar")
			self.clicado = True

		else:

			self.setStyleSheet("""
					background-color: #606060;
					color: white;
					""")
			self.clicado = False
			janela.baixar_ep(self.link, "remover")


class Janela_Principal(QMainWindow):

	def __init__(self):
		super(Janela_Principal, self).__init__()

		global down
		
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		#verifica qual o sistema e adiciona icone a jenala
		
		if sistema == "Linux":
			
			self.icon = QIcon("/bin/DownAnime/downanime.ico")
			
		elif sistema == "Windows":
			
			self.icon = QIcon("downanime.ico")
		
		#Adiciona icone a janela quando compilado com pyinstaller
		#self.icon = QIcon(sys._MEIPASS+"/downanime.ico")
		self.setWindowIcon(self.icon)
		#conecta o botão a função de pesquisa
		self.ui.botao_pesquisa.clicked.connect(self.pesquisar)
		self.barra = 0
		#armazena a label que foi clicada para trocar cor e pega links
		self.link_clicado = None
		#conecta o botão de baixar a função baixar
		self.ui.baixar_btn.clicked.connect(self.baixar)
		#variavel para verificar se o download esta ativo ou não
		self.download_on = False
		#cria uma caixa de dialogo para mostra que o download ja iniciou
		self.msg_download = QMessageBox()
		self.msg_download.setStyleSheet("""
			background-color: blue;
			""")

	def baixando(self):
		
		global down

		if down.total < int(down.header_total_arquivo["content-length"]):
			#calculo de porcentagem para pega progresso do download
			porcentagem = down.total/int(down.header_total_arquivo["content-length"])
			#multiplica o valor obtido no calculo de porcentagem para pega um valor mais redondo
			porcentagem *= 100
			#altera o valor da barra de progresso
			self.ui.progressBar.setValue(porcentagem)

		else:
			#altera o valo da barra pra 100 quando o download ja foi feito
			self.ui.progressBar.setValue(0)
			#para um objeto QTimer que fica chamando essa função a cada 30s
			self.time_progress_bar.stop()
			self.msg_download.setText("Download finalizado.")
			self.msg_download.exec()
			#espera finalizar a thread de download
			self.t.join()

	@Slot()
	def pesquisar(self, pos):

		global down
		
		#pesquisa os animes disponiveis 
		down.pesquisar(self.ui.barra_pesquisa.toPlainText().replace("\n","+"))

		#limpa a area onde ficara os animes/episódios
		for i in reversed(range(self.ui.area_animes_r.count())):

			self.ui.area_animes_r.itemAt(i).widget().deleteLater()
		
		#coloca os resultados na tela
		for resu in down.resultados:
			
			#cria label com nomes do anime
			label = Label(text=resu["nome"].text)
			#pega o index para depois passa qual anime foi escolhido da lista
			label.escolha = resu["index"]
			#adiciona a função mostra do label ao mousepressevent
			label.mousePressEvent = label.mostra_anime_ep
			#adiciona o label a area de animes
			self.ui.area_animes_r.addWidget(label)


	def episodios(self):
		
		global down

		self.episodios = []

		
		#limpa a area onde fica os animes/episódios
		for i in reversed(range(self.ui.area_animes_r.count())):
			
			self.ui.area_animes_r.itemAt(i).widget().deleteLater()
			#evita bugs na hora refenciar esse atributo
			self.link_clicado = None
		
		#constroi a lista de episódios
		for ep in down.anime_episodios:
			
			#constroi label com nome dos episodios
			label = Label(text=ep)
			#pega o link do episodio
			label.link = ep
			#atribui uma função sua ao mousepressevent
			label.mousePressEvent = label.baixar
			#adiciona o label a area de animes
			self.ui.area_animes_r.addWidget(label)

	def baixar_ep(self, link, acao):

		global down
		

		if acao == "adicionar":

			self.episodios.append(link)

		else:

			self.episodios.remove(link)
			

	def baixar(self):
		"""		Esta função inicia o download do episodio em uma nova thread para que não atrapalhe o fluxo normal do programa.
		"""

		global down
		
		if down.completo:

			#inicia uma thread para baixar o anime
			self.t = Thread(target=down.baixar_ep, args=(self.episodios, ))
			self.t.start()
			
			#instancia do objeto QTimer para agenda um evento a cada 500 milissegundos
			self.time_progress_bar = QTimer(self)
			#conecta esse QTimer a função baixando da classe
			self.time_progress_bar.timeout.connect(self.baixando)
			#inicia a contagem
			self.time_progress_bar.start(30000)
			self.msg_download.setText("Download iniciado....")
			self.msg_download.exec()
			
		else:
			
			self.msg_download.setText("Espere o outro download terminar!!")
			self.msg_download.exec()
			
	def closeEvent(self, *args):
		
		global down
		
		down.finalizar = True
		

if __name__ == "__main__":

	app = QApplication(sys.argv)
	janela = Janela_Principal()
	janela.show()
	sys.exit(app.exec_())

