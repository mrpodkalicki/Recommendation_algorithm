import pymysql
import requests
import random
from scipy import spatial


def connectDatabase(name):
    db=pymysql.connect(host="127.0.0.1",
                        user="root",
                        password="root",
                        db=name)
    return db

def create_user():
    userdata={}
    response =requests.get("https://randomuser.me/api/")
    user = response.json()
    userdata["login"]=user['results'][0]['login']['username']
    userdata["email"]=user['results'][0]['email']
    userdata["artist_name"]=user['results'][0]["name"]["last"]
    return userdata




class Person:
    def __init__(self, id_person, name, password=None,email=None):
        self.id_person=id_person
        self.name=name
        self.email=email
    
    def person_data(self):
        return {'id':self.id_person,'username':self.name,'password':self.password,'email':self.email}
    


class User(Person):
    def query_insert(self,cursor):
        query="""INSERT INTO user(id,username,email,password) VALUES (%s,%s,%s,%s) """
        cursor.execute(query,[self.id_person,self.name,self.email])

class Artist(Person):
        def query_insert(self,cursor):
            query="""INSERT INTO artist(id,name) VALUES (%s,%s) """
            cursor.execute(query,[self.id_person,self.name])


def inserting_users(users_amount, cursor_obj, person_db, db_name, name_person):
    cursor = cursor_obj.cursor()
    # how many users exist in database
    number_rows = cursor.execute("SELECT * FROM {}".format(db_name))
    #sa
    i = number_rows+1  # adding users from the last user that exists in the database
    end_loop = users_amount+number_rows+1
    while i <= end_loop:
        number_rows = cursor.execute("SELECT * FROM {}".format(db_name))
        person_data=create_user()
        check_name = 0  
        for j in range(1,number_rows+1):
            cursor.execute("SELECT * FROM {} WHERE id = {}".format(db_name, j))
            row = cursor.fetchone()
            # checking  if exist user with the same name
            check_name += 1 if row[1] == person_data[name_person] else check_name
        if check_name==0:
            person_exec = person_db(i, person_data[name_person], person_data['email'])
            person_exec.query_insert(cursor)
            cursor_obj.commit()
            i += 1

def create_profil(cursor_db):
    cursor = cursor_db.cursor()
    number_rows_artist = cursor.execute("SELECT * FROM  artist")
    number_row_profil = cursor.execute("SELECT * FROM   user_profil")
    id_number = number_row_profil+1
    for i in range(1, 50):
        zero=0
        for j in range(1, number_rows_artist+1):
            if_listen=random.randint(0, 1)
            if if_listen==0:
                zero+=1
                if zero>20:
                    query = """INSERT INTO user_profil(id,iduser,idartist) VALUES (%s,%s,%s) """
                    cursor.execute(query, [id_number, i, j])
                    cursor_db.commit()
                    id_number+=1

#the function return  a user profile that describes which artists the user likes,the user profile is binary
def vector_user(cursor_db,id_user):
    cursor = cursor_db.cursor()
    number_rows_artist = cursor.execute("SELECT * FROM  artist")
    number_row_profil = cursor.execute("SELECT * FROM   user_profil")
    vector_profil = [0 for i in range(number_rows_artist)]
    for i in range(1, number_row_profil+1):
            cursor.execute("SELECT * FROM  user_profil WHERE id = {}".format(i))
            row = cursor.fetchone()
            if row[1]==id_user:
                vector_profil[row[2]-1]=1
    return vector_profil

#the function which return the users' similarity using Vector Cosine-Based Similarity method
def similarity_users(cursor_db,id_user):
    cursor = cursor_db.cursor()
    number_rows_users = cursor.execute("SELECT * FROM  user")
    vector_of_best_users = {}
    for j in range(1, number_rows_users+1):
        profil_user_first = vector_user(cursor_db, id_user)
        profil_user_two = vector_user(cursor_db, j)
        result = round(1 - spatial.distance.cosine(profil_user_first, profil_user_two), 5) if id_user != j else -1
        vector_of_best_users[j]=result
    return vector_of_best_users

    #the function which compares all users and chooses five best similarity users, add these users to the database
def best_similar_users(cursor_db):
    cursor = cursor_db.cursor()
    number_rows_simple_user = cursor.execute("SELECT * FROM  simple_user")
    id_number = 1+number_rows_simple_user
    for i in range(1,49):
        knn_coefficient = similarity_users(cursor_db, i)
        sort_knn_coefficient = sorted(knn_coefficient.items() ,key=lambda x:x[1],reverse=True)
        for j in range(5):
            id_simple_user = int(sort_knn_coefficient[j][0])
            coefficient_value = float(sort_knn_coefficient[j][1])
            query = """INSERT INTO similar_user(id,id_user,id_similar_user,coefficient) VALUES (%s,%s,%s,%s) """
            cursor.execute(query, [id_number, i, id_simple_user, coefficient_value])
            cursor_db.commit()
            id_number+=1
            
#the function that returns recommended artists to the user with the given id in the database
def recomadn_artist(cursor_db,id_user):
    cursor = cursor_db.cursor()
    number_rows_similar_user = cursor.execute("SELECT * FROM  simpilar_user")
    all_index_songs=[]
    all_song=[]
    stop = id_user*5
    start = stop-4
    similar_user_id=[]
    for j in range(start,stop+1):
        cursor.execute("SELECT * FROM  similar_user WHERE id = {}".format(j))
        row = cursor.fetchone()
        similar_user_id.append(row[2])
    for i in range(len(similar_user_id)):
        vector = vector_user(cursor_db, similar_user_id[i])
        len_vector = len(vector)
        songs_index = [i+1 for i in range(len_vector) if vector[i] == 1]
        if all_index_songs==[]:
            all_index_songs = songs_index
        else:
                for i in range(len((songs_index))):
                    count_rep_song=0
                    for j in range(len(all_index_songs)):
                        if songs_index[i] == all_index_songs[j]:
                            count_rep_song+=1
                    if count_rep_song==0:
                        all_index_songs.append(songs_index[i])
    for i in range(len(all_index_songs)):
        cursor.execute(
            "SELECT * FROM  artist WHERE id = {}".format(all_index_songs[i]))
        row = cursor.fetchone()
        all_song.append(row[1])
    return all_song

#the function that simulates the creation of users and their profiles
def data_simulation(cursor_db):
    cursor_obj = connectDatabase("dbmusic")
    create_profil(cursor_obj)
    inserting_users(10, cursor_obj, User, "user", "login")
   
def main():
    cursor_obj=connectDatabase("dbmusic")
    cursor = cursor_obj.cursor()
    best_similar_users(cursor_obj)
    while True:
        print("Give index user:")
        index_user=int(input())
        if index_user == 0:break
        cursor.execute("SELECT username FROM  user WHERE id = {}".format(index_user))
        row = cursor.fetchone()
        name = row[0]
        print(name)
        print(("Recomand artists for {} user").format(name))
        print(recomadn_artist(cursor_obj, index_user))
       
main()
