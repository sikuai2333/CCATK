'''
I'm working on Aoyama's update so this project will stop for a while
'''
import requests
import socket
import socks
import time
import random
import json
import threading
import sys
import ssl
import urllib.request

url1 = 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt'
url2 = 'https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt'
url3 = 'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/socks5.txt'
url4 = 'https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt'
url5 = ''
url6 = 'https://raw.githubusercontent.com/prxchk/proxy-list/main/all.txt'
url7 = ''

# https://raw.githubusercontent.com/Zaeem20/FREE_PROXIES_LIST/blob/master/socks5.txt

useragents = ["Mozilla/5.0 (Android; Linux armv7l; rv:10.0.1) Gecko/20100101 Firefox/10.0.1 Fennec/10.0.1",
              "Mozilla/5.0 (iphone x Build/MXB48T; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.49 Mobile MQQBrowser/6.2 TBS/043632 Safari/537.36 MicroMessenger/6.6.1.1220(0x26060135) NetType/WIFI Language/zh_CN",]

acceptall = [
    "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\nAccept-Language: en-US,en;q=0.5\r\nAccept-Encoding: gzip, deflate\r\n",
    "Accept: text/plain;q=0.8,image/png,*/*;q=0.5\r\nAccept-Charset: iso-8859-1\r\n",]
referers = [
    "https://www.google.com/search?q=",
    "https://check-host.net/",
    "https://www.facebook.com/",
    "https://www.youtube.com/",
    "https://www.fbi.com/",
    "https://www.bing.com/search?q=",
    "https://r.search.yahoo.com/",
]

strings = "asdfghjklqwertyuiopZXCVBNMQWERTYUIOPASDFGHJKLzxcvbnm1234567890&"
socket_list = []
nums = 0


def checking(lines, socks_type, ms):  # Proxy checker coded by BlueSkyXN
    global nums
    global proxies
    proxy = lines.strip().split(":")
    try:
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5,
                              str(proxy[0]), int(proxy[1]), True)
    except:
        pass
    err = 0
    while True:
        if err == 3:
            proxies.remove(lines)
            break
        try:
            s = socks.socksocket()
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(ms)  # You can change by yourself
            s.connect((str(ip), int(port)))
            if port == 443:
                s = ssl.wrap_socket(s)
            s.send(str.encode("GET / HTTP/1.1\r\n\r\n"))
            s.close()
            break
        except:
            err += 1
    nums += 1


def check_socks(ms):  # Coded by BlueSkyXN
    global nums
    thread_list = []
    for lines in list(proxies):
        th = threading.Thread(target=checking, args=(lines, 5, ms,))
        th.start()
        thread_list.append(th)
        time.sleep(0.01)
        sys.stdout.write("> Checked "+str(nums)+" proxies\r")
        sys.stdout.flush()
    for th in list(thread_list):
        th.join()
        sys.stdout.write("> Checked "+str(nums)+" proxies\r")
        sys.stdout.flush()
    print("\r\n> Checked all proxies, Total Worked:"+str(len(proxies)))
    ans = "y"
    if ans == "y" or ans == "":
        with open("socks5.txt", 'wb') as fp:
            for lines in list(proxies):
                fp.write(bytes(lines, encoding='utf8'))
        fp.close()
        print("> They are saved in socks5.txt.")


def check_list(socks_file):
    print("> Checking list")
    temp = open(socks_file).readlines()
    temp_list = []
    for i in temp:
        if i not in temp_list:
            temp_list.append(i)
    rfile = open(socks_file, "wb")
    for i in list(temp_list):
        rfile.write(bytes(i, encoding='utf-8'))
    rfile.close()


def main():
    global ip
    global url2
    global port
    global proxies
    global multiple
    global choice
    ip = ""
    thread_num = int(2000)
    port = ""
    # print("> Mode: [cc/post/slow/check]")
    mode = str("check")
    ip = str("1.1.1.1")
    port = str("80")
    socks_type = 5
    choice = ""
    f = open("socks5.txt", 'wb')
    try:
        r = requests.get(
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&country=all")
        f.write(r.content)
    except:
        pass
    try:
        r = requests.get(
            "https://www.proxy-list.download/api/v1/get?type=socks5")
        f.write(r.content)
        f.close()
    except:
        f.close()
    getList()
    clearBlankLine()
    print("> Have already downloaded socks5 list as socks5.txt")
    out_file = str("socks5.txt")
    check_list(out_file)
    proxies = open(out_file).readlines()
    print("> Number Of Socks%s Proxies: %s" % (choice, len(proxies)))
    time.sleep(0.03)
    ans = "y"
    if ans == "y":
        ms = int(2)
        try:
            ms = int(ms)
        except:
            ms = float(ms)
        check_socks(ms)
    print("> End of process")
    return


def getList():
    try:
        res1 = requests.get(url=url1, timeout=20)
        print("url1访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res1.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', '').replace('socks4://', ''))
            f.close
    except:
        print("url1访问失败")
    try:
        res2 = requests.get(url=url2, timeout=20)
        print("url2访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res2.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', ''))
            f.close
    except:
        print("url2访问失败")
    try:
        res3 = requests.get(url=url3, timeout=20)
        print("url3访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res3.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', ''))
            f.close
    except:
        print("url3访问失败")
    try:
        res4 = requests.get(url=url4, timeout=20)
        print("url4访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res4.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', ''))
            f.close
    except:
        print("url4访问失败")
    try:
        res5 = requests.get(url=url5, timeout=20)
        print("url5访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res5.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', ''))
            f.close
    except:
        print("url5访问失败")
    try:
        res6 = requests.get(url=url6, timeout=20)
        print("url6访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res6.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', ''))
            f.close
    except:
        print("url6访问失败")
    try:
        res7 = requests.get(url=url7, timeout=20)
        print("url7访问成功")
        with open('temp.txt', 'a') as f:
            f.write(res7.text.replace('socks5://',
                    '').replace('http://', '').replace('https://', ''))
            f.close
    except:
        print("url7访问失败")


def clearBlankLine():
    file1 = open('temp.txt', 'r', encoding='utf-8')  # 要去掉空行的文件
    file2 = open('socks5.txt', 'w', encoding='utf-8')  # 生成没有空行的文件
    try:
        for line in file1.readlines():
            if line == '\n':
                line = line.strip("\n")
            file2.write(line)
    finally:
        file1.close()
        file2.close()


if __name__ == "__main__":
    with open('temp.txt', 'w') as f:
        f.write("")
        f.close
        with open('socks5.txt', 'w') as f:
            f.write("")
            f.close
    main()  # Coded by BlueSkyXN
