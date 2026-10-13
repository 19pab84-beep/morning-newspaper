"""Inspect the actual PDF, not optimistic flags supplied by a manifest."""
from datetime import date
import hashlib
from pathlib import Path
import re
import fitz
from PIL import Image
from v3.renderer.press import external_assets


def compact(s):
    return re.sub(r'\s+','',s).casefold()


def check(pdf,issue,manifest,*,raster_dir=None):
    errors=[];pages=[]
    n=issue['issue_no']
    expected_nr=f'NR {n:03d}'
    expected_date=date.fromisoformat(issue['date']).strftime('%d.%m.%Y')
    with fitz.open(pdf) as doc:
        if len(doc)!=4:
            errors.append('PDF musi mieć 4 strony')
        for i,page in enumerate(doc,1):
            if abs(page.rect.width-595.2756)>.1 or abs(page.rect.height-841.8898)>.1:
                errors.append(f'Strona {i}: nie jest A4')
            text=page.get_text()
            if expected_date not in text or not re.search(r'NR\s+'+f'{n:03d}'+r'\b',text):
                errors.append(f'Strona {i}: błędny numer/data')
            all_numbers=re.findall(r'NR\s+(\d+)',text)
            if any(int(v)!=n for v in all_numbers):
                errors.append(f'Strona {i}: sprzeczne numery')
            spans=[s for b in page.get_text('dict')['blocks'] if b['type']==0
                   for line in b['lines'] for s in line['spans']]
            mastheads=[s for s in spans if 'PORANNA PRASA' in s['text'] and s['size']>=20]
            if len(mastheads)!=(1 if i==1 else 0):
                errors.append(f'Strona {i}: niewłaściwa duża winieta')
            if i==4 and ('OSTATNIA STRONA' in text or 'PORANNA PRASA' in text):
                errors.append('Strona 4: niedozwolony nagłówek')
            if i in (2,3):
                folios=[s for s in spans if 'PORANNA PRASA' in s['text']]
                if len(folios)!=1 or folios[0]['size']>9 or folios[0]['bbox'][3]>35:
                    errors.append(f'Strona {i}: pagina nie jest mała i wąska')
            outside=[s for s in spans if s['bbox'][0]<23 or s['bbox'][2]>page.rect.width-23
                     or s['bbox'][1]<15 or s['bbox'][3]>page.rect.height-17]
            if outside:
                errors.append(f'Strona {i}: {len(outside)} fragmenty poza marginesem')
            if '\ufffd' in text or '\x00' in text:
                errors.append(f'Strona {i}: uszkodzony polski znak')
            if f'{i}/4' not in text:
                errors.append(f'Strona {i}: błędny numer w stopce')
            if i>1 and not any(s['text'].strip()==str(i) and s['bbox'][0]<38
                              and s['bbox'][3]<35 for s in spans):
                errors.append(f'Strona {i}: błędny numer paginy')
            # Text lines may touch in justified prose; near-total bbox intersection is never valid.
            lines=[fitz.Rect(line['bbox']) for b in page.get_text('dict')['blocks'] if b['type']==0 for line in b['lines']]
            overlaps=0
            for a,line in enumerate(lines):
                for other in lines[a+1:]:
                    intersect=line & other
                    if intersect.get_area()>0.55*min(line.get_area(),other.get_area()):
                        overlaps+=1
            if overlaps:
                errors.append(f'Strona {i}: nakładające się wiersze ({overlaps})')
            content=compact(text)
            for story in issue['stories']:
                if story['page']==i:
                    for para in story['paragraphs']:
                        if compact(para) not in content:
                            errors.append(f'Strona {i}: utracony akapit {story["story_id"]}')
            images=page.get_image_info(hashes=True)
            if i==4:
                folder=external_assets()
                target=(folder/issue['comic']['image']).resolve()
                if not target.is_relative_to(folder):
                    raise ValueError('Comic path escapes the external asset directory')
                with Image.open(target) as im:
                    digest=hashlib.md5(im.convert('L').tobytes()).digest()
                comic=[im for im in images if im['digest']==digest]
                if not comic or abs(comic[0]['bbox'][1]-44)>2:
                    errors.append('Komiks nie rozpoczyna strony 4 bezpośrednio pod paginą')
                for balloon in issue['comic']['balloons']:
                    if compact(balloon) not in content:
                        errors.append('Brak lub ucięty dymek komiksu')
                if 'SUDOKU 9' not in text:
                    errors.append('Brak sudoku 9×9')
            if i==1:
                actual=[int(p) for p in re.findall(r'STR\.\s*(\d+)',text)]
                expected=[manifest['story_pages'][t['story_id']] for t in issue['teasers']]
                if actual!=expected:
                    errors.append('Odsyłacze okładki nie zgadzają się z rzeczywistymi stronami')
            if raster_dir:
                Path(raster_dir).mkdir(parents=True,exist_ok=True)
                pix=page.get_pixmap(dpi=300,colorspace=fitz.csGRAY,alpha=False)
                pix.save(str(Path(raster_dir)/f'page-{i:02d}.png'))
                if pix.height<3508 or pix.width<2480:
                    errors.append('Raster poniżej A4/300 dpi')
            pages.append({'page':i,'size_pt':[round(page.rect.width,3),round(page.rect.height,3)],
                          'words':len(page.get_text('words')),'images':len(images),
                          'large_mastheads':len(mastheads),'overlap_lines':overlaps,
                          'outside_spans':len(outside)})
        # Verify linked destinations as well as printed teaser labels.
        if len(doc)==4:
            links=[link for link in doc[0].get_links() if link['kind'] in (fitz.LINK_GOTO,fitz.LINK_NAMED)]
            expected=[manifest['story_pages'][t['story_id']]-1 for t in issue['teasers']]
            actual=[link['page'] if link['kind']==fitz.LINK_GOTO else int(link['page'])-1 for link in links]
            if actual!=expected:
                errors.append('Klikalne odsyłacze mają błędne cele')
    return {'status':'PASS' if not errors else 'FAIL','errors':errors,'pages':pages,
            'automated_gates':['4×A4','issue/date','single masthead','small folios','real teaser targets',
                               'complete paragraphs','safe margins','line overlaps','comic asset and lettering',
                               '300 dpi monochrome renders'],
            'requires_human':['visual style acceptance','physical Brother print','source interpretation'],
            'live_api_tested':issue.get('provenance',{}).get('api_calls',0)>0,
            'publication_allowed':False}
