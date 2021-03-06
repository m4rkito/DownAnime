from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import re, requests, urllib3
from bs4 import BeautifulSoup as bs
import time, platform, threading, os

class DownAnime():

	def __init__(self):

		#instancia o RoboBrowser, seta o parser como html.parser para que analise o html
		self.escolha_anime =  None
		self.completo = False
		self.link = "https://www.superanimes.org/busca?parametro="
		self.resultados = []
		self.anime_episodios = []
		self.sistema = platform.system()
		self.opcoes = Options()
		self.opcoes.add_argument("--headless")

	#função para fazer pesquisa do anime
	def pesquisar(self, nome):
		
		#verifica qual o site pq a ideia e pesquisar em varios sites caso não ache o anime neste
		if self.link == "https://www.superanimes.org/busca?parametro=":
			
			#tranforma os espaços em (+) para realizar a pesquisa
			nome = nome.replace(" ", "+")
			#pesquisa os animes com nome parecido
			self.conexao = requests.get(f"{self.link}{nome}")
			pesquisa = bs(self.conexao.text, "html.parser")
			#percorre pelos resultados
			for index, anime in enumerate(pesquisa.find_all("article")):
				#armazena os resultados
				self.resultados.append({"index": index, "nome": anime})
			
	def mostra_animes(self):


			#mostra os resultados
			for anime in self.resultados:

				print(f"{anime['index']}--{anime['nome'].h1.text}")

	#pega todos os episódios disponiveis
	def episodios(self):
		if self.link == "https://www.superanimes.org/busca?parametro=":

			#abre a pagina dos ep
			self.conexao = requests.get(self.resultados[self.escolha_anime]["nome"].h1.a["href"])
			#guarda o nome do anime
			self.nome_anime = self.resultados[self.escolha_anime]["nome"].h1.text
			#guarda o link do anime
			self.link_anime = self.conexao.url
			#parser para busca os eps
			pesquisa = bs(self.conexao.text, "html.parser")
			#pega as divs que contem os episodios
			numero_episodios = pesquisa.find("ul", "boxAnimeSobre")
			numero_episodios = re.findall("[\d]+", numero_episodios.find("div").find("li").text)[0]
			numero = int(numero_episodios)
			#constroi uma lista com todos os episodios disponiveis
			self.anime_episodios = [f"episodio-{episodio}" for episodio in range(1, numero+1)]
			

	def mostra_episodios(self):
		#mosta os episodios
		for index, ep in enumerate(self.anime_episodios):
				
			print(f"{index} -- Episodio-{ep}")

	
	def baixar_ep(self, eps=[]):
		try:

			self.firefox = webdriver.Firefox(firefox_options=self.opcoes)
			self.completo = False

			for ep in eps:
				#abre a pagina do episodio
				self.firefox.get(f"{self.link_anime}/{ep}")
				#busca os elementos que contem os players de video
				video = self.firefox.find_elements_by_class_name("btVideo")
				#pega o link do player
				video = video[1].get_attribute("data-video-url")
				#requisita a pagina do player
				self.firefox.get(f"{video}")
				#busca o elemento video
				video = self.firefox.find_element_by_tag_name("video")
				#pega o link do video
				link = video.get_attribute("src")
				
				#requisita o video
				video = requests.get(link, stream=True)

				self.headers = video.headers
				self.total = 0

				#escreve cada fatia em um arquivo
				with open(f"{self.nome_anime}-{ep}.mp4", "wb") as arquivo:

					for chunk in video.iter_content(chunk_size=1024):

						arquivo.write(chunk)
						self.total += 1024
				
			self.firefox.close()
			self.completo = True
			
		except KeyboardInterrupt:

			self.completo = True
			self.firefox.close()
			print("programa parado")

	
	def baixando(self):
		
		self.sistema = platform.system()

		if self.sistema == "Linux":

			os.system("clear")

		elif self.sistema == "Windows":

			os.system("cls")

		while not self.completo:
			
			print("baixando", end="", flush=True)

			for c in [".",".",".","."]:

				print(c, end="", flush=True)
				time.sleep(1)
			print()

			if self.sistema == "Linux":

				os.system("clear")

			elif self.sistema == "Windows":

				os.system("cls")


