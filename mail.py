from flask import Flask
from flask_mail import Mail, Message

app =Flask(__name__)
mail=Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'urwithshanu@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/")
def index():
   msg = Message('AntHill Creations Registration', sender = 'urwithshanu@gmail.com', recipients = ['urwithshanu@outlook.com'])
   msg.body = "Confirmation Link !!!!!"
   with app.open_resource("brochure.pdf") as fp:
      msg.attach("brochure.pdf", "brochure/pdf", fp.read())
   mail.send(msg)
   return "Sent"

if __name__ == '__main__':
   app.run(debug = True)