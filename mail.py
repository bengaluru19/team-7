import smtplib
server = smtplib.SMTP('smtp-mail.outlook.com', 587)

#Next, log in to the server
server.login("urwithshanu@outlook.com", "Sandeep123")

#Send the mail
msg = "Sample msg, Hello!" # The /n separates the message from the headers
server.sendmail("urwithshanu@outlook.com", "urwithshanu@gmail.com", msg)