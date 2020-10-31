from flask import Flask, render_template, request
from flask import *
import os
from flask import Flask, request, redirect, url_for, send_from_directory,render_template
import pandas as pd
import numpy as np
from collections import defaultdict
import pickle
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
filename3 = 'vector.sav'

vectorizer = pickle.load(open(filename3, 'rb'))

books_users_ratings = pd.read_csv("books_users_ratings")
books_users_ratings = books_users_ratings.iloc[:,1:]


d = pd.read_csv("test")
d = d.iloc[:,1:]

testset = d.values.tolist()
for i in range(len(testset)):
  testset[i]=tuple(testset[i])


app = Flask(__name__) # must include
app.secret_key="abc" # include



filename = 'recom_model.sav'
filename2 = 'senti_model.sav'
loaded_model = pickle.load(open(filename, 'rb'))
sentiment_pred = pickle.load(open(filename2, 'rb'))

predictions = loaded_model.test(testset)

def predict_s(text):
    td = pd.DataFrame([text])
    sample_test_matrix = vectorizer.transform(td[0])
    p = sentiment_pred.predict(sample_test_matrix)
    return p[0]

def add_entry(uid,isbn,b):
  b['user'].append(uid)
  b['isbn'].append(isbn)
  print("\n\nADDED ",uid,isbn)
  return b

def get_top_n(predictions, n=100):
    
    top_n = defaultdict(list)
    for uid, iid, true_r, est, _ in predictions:
        top_n[uid].append((iid, est))
    
    print(len(top_n[uid]))
    for uid, user_ratings in top_n.items():
        user_ratings.sort(key=lambda x: x[1], reverse=True)
        top_n[uid] = user_ratings[:n]
        
    return top_n


def get_reading_list(userid):

    reading_list = defaultdict(list)
    for i in [10,20,30,40,50,60,2000]:
      top_n = get_top_n(predictions, n=i)
      print(len(top_n[userid]))
      for n in top_n[userid]:
          book, rating = n
          title = books_users_ratings.loc[books_users_ratings.isbn==book].book_title.unique()[0]
          item=books_users_ratings[books_users_ratings['book_title']==title]['isbn'].unique().tolist()
          url = books_users_ratings.loc[books_users_ratings.isbn==book].image_url_l.unique()[0]
          
          books_b = pd.DataFrame(session['books'])

          user_seen = books_b[books_b['user']==userid]['isbn'].unique().tolist()
          print("\n\n :",i,item,user_seen)
          print("\n\n\n BOOKSB",books_b)
          if item[0] not in user_seen:
            print("YES!")
            reading_list[title] = [rating,url,item[0]]
          else:
            print("NO!")
      if(len(reading_list)>15):
        print("\nOK!")
        break;
    return reading_list


#print(predict_s("I hate that book!"))
#example_reading_list = get_reading_list(userid=69)
#for book, rating in example_reading_list.items():
#    print(f'{book}: {rating[1]}')

@app.route('/') 
def upload_file():
  return render_template('index.html')

@app.route('/load') 
def upload_fi():
  session['books'] = {'user':[],'isbn':[]}

  return render_template('index.html')

@app.route('/recommend') # this function is autoatically called 
def rec():
   return render_template('recommend.html')
@app.route('/sentiment') # this function is autoatically called 
def senti():
   return render_template('sentiment.html')

@app.route('/user_rec',methods=['POST','GET'])

def user_rec():
  if request.method=='POST':
    uid=request.form['uid']
    uid=int(uid)
    user_rec_list = get_reading_list(userid=uid)
    print(user_rec_list)

    title=[]
    url=[]
    isbn=[]
    for book, rating in user_rec_list.items():
      title.append(book)
      url.append(rating[1])
      isbn.append(rating[2])
    n = len(isbn)
      
    session['uid']=uid
    return render_template("show_rec.html" , title=title,url=url,isbn=isbn,n=n) 

  else:
    print("HELLLO")

@app.route('/text_senti',methods=['POST','GET'])

def text_senti():
  if request.method=='POST':
    review=request.form['review']

    
    pred = predict_s(review)
    print(pred)

    return render_template("show_senti.html" , pred = pred , review=review ) 
  else:
    print("HELLLO")


@app.route('/add',methods=['POST','GET'])

def add():
  if request.method=='POST':

    isbn=request.form['isbn']
    
    session['books']=add_entry(session['uid'],isbn,session['books'])

    return render_template("bought.html") 








if __name__ == '__main__':
   app.run(host="localhost",port=5000, debug = True)

   