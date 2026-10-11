#!/usr/bin/env python3
"""Gazetowy, gęsty i przewidywalny skład A4. Tylko DEMO, nic nie publikuje.
Layout jest świadomie jawny: teksty nie przechodzą samoczynnie na ostatnią stronę.
"""
from pathlib import Path
import sys, html, json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.colors import HexColor
from sample_content import FRONT,P2,P3,BACK

OUT=Path(sys.argv[1]) if len(sys.argv)>1 else Path('/mnt/data/morning_newspaper_v3/preview/poranna_prasa_v3.pdf')
OUT.parent.mkdir(parents=True,exist_ok=True)
W,H=A4; M=29; GAP=12; CW=(W-2*M-2*GAP)/3
INK=HexColor('#151515');GRAY=HexColor('#505050'); MID=HexColor('#888888');WHITE=HexColor('#FFFFFF')
ROOT='/usr/share/fonts/truetype/liberation2/'
for key,file in {
'Serif':'LiberationSerif-Regular.ttf','SerifB':'LiberationSerif-Bold.ttf',
'SerifI':'LiberationSerif-Italic.ttf','Sans':'LiberationSans-Regular.ttf',
'SansB':'LiberationSans-Bold.ttf','SansI':'LiberationSans-Italic.ttf',
}.items():
    p=Path(ROOT+file)
    if not p.is_file():p=Path('/usr/share/fonts/truetype/liberation/'+file)
    pdfmetrics.registerFont(TTFont(key,str(p)))
ST={}
for key,font,size,lead,align in [
('body','Serif',8.25,10.45,TA_JUSTIFY),
('body2','Serif',8.0,10.25,TA_JUSTIFY),
('intro','SerifI',9.25,11.4,TA_LEFT),
('deck','SerifI',9.25,12.0,TA_LEFT),
('small','Serif',8.0,10.1,TA_LEFT),
('smallbold','SerifB',8.0,10.1,TA_LEFT),
('source','Sans',6.35,8.1,TA_LEFT),
('ad','Serif',7.85,10.0,TA_LEFT),
]:
 ST[key]=ParagraphStyle(key,fontName=font,fontSize=size,leading=lead,alignment=align,textColor=INK,
                         allowWidows=0,allowOrphans=0,wordWrap=None)

def plain(c,x,y,text,size=7.0,font='Sans',color=INK):
 c.setFillColor(color);c.setFont(font,size);c.drawString(x,y,text)

def right(c,x,y,text,size=7.0,font='Sans',color=INK):
 c.setFillColor(color);c.setFont(font,size);c.drawRightString(x,y,text)

def line(c,x1,y,x2,width=.5,color=INK):
 c.setStrokeColor(color);c.setLineWidth(width);c.line(x1,y,x2,y)

def fit(c,x,y,w,text,style='body',gap=0,min_y=50):
 p=Paragraph(html.escape(text).replace('\n','<br/>'),ST[style]);_,h=p.wrap(w,9999)
 if y-h < min_y:
    raise ValueError(f'overflow: "{text[:35]}" at {y-h:.1f}, minimum {min_y}, page {c.getPageNumber()}')
 p.drawOn(c,x,y-h)
 return y-h-gap

def title(c,text,x,y,w,size=15.2,lead=None,min_y=45):
 lead=lead or size*1.04
 words=text.split();rows=[];row=''
 for word in words:
  cand=(row+' '+word).strip()
  if pdfmetrics.stringWidth(cand,'SerifB',size)<=w:row=cand
  else:
   if row:rows.append(row)
   row=word
 if row:rows.append(row)
 if y-(len(rows)-1)*lead < min_y:raise ValueError('headline overflow '+text[:30])
 c.setFillColor(INK);c.setFont('SerifB',size)
 for i,s in enumerate(rows):c.drawString(x,y-i*lead,s)
 return y-(len(rows))*lead-2

def rubric(c,text,x,y,w):
 line(c,x,y+5,x+w,0.7)
 plain(c,x,y-6,text.upper(),7.2,'SansB')
 return y-18

def article(c,entry,x,y,w,bsize=8.25):
 y=rubric(c,entry['rubric'],x,y,w)
 y=title(c,entry['headline'],x,y,w,size=13.0 if len(entry['headline'])>45 else 14.1,lead=14.1)
 if entry.get('deck'):
  y=fit(c,x,y-1,w,entry['deck'],'intro',gap=8)
 else:y-=5
 for p in entry['paras']:
  y=fit(c,x,y,w,p,'body' if bsize>=8.2 else 'body2',gap=6)
 if entry.get('source'):
  y=fit(c,x,y,w,entry['source'],'source',gap=8)
 return y-8

def topbar(c,section,num):
 plain(c,M,H-28,'PORANNA PRASA  /  CODZIENNIK OSOBLIWOŚCI',7.0,'SansB')
 right(c,W-M,H-28,'11.10.2026  •  NR 001  •  MAKIETA',7.0,'Sans')
 line(c,M,H-36,W-M,0.9)
 plain(c,M,H-62,section,18.8,'SerifB')
 right(c,W-M,H-59,f'{num} / 4',7.3,'SansB')
 line(c,M,H-69,W-M,1.2)

