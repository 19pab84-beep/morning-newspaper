"""Deterministic old-press A4 composition. Never drops or truncates body copy."""
from __future__ import annotations
from datetime import date
import html
import os
from pathlib import Path
import random

from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

W, H = A4
M, GAP = 25, 12
WIDTH = W - 2*M
CW = (WIDTH - 2*GAP)/3
ROOT = Path(__file__).resolve().parents[1]


def external_assets():
    value = os.environ.get('PORANNA_PRASA_ASSETS')
    if not value:
        raise ValueError('Set PORANNA_PRASA_ASSETS to the extracted Drive asset directory')
    folder = Path(value).resolve()
    if folder.is_relative_to(ROOT.parent):
        raise ValueError('Edition assets must be outside the repository')
    return folder


def fonts():
    folder = external_assets()/'fonts'
    for key, file in {'Press':'LiberationSerif-Regular.ttf', 'PressB':'LiberationSerif-Bold.ttf',
                      'PressI':'LiberationSerif-Italic.ttf', 'Meta':'LiberationSans-Regular.ttf',
                      'MetaB':'LiberationSans-Bold.ttf'}.items():
        pdfmetrics.registerFont(TTFont(key, str(folder/file)))
    pdfmetrics.registerFontFamily('Press', normal='Press', bold='PressB', italic='PressI', boldItalic='PressB')


class Overflow(ValueError):
    pass


