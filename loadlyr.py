#!/usr/bin/python
import urllib
import urllib.request
import lxml.html
import lxml.html.clean
import time
import os
import os.path
import string
import datetime
import socket

config_urlloaddelay = 0
config_loadtimeout = 3
config_gui = 0
cfg_logfilename = ""
cfg_errlog = ""
cfg_songsavepath = ""
cfg_referencesite = ""
cfg_siteroot = ""
cfg_archroot = ""
cfg_addrlog = ""
cfg_artistlog = ""
config_verbose = 1
cfg_maxretries = 10


def getparsedhtmlbyurl(purl):
    savelog("opening url " + purl)
    socket.setdefaulttimeout(config_loadtimeout)
    execstat = 0
    maxretries = cfg_maxretries
    retries = 0
    parsedpage = None
    while (execstat == 0) and (retries < maxretries):
        retries += 1
        try:
            if retries != 1:
                if config_urlloaddelay != 0:
                    time.sleep(config_urlloaddelay)
            sock = urllib.request.urlopen(purl)
            htmlsource = sock.read()
            sock.close()
        # except urllib.request.HTTPError as e:
        #     execstat = 0
        #     savelog("error " + str(e.code))
        except urllib.request.URLError as e:
            execstat = 0
            savelog("error fetching " + purl + ": " + str(e.reason))
            # return execstat, parsedpage
        except socket.timeout:
            execstat = 0
            savelog("error fetching " + purl + ": timeout")
        else:
            execstat = 1
            parsedpage = lxml.html.fromstring(htmlsource)
            return execstat, parsedpage
    if retries >= maxretries:
        savelog("load failed after " + str(retries) + " retries " + purl)
    return execstat, parsedpage


def clearfname(pfname):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    pfname = ''.join(c for c in pfname if c in valid_chars)
    return pfname


def getlistofurlsfromdivs(htmlpage, divlist, linklist, typeattrib, ppagetitle):  # typeattrib - class, id
    ppagetitle.append(htmlpage.find(".//title").text)
    divset = set(divlist)
    for currdiv in htmlpage.body.iter("div"):
        if currdiv.get(typeattrib) in divset:
            for linkinstance in currdiv.iter():
                if linkinstance.get("href") is not None:
                    stringurl = str(linkinstance.get("href"))
                    addlink(linklist, stringurl, linkinstance.text)
    return


def getlistofurlsfromalbumdiv(htmlpage, linklist, ppagetitle):  # typeattrib - class, id
    curralbum = ""
    ppagetitle.append(htmlpage.find(".//title").text)
    divset = {"listAlbum"}
    for currdiv in htmlpage.body.iter("div"):
        if currdiv.get("id") in divset:
            for linkinstance in currdiv.iter():
                if linkinstance.tag == "b":
                    curralbum = linkinstance.tail + linkinstance.text
                if linkinstance.get("href") is not None:
                    stringurl = str(linkinstance.get("href"))
                    addlink(linklist, stringurl, (linkinstance.text, curralbum))
    return


def gettextfromhtml(htmlpage):
    songtitle = htmlpage.find(".//title").text
    songtext = ""
    for currdiv in htmlpage.body.iter("div"):
        if currdiv.get("id") == "main":
            maindiv = currdiv
            for subdiv in maindiv.iter("div"):
                if (subdiv.get("class") is None) and (subdiv.get("id") != "main"):
                    songtext = songtext + subdiv.text_content()
    return songtitle, songtext


def savelog(msg):
    if cfg_logfilename != "":
        msg1 = "".join([str(datetime.datetime.now()), " ", msg])
        with open(cfg_logfilename, 'a') as f:
            f.write(msg1 + "\n")
        if config_verbose == 1:
            print(msg1)
    return


def saveartistlog(artistname, artistlink):
    if cfg_artistlog != "":
        # msg1 = "".join([str(datetime.datetime.now()), " ", artistname, " ", artistlink])
        msg1 = "".join(["'", artistname.replace("'", "''"), "','", artistlink, "'"])
        with open(cfg_artistlog, 'a') as f:
            f.write(msg1 + "\n")
        if config_verbose == 1:
            print(msg1)
    return


