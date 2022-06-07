from logging import NullHandler
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.uix.recyclegridlayout import RecycleGridLayout
from kivy.graphics import Color, Rectangle
from kivy.uix.floatlayout import FloatLayout
import psycopg2
from psycopg2 import Error
import cv2
from pyzbar.pyzbar import decode
import time
from datetime import datetime
from kivy.core.window import Window
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.properties import BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
Window.maximize()

connection = psycopg2.connect(user="postgres",
                                    password="********", #senha pessoal para entrar no pgAdmin4
                                    host="127.0.0.1",
                                    port="5432",
                                    database="postgres") #nome do database criado no pgAdmin4

class InfoLayout(FocusBehavior, LayoutSelectionBehavior, RecycleGridLayout):
  pass
class InfoButton(RecycleDataViewBehavior, Button):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
class Info(Screen):
    data_items = ListProperty([])

    def __init__(self, **kwargs):
        super(Info, self).__init__(**kwargs)
        self.mview()

    def mview(self):
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM public.emprestimo_livros ORDER BY horario DESC")
        rows = cursor.fetchall()
        for row in rows:
            for col in row:
                self.data_items.append(col)
class Menu(Screen):
  pass
class Conta(Screen):
  pass
class Emprestimo1(Screen):
  pass  
class AcessoInterno(Screen):
  pass
class AcessoInterno2(Screen):
  pass
class CadastrarAlunos(Screen):
  pass
class CadastrarLivros(Screen):
  pass
class Pesquisa(Screen):
  pass