class Press:
    def __init__(self, issue, path, *, texture=True):
        fonts()
        self.issue = issue
        self.c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1, invariant=1)
        self.c.setTitle(f"Poranna Prasa · nr {issue['issue_no']:03d} · {issue['date']}")
        self.c.setAuthor('Redakcja Porannej Prasy · pilot literacki AI')
        self.day = date.fromisoformat(issue['date']).strftime('%d.%m.%Y')
        self.nr = f"NR {issue['issue_no']:03d}"
        self.page = 0
        self.story_pages = {}
        self.regions = []
        self.texture = texture
        self.styles = {}
        for name, font, size, leading, align in [
            ('body','Press',8.7,10.35,TA_JUSTIFY),
            ('short','Press',8.4,10.0,TA_JUSTIFY),
            ('deck','PressI',10.3,12,TA_LEFT),
            ('caption','PressI',7.1,8.5,TA_LEFT),
            ('balloon','PressB',8.5,10,TA_LEFT),
            ('source','Meta',6.9,8.3,TA_LEFT)]:
            self.styles[name] = ParagraphStyle(name, fontName=font, fontSize=size,
                leading=leading, alignment=align, textColor='#141414',
                allowWidows=0, allowOrphans=0, splitLongWords=0)

    def text(self, text, x, top, width, style='body', *, bottom=52):
        p = Paragraph(html.escape(text), self.styles[style])
        _, h = p.wrap(width, H)
        if top-h < bottom:
            raise Overflow(f'Page {self.page}, text does not fit: {text[:60]} ({top-h:.1f}<{bottom})')
        p.drawOn(self.c, x, top-h)
        return top-h

    def label(self, text, x, y, size=7.2, font='MetaB'):
        self.c.setFillGray(.075)
        self.c.setFont(font, size)
        self.c.drawString(x, y, text)

    def rule(self, x, y, width, weight=.6):
        self.c.setStrokeGray(.16)
        self.c.setLineWidth(weight)
        self.c.line(x,y,x+width,y)

    def headline(self, text, x, top, width, size=24, max_lines=None):
        st = ParagraphStyle('head', fontName='PressB', fontSize=size,
                            leading=size*.98, spaceAfter=0, textColor='#101010')
        p=Paragraph(html.escape(text), st)
        _, h=p.wrap(width,H)
        while max_lines and h>max_lines*st.leading+.1 and st.fontSize>19:
            st.fontSize-=.5
            st.leading=st.fontSize*.98
            p=Paragraph(html.escape(text),st)
            _,h=p.wrap(width,H)
        p.drawOn(self.c,x,top-h)
        return top-h-6

    def block(self, story, x, top, width, bottom=55):
        self.story_pages[story['story_id']] = self.page
        self.rule(x,top,width)
        self.label(story['rubric'].upper(),x,top-12,6.9)
        y=self.headline(story['headline'],x,top-22,width,14.2)
        if story.get('deck'):
            y=self.text(story['deck'],x,y,width,'caption',bottom=bottom)-7
        for para in story['paragraphs']:
            y=self.text(para,x,y,width,'short',bottom=bottom)-4
        self.regions.append({'story_id':story['story_id'],'page':self.page,
                             'bbox':[x,H-top,x+width,H-y]})
        return y-6

    def flow(self, story, boxes):
        """Flow all paragraphs through explicit columns, with lossless splits."""
        self.story_pages[story['story_id']]=self.page
        queue=[Paragraph(html.escape(p),self.styles['body']) for p in story['paragraphs']]
        for x,top,width,bottom in boxes:
            y=top
            start_y=y
            while queue:
                p=queue[0]
                _,h=p.wrap(width,H)
                if h <= y-bottom:
                    p.drawOn(self.c,x,y-h)
                    y-=h+6
                    queue.pop(0)
                else:
                    fragments=p.split(width,y-bottom)
                    if fragments:
                        first=fragments[0]
                        _,h=first.wrap(width,H)
                        first.drawOn(self.c,x,y-h)
                        y-=h
                        queue[0:1]=fragments[1:]
                    break
            self.regions.append({'story_id':story['story_id'],'page':self.page,
                                 'bbox':[x,H-start_y,x+width,H-y]})
        if queue:
            remaining=' '.join(getattr(p,'text','') or '' for p in queue)
            raise Overflow(f'Page {self.page}: remaining story {story["story_id"]}: {remaining[:90]}')

    def image(self, name, x, top, width, height):
        folder=external_assets()
        p=(folder/name).resolve()
        if not p.is_relative_to(folder):
            raise ValueError('Illustration path escapes the external asset directory')
        if not p.is_file():
            raise ValueError('Brak gotowej ilustracji: '+str(p))
        with Image.open(p) as im:
            scale=max(width/im.width,height/im.height)
            iw,ih=im.width*scale,im.height*scale
            self.c.saveState()
            clip=self.c.beginPath()
            clip.rect(x,top-height,width,height)
            self.c.clipPath(clip,stroke=0,fill=0)
            self.c.drawImage(ImageReader(im.convert('L')),x+(width-iw)/2,top-height+(height-ih)/2,iw,ih,mask='auto')
            self.c.restoreState()
        self.c.setStrokeGray(.2)
        self.c.setLineWidth(.35)
        self.c.rect(x,top-height,width,height,fill=0,stroke=1)

    def begin(self, number):
        self.page=number
        if self.texture:
            # Very light, repeatable monochrome paper grain; no dirty text zones.
            rng=random.Random(170+number)
            im=Image.new('L',(620,877),253)
            pixels=im.load()
            for yy in range(im.height):
                for xx in range(im.width):
                    pixels[xx,yy]=rng.choice((251,252,253,253,254,255))
            self.c.drawImage(ImageReader(im),0,0,W,H)
        if number==1:
            self.label(f'{self.nr}  ·  ROK I  ·  4 STRONY',M,H-25,7.1)
            self.c.setFont('MetaB',7.1)
            self.c.drawRightString(W-M,H-25,f'{self.day}  /  WYDANIE PRÓBNE')
            self.rule(M,H-34,WIDTH,.65)
            self.c.setFont('PressB',48)
            self.c.drawCentredString(W/2,H-82,'PORANNA PRASA')
            self.label('CODZIENNIE. TROCHĘ JAŚNIEJ. TROCHĘ DZIWNIEJ.',M,H-99,6.6)
            self.c.setFont('MetaB',6.6)
            self.c.drawRightString(W-M,H-99,'NIEZALEŻNY DZIENNIK OSOBLIWOŚCI')
            self.rule(M,H-108,WIDTH,1.3)
        else:
            self.label(str(number),M,H-25,9,'PressB')
            if number in (2,3):
                self.label('PORANNA PRASA',M+19,H-25,8,'PressB')
            self.c.setFont('Meta',7)
            self.c.drawRightString(W-M,H-25,f'{self.day}  ·  {self.nr}  ·  WYDANIE PRÓBNE')
            self.rule(M,H-33,WIDTH,.8)
        return H-44

    def end(self):
        self.rule(M,38,WIDTH,.55)
        self.label('PULS NOCY, BLOK 3A I LOKALNE OGŁOSZENIA: FIKCJA LITERACKA. ILUSTRACJE AI.',M,26,5.9,'Meta')
        self.c.setFont('MetaB',6.2)
        self.c.drawRightString(W-M,26,f'{self.nr}  |  {self.page}/4')
        self.c.showPage()

    def cover(self, stories):
        self.begin(1)
        cover=next(s for s in stories if s['role']=='cover')
        self.label('KRONIKA MIEJSKA  /  PULS NOCY',M,H-126,7.4)
        y=self.headline(cover['headline'].upper(),M,H-140,WIDTH,26)
        y=self.text(cover['deck'],M,y,WIDTH,'deck')-10
        self.rule(M,y,WIDTH,.7)
        self.label('ALEKSANDRA W.  /  REPORTAŻ LITERACKI',M,y-12,6.8)
        top=y-23
        art_x=M+CW+GAP
        art_w=2*CW+GAP
        art_h=150
        self.image(self.issue['hero'],art_x,top,art_w,art_h)
        cap_end=self.text(self.issue['hero_caption'],art_x,top-art_h-5,art_w,'caption')
        # Fixed front reserve; teasers are resolved from the completed story map.
        bottom=280
        self.flow(cover,[(M,top,CW,bottom),
                         (art_x,cap_end-12,CW,bottom),
                         (M+2*(CW+GAP),cap_end-12,CW,bottom)])
        self.rule(M,264,WIDTH,1)
        self.label('W TYM NUMERZE  /  TRZY SPRAWY, DO KTÓRYCH WARTO WRÓCIĆ',M,252,7)
        for i,teaser in enumerate(self.issue['teasers']):
            x=M+i*(CW+GAP)
            story=next((s for s in stories if s['story_id']==teaser['story_id']),None)
            if story is None and teaser['story_id']!=self.issue['comic']['story_id']:
                raise ValueError('Nieznany materiał zapowiedzi')
            if story is None:
                story=self.issue['comic']
            image=teaser.get('image',self.issue['comic']['image'])
            self.image(image,x,240,CW,65)
            yy=self.headline(story['headline'],x,166,CW,13.2)
            self.text(teaser['text'],x,yy,CW,'short',bottom=64)
            page=self.story_pages[teaser['story_id']]
            self.c.setFont('MetaB',7)
            self.c.drawRightString(x+CW,52,f'STR. {page}')
            self.c.linkRect('',f'story:{teaser["story_id"]}',(x,46,x+CW,240),relative=0,thickness=0)
        self.end()

    def source_note(self, story, x, top, width):
        ids=story.get('source_ids',[])
        sources=self.issue['sources']
        if not ids:
            return top
        self.rule(x,top,width,.45)
        y=top-10
        self.label('ŹRÓDŁA I ZAKRES',x,y,6.8)
        y-=8
        for sid in ids:
            s=sources[sid]
            text=s['publisher']+' · '+s['title']+'. '+s['print_note']
            y=self.text(text,x,y,width,'source',bottom=46)-6
            # URLs remain clickable; full bibliography is shipped with the source bundle.
            self.c.linkURL(s['url'],(x,y,x+width,y+15),relative=0,thickness=0)
        return y

    def inside(self, number, stories):
        top=self.begin(number)
        feature=next(s for s in stories if s['page']==number and s['role']=='feature')
        shorts=[s for s in stories if s['page']==number and s['role']=='short']
        span=2*CW+GAP
        self.label(feature['rubric'].upper(),M,top-4,7.2)
        y=self.headline(feature['headline'].upper(),M,top-15,span,23,max_lines=2)
        y=self.text(feature['deck'],M,y,span,'deck')-10
        art_h=112 if number==2 else 126
        self.image(feature['image'],M,y,span,art_h)
        y=self.text(feature['caption'],M,y-art_h-5,span,'caption')-12
        self.c.bookmarkPage('story:'+feature['story_id'])
        self.flow(feature,[(M,y,CW,65),(M+CW+GAP,y,CW,65)])
        # Separator prevents modern card-style grouping.
        self.c.setLineWidth(.25)
        self.c.setStrokeGray(.5)
        x=M+2*CW+1.5*GAP
        self.c.line(x,H-53,x,58)
        sx=M+2*(CW+GAP)
        sy=top-2
        for s in shorts:
            self.c.bookmarkPage('story:'+s['story_id'])
            sy=self.block(s,sx,sy,CW)
        sy=self.source_note(feature,sx,sy,CW)
        if sy>120 and feature.get('margin_note'):
            sy=self.text(feature['margin_note'],sx,sy-8,CW,'short')
        self.end()

    def sudoku(self, puzzle, x, top):
        self.label('SUDOKU 9 × 9  /  JEDNO ROZWIĄZANIE',x,top,6.9)
        size=CW
        cell=size/9
        top-=12
        self.c.setFillGray(1)
        self.c.rect(x,top-size,size,size,fill=1,stroke=0)
        self.c.setStrokeGray(.1)
        for k in range(10):
            self.c.setLineWidth(1.0 if k%3==0 else .3)
            self.c.line(x+k*cell,top,x+k*cell,top-size)
            self.c.line(x,top-k*cell,x+size,top-k*cell)
        self.c.setFillGray(.05)
        self.c.setFont('Meta',10.4)
        for r in range(9):
            for col in range(9):
                if puzzle[r][col]:
                    self.c.drawCentredString(x+(col+.5)*cell,top-(r+.5)*cell-3.5,str(puzzle[r][col]))
        self.text('Cyfry 1–9: raz w wierszu, kolumnie i każdym kwadracie 3 × 3. Rozwiązanie w materiałach numeru.',x,top-size-7,CW,'caption')
        return top-size-42

    def back(self, stories):
        top=self.begin(4)
        comic=self.issue['comic']
        self.story_pages[comic['story_id']]=4
        self.c.bookmarkPage('story:'+comic['story_id'])
        # Comic starts immediately after narrow folio, without a section heading.
        height=184
        self.image(comic['image'],M,top,WIDTH,height)
        pw=WIDTH/4
        for i,balloon in enumerate(comic['balloons']):
            x=M+i*pw+6
            # Editable lettering in the image's deliberately empty top quarter.
            self.c.setFillGray(1)
            self.c.setStrokeGray(.1)
            self.c.setLineWidth(.5)
            self.c.roundRect(x,top-43,pw-12,34,7,fill=1,stroke=1)
            self.c.line(x+pw/2-5,top-43,x+pw/2+2,top-51)
            self.text(balloon,x+5,top-14,pw-22,'balloon',bottom=top-45)
        self.label('BLOK 3A  /  '+comic['headline'].upper(),M,top-height-12,7)
        self.regions.append({'story_id':comic['story_id'],'page':4,'bbox':[M,H-top,W-M,H-top+height]})
        y=top-height-28
        shorts=[s for s in stories if s['page']==4 and s['role']=='short']
        # Three stable last-page variants; the comic never moves below the fold.
        column_map=({0:0,1:1,2:2},{0:1,1:0,2:2},{0:2,1:1,2:0})[self.issue['issue_no']%3]
        for col in range(3):
            sx=M+col*(CW+GAP)
            sy=y
            if col==column_map[2]:
                sy=self.sudoku(self.issue['sudoku'],sx,sy)
            for story in (s for s in shorts if column_map[s['column']]==col):
                self.c.bookmarkPage('story:'+story['story_id'])
                sy=self.block(story,sx,sy,CW,50)
        self.end()

    def render(self):
        stories=self.issue['stories']
        # Build all destinations BEFORE cover teasers. Page order remains 1..4.
        self.story_pages={s['story_id']:s['page'] for s in stories}
        self.story_pages[self.issue['comic']['story_id']]=4
        self.cover(stories)
        self.inside(2,stories)
        self.inside(3,stories)
        self.back(stories)
        self.c.save()
        return {'issue_no':self.issue['issue_no'],'date':self.issue['date'],
                'story_pages':self.story_pages,'regions':self.regions,
                'teasers':[dict(story_id=t['story_id'],page=self.story_pages[t['story_id']])
                           for t in self.issue['teasers']],
                'status':'REVIEW_ONLY','dpi':300,'fiction_disclaimer':True,
                'comic_panels':4,'production_published':False}
