"""Code-native explanatory schematics, deliberately not fake photographs."""
from pathlib import Path
import io
import math
import random
from PIL import Image
import fitz
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from v3.renderer.press import fonts, external_assets


def diagram(name,draw):
    fonts()
    data=io.BytesIO()
    c=canvas.Canvas(data,pagesize=(360,125),invariant=1)
    c.setFillGray(.97);c.rect(0,0,360,125,fill=1,stroke=0)
    c.setFillGray(.12);c.setStrokeGray(.12)
    draw(c)
    c.showPage();c.save()
    with fitz.open(stream=data.getvalue(),filetype='pdf') as d:
        d[0].get_pixmap(dpi=300,colorspace=fitz.csGRAY).save(str(external_assets()/name))


def label(c,x,y,s,size=10,font='Press'):
    c.setFont(font,size);c.drawString(x,y,s)


def create():
    def hollerith(c):
        label(c,15,108,'ZNAK  /  ODCZYT  /  INTERPRETACJA',9,'MetaB')
        c.setLineWidth(.7);c.rect(20,25,105,65)
        for col in range(7):
            for row in range(4):
                if (col+2*row)%4==0:
                    c.circle(30+col*13,37+row*13,2.8,fill=1)
        label(c,25,12,'karta: położenie otworów',8)
        c.line(136,55,173,55);c.line(173,55,166,60);c.line(173,55,166,50)
        c.rect(188,32,56,51);label(c,196,52,'STYK',9,'MetaB')
        c.line(255,55,284,55);c.line(284,55,277,60);c.line(284,55,277,50)
        c.circle(318,58,25);c.line(318,58,328,76);label(c,298,12,'licznik',8)
    diagram('hollerith.png',hollerith)
    def wallpaper(c):
        for i in range(20):
            x=8+i*18
            c.setLineWidth(.4)
            for y in (25,50,75,100):
                c.ellipse(x,y-10,x+13,y+8,fill=0)
        c.setFillGray(.97);c.rect(60,30,240,70,fill=1,stroke=1)
        c.setFillGray(.12)
        label(c,75,78,'CO WIDZĘ?',11,'PressB')
        label(c,75,58,'CO Z TEGO WNIOSKUJĘ?',11,'PressB')
        label(c,75,38,'CO MOGĘ SPRAWDZIĆ?',11,'PressB')
    diagram('wallpaper.png',wallpaper)
    def tardis(c):
        label(c,14,106,'EKSPERYMENT TARDIS  /  FOTON-M3  /  2007',9,'MetaB')
        for i,(title,sub) in enumerate([('PRÓŻNIA','warunek ekspozycji'),('PROMIENIOWANIE','drugi czynnik'),('NAWODNIENIE','ocena po powrocie')]):
            x=12+i*116
            c.rect(x,30,104,54,stroke=1,fill=0)
            label(c,x+7,61,title,9,'MetaB');label(c,x+7,41,sub,8)
        label(c,15,13,'Schemat pytań do badania, nie pomiar poziomu przeżywalności.',8)
    diagram('tardis.png',tardis)
    def go(c):
        unit=10;x=22;y=20
        for k in range(9):
            c.line(x+k*unit,y,x+k*unit,y+80);c.line(x,y+k*unit,x+80,y+k*unit)
        c.setFillGray(.05);c.circle(x+40,y+40,4.1,fill=1)
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            c.setLineWidth(.6);c.circle(x+(4+dx)*unit,y+(4+dy)*unit,3,fill=0)
        label(c,132,91,'KAMIEŃ I CZTERY ODDECHY',12,'PressB')
        label(c,132,68,'Sąsiadujemy poziomo i pionowo.',10)
        label(c,132,48,'Puste przecięcia liczymy raz.',10)
        label(c,132,28,'Miniatura 9×9: model do ćwiczeń.',9)
    diagram('go.png',go)
    def theremin(c):
        label(c,14,107,'DWA NIEZALEŻNE RUCHY',10,'MetaB')
        c.rect(120,26,130,30)
        c.line(237,56,237,96);c.ellipse(70,45,124,62,stroke=1,fill=0)
        label(c,252,87,'wysokość',10)
        label(c,14,72,'głośność',10)
        label(c,132,36,'THEREMIN',12,'PressB')
        label(c,18,12,'Schemat: pionowa antena i boczna pętla. Bez skali technicznej.',8)
    diagram('theremin.png',theremin)
    def doors(c):
        label(c,12,108,'TRZY MOŻLIWE POŁOŻENIA NAGRODY',10,'MetaB')
        for i,(first,stay,change) in enumerate([('A','WYGRANA','PRZEGRANA'),('B','PRZEGRANA','WYGRANA'),('C','PRZEGRANA','WYGRANA')]):
            x=12+i*116;c.rect(x,23,104,65)
            label(c,x+9,70,'Nagroda: '+first,10,'PressB')
            label(c,x+9,51,'zostań: '+stay.lower(),8)
            label(c,x+9,34,'zmień: '+change.lower(),8)
        label(c,14,10,'Pierwszy wybór A. Prowadzący wie, gdzie jest nagroda, i pokazuje pustkę.',8)
    diagram('doors.png',doors)

if __name__=='__main__':
    create()
