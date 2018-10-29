#!/usr/local/Cellar/python/3.6.4_4/bin/python

"""
command line argument #1 ("sys.argv[0]") is hostname to connect to.
./guiClient.py localhost   # connects to chat server on local
./guiClient.py 192.168.1.1 # connects to server on other machine in the network
"""

QUITMSG = "{quit}"

def toBytes(myStr):
	return bytes(myStr, "utf-8")	

__all__ = ['ScrolledText']
from tkinter import Frame, Text, Scrollbar, Pack, Grid, Place
from tkinter.constants import RIGHT, LEFT, Y, BOTH
class ScrolledText(Text):
	# https://github.com/python/cpython/blob/3.7/Lib/tkinter/scrolledtext.py
	"""A ScrolledText widget feels like a text widget but also has a
	vertical scroll bar on its right.  (Later, options may be added to
	add a horizontal bar as well, to make the bars disappear
	automatically when not needed, to move them to the other side of the
	window, etc.)
	Configuration options are passed to the Text widget.
	A Frame widget is inserted between the master and the text, to hold
	the Scrollbar widget. Most methods calls are inherited from the Text widget; Pack, Grid and
	Place methods are redirected to the Frame widget however.
	"""
	def __init__(self, master=None, **kw):
		self.frame = Frame(master)
		self.vbar = Scrollbar(self.frame)
		self.vbar.pack(side=RIGHT, fill=Y)

		kw.update({'yscrollcommand': self.vbar.set})
		Text.__init__(self, self.frame, **kw)
		self.pack(side=LEFT, fill=BOTH, expand=True)
		self.vbar['command'] = self.yview

		# Copy geometry methods of self.frame without overriding Text
		# methods -- hack!
		text_meths = vars(Text).keys()
		methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
		methods = methods.difference(text_meths)

		for m in methods:
			if m[0] != '_' and m != 'config' and m != 'configure':
				setattr(self, m, getattr(self.frame, m))

	def __str__(self):
		return str(self.frame)

from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread

def isCommand(msg):
	if msg.split()[0] == "server:":
		return True
	return False

def receive():
	# TODO test
	while 1:
		try:
			msg = clientSocket.recv(BUFSZ).decode("utf-8")
			print("msg contents =", msg)
			if not isCommand(msg):
				print("isCommand() = False")
				convo.insert(tkinter.END, "%s" % msg) # inserts received message into messages textbox
			else:
				# pertains to user entering/leaving chat, update active users list
				print("isCommand() = True")
				updateChatMembers(msg)
		except OSError: # client left chat?
			break

def send(event=None):
	# TODO test
	print("send() func called")
	msg = msgEntry.get()
	msgEntry.delete(0, tkinter.END) # when you send a message, this erases what's in the entry field
	clientSocket.send(toBytes(msg))
	if msg == QUITMSG:
		clientSocket.close()
		window.quit()



