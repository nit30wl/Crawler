# HTTP brute forcer to find hidden resources.
# goal of script: find hidden resources by appending the URL via iteration of a given text file and gives status codes as well.
# additions from 1.0: sorting status codes by color, gives # of chars, words, and lines. hides results by status codes for filtering.
# additions from 1.1: detects redirects, gives response times, generates a hash of the content response.
# brute forces forms 

import requests
from threading import Thread
import sys
import getopt
import time
import re
import termcolor
from termcolor import colored
import hashlib


def banner():
    print('\n*****************************************')
    print('* ForzaBruta 1.3 *')
    print('*****************************************')

def usage():
    print('Usage:')
    print('         -w: url (http://somesite.com/FUZZ)')
    print('         -t: threads')
    print('         -f: dictionary file\n')
    print('         -c: filter by status code')
    print('example: forzabruta.py -w http://www.targetsite.com/FUZZ -t 5 -f common.txt\n')


class request_performer(Thread):
    def __init__(self,word,url,hidecode, payload):
        Thread.__init__(self)
        self.word = word.split('\n')[0]
        self.urly = url.replace('FUZZ',self.word)
        self.url = self.urly
        if payload != '':
            self.payload = payload.replace('FUZZ', self.word)
        else:
            self.payload = payload
        self.hidecode = hidecode


    def run(self):
    #    try:
            start = time.time()
            if self.payload == '':
                r = requests.get(self.url)
                elaptime = time.time()
                totaltime = str(elaptime - start)
            else:
                list = self.payload.replace('=',' ').replace('&', ' ').split(' ')
                payload = dict([(k, v) for k,v in zip (list[::2], list[1::2])])
                r = requests.post(self.url, data = payload)
                elaptime = time.time()
                totaltime = str(elaptime - start)[1:10]

            lines = str(r.content).count('\n') #content returns byte object, wrap in string to fix
            chars = len(r._content)
            words = len(re.findall('\S+', str(r.content)))
            code = r.status_code
            hash = hashlib.md5(r.content).hexdigest()

            if r.history != []:
                first = r.history[0]
                code = first.status_code
            else:
                pass

            if self.hidecode != code:
                if 200 <= code < 300:
                    print("{} \t {} \t {} \t {} \t {} \t {} \t {}".format(totaltime,colored(code,'green'),chars,words,lines,r.headers['server'],self.word))
                elif 300 <= code < 400:
                    print("{} \t {} \t {} \t {} \t {} \t {} \t {}".format(totaltime,colored(code,'blue'),chars,words,lines,r.headers['server'],self.word))
                elif 400 <= code < 500:
                    print("{} \t {} \t {} \t {} \t {} \t {} \t {}".format(totaltime,colored(code,'red'),chars,words,lines,r.headers['server'],self.word))
                else:
                    print("{} \t {} \t {} \t {} \t {} \t {} \t {}".format(totaltime,colored(code,'yellow'),chars,words,lines,r.headers['server'],self.word))
            else:
                pass
            i[0] = i[0] - 1  #remove one thread from the counter
    #    except Exception as e:
    #        print('Exception 2:',e)

def start(argv):
    banner()
    if len(sys.argv) < 5:
        usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(argv,'w:f:t:p:c:')
    except getopt.GetoptError:
            print('Error in arguments')
            sys.exit()
    hidecode = 000
    payload = ''
    for opt,arg in opts:
        if opt == '-w':
            url = arg
        elif opt == '-f':
            dict =  arg
        elif opt == '-t':
            threads = arg
        elif opt == '-p':
            payload = arg
        elif opt == '-c':
            hidecode = arg
    try:
        f = open(dict, 'r')
        words = f.readlines()
    except:
        print('Failed opening file: '+ dict+ '\n')
        sys.exit()
    launcher_thread(words,threads,url,hidecode,payload)

def launcher_thread(names,th,url,hidecode,payload):
    global i
    i = []
    resultlist = []
    i.append(0)
    print('--------------------------------------------------------------------------------------------------------')
    print('Time' + '\t\t\t' + 'Code' + '\tChars\tWords\tLines\tMD5\t\t\t\t\t String')
    print('--------------------------------------------------------------------------------------------------------')
    while len(names):
        try:
            if i[0] < len(th):
                n = names.pop(0)
                i[0] = i[0] + 1
                thread = request_performer(n,url,hidecode,payload)
                thread.start()

        except KeyboardInterrupt:
            print('ForzaBruta interrupted by user. Finishing attack...')
            sys.exit()
        thread.join()
    return

if __name__ == '__main__':
    try:
        start(sys.argv[1:])
    except KeyboardInterrupt:
        print('ForzaBruta interrupted by user, killing all threads..!')
