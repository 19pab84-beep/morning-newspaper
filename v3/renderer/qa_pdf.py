"""Structural PDF sanity checks for the V3 newspaper demo."""
from pathlib import Path
import sys
import fitz

def check(path: Path):
    doc=fitz.open(path)
    problems=[]
    if len(doc)!=4: problems.append(f"Expected four pages, got {len(doc)}")
    for i,page in enumerate(doc,1):
        words=page.get_text("words")
        if len(words)<480:problems.append(f"Page {i}: too little text")
        if any(x0<20 or x1>page.rect.width-20 or y0<17 or y1>page.rect.height-15
               for x0,y0,x1,y1,*_ in words):
            problems.append(f"Page {i}: text outside safe margins")
    if "OGŁOSZENIA" not in doc[-1].get_text() or "SUDOKU" not in doc[-1].get_text():
        problems.append("Missing true back page")
    if "Gremlin Nob" not in doc[1].get_text() or "Lagavulin" not in doc[1].get_text():
        problems.append("Game essay lacks concrete mechanics")
    return problems

if __name__=="__main__":
    problems=check(Path(sys.argv[1]))
    print("OK" if not problems else "\n".join(problems))
    raise SystemExit(bool(problems))