def footer(c,p):
 line(c,M,45,W-M,0.6)
 plain(c,M,34,'PULS NOCY / PORANNA PRASA  •  MAKIETA • FIKCJA LITERACKA W TEKSTACH OZNACZONYCH',6.3,'Sans',GRAY)
 right(c,W-M,34,f'NR 001     {p}',6.7,'SansB')

def divider_columns(c,top=730,bottom=62):
 for i in (1,2):
  x=M + i*CW + (i-.5)*GAP
  c.setStrokeColor(HexColor('#c5c5c5'));c.setLineWidth(.27);c.line(x,top,x,bottom)

endpoints={}
c=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
c.setTitle('PORANNA PRASA — V3 / wydanie redakcyjne próbne')
c.setAuthor('Puls Nocy, fikcyjna redakcja')

# —————————— PAGE ONE ——————————
plain(c,M,H-30,'NIEDZIELA   11 PAŹDZIERNIKA 2026  •  CENA: JEDEN PORANEK',7.0,'SansB')
right(c,W-M,H-30,'NUMER 001  /  ROK I   /   4 STRONY',7.1,'SansB')
line(c,M,H-38,W-M,0.7)
c.setFillColor(INK);c.setFont('SerifB',38);c.drawCentredString(W/2,H-82,'PORANNA PRASA')
c.setFont('SansB',7.9);c.drawCentredString(W/2,H-98,'ODKRYCIA  •  KULTURA  •  SPRAWY NIEZUPEŁNIE ZWYKŁE')
line(c,M,H-107,W-M,2.0)
plain(c,M,H-126,'TEMAT DNIA / KRONIKA MIEJSKA',7.5,'SansB')
right(c,W-M,H-126,'PULS NOCY   |   STR. 1',7.5,'SansB')
y=title(c,FRONT['headline'],M,H-149,W-2*M,size=23,lead=23.5)
y=fit(c,M,y-3,W-2*M,FRONT['deck'],'deck',gap=7)
line(c,M,y+1,W-M,.9)
plain(c,M,y-12,FRONT['byline'],6.9,'SansB');y-=25
ends=[]
for i,ps in enumerate(FRONT['columns']):
 x=M+i*(CW+GAP);p_y=y
 for para in ps:p_y=fit(c,x,p_y,CW,para,'body',gap=7,min_y=82)
 ends.append(p_y)
endpoints[1]=ends
# At column bottoms, invite rereading; still editorial, not filler.
minend=min(ends)
if minend>100:
 line(c,M,minend-10,W-M,.7)
 plain(c,M,minend-24,'W NASTĘPNYM NUMERZE',7.5,'SansB')
 fit(c,M,minend-30,W-2*M,'Zapis ze spotkania zarządców i odpowiedź na list, który nadano przed godziną jego napisania. Czytelników prosimy o zachowanie kopert.', 'small',min_y=53)
divider_columns(c,top=y+8,bottom=63)
footer(c,1);c.showPage()

# —————————— PAGE TWO ——————————
topbar(c,'GRY, MECHANIKI, SAMOTNE ODKRYCIA',2)
plain(c,M,H-88,'KONKRETY, NIE ENTUZJASTYCZNE OGÓLNIKI  /  STUDIA PRZYPADKU',7.0,'SansB',GRAY)
start=H-109; ends=[]
for i,arts in enumerate(P2):
 x=M+i*(CW+GAP);y=start
 for a in arts:y=article(c,a,x,y,CW)
 ends.append(y)
endpoints[2]=ends
divider_columns(c,top=start+8,bottom=63)
footer(c,2);c.showPage()

# —————————— PAGE THREE ——————————
topbar(c,'ARCHIWUM, HORROR, NINTENDO',3)
plain(c,M,H-88,'W TYM WYDANIU: DOKUMENT FIKCYJNY / ANALIZA / WARSZTAT',7.0,'SansB',GRAY)
start=H-109; ends=[]
for i,arts in enumerate(P3):
 x=M+i*(CW+GAP);y=start
 for a in arts:y=article(c,a,x,y,CW)
 ends.append(y)
endpoints[3]=ends
divider_columns(c,top=start+8,bottom=63)
footer(c,3);c.showPage()

# —————————— LAST PAGE ——————————
topbar(c,'OGŁOSZENIA, LISTY, ZAGADKI',4)
plain(c,M,H-86,'OSTATNIA STRONA',7.4,'SansB',GRAY)
line(c,M,H-94,W-M,.5)
coltop=H-113
# Left column — classifieds
x=M;y=rubric(c,'OGŁOSZENIA DROBNE',x,coltop,CW)
for tag,body in BACK['ads']:
 plain(c,x,y,tag,6.8,'SansB');y-=5
 y=fit(c,x,y-2,CW,body,'ad',gap=6,min_y=254)
 y-=5
end0=y
# Middle — letters and correction
x=M+CW+GAP;y=rubric(c,'LISTY DO REDAKCJI',x,coltop,CW)
for tag,body in BACK['letters']:
 y=title(c,tag,x,y,CW,10.9,lead=11.3)
 y=fit(c,x,y-1,CW,body,'ad',gap=10,min_y=170)
for tag,body in BACK['notes'][:1]:
 y=rubric(c,tag,x,y,CW)
 y=fit(c,x,y,CW,body,'ad',gap=8,min_y=160)
end1=y
# Right — sudoku, warning and letters
x=M+2*(CW+GAP);y=rubric(c,'ŁAMIGŁÓWKA / SUDOKU 4 × 4',x,coltop,CW)
y=fit(c,x,y,CW,'Wypełnij pola cyframi 1–4. Każda cyfra raz w wierszu, kolumnie i kwadracie 2 × 2. Rozwiązanie jutro.','small',gap=9,min_y=450)
# valid unique 4x4 puzzle
puzzle=[[1,2,0,4],[0,4,1,0],[0,1,4,0],[4,0,0,1]]
cell=30;left=x+(CW-cell*4)/2;top=y
c.setFillColor(WHITE);c.rect(left,top-4*cell,4*cell,4*cell,stroke=0,fill=1)
for i in range(5):
 c.setLineWidth(1.25 if i%2==0 else .35);c.setStrokeColor(INK)
 c.line(left+i*cell,top,left+i*cell,top-cell*4)
 c.line(left,top-i*cell,left+cell*4,top-i*cell)
for rr in range(4):
 for cc in range(4):
  n=puzzle[rr][cc]
  if n:
   c.setFont('SerifB',16);c.setFillColor(INK);c.drawCentredString(left+(cc+.5)*cell,top-(rr+.69)*cell,str(n))
y=top-4*cell-15
for tag,body in BACK['notes'][1:]:
 y=rubric(c,tag,x,y,CW)
 y=fit(c,x,y,CW,body,'ad',gap=8,min_y=158)
end2=y
endpoints[4]=[end0,end1,end2]
divider_columns(c,top=coltop+7,bottom=252)
# The last page carries a three-panel comic below classifieds, not leftover stories.
line(c,M,244,W-M,.7)
plain(c,M,233,'KOMIKS / TRZY KADRY — „URZĄD DORĘCZEŃ”',7.1,'SansB')
for idx in range(3):
    xx=M+idx*(CW+GAP);by=152;hh=73
    c.setStrokeColor(INK);c.setLineWidth(.75)
    c.rect(xx,by,CW,hh,stroke=1,fill=0)
    # Tiny vector tableau: door, mailbox and a clock, no image assets.
    c.setStrokeColor(INK);c.setLineWidth(.95)
    if idx==0:
        c.rect(xx+13,by+13,32,45,stroke=1,fill=0)
        c.circle(xx+39,by+34,1.4,stroke=0,fill=1)
        c.rect(xx+54,by+17,27,19,stroke=1,fill=0)
        c.line(xx+55,by+27,xx+80,by+27)
        plain(c,xx+90,by+45,'DO DRZWI',6.7,'SansB')
        plain(c,xx+90,by+36,'TRAFIŁ',6.7,'SansB')
        plain(c,xx+90,by+27,'LIST.',6.7,'SansB')
    elif idx==1:
        c.rect(xx+11,by+13,38,48,stroke=1,fill=0)
        c.line(xx+30,by+13,xx+30,by+58)
        plain(c,xx+59,by+49,'„NIE MA',7,'SansB')
        plain(c,xx+59,by+38,'MNIE',7,'SansB')
        plain(c,xx+59,by+27,'W DOMU”.',7,'SansB')
    else:
        c.rect(xx+12,by+15,34,42,stroke=1,fill=0)
        c.rect(xx+51,by+24,30,19,stroke=1,fill=0)
        plain(c,xx+89,by+48,'„KTO TO',7,'SansB')
        plain(c,xx+89,by+37,'PODPISAŁ?”',7,'SansB')
        plain(c,xx+89,by+25,'„DOM”.',7,'SansB')
# Back-page lower banner. All content above banner.
line(c,M,140,W-M,1.25)
plain(c,M,128,'NIEZALEŻNE BIURO KOREKT',7.1,'SansB')
plain(c,M,111,'Zajmujemy się wersjami wydarzeń, które zniknęły z protokołów.',10.7,'SerifB')
line(c,M,101,W-M,.5)
plain(c,M,88,'BIURO PRZYJMUJE SPROSTOWANIA   •   WT.–PT.   •   W GODZINACH POTWIERDZONYCH PRZEZ ZEGAR',6.95,'SansB')
plain(c,M,62,'Kolofon: To fikcyjny dziennik literacki. Fakty o grach opisujemy jako analizę, nie jako wiadomości.',6.65,'Sans',GRAY)
footer(c,4);c.showPage()
c.save()
print(json.dumps({'pdf':str(OUT),'column_endpoints':endpoints,'pages':4},indent=2))
