import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from bottle import request
from bottle import run
from bottle import route
from bottle import HTTPError

Base=declarative_base()
#------------------Работа с базой данных--------------------------------------
class Artists(Base):
    __tablename__='album'
    id=sa.Column(sa.Integer(), primary_key=True)
    year=sa.Column(sa.Integer())
    artist=sa.Column(sa.Text())
    genre=sa.Column(sa.Text())
    album= sa.Column(sa.Text())

    def __str__(self):
        return str(self.year) + " | " + str(self.artist) + " | " + str(self.genre) + " | " + str(self.album) 

def lets_connect():
    engine = sa.create_engine('sqlite:///albums.sqlite3')
    Base.metadata.create_all(engine)
    session=sessionmaker(engine)
    return session()
session=lets_connect()

#-------------------Вспомогательные функции и исключения------------------
 
def find_track(art):
    """Ищет в базе данных артиста с точно такими же данными что переданы в переменную art
    Выдаёт True если данные дублируются"""
    query = session.query(Artists).filter(Artists.year == art.year, Artists.artist == art.artist, Artists.genre == art.genre, Artists.album == art.album)
    return True if query.count() > 0 else False

def invalid_data(track):
    """Проверяет правильность введённых данных. Имена и альбомы могут 
    быть хоть из сплошных точек, все мы знаем что творческих людей не понять, верно?
    В случае неправиьности введённых данных возвращает True (наличие ошибки)"""

    result1 = False if track.year>0 else True #не проверяется год выше нынешнего чтобы можно было добовлять альбомы Самурая (если в теме, ставь лайк <3) 
    try:
        int(track.genre)
    except ValueError as e:
        pass
    else:
        result2=True
    result = result1 and result2
    return result

def if_empty(tada):
    """Проверяет данные на наличие пустых строк
    Выдаёт True если таковые найдены"""
    result=False if tada.year!='' and tada.artist!='' and tada.genre!='' and tada.album!='' else True
    return result

def er_400_empty_str():  
    """Возвращает ошибку 400 с текстом о пустых строках"""

    er_message=''
    try:
        with open("Errors/er400_empty_string.html", encoding='utf-8') as htmlText:
            er_message = htmlText.read()
    except FileNotFoundError as e:
        er_message = 'Были введены пустые строки.  \n Заполните все поля и повторите попытку'
        return HTTPError(400, er_message)
    else:
        return er_message
    # finally:
    #     return HTTPError(400, 'asdads')
    
def er_400_type_er():
    """Возвращает ошибку 400 с текстом о неправильных введённых данных"""
    er_message=''
    try:
        with open("Errors/er400_bad_type.html", encoding='utf-8') as htmlText:
            er_message = htmlText.read()
    except FileNotFoundError as e:
        er_message = 'Были введены неправильные данные.  \n Проверьте данные и повторите попытку'
        return HTTPError(400, er_message)
    else:
        return er_message

def er_409_duble():
    """Возвращает ошибку 400 с текстом о неправильных введённых данных"""
    er_message=''
    try:
        with open("Errors/er409_duble.html", encoding='utf-8') as htmlText:
            er_message = htmlText.read()
    except FileNotFoundError as e:
        er_message = 'Такой трек уже сохранён в БД!'
        return HTTPError(409, er_message)
    else:
        return er_message
#-------------------Основные функции-------------------------------------------

@route('/albums/')
def show_main_page():

    with open ("main.html", encoding='utf-8') as htmlText:
        main_page=htmlText.read()
    return main_page

artist_=''
@route('/albums/<param>')
def find_artist(param):

    # artist_=request.query.artist
    query = session.query(Artists).filter(Artists.artist==param)
    artist_= [str(att) for att in query.all()]
    # retete=["<br>".format(item) for item in artist_]
    result=[]
    result.append("Всего найдено {} треков группы {} <br> <hr> ".format(str(query.count()), param))
    result.append('<br>'.join(artist_))
    # return str(query.count())
    return result

@route('/albums', method = 'POST')
def seve_new_user():
    # session=lets_connect()
    try:
        new_user=Artists(
        year = int(request.forms.get('year')),
        artist = request.forms.get('artist'),
        genre = request.forms.get('genre'),
        album = request.forms.get('album')
        )
    except ValueError as e:
        return er_400_type_er()
    
    if if_empty(new_user):
        return er_400_empty_str()

    if invalid_data(new_user):
        return er_400_type_er()

    if find_track(new_user):
        return er_409_duble()
        
    session.add(new_user)
    session.commit()
    return  "Данные успешно сохранены"



if __name__ == "__main__":
    print('Сервер запускается')
    run(host="localhost", port = 8080, debug=True)
