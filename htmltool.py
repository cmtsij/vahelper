import re
import HTMLParser

# HTML entity tranlate to unicode
# ref: http://fredericiana.com/2010/10/08/decoding-html-entities-to-text-in-python/
def decode_entity(html):
    html=HTMLParser.HTMLParser().unescape(html)
    html=re.sub("(&#x?)([\d]{1,5}|[\da-f]{1,4});",
                lambda m:(unichr(int(m.group(2),16)) if (len(m.group(1)) == 3) else unichr(int(m.group(2),10))),
                html,
                re.IGNORECASE)
    
    return html

# ref from nltk.clean_html(html)
def remove_tags(html, remove_tags_list=["script","style","head","nobr","span","cite"], repl=""):
    html=html.strip()
    if len(remove_tags_list):
        # First we remove inline JavaScript/CSS:
        html = re.sub(r"(?is)<(%s).*?>.*?(</\1>)"%("|".join(remove_tags_list)), repl, html)
    return html

def clean_tags(html,repl=""):
    html=html.strip()
    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    html = re.sub(r"(?s)<!--(.*?)-->[\n]?", repl, html)
    # Next we can remove the remaining tags:
    html = re.sub(r"(?s)<.*?>", repl, html)
    return html
    

#UNITEST
if __name__ == "__main__":
    import defaultencoding
    print decode_entity(u'&copy;'+u'&#169;'+u'&#xa9;')

    html=remove_tags("Ahead<a>Adata</a>Atail\n<b>Bdata</b>",["a"],"_repl_")
    print "==== some tag removed start ====\n%s\n==== some tag removed end ===="%(html)

    html=clean_tags(html)
    print "==== clean test start ====\n%s\n==== clean test end ===="%(html)
    
