from robobrowser import RoboBrowser
import re, requests
from bs4 import BeautifulSoup as bs
from threading import Thread

class DownAnime():

	def __init__(self):

		#instancia o RoboBrowser, seta o parser como html.parser para que analise o html
		self.browser = RoboBrowser(history=True, parser="html.parser")
		self.escolha_anime =  None
		self.nome_ep = self.link_ep = ""
		self.baixando = self.finalizar = False

	#faz a requisição do site
	def abrir_site(self, link="https://animesbz.com/episodios-de-animes/"):
		
		self.link = link
		self.browser.open(self.link, method="get")

	#função para fazer pesquisa do anime
	def pesquisa(self, nome):
		
		#verifica qual o site pq a ideia e pesquisar em varios sites caso não ache o anime neste
		if self.link == "https://animesbz.com/episodios-de-animes/":

			#procura os animes disponiveis
			self.animes = self.browser.find_all("em")
			#guarda os nomes dos animes
			self.animes_nome = []
			#guarda o resultado da pesquisa do anime
			self.resultados = []
			#tranforma o nome do anime em um padrão pro site
			novo_nome = []
			for index, anime in enumerate(self.animes):
				#salvando os nomes dos animes
				self.animes_nome.append({"nome":anime.text, "index": index})
				
			#modificar o nome para pesquisar o anime
			for pos, cara in enumerate(nome):

				if pos == 0:
					novo_nome.append(cara.upper())

				else:

					novo_nome.append(cara)
			
			nome = ""
			for cara in novo_nome:
				
				nome += cara
			
			self.nome_anime = nome
			
			#pesquisa o anime na lista de nomes
			for anime in self.animes_nome:
				
				if len(re.findall(f"{nome}[\w /\\\+\.\-\*\: 0-9 A-z]*", anime["nome"])) > 0:

					self.resultados.append({"nome": re.findall(f"{nome}[\w /\\\+\.\-\*\: 0-9 A-z]*", anime["nome"]), "index":anime["index"]})
			
	def mostra_animes(self):


			#mostra os resultados
			for anime in self.resultados:

				print(f"{anime['index']}--{anime['nome'][0]}")

	#pega todos os episódios disponiveis
	def episodios(self):
		if self.link == "https://animesbz.com/episodios-de-animes/":

			#abre a pagina dos ep
			self.browser.open(self.animes[self.escolha_anime].a["href"], method="get")
			#busca todas as listas não ordenadas
			busca = self.browser.find_all("ul")
			#lista que vai guarda os episodios
			self.anime_episodios = []
			#busca todos os li
			for li in busca[3]:
				#adiciona o episodio a lista de episodios
				self.anime_episodios.append(li)

	def mostra_episodios(self):
		#mosta os episodios
		for index, ep in enumerate(self.anime_episodios):
				
			print(f"{index} -- {ep.text}")
	
	def baixar_ep(self, link, nome):
        
		#variavel para verificação se esta baixando ou não
		self.baixando = True
		#intancia do robobrowser para pega o link do video
		baixar = RoboBrowser(history=True, parser="html.parser")
		#variavel para controla o total ja baixado
		self.total = 0
		#abre o site do video
		baixar.open(link, method="get")
		#pega o elemento com tag de video
		video = baixar.find_all("video")
		#pega os headers da pagina do video para saber o total ja baixado
		self.header_total_arquivo = requests.head(video[0].source["src"])
		#abre o arquivo para escrita
		arquivo = open(f"{nome}.mp4", "ab")
		#faz a requisão do video
		baixar = requests.get(video[0].source["src"], stream=True)
		#faz a transmissão dos por partes
		for chunk in baixar.iter_content(chunk_size=1048576):
			#escreve no arquivo os bytes recebidos
			arquivo.write(chunk)
			#soma no total a quantidade ja baixada
			self.total += 1048576
			
			if self.finalizar:
				
				break
			
		#fecha o arquivo
		arquivo.close()
		baixar.close()
		#variavel para verificação se esta baixando ou não
		self.baixando = False
		
		return True