def savesong(filename, songcontent):
    with open(filename, "a") as f:
        f.write(songcontent[0] + "\n" + songcontent[1] + "\n")


def saveerrlog(errtype, msg):
    if cfg_errlog != "":
        msg1 = "".join([errtype, msg, "\n"])
        with open(cfg_errlog, 'a') as f:
            f.write(msg1)
    return


def saveaddrlog(addr):
    if cfg_addrlog != "":
        msg1 = "".join([addr, "\n"])
        with open(cfg_addrlog, 'a') as f:
            f.write(msg1)
    return


def savesongbyurl(songlink, fname, foldername):
    parsedhtml = getparsedhtmlbyurl(songlink)
    if parsedhtml[0] == 1:
        songcontent = gettextfromhtml(parsedhtml[1])
        # if not os.path.exists(cfg_songsavepath + foldername):
        #    os.makedirs(cfg_songsavepath + foldername)
        makedir(cfg_songsavepath + foldername)
        savesong(cfg_songsavepath + foldername + "/" + fname + ".txt", songcontent)
        savelog("saved " + songcontent[0])
    else:
        saveerrlog("3", songlink)


def saveoneartist(artistlink):
    saveartistlog(artistlink[1], artistlink[0])
    # songlinklist = []
    # pagetitle = []
    # parsedhtml = getparsedhtmlbyurl(artistlink)
    # if parsedhtml[0] == 1:
    #    currpagetitle = pagetitle.pop()
    #    saveartistlog(currpagetitle, artistlink)
    #    savelog("started saving songs of " + currpagetitle)
    #    getlistofurlsfromdivs(parsedhtml[1], ["listAlbum"], songlinklist, "id", pagetitle)
    #    for onesonglink in songlinklist:
    #       savesongbyurl(onesonglink[0], clearfname(onesonglink[1]))
    #    savelog("finished saving songs of " + currpagetitle)
    # else:
    #    saveerrlog("2", artistlink)


def saveoneartistpage(artistlink):
    songlinklist = []
    pagetitle = []
    parsedhtml = getparsedhtmlbyurl(artistlink)
    if parsedhtml[0] == 1:
        currpagetitle = parsedhtml[1].find(".//title").text
        saveartistlog(currpagetitle, artistlink)
        savelog("started saving songs of " + currpagetitle)
        getlistofurlsfromalbumdiv(parsedhtml[1], songlinklist, pagetitle)
        ctr = 0
        albname = ""
        for onesonglink in songlinklist:
            if albname != clearfname(onesonglink[1][1]):
                albname = clearfname(onesonglink[1][1])
                ctr += 1
            savesongbyurl(onesonglink[0], str(ctr).zfill(4) + " " + clearfname(onesonglink[1][1]),
                          clearfname(currpagetitle))
        savelog("finished saving songs of " + currpagetitle)
    else:
        saveerrlog("2", artistlink)
    return


def saveoneletter(letterlink):
    artistlinklist = []
    pagetitle = []
    parsedhtml = getparsedhtmlbyurl(letterlink)
    if parsedhtml[0] == 1:
        # getlistofurlsfromdivs(parsedhtml[1], ["artists fr", "artists fl"], artistlinklist, "class", pagetitle)
        getlistofurlsfromdivs(parsedhtml[1], ["col-sm-6 text-center artist-col"], artistlinklist, "class", pagetitle)
        savelog("currpage:" + pagetitle.pop())
        for oneartistlink in artistlinklist:
            saveoneartist(oneartistlink)
    else:
        saveerrlog("1", letterlink)
    return


def addlink(linklist, address, caption):
    saveaddrlog(address)
    if len(address) > 4:
        if address[0:1] == "/":
            if address[0:4].lower() == "/web":
                if address.find(cfg_referencesite) != -1:
                    linklist.append((cfg_siteroot + address, caption))
        else:
            if address[0:4].lower() != "http":
                linklist.append((cfg_archroot + address, caption))
            else:
                linklist.append((address, caption))
    return


def makedir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return
