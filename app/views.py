from django.shortcuts import render
from django.views.generic.base import TemplateView 
import requests
from lxml import html
from bs4 import BeautifulSoup

class IndexView(TemplateView):
	template_name = 'index.html'

	def get_html(self, codigo):
		USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
		LANGUAGE = "en-US,en;q=0.5"
		session = requests.Session()
		session.headers['User-Agent'] = USER_AGENT
		session.headers['Accept-Language'] = LANGUAGE
		session.headers['Content-Language'] = LANGUAGE
		html_conteudo = session.get(f'https://aisweb.decea.mil.br/?i=aerodromos&codigo={codigo}')
		return html_conteudo

	def get(self, request, *args, **kwargs):
		return render(request, self.template_name)

	def post(self, request, *args, **kwargs):
		icao = request.POST.get('icao')
		requisicao = self.get_html(icao)
		#lxml
		tree = html.fromstring(requisicao.content)
		erro = tree.xpath("/html/body/div[1]/h1/text()")
		if erro:
			contexto = {
				'resultado': False,
				'mensagem': 'A pesquisa não retornou nenhum resultado, verifique o ICAO'
			}
		else:
			if tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/h4/sunrise/text()'):
				nascer_do_sol = tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/h4/sunrise/text()')[0]
			else:
				nascer_do_sol = 'Não há informações sobre nascer do sol'
			if tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/h4/sunset/text()'):
				por_do_sol = tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/div[1]/div[2]/h4/sunset/text()')[0]
			else:
				por_do_sol = 'Não há informações de por do sol'
			cartas = {'cartas': []}
			if tree.xpath('.//div/ul/li/a'):

				for carta in tree.findall('.//div/ul/li/a'):
					cartas['cartas'].append(
						{
							'nome': carta.text, 'link': carta.attrib['href']
						}
					)

				cartas['cartas'].pop(0)
			else:
				cartas['cartas'].append(
						{
							'nome': 'Não há cartas disponíveis', 'link': 'Não há links disponíveis'
						}
					)
			metar = str()
			if tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/p[2]/text()'):
				
				metar = tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/p[2]/text()')[0]
				
			else:

				metar = 'Não há informação sobre Metar disponível na página'

			taf = str()
			if tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/p[3]/text()'):

				taf = tree.xpath('/html/body/div[1]/div/div/div[2]/div[2]/p[3]/text()')[0]

			else:

				taf = 'Não há informação sobre Taf disponível na página'

			contexto = {
				'resultado': True,
				'nascer_do_sol': nascer_do_sol,
				'por_do_sol': por_do_sol,
				'metar': metar,
				'taf': taf,
				'cartas': cartas['cartas'],
			}
		return render(request, self.template_name, contexto)