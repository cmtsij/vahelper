import sys
import locale
reload(sys)

encode=locale.getpreferredencoding()
if encode.lower() not in ["mbcs","utf-8"]:
    encode = "utf-8"
sys.setdefaultencoding(encode)

#UNITEST
if __name__ == "__main__":
    print "locale preferred encoding: " +locale.getpreferredencoding() 
    print "sys default encoding: "+ sys.getdefaultencoding()
