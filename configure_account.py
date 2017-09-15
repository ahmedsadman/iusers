import wx
import json

class ChangeAccountGUI(wx.Frame):
	def __init__(self, *args, **kwargs):
		super(ChangeAccountGUI, self).__init__(*args, **kwargs)
		self.data = self.load_json()
		self.InitUI()


	def InitUI(self):
		panel = wx.Panel(self, -1)
		vbox = wx.BoxSizer(wx.VERTICAL)
		combo_choice = ["Account 1", "Account 2", "Account 3", "Account 4", "Account 5"]
		self.combo_box = wx.ComboBox(panel, choices=combo_choice, style=wx.CB_READONLY)
		self.combo_box.SetSelection(0)

		self.st_info = wx.StaticText(panel, label='IUSERS Account')
		self.st_user = wx.StaticText(panel, label='Username/Email')
		self.st_pass = wx.StaticText(panel, label='Password')
		self.st_conn = wx.StaticText(panel, label='Connection Name')

		self.user_txt = wx.TextCtrl(panel, size=(200, -1))
		self.pass_txt = wx.TextCtrl(panel, size=(200, -1))
		self.conn_txt = wx.TextCtrl(panel, size=(200, -1))
		self.btnConfirm = wx.Button(panel, label='Save and Activate', size = (130, 40))
		self.loadcombo()

		vbox.Add(-1, 10)
		vbox.Add(self.st_info, flag = wx.LEFT | wx. RIGHT, border = 20)
		vbox.Add(-1, 10)
		vbox.Add(self.combo_box, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(-1, 10)
		vbox.Add(self.st_user, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(self.user_txt, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(-1, 10)
		vbox.Add(self.st_pass, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(self.pass_txt, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(-1, 10)
		vbox.Add(self.st_conn, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(self.conn_txt, flag = wx.LEFT | wx.RIGHT, border = 20)
		vbox.Add(-1, 20)
		centre_pos = vbox.GetMinSize()[0]/2 - 65
		vbox.Add(self.btnConfirm, flag = wx.LEFT, border = centre_pos)
		vbox.Add(-1, 10)
		panel.SetSizer(vbox)

		# event bindings
		self.Bind(wx.EVT_COMBOBOX, self.onCombo, self.combo_box)
		self.Bind(wx.EVT_BUTTON, self.onSave, self.btnConfirm)

		self.SetSize(vbox.GetMinSize()[0], vbox.GetMinSize()[1])
		vbox.Fit(self)
		self.Centre()
		self.Show(True)


	def SetFieldValue(self, info):
		self.user_txt.SetValue(info['username'])
		self.pass_txt.SetValue(info['password'])
		self.conn_txt.SetValue(info['connection'])


	def onCombo(self, e):
		active = e.GetString().split()[1]
		info = self.data['info'][int(active)-1]
		print info['username'], info['password']
		self.SetFieldValue(info)


	def loadcombo(self):
		active = int(self.data['active']) - 1
		# when no account is configured, first account is auto-selected
		if active < 0:
			active = 0

		info = self.data['info'][active]
		self.combo_box.SetSelection(active)
		self.SetFieldValue(info)


	def onSave(self, e):
		active = int(self.combo_box.GetStringSelection().split()[1]) - 1
		self.data['info'][active]['username'] = self.user_txt.GetValue()
		self.data['info'][active]['password'] = self.pass_txt.GetValue()
		self.data['info'][active]['connection'] = self.conn_txt.GetValue()
		self.data['active'] = active + 1

		with open('login_info.json', 'w') as f:
			f.write(json.dumps(self.data))
		if not f.closed: f.close()

		self.Destroy()


	def load_json(self):
		with open('login_info.json') as jfile:
			data = json.load(jfile)
		if not jfile.closed: jfile.close()
		return data


def main():
	app = wx.App()
	ChangeAccountGUI(None, -1, 'Configure Account', style=wx.STAY_ON_TOP | wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX)
	app.MainLoop()


if __name__ == "__main__":
	main()