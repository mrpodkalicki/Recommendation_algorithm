import pymysql
import requests
import random
from scipy import spatial
# import random
# from scipy import spatial
# import numpy as np
# import pandas as pd
# import csv
# import numpy as np


def connectDatabase(name):
    db=pymysql.connect(host="127.0.0.1",
                        user="root",
                        password="root",
                        db=name)
    
    return db


# 

def create_user():
    userdata={}
    response =requests.get("https://randomuser.me/api/")
    user = response.json()
    # print(user)
    userdata["login"]=user['results'][0]['login']['username']
    userdata["password"]=user['results'][0]['login']['password']
    userdata["email"]=user['results'][0]['email']
    userdata["artist_name"]=user['results'][0]["name"]["last"]
    # print(username,password,email)
    return userdata




class Person:
    def __init__(self, id_person, name, password=None,email=None):
        self.id_person=id_person
        self.name=name
        self.email=email
        self.password=password
    
    def person_data(self):
        return {'id':self.id_person,'username':self.name,'password':self.password,'email':self.email}
    


class User(Person):
    def query_insert(self,cursor):


        query="""INSERT INTO user(id,username,email,password) VALUES (%s,%s,%s,%s) """
        cursor.execute(query,[self.id_person,self.name,self.email,self.password])

class Artist(Person):
        def query_insert(self,cursor):
            query="""INSERT INTO artist(id,name) VALUES (%s,%s) """
            cursor.execute(query,[self.id_person,self.name])


def insert(count, cursor_obj, person_db, db_name, name_person):
    cursor = cursor_obj.cursor()
    number_rows = cursor.execute("SELECT * FROM {}".format(db_name))
    i = number_rows+1
    end_loop = count+number_rows+1
    while i <= end_loop:
        # print(i,"i")
        # print(end_loop,"end")
        number_rows = cursor.execute("SELECT * FROM {}".format(db_name))
        person_data=create_user()
        check_name = 0
        for j in range(1,number_rows+1):
            cursor.execute("SELECT * FROM {} WHERE id = {}".format(db_name, j))
            row = cursor.fetchone()
            check_name += 1 if row[1] == person_data[name_person] else check_name
            # print(person_data[name_person], row[1]) if row[1] == person_data[name_person] else check_name
        if check_name==0:
            person_exec = person_db(i, person_data[name_person], person_data['password'], person_data['email'])
            person_exec.query_insert(cursor)
            cursor_obj.commit()
            i += 1

def create_profil(cursor_db):
    cursor = cursor_db.cursor()
    number_rows_artist = cursor.execute("SELECT * FROM  artist")
    number_rows_users = cursor.execute("SELECT * FROM  user")
    number_row_profil = cursor.execute("SELECT * FROM   user_profil")
    id_number = number_row_profil+1
    print(id_number,"idprzed")
    for i in range(1, 50):
        zero=0
        for j in range(1, number_rows_artist+1):
            if_listen=random.randint(0, 1)

            if if_listen==0:
                zero+=1
                if zero>20:
                    print(zero,"zero")
                    print(id_number,"id")
                    print(i,"iduser")
                    print(j,"idsong")
                    query = """INSERT INTO user_profil(id,iduser,idartist) VALUES (%s,%s,%s) """
                    cursor.execute(query, [id_number, i, j])
                    cursor_db.commit()
                    id_number+=1


def vector_user(cursor_db,id_user):
    cursor = cursor_db.cursor()
    number_rows_artist = cursor.execute("SELECT * FROM  artist")
    number_row_profil = cursor.execute("SELECT * FROM   user_profil")
    vector_profil = [0 for i in range(number_rows_artist)]
    # print(len(vector_profil))
    for i in range(1, number_row_profil+1):
            cursor.execute("SELECT * FROM  user_profil WHERE id = {}".format(i))
            row = cursor.fetchone()
            if row[1]==id_user:
                # print(row[2])
                vector_profil[row[2]-1]=1
    return vector_profil


def knn_vector(cursor_db,id_user):
    cursor = cursor_db.cursor()
    number_rows_users = cursor.execute("SELECT * FROM  user")
    # vector_coefficient=[]

    vector_coefficient = {}
    for j in range(1,50):
        profil_user_first = vector_user(cursor_db, id_user)
        profil_user_two = vector_user(cursor_db, j)
        # print(profil_user_first)
        # print(profil_user_two)
        result = round(1 - spatial.distance.cosine(profil_user_first, profil_user_two), 5) if id_user != j else -1
        # print(result,"i:",i,"j:",j)
        vector_coefficient[j]=result

    return vector_coefficient


def similar_user(cursor_db):
    cursor = cursor_db.cursor()
    number_rows_simple_user = cursor.execute("SELECT * FROM  simple_user")
    id_number = 1+number_rows_simple_user
    for i in range(1,49):
        print(id_number,"id_number")
        knn_coefficient = knn_vector(cursor_db, i)
        sort_knn_coefficient = sorted(knn_coefficient.items() ,key=lambda x:x[1],reverse=True)
        for j in range(5):
            id_simple_user = int(sort_knn_coefficient[j][0])
            coefficient_value = float(sort_knn_coefficient[j][1])
            print(sort_knn_coefficient[j])
            print(type(id_simple_user))
            print(type(coefficient_value))
            print(coefficient_value)
            query = """INSERT INTO simple_user(id,id_user,id_simple_user,coefficient) VALUES (%s,%s,%s,%s) """
            cursor.execute(query, [id_number, i, id_simple_user, coefficient_value])
            cursor_db.commit()
            id_number+=1
            

def recomadn_artist(cursor_db,id_user):
    cursor = cursor_db.cursor()
    number_rows_simple_user = cursor.execute("SELECT * FROM  simple_user")
    all_index_songs=[]
    all_song=[]
    stop = id_user*5
    start = stop-4
    similar_user_id=[]
    for j in range(start,stop+1):
        cursor.execute("SELECT * FROM  simple_user WHERE id = {}".format(j))
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
        # print(row[1])
    return all_song


def data_to_alghoritm(cursor_db):
    pass
    # create_profil(cursor_obj)
    # insert(10, cursor_obj, User, "user", "login")
    # insert(100, cursor_obj, Artist, "artist", "artist_name")




def main():
    cursor_obj=connectDatabase("dbmusic")
    cursor = cursor_obj.cursor()
    # similar_user(cursor_obj)
    while True:
        print("Give index user:")
        index_user=int(input())
        if index_user == 0:break
        user_name = cursor.execute("SELECT username FROM  user WHERE id = {}".format(index_user))
        row = cursor.fetchone()
        name = row[0]
        print(name)
        print(("Recomand artists for {} user").format(name))
        print(recomadn_artist(cursor_obj, index_user))
       


    
    
    


main()