if __name__ == "__main__":
	import tkinter # for GUI
	import random # for randomly selecting GUI color
	import sys # for using command line arguent as hostname to connect to 

	#...Open connection to server	
	BUFSZ = 1024
	HOST = sys.argv[1]
	PORT = 8080
	ADDR = (HOST, PORT)
	clientSocket = socket(AF_INET, SOCK_STREAM)
	try:
		clientSocket.connect(ADDR)
	except:
		# connection failed
		print("The server is not available.")
		quit()

	window = tkinter.Tk()
	window.title("~ ChattChat ~")
	window.geometry("525x250")
	
	# MENU BAR
	def menuQuitCommand():
		window.quit() # TODO this doesn't work
	def menuHelpCommand():
		print("user clicked, asking for help.\nin CPSC4550, no one can hear you scream")
	menu = tkinter.Menu(window)
	newItem = tkinter.Menu(menu)
	newItem.add_command(label="Quit", command=menuQuitCommand)
	newItem.add_command(label="Help", command=menuHelpCommand)
	menu.add_cascade(label="Menu", menu=newItem)
	#window.config(menu=menu)
	# COLOR MENU BAR
	windowColors = ["gold", "orange", "indian red", "tomato", "dodger blue", "khaki", "navajo white"]
	window.configure(bg=windowColors[random.randint(0, len(windowColors)-1)]) #sets background color randomly
	colorMenu = tkinter.Menu(window)
	newItem_color = tkinter.Menu(colorMenu)
	def changeColorGold():
		window.configure(bg="gold")
	def changeColorOrange():
		window.configure(bg="orange")
	def changeColorIndianRed():
		window.configure(bg="indian red")
	def changeColorTomato():
		window.configure(bg="tomato")
	def changeColorDodgerBlue():
		window.configure(bg="dodger blue")
	def changeColorKhaki():
		window.configure(bg="khaki")
	def changeColorNavajoWhite():
		window.configure(bg="navajo white")
	def changeColorWhite():
		window.configure(bg="white")
	newItem_color.add_command(label="gold", command=changeColorGold)
	newItem_color.add_command(label="orange", command=changeColorOrange)
	newItem_color.add_command(label="indian red", command=changeColorIndianRed)
	newItem_color.add_command(label="tomato", command=changeColorTomato)
	newItem_color.add_command(label="dodger blue", command=changeColorDodgerBlue)
	newItem_color.add_command(label="khaki", command=changeColorKhaki)
	newItem_color.add_command(label="navajo white", command=changeColorNavajoWhite)
	newItem_color.add_command(label="white", command=changeColorWhite)
	
	menu.add_cascade(label="Choose Color", menu=newItem_color)
	window.config(menu=menu)

	# CHAT DIALOG AREA
	chatLbl = tkinter.Label(window, text="Conversation")
	chatLbl.grid(column=0, row=0, pady=5)
	convo = ScrolledText(window, width=40, height=10)
	#convo.insert(tkinter.END, "lorem ipsum dolor sit amet lorem ipsum dolor sit amet lorem ipsum dolor sit amet lorem ipsum dolor sit amet")
	#convo.insert(tkinter.END, "")
	convo.grid(column=0, row=1, sticky=tkinter.W, padx=5, pady=5)	

	# CHAT ROOM MEMBERS LIST AREA
	chatMembersLbl = tkinter.Label(window, text="People online")
	chatMembersLbl.grid(column=2, row=0, pady=5)
	chatMembers = ScrolledText(window, width=15, height=10)
	#chatMembers.insert(tkinter.END, "lorem ipsum dolor sit amet lorem ipsum dolor sit amet lorem ipsum dolor sit amet lorem ipsum dolor sit amet")
	#chatMembers.insert(tkinter.END, "") # writes text to box
	chatMembers.grid(column=2, row=1, columnspan=2, padx=5, pady=5)
	def updateChatMembers(msg):
		words = msg.split()
		#print(eval(''.join(words[1:])))
		userlist = eval(''.join(words[1:]))
		chatMembers.config(state=tkinter.NORMAL)
		chatMembers.delete(1.0, tkinter.END)
		for user in userlist:
			chatMembers.insert(tkinter.END, "\n%s" % user)

	# MESSAGE ENTRY FIELD
	msgEntry = tkinter.Entry(window, width=30)
	msgEntry.grid(column=0, row=2)
	msgEntry.focus_set() #should make cursor snap to this area when window is activated

	# SEND OPERATION HANDLER
	# event=None required to work for msgEntry 'Return' key binding...some real nonsense
	def sendClicked(event=None):
		print("send button was clicked.")
		print("text in msgEntry box was--", msgEntry.get())
		send()
	msgEntry.bind("<Return>", sendClicked)
	# SEND BUTTON
	sendButton = tkinter.Button(window, text="Send", command=sendClicked)
	sendButton.grid(column=1, row=2, padx=5, pady=10, sticky=tkinter.E)

	# CLOSING FUNCTIONALITY
	def onClosing(event=None):
		# TODO this doesn't work at all LOL
		msgEntry.set(QUITMSG)
		send()
		window.quit()
		quit()
	window.protocol("WM_DELETE_WINDOW", onClosing)

	# Start various threads and helper functions to continuously update different text boxes, etc.
	def refocusConvo():
		#https://stackoverflow.com/questions/25753632/tkinter-how-to-use-after-method
		convo.tk.eval(convo.vbar['command'] + ' moveto 1.0') # this snaps the conversation area to the bottom line/ last message sent. https://stackoverflow.com/questions/44190742/how-to-position-a-scrolledwindow-tkinter-scrollbar-at-the-bottom
		window.after(100, refocusConvo) # function calls itself every 100 ms
	receiveThread = Thread(target = receive)
	receiveThread.start()
	window.after(0, refocusConvo) # makes refocusConvo run once (which calls itself)
	
	window.mainloop()
	