"""i18n/*.json の訳を index.html の I18N 定数に埋め込む。
使い方: python3 tools/build_i18n.py            （埋め込み）
        python3 tools/build_i18n.py --missing  （訳のない日本語文字列を一覧）"""
import json,re,sys,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML=os.path.join(ROOT,'index.html'); LANGS=['en','zh','pt']
JP=re.compile(r'[぀-ヿ㐀-鿿！-｠　-〿]')
def scan(s):
    res=[]
    for m in re.finditer(r'<script>([\s\S]*?)</script>',s):
        a,b=m.start(1),m.end(1); i=a
        while i<b:
            c=s[i]
            if s.startswith('/*',i): i=s.index('*/',i)+2; continue
            if s.startswith('//',i) and s[i-1] in ' \n\t;{}(),': i=s.find('\n',i); continue
            if c=='/' and re.match(r'[=(,:!&|?{};\n]\s*$', s[max(a,i-3):i]):
                j=i+1
                while s[j]!='/':
                    if s[j]=='\\': j+=1
                    if s[j]=='[':
                        while s[j]!=']': j+=1
                    j+=1
                i=j+1; continue
            if c in "'\"`":
                j=i+1
                while s[j]!=c:
                    if s[j]=='\\': j+=1
                    j+=1
                res.append(s[i+1:j]); i=j+1; continue
            i+=1
    return res
def dec(v):
    out=[];i=0
    while i<len(v):
        if v[i]=='\\': out.append({'n':'\n','t':'\t'}.get(v[i+1],v[i+1])); i+=2
        else: out.append(v[i]); i+=1
    return ''.join(out)
def keys(s):
    ks=[];seen=set()
    def add(k):
        if k not in seen: seen.add(k); ks.append(k)
    body=s[s.index('/*I18N-END*/'):]
    for v in scan(body):
        if JP.search(v): add(dec(v))
    h=re.sub(r'<script>[\s\S]*?</script>|<style>[\s\S]*?</style>',' ',s)
    for m in re.finditer(r'>([^<]+)<',h):
        t=' '.join(m.group(1).split())
        if JP.search(t): add(t)
    for m in re.finditer(r'(?:aria-label|title|placeholder)="([^"]*)"',h):
        t=' '.join(m.group(1).split())
        if JP.search(t): add(t)
    return ks
s=open(HTML,encoding='utf-8').read()
D={l:json.load(open(os.path.join(ROOT,'i18n',l+'.json'),encoding='utf-8')) for l in LANGS}
if '--missing' in sys.argv:
    for k in keys(s):
        miss=[l for l in LANGS if k not in D[l]]
        if miss: print(miss,repr(k))
    sys.exit()
blob='const I18N='+json.dumps(D,ensure_ascii=False,separators=(',',':'))+';'
s=re.sub(r'/\*I18N-BEGIN\*/[\s\S]*?/\*I18N-END\*/',lambda m:'/*I18N-BEGIN*/'+blob+'/*I18N-END*/',s)
open(HTML,'w',encoding='utf-8').write(s); print('embedded',{l:len(D[l]) for l in LANGS})
