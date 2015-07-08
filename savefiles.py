#!/usr/bin/python
import loadlyr

loadlyr.cfg_logfilename = "load.log"
loadlyr.cfg_errlog = "loaderr.log"
loadlyr.cfg_addrlog = "addr.log"
loadlyr.cfg_artistlog = "artst.log"
loadlyr.cfg_songsavepath = "lyrlib/"
loadlyr.cfg_referencesite = "azlyrics.com"
# loadlyr.cfg_siteroot = "http://web.archive.org"
# loadlyr.cfg_archroot = "http://web.archive.org/web/20140831154350/http://www.azlyrics.com/"
# loadlyr.cfg_siteroot = "http://www.azlyrics.com"
# loadlyr.cfg_archroot = "http://www.azlyrics.com"
loadlyr.cfg_siteroot = "http://web.archive.org"
loadlyr.cfg_archroot = "http://web.archive.org/web/20150609111537/http://www.azlyrics.com/"
loadlyr.config_verbose = 1

letterlinklist = []
pagetitle = []
parsedhtml = loadlyr.getparsedhtmlbyurl(loadlyr.cfg_archroot)
if parsedhtml[0] == 1:
    # loadlyr.getlistofurlsfromdivs(parsedhtml[1], ["listrow"], letterlinklist, "class", pagetitle)
    loadlyr.getlistofurlsfromdivs(parsedhtml[1], ["btn-group text-center"], letterlinklist, "class", pagetitle)
    loadlyr.savelog("currpage:" + pagetitle.pop())
    for oneletterlink in letterlinklist:
        loadlyr.saveoneletter(oneletterlink[0])
