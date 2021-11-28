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

#-------------------Основные функции-------------------------------------------

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
        message = 'Введены пустые строки'
        return HTTPError(400, message)

    if invalid_data(new_user):
        message = 'Введены неправильные данные'
        return HTTPError(400, message)

    if find_track(new_user):
        message = 'Такой трек уже сохранён в БД'
        return HTTPError(409, message)
    session.add(new_user)
    session.commit()
    return  "Данные успешно сохранены"



if __name__ == "__main__":
    print('Сервер запускается')
    run(host="localhost", port = 8080, debug=True)
