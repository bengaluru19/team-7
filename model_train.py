import pandas as pd
import numpy as np
from sklearn.naive_bayes import GaussianNB
import pickle
import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="anthill"
)

mycursor = mydb.cursor()
mycursor.execute(
    "SELECT survey.budget,survey.area,survey.student_no,survey.disability,survey.snake,survey.play_elements, project.template_id FROM survey LEFT JOIN project ON survey.survey_id = project.survey_id")
ip = mycursor.fetchall()

print(ip)

for i in range(len(ip)):
    ip[i] = list(ip[i])

features = ['budget', 'area', 'no_of_students',
            'disability', 'snake', 'play_elements']
label = ['design']

label_values = []
feature_values = []

for i in range(len(ip)):
    row = []
    row.append(int(ip[i][0]/50000))
    row.append(int(ip[i][1]/200))
    row.append(int(ip[i][2]/20))
    row.append(ip[i][3])
    row.append(ip[i][4])
    row.append(ip[i][5])
    feature_values.append(row)
    label_values.append(ip[i][6])

model = GaussianNB()
model.fit(feature_values, label_values)

filename = "model.pkl"
model_pickle = open(filename, "wb")
pickle.dump(model, model_pickle)
model_pickle.close()