class Bibliotec(App):  
  def build(self):
   sm = ScreenManager()
   sm.add_widget(Menu(name='menu'))
   sm.add_widget(Conta(name='conta'))
   sm.add_widget(Emprestimo1(name='emprestar'))
   sm.add_widget(AcessoInterno(name='interno'))
   sm.add_widget(AcessoInterno2(name='ac_interno'))
   sm.add_widget(CadastrarAlunos(name='al_cadastrar'))
   sm.add_widget(CadastrarLivros(name='li_cadastrar'))
   sm.add_widget(Pesquisa(name='pesquisar'))
   sm.add_widget(Info(name='testpesq'))
   return sm

  def scan_camera(self):
    codigo = '0'
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(3,900)
    cap.set(4,600)
    camera = True
    start = time.time()
    end = time.time()
    while (camera == True and end - start < 20):
        end = time.time()
        sucess, frame = cap.read()
        for code in decode(frame):
          codigo = code.data.decode('utf-8')
          camera = False
        cv2.imshow('Scanneando por livros',frame)
        cv2.waitKey(1)
    time.sleep(1)
    cv2.destroyAllWindows()
    return codigo

  def insert(self):
    aluno_RA_aux = self.root.get_screen('conta').ids.RA.text
    livro_id_aux = self.scan_camera()
    cursor = connection.cursor()
    cursor.execute("select disponibilidade from public.livro where id = " + livro_id_aux + ";")
    disponibilidade_aux = cursor.fetchone()
    if disponibilidade_aux is not None:
      if disponibilidade_aux[0] is True: 
        cursor.execute("select multa from public.aluno where RA = " + aluno_RA_aux + ";")
        multa = cursor.fetchone()
        if(int(multa[0]) <= 0):
          cursor.execute("select devolucao from public.emprestimo where aluno_RA = " + aluno_RA_aux + ";")
          devolucao = cursor.fetchall()
          for i in range(len(devolucao)):
            if str(devolucao[i][0]) < str(datetime.now().strftime('%Y-%m-%d')):
              popup = Popup(title = 'Erro', content=Label(text="Você possui livros atrasados\nDevolva-os antes de adquirir novos livros."),size_hint =(None, None),size =(400, 200))  
              popup.open()
              return -1
          cursor.execute("insert into public.emprestimo (livro_id, aluno_RA, horario, devolucao) values (" + livro_id_aux + " , " + str(aluno_RA_aux) + " , " + "now(), CAST (now() + INTERVAL '7 day' as date));")
          connection.commit()
          cursor.execute("select devolucao from public.emprestimo where livro_id = " + livro_id_aux + ";")
          devolucao_aux = cursor.fetchone()[0]
          popup = Popup(title = 'Sucesso', content=Label(text="O emprestimo foi realizado com sucesso.\n\n   A data de devolução ficou para o dia:\n                           " + str(devolucao_aux.strftime('%d/%m/%Y')) ),size_hint =(None, None),size =(400, 200))  
          popup.open()
        else:
          popup = Popup(title = 'Erro', content=Label(text="Você possui multa pendente\nPague-a antes de adquirir novos livros."),size_hint =(None, None),size =(400, 200))  
          popup.open()
      else:
        popup = Popup(title = 'Erro', content=Label(text="Esse livro já se encontra em posse de outro aluno. \nTente Novamente."),size_hint =(None, None),size =(400, 200))  
        popup.open()
    else:
      popup = Popup(title = 'Erro', content=Label(text="O Código de Barras está incorreto.\nTente novamente ou, se o erro persistir, fale com um de nossos responsáveis."),size_hint =(None, None),size =(600, 200))  
      popup.open()

  def delete(self):
    aluno_RA_aux = self.root.get_screen('conta').ids.RA.text
    livro_id_aux = self.scan_camera()
    cursor = connection.cursor()
    select_query = "select aluno_RA from public.emprestimo where livro_id = " + livro_id_aux + ";"
    cursor.execute(select_query)
    RA = cursor.fetchone()
    if RA is not None:
      if str(RA[0]) == aluno_RA_aux:
        delete_query = "delete from public.emprestimo where livro_id = " + livro_id_aux + ";"
        cursor.execute(delete_query)
        connection.commit()
        popup = Popup(title = 'Sucesso', content=Label(text="Esse livro foi devolvido com sucesso."),size_hint =(None, None),size =(350, 200))  
        popup.open()
      else:
        popup = Popup(title = 'Erro', content=Label(text="Esse livro não se encontra em sua posse. \nTente Novamente."),size_hint =(None, None),size =(400, 200))  
        popup.open()
    else:
      popup = Popup(title = 'Erro', content=Label(text="Esse livro não se encontra em sua posse. \nTente Novamente."),size_hint =(None, None),size =(400, 200))  
      popup.open()

  def check_aluno(self):
    RA = self.root.get_screen('conta').ids.RA.text
    senha = self.root.get_screen('conta').ids.SENHA.text
    if senha.isnumeric() and RA.isnumeric():
        senha = int(senha)
        cursor = connection.cursor()
        select_query = "select senha from public.aluno where RA = " + str(RA) + ";"
        cursor.execute(select_query)
        senha_aux = cursor.fetchone()
        if senha_aux is not None:     
          senha_aux = int(senha_aux[0])     
          if(senha == senha_aux):
            self.root.current = 'emprestar'
          else:
            popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
            popup.open()
        else:
            popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
            popup.open()
    else:
          popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
          popup.open()

  def check_interno(self):
    matricula = self.root.get_screen('interno').ids.MATRICULA.text
    senha = self.root.get_screen('interno').ids.SENHA.text
    if senha.isnumeric() and matricula.isnumeric():
        senha = int(senha)
        cursor = connection.cursor()
        select_query = "select senha from public.funcionario where matricula = " + str(matricula) + ";"
        cursor.execute(select_query)
        senha_aux = cursor.fetchone()
        if senha_aux is not None:     
          senha_aux = int(senha_aux[0])     
          if(senha == senha_aux):
            self.root.current = 'ac_interno'
          else:
            popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
            popup.open()
        else:
            popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
            popup.open()
    else:
          popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
          popup.open()

  def clear_text(self):
      self.root.get_screen('conta').ids.RA.text = ''
      self.root.get_screen('conta').ids.SENHA.text = ''
      self.root.get_screen('interno').ids.MATRICULA.text = ''
      self.root.get_screen('interno').ids.SENHA.text = ''
      self.root.get_screen('al_cadastrar').ids.NOME.text = ''
      self.root.get_screen('al_cadastrar').ids.RA.text = ''
      self.root.get_screen('al_cadastrar').ids.EMAIL.text = ''
      self.root.get_screen('al_cadastrar').ids.SENHA.text = ''
      self.root.get_screen('al_cadastrar').ids.CURSO.text = ''
      self.root.get_screen('li_cadastrar').ids.CODIGO.text = ''
      self.root.get_screen('li_cadastrar').ids.TITULO.text = ''
      self.root.get_screen('li_cadastrar').ids.AUTOR.text = ''
      self.root.get_screen('li_cadastrar').ids.CATEGORIA.text = ''

  def cadastrar_aluno(self):
    cursos = ['Eng. Computação', 'Eng. Eletrica', 'Eng. Mecanica', 'Eng. Civil', 'Letras', 'Quimica', 'Administração', 'Matematica', 'Analise e Desenvolvimento de Sistemas', 'Manutenção Mecanica', 'Agronomia']
    nome_aux = self.root.get_screen('al_cadastrar').ids.NOME.text
    RA_aux = self.root.get_screen('al_cadastrar').ids.RA.text
    email_aux = self.root.get_screen('al_cadastrar').ids.EMAIL.text
    senha_aux = self.root.get_screen('al_cadastrar').ids.SENHA.text
    curso_aux = self.root.get_screen('al_cadastrar').ids.CURSO.text

    if(RA_aux.isnumeric() and senha_aux.isnumeric() and len(senha_aux) == 6):
        cursor = connection.cursor()
        cursor.execute("select * from public.aluno where RA = " + RA_aux + ";")
        RA = cursor.fetchone()
        if(RA is None):
          if(curso_aux in cursos):
            insert_query = "insert into public.aluno (RA, nome, senha, email, curso) values (" + RA_aux +", '" + nome_aux + "'," + senha_aux +", '" + email_aux + "', '" + curso_aux + "');"
            cursor.execute(insert_query)
            connection.commit()
            self.root.current = 'ac_interno'
            self.clear_text()
            popup = Popup(title = 'Sucesso', content=Label(text="Aluno Cadastrado com sucesso."),size_hint =(None, None),size =(300, 200))  
            popup.open()
          else:
            popup = Popup(title = 'Erro', content=Label(text="Insira um curso válido para esse câmpus:\n" + '\n'.join(cursos)),size_hint =(None, None),size =(400, 350))  
            popup.open()
        else:
          popup = Popup(title = 'Erro', content=Label(text="Um aluno com esse RA já existe.\n Revise o RA e tente novamente."),size_hint =(None, None),size =(300, 200))  
          popup.open()
    else:
      popup = Popup(title = 'Erro', content=Label(text="Senha ou RA incorretos.\n Tente Novamente."),size_hint =(None, None),size =(300, 200))  
      popup.open()
  
  def cadastrar_livro(self):
    id_aux = self.root.get_screen('li_cadastrar').ids.CODIGO.text
    titulo_aux = self.root.get_screen('li_cadastrar').ids.TITULO.text
    autor_aux = self.root.get_screen('li_cadastrar').ids.AUTOR.text
    categoria_aux = self.root.get_screen('li_cadastrar').ids.CATEGORIA.text

    if(id_aux.isnumeric()):
      cursor = connection.cursor()
      cursor.execute("select * from public.livro where id = " + id_aux + ";")
      codigo = cursor.fetchone()
      if(codigo is None):
        insert_query = "insert into public.livro (id, titulo, autor, categoria) values (" + id_aux +", '" + titulo_aux + "', '" + autor_aux +"', '" + categoria_aux + "');"
        cursor = connection.cursor()
        cursor.execute(insert_query)
        connection.commit()
        self.root.current = 'ac_interno'
        self.clear_text()
        popup = Popup(title = 'Sucesso', content=Label(text="Livro Cadastrado com sucesso.\n Insira-o nas prateleiras."),size_hint =(None, None),size =(300, 200))  
        popup.open()
      else:
        popup = Popup(title = 'Erro', content=Label(text="Um livro com esse id já está cadastrado."),size_hint =(None, None),size =(300, 200))  
        popup.open()
    else:
      popup = Popup(title = 'Erro', content=Label(text="Codigo invalido.\n Insira um código numerico."),size_hint =(None, None),size =(300, 200))  
      popup.open()


  def scan_codigo(self):
    self.root.get_screen('li_cadastrar').ids.CODIGO.text = self.scan_camera()

Bibliotec().run()      