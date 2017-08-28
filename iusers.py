import os
import json
import sys
import requests
import time
import win32gui
import win32con
import platform
from subprocess import call
from win10toast import ToastNotifier
from bs4 import BeautifulSoup

LOGIN_URL = 'http://10.220.20.12/index.php/home/loginProcess'


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
    print 'Connecting using %s' % username
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
    r = requests.post(LOGIN_URL, data=payload)
    usage = get_usage(r.text)
    notify(usage)
    sys.exit(0)


def main():
    intro()
    win_ver= platform.win32_ver()[0]
    if win_ver != '10':
        print 'Sorry, this program is made only for Windows 10'
        raw_input("")
        sys.exit(0)

    data = load_json('login_info.json')['info']
    payload = {'username': data['username'], 'password': data['password']}

    connect_internet(data['username'], data['password'], data['connection'])
    print "\nPress ENTER to disconnect"
    raw_input("")
    on_disconnect(payload)


if __name__ == '__main__':
    main()
