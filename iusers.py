import os
import json
import sys
import requests
import wx
import time
import win32gui
import win32con
import platform
from subprocess import call
from win10toast import ToastNotifier
from bs4 import BeautifulSoup
from threading import Thread

LOGIN_URL = 'http://10.220.20.12/index.php/home/loginProcess'


def setToCorner(win):
	x, y, dw, dh = wx.ClientDisplayRect()
	w, h = win.GetSize()
	x = dw - w - 3
	y = dh - h - 6
	win.SetPosition((x, y))


class CustomNotification(wx.Frame):
	def __init__(self, user, time_total, time_rem, bill, *args, **kwargs):
		super(CustomNotification, self).__init__(*args, **kwargs)
		self.user = user
		self.time_total = time_total
		self.time_rem = time_rem
		self.bill = bill
		self.amount = 0
		self.delta = 15
		self.InitUI()

	def InitUI(self):
		panel = wx.Panel(self, -1)
		self.SetTransparent(self.amount)
		hbox_main = wx.BoxSizer(wx.HORIZONTAL)
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		vbox2 = wx.BoxSizer(wx.VERTICAL)

		self.font_content = wx.Font(pointSize = 12, family = wx.DEFAULT, faceName = "Cambria", style = wx.NORMAL, weight = wx.NORMAL)

		#self.stbox = wx.StaticBox(panel, label="Usage", size = (240, 170))
		self.st_user_name = wx.StaticText(panel, label="User")
		self.st_user = wx.StaticText(panel, label = self.user)
		self.st_usage_name = wx.StaticText(panel, label = "Total Usage")
		self.st_usage_rem = wx.StaticText(panel, label = "Remaining")
		self.st_usage = wx.StaticText(panel, label=self.time_total)
		self.st_rem = wx.StaticText(panel, label=self.time_rem)

		self.st_user_name.SetFont(self.font_content)
		self.st_user.SetFont(self.font_content)
		self.st_usage_name.SetFont(self.font_content)
		self.st_usage.SetFont(self.font_content)
		self.st_usage_rem.SetFont(self.font_content)
		self.st_rem.SetFont(self.font_content)

		#vbox.Add(self.stbox, flag = wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border = 10)
		vbox1.Add(-1, 5)
		vbox2.Add(-1, 5)
		vbox1.Add(self.st_user_name)
		vbox1.Add(-1, 3)
		vbox2.Add(self.st_user)
		vbox2.Add(-1, 3)
		vbox1.Add(self.st_usage_name)
		vbox1.Add(-1, 3)
		vbox2.Add(self.st_usage)
		vbox2.Add(-1, 3)
		vbox1.Add(self.st_usage_rem)
		vbox2.Add(self.st_rem)

		# check if there are any bills, and show if necessary
		if self.bill:
			vbox1.Add(-1, 3)
			vbox2.Add(-1, 3)
			self.st_bill_name = wx.StaticText(panel, label="Bill")
			self.st_bill = wx.StaticText(panel, label=self.bill)
			self.st_bill_name.SetFont(self.font_content)
			self.st_bill.SetFont(self.font_content)
			vbox1.Add(self.st_bill_name)
			vbox2.Add(self.st_bill)

		vbox1.Add(-1, 5)
		vbox2.Add(-1, 5)
		hbox_main.Add(vbox1, flag = wx.LEFT | wx.RIGHT, border = 40)
		hbox_main.Add(vbox2, flag = wx.LEFT | wx.RIGHT, border = 40)
		panel.SetSizer(hbox_main)
		hbox_main.Fit(self)
		#self.SetSize(200, 200)
		setToCorner(self)

		## ------- Fader Timer -------- ##
		self.timer = wx.Timer(self, wx.ID_ANY)
		self.timer.Start(5)
		self.Bind(wx.EVT_TIMER, self.FadeIn)
		## ---------------------------- ##
		
		self.Show(True)
		Thread(target=self.DestroyIt).start()

	def FadeIn(self, evt):
		self.amount += self.delta
		if self.amount >= 255:
			self.amount = 255
			self.timer.Stop()
		self.SetTransparent(self.amount)

	def DestroyIt(self):
		time.sleep(7)
		wx.CallAfter(self.Destroy)


def intro():
	try:
		import ctypes
		ctypes.windll.kernel32.SetConsoleTitleA('IUSERS Notify')
	except ImportError:
		pass

	print "IUSERS Notify"
	print "Developed by : Sadman Muhib Samyo"
	print "Email: ahmedsadman.211@gmail.com"
	print "---------------------------------\n"


def load_json(file):
	with open('login_info.json') as jfile:
		data = json.load(jfile)
	return data


def get_usage(htmldata):
	usage = {
		'username': None,
		'total': 0,
		'remaining': 0,
		'bill': None
	}
	free_limit = 3000

	soup = BeautifulSoup(htmldata, 'html.parser')
	table = soup.find('table', attrs={'class':'table invoicefor'})
	table_body = table.find('tbody')
	rows = table_body.find_all('tr')

	for row in rows:
		cols = row.find_all('td')
		if 'Username' in cols[0].text:
			usage['username'] = cols[1].text
		elif 'Total Use' in cols[0].text:
			usage['total'] = int(cols[1].text.split()[0])
		elif 'Free Limit' in cols[0].text:
			free_limit = int(cols[1].text)
		elif 'Estimated Bill' in cols[0].text and '0 Taka' not in cols[1].text:
			usage['bill'] = cols[1].text

	usage['remaining'] = free_limit - usage['total']
	return usage


def connect_internet(username, password, connection):
	print 'Connecting using %s\n' % username
	conn = call(['rasdial', connection, username, password]);
	if conn == 0:
		print '\nSuccessfully connected'
	else:
		print '\n\nAn error occured\n'
		print 'Possible Reasons of error:'
		print '1. Username or Password or Connection Name is incorrect'
		print '2. There is a problem with IUT server'
		raw_input("")
		sys.exit(-1)


def notify(usage):
	try:
		toaster = ToastNotifier()
		user = '%s\t\t:    %s\n' % ('User', usage['username'])
		total = '%s\t\t:    %s\n' % ('Total Use', usage['total'])
		rem = '%s\t:    %s' % ('Remaining', usage['remaining'])
		bill = '%s\t\t:    %s' % ('Bill', usage['bill'])

		if usage['bill'] == None:
			string = user + total + rem
		else:
			string = user + total + rem + '\n' + bill

		toaster.show_toast("Internet Usage", string, icon_path="python.ico")
	except:
		app = wx.App()
		CustomNotification(usage["username"], repr(usage["total"]), repr(usage["remaining"]), usage["bill"], None, -1, style=wx.STAY_ON_TOP | wx.CLOSE_BOX)
		app.MainLoop()


def on_disconnect(payload):
	call(['rasdial', '/disconnect'])
	print "Disconnected\n"

	# minimize the script window
	try:
		Minimize = win32gui.GetForegroundWindow()
		win32gui.ShowWindow(Minimize, win32con.SW_MINIMIZE)
	except:
		pass

	time.sleep(1)
	try:
		r = requests.post(LOGIN_URL, data=payload)
		usage = get_usage(r.text)
	except:
		print "Error occured. Please make sure 10.220.20.12 (IUSERS website) is accessible from your cable/wifi."
		raw_input("")
		sys.exit(-1)

	try:
		notify(usage)
		sys.exit(0)
	except Exception, e:
		print "An error occured related to toast notification. Please contact the developer with the error"
		print "ERROR: ", e
		raw_input("")
		sys.exit(-1)


def main():
	intro()
	# win_ver= platform.win32_ver()[0]
	# if win_ver != '10':
	# 	print 'Sorry, this program is made only for Windows 10'
	# 	raw_input("")
	# 	sys.exit(0)

	data = load_json('login_info.json')
	active = data['active']
	if int(active) == 0:
		print "## No account configured. Please run configure_account to enter account details ##"
		raw_input("")
		sys.exit(0)

	info = data['info'][int(active)-1]
	payload = {'username': info['username'], 'password': info['password']}

	connect_internet(info['username'], info['password'], info['connection'])
	print "\nPress ENTER to disconnect"
	raw_input("")
	on_disconnect(payload)


if __name__ == '__main__':
	main()
