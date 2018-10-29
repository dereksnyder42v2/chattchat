#!/usr/local/Cellar/python/3.6.4_4/bin/python

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

#helper function, so you don't have to encode everything as Bytes
def toBytes(myStr):
	return bytes(myStr, "utf-8")

# thread to handle new clients. once handled, starts thread for each new client.
def handleNewClient():
	# TODO document
	while 1:
		newClientSock, newClientAddress = SERVER.accept()
		#clientList.append([newClientSock, newClientAddress]) #
		Thread(target = handleClient, args = (newClientSock,)).start() #starts new thread to continuously manage client

def isDM(msg):
	words = msg.split()
	if len(words) > 0:
		if '@' in words[0]:
			for name in clientNameDict.keys():
				if name in words[0]:
					return True
	return False

def sendDM(msg, fromUser=""):
	recipient = ""
	words = msg.split()
	if len(words) > 0:
		if '@' in words[0]:
			for name in clientNameDict.keys():
				if name in words[0]:
					recipient = name
					break
	if recipient == "":
		raise NameError("sendDM failed")
		print("send DM() recipient = %s" % str(recipient))
	else:
		if fromUser == "":
			clientNameDict[recipient].send(toBytes(msg))
		else:
			clientNameDict[recipient].send(toBytes("\n%s: %s\n" % (fromUser, msg)))

def handleClient(client):
	#check name against clientNameDict/ if good, add name, send msgs with name prefix
	nameOk = False
	while (not nameOk):
		client.send(toBytes("Please enter a username:\n"))
		name = client.recv(BUFSZ).decode("utf-8").replace(' ', '')
		if name in clientNameDict.keys() or name == "":
			client.send(toBytes("That user name is already taken. Try a different one.\n"))
		else:
			clientNameDict[name] = client
			nameOk = True
	for client in clientNameDict.values(): # tell all named clients a list of active users when someone joins
		client.send(toBytes("server: %s\n" % str(list(clientNameDict.keys()))))
	while 1:
		msg = client.recv(BUFSZ).decode("utf-8")
		if msg != QUITMSG:
			print("Someone sent a message--%s: %s" % (name, msg))
			# TODO if msg is a DM, don't broadcast
			if isDM(msg):
				client.send(toBytes("%s: %s\n" % (name, msg)))
				with open(chatlogName, 'a') as f: #write message contents to chatlog
					f.write("%s: %s\n" % (name, msg))
				sendDM(msg, fromUser=name)
			else:
				with open(chatlogName, 'a') as f: #write message contents to chatlog
					f.write("%s: %s\n" % (name, msg))
				broadcast(msg, prefix=name)
		else:
			client.send(toBytes(QUITMSG)) # not sure the server needs to send a 'quit' to the client?
			"""
			for pair in clientList: #remove client from list
				if pair[0] == client:
					removethisclientpair = pair
			clientList.remove(removethisclientpair) # soooo sloppy. you can do better than this derek...
			"""
			client.close()
			clientNameDict.pop(name, None) #remove client from dict. to be clear. there is NO good reason that there is a list AND a dict...
			for client in clientNameDict.values(): # tell all named clients a list of active users when someone leaves
				client.send(toBytes("server: %s\n" % str(list(clientNameDict.keys()))))
			break
#sends message to all clients
def broadcast(msg, prefix=""):
	for clientName in clientNameDict.keys():
		if prefix == "":
			clientNameDict[clientName].send(toBytes("%s\n" % msg)) #inner object is a socket we are sending to
		else:
			clientNameDict[clientName].send(toBytes("%s: %s\n" % (prefix, msg))) # TODO this doesn't work when user sends QUITMSG

if __name__ == "__main__":
	import datetime # for timestamping chatlogs
	
	QUITMSG = "{quit}"
	HOST = ""
	PORT = 8080
	BUFSZ = 1024
	ADDR = (HOST, PORT)

	SERVER = socket(AF_INET, SOCK_STREAM)
	SERVER.bind(ADDR)
	SERVER.listen(5) # mandatory; optional for python >=3.5
	# make "chatlog YYYY-MM-DD HHMMSS.txt" file
	chatlogName = "chatlog %04d-%02d-%02d %02d%02d%02d.txt" % (
		datetime.datetime.today().year,
		datetime.datetime.today().month,
		datetime.datetime.today().day,
		datetime.datetime.today().hour,
		datetime.datetime.today().minute,
		datetime.datetime.today().second)
	chatlog = open(chatlogName, 'w')
	chatlog.close()
	print("Server started...")

	clientList = [] # list of lists. inner list is a pair, [socket, ip address]
	clientNameDict = dict() # key: client name, value: socket object
	try:
		acceptThread = Thread(target=handleNewClient)
		acceptThread.start()
		acceptThread.join()
		SERVER.close()
	except:
		print("Something went wrong! Quitting")
		SERVER.close()
		quit()

	