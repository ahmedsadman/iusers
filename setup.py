from distutils.core import setup
import py2exe

includes = ['win32api', 'win32con', 'win32gui', 'json', 'win10toast']

setup(
	options = {
		"py2exe":
		{
			"includes": includes,
			"bundle_files": 3,
			"optimize": 2,
		}
	},
	console=['iusers.py'], zipfile=None)