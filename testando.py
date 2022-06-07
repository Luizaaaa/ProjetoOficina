#from kivy.uix.popup import Popup
#from kivy.uix.label import Label
#from kivy.app import App
#class teste(App):
# def build(self):
#    popup = Popup(title='Test popup',
#    content=Label(text='Hello world'),
#    size_hint=(None, None), size=(400, 400))
#    return popup
#teste().run()    
import psycopg2
from psycopg2 import Error
import tkinter as tk
import cv2
from pyzbar.pyzbar import decode

aluno_RA_aux = 0

def delete():
    global aluno_RA_aux
    aluno_RA_aux = RA.get()
    aluno_senha_aux = senha.get()
    cursor = connection.cursor()
    delete_query = "delete from emprestimo where aluno_RA = " + aluno_RA_aux + ";"
    cursor.execute(delete_query)
    connection.commit()

def view():
    cursor = connection.cursor()
    select_query = "select * from emprestimo;"
    cursor.execute(select_query)
    record = cursor.fetchall()
    view_text = tk.Label(root, text=record)
    view_text.pack()

def get_name():
        global aluno_RA_aux
        aluno_RA_aux = RA.get()
        aluno_senha_aux = senha.get()
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        cap.set(3, 640)
        cap.set(4,480)
        camera = True
        while (camera == True):
            sucess, frame = cap.read()
            for code in decode(frame):
                cursor = connection.cursor()
                insert_query = "insert into emprestimo (livro_id, aluno_RA, horario, devolucao) values (" + code.data.decode('utf-8') + " , " + aluno_RA_aux + " , " + "now(), CAST (now() + INTERVAL '3 day' as date));"
                cursor.execute(insert_query)
                connection.commit()
                camera = False
            cv2.imshow('Testing-code-scan',frame)
            cv2.waitKey(1)


root = tk.Tk()

RA = tk.Entry(root, width=50, font=('Helvetica', 18))
RA.pack()
RA.insert(0, "RA")
senha = tk.Entry(root, width=50, font=('Helvetica', 18))
senha.pack()
senha.insert(0, "Senha")

try:
        connection = psycopg2.connect(user="postgres",
                                    password="d05m11lu",
                                    host="127.0.0.1",
                                    port="5432",
                                    database="postgres")
except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)

Bt = tk.Button(root, text="Insert", command=get_name).pack()
Bt = tk.Button(root, text="Delete", command=delete).pack()
Bt = tk.Button(root, text="View", command=view).pack()

root.mainloop()