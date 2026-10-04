import json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('.')
STORIES = ROOT/'stories.json'
OUT = ROOT/'generated'
HISTORY = OUT/'history.json'
LATEST = OUT/'latest.json'
REPO_RAW = 'https://raw.githubusercontent.com/abhishekmehrotra1988-lgtm/vishu-chronicles-media/main'

W,H = 1080,1350
MARGIN=32
TITLE_H=88
FOOT_H=140
GAP=18
ROWS=3
PANEL_W=(W-2*MARGIN-GAP)//2
PANEL_H=(H-MARGIN*2-TITLE_H-FOOT_H-GAP*(ROWS-1))//ROWS
PALETTES=[('#fff7e8','#ffe6b8'),('#f8f1ff','#eadcff'),('#eef9ff','#d9f0ff'),('#fff0f4','#ffdbe6'),('#f2fff2','#dcf6dc'),('#fff9ef','#f5e5bd')]

def font(size,bold=False):
    paths=(['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf'] if bold else ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf'])
    for p in paths:
        try: return ImageFont.truetype(p,size)
        except OSError: pass
    return ImageFont.load_default()

F_TITLE=font(38,True); F_PANEL=font(24,True); F_BUBBLE=font(22,True); F_RULE=font(25,True); F_HOOK=font(22)

def wrap(draw,text,f,maxw):
    words=text.split(); lines=[]; cur=''
    for w in words:
        trial=w if not cur else cur+' '+w
        if draw.textlength(trial,font=f)<=maxw: cur=trial
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def bubble(draw,box,text):
    x0,y0,x1,y1=box
    draw.rounded_rectangle(box,24,fill='white',outline='#333333',width=3)
    lines=wrap(draw,text,F_BUBBLE,(x1-x0)-28)
    yy=y0+14
    for ln in lines[:4]:
        draw.text((x0+14,yy),ln,font=F_BUBBLE,fill='#222222'); yy+=30

def draw_pihu(draw,x,y,scale=1.0,flip=False):
    s=scale; skin='#f2c9a5'; outline='#333333'; hair='#1f1b1a'; purple='#7751b5'
    draw.ellipse((x-28*s,y-98*s,x+28*s,y-42*s),fill=skin,outline=outline,width=max(2,int(2*s)))
    draw.pieslice((x-31*s,y-105*s,x+31*s,y-46*s),180,360,fill=hair)
    px=x-30*s if not flip else x+30*s
    draw.ellipse((px-12*s,y-86*s,px+12*s,y-60*s),fill=hair,outline=outline)
    gy=y-75*s
    draw.ellipse((x-20*s,gy-9*s,x-3*s,gy+8*s),outline='#222',width=max(2,int(2*s)))
    draw.ellipse((x+3*s,gy-9*s,x+20*s,gy+8*s),outline='#222',width=max(2,int(2*s)))
    draw.line((x-3*s,gy,x+3*s,gy),fill='#222',width=max(2,int(2*s)))
    draw.rounded_rectangle((x-28*s,y-42*s,x+28*s,y+35*s),12,fill=purple,outline=outline,width=max(2,int(2*s)))
    draw.line((x-18*s,y+35*s,x-20*s,y+73*s),fill=outline,width=max(3,int(4*s)))
    draw.line((x+18*s,y+35*s,x+20*s,y+73*s),fill=outline,width=max(3,int(4*s)))
    draw.line((x-28*s,y-20*s,x-46*s,y+10*s),fill=outline,width=max(3,int(4*s)))
    draw.line((x+28*s,y-20*s,x+46*s,y+10*s),fill=outline,width=max(3,int(4*s)))

def draw_vishu(draw,x,y,scale=1.0,flip=False):
    s=scale; skin='#f2c9a5'; outline='#333333'; hair='#1f1b1a'; yellow='#f2c94c'
    draw.ellipse((x-31*s,y-96*s,x+31*s,y-34*s),fill=skin,outline=outline,width=max(2,int(2*s)))
    draw.pieslice((x-29*s,y-101*s,x+29*s,y-48*s),185,355,fill=hair)
    draw.ellipse((x-12*s,y-69*s,x-6*s,y-63*s),fill='#222')
    draw.ellipse((x+6*s,y-69*s,x+12*s,y-63*s),fill='#222')
    draw.arc((x-9*s,y-59*s,x+9*s,y-49*s),0,180,fill='#8d4f43',width=max(2,int(2*s)))
    draw.rounded_rectangle((x-24*s,y-34*s,x+24*s,y+27*s),14,fill=yellow,outline=outline,width=max(2,int(2*s)))
    draw.line((x-12*s,y+27*s,x-14*s,y+49*s),fill=outline,width=max(3,int(4*s)))
    draw.line((x+12*s,y+27*s,x+14*s,y+49*s),fill=outline,width=max(3,int(4*s)))
    draw.line((x-24*s,y-16*s,x-39*s,y+2*s),fill=outline,width=max(3,int(4*s)))
    draw.line((x+24*s,y-16*s,x+39*s,y+2*s),fill=outline,width=max(3,int(4*s)))

def prop(draw,kind,cx,cy):
    import math
    if kind=='stickers':
        for dx,dy in [(-35,-12),(0,18),(34,-20)]:
            pts=[]
            for i in range(10):
                a=-math.pi/2+i*math.pi/5; r=18 if i%2==0 else 8
                pts.append((cx+dx+r*math.cos(a),cy+dy+r*math.sin(a)))
            draw.polygon(pts,fill='#ffd54f',outline='#8a6d00')
    elif kind=='cups':
        for i,(dx,dy) in enumerate([(-40,20),(0,0),(40,20)]):
            draw.rectangle((cx+dx-18,cy+dy-24,cx+dx+18,cy+dy+24),fill=['#8ecae6','#ffb4a2','#bde0a8'][i],outline='#444',width=2)
    elif kind=='tissues':
        draw.rounded_rectangle((cx-55,cy-28,cx+55,cy+28),8,fill='#bde0fe',outline='#555',width=2)
        draw.polygon([(cx-5,cy-20),(cx+10,cy-65),(cx+26,cy-20)],fill='white',outline='#aaa')
    elif kind=='blocks':
        for dx,dy,c in [(-42,22,'#ef476f'),(0,0,'#ffd166'),(42,22,'#06d6a0')]:
            draw.rectangle((cx+dx-20,cy+dy-20,cx+dx+20,cy+dy+20),fill=c,outline='#444',width=2)
    elif kind=='magnets':
        for i,ch in enumerate('ABC'):
            x=cx-45+i*45
            draw.rounded_rectangle((x-16,cy-18,x+16,cy+18),5,fill=['#ffadad','#caffbf','#a0c4ff'][i],outline='#555')
            draw.text((x-9,cy-15),ch,font=font(22,True),fill='#222')
    elif kind=='spoons':
        for dx in (-24,24):
            draw.ellipse((cx+dx-10,cy-42,cx+dx+10,cy-20),fill='#ddd',outline='#666')
            draw.rectangle((cx+dx-3,cy-20,cx+dx+3,cy+38),fill='#bbb',outline='#666')
    elif kind=='laundry':
        draw.rectangle((cx-55,cy-32,cx+55,cy+34),fill='#d6ccc2',outline='#555',width=3)
        for dx,c in [(-28,'#9b5de5'),(0,'#fee440'),(28,'#00bbf9')]: draw.ellipse((cx+dx-18,cy-24,cx+dx+18,cy+12),fill=c)
    elif kind=='books':
        for i,c in enumerate(['#a8dadc','#f4a261','#cdb4db']): draw.rectangle((cx-60,cy+20-i*18,cx+60,cy+36-i*18),fill=c,outline='#555')
    else:
        draw.ellipse((cx-30,cy-30,cx+30,cy+30),fill='#ffcad4',outline='#555')

def render(story,outpath):
    img=Image.new('RGB',(W,H),'#fffaf3'); d=ImageDraw.Draw(img)
    title=f"VISHU CHRONICLES — {story['title']}"
    tw=d.textlength(title,font=F_TITLE)
    d.text(((W-tw)/2,MARGIN),title,font=F_TITLE,fill='#3b2f2f')
    y0=MARGIN+TITLE_H
    for i,p in enumerate(story['panels'][:6]):
        row=i//2; col=i%2
        x=MARGIN+col*(PANEL_W+GAP); y=y0+row*(PANEL_H+GAP)
        bg,_=PALETTES[i%len(PALETTES)]
        d.rounded_rectangle((x,y,x+PANEL_W,y+PANEL_H),18,fill=bg,outline='#5a4a42',width=3)
        d.text((x+14,y+10),f"{i+1}",font=F_PANEL,fill='#5a4a42')
        d.line((x+10,y+PANEL_H-78,x+PANEL_W-10,y+PANEL_H-78),fill='#ccb8aa',width=3)
        prop(d,story.get('prop','toy'),x+PANEL_W//2,y+PANEL_H-118)
        if i%2==0: px=x+100; vx=x+PANEL_W-95
        else: px=x+PANEL_W-100; vx=x+95
        draw_pihu(d,px,y+PANEL_H-92,0.88,flip=i%2==1)
        draw_vishu(d,vx,y+PANEL_H-82,0.78,flip=i%2==0)
        speaker=p.get('speaker','Vishu')
        if speaker.lower().startswith(('pihu','didi')):
            box=(x+18,y+42,x+PANEL_W//2+35,y+153) if px>x+PANEL_W/2 else (x+PANEL_W//2-10,y+42,x+PANEL_W-18,y+153)
        else:
            box=(x+18,y+42,x+PANEL_W//2+35,y+153) if vx>x+PANEL_W/2 else (x+PANEL_W//2-10,y+42,x+PANEL_W-18,y+153)
        bubble(d,box,f"{speaker}: {p['text']}")
    fy=H-MARGIN-FOOT_H+8
    d.rounded_rectangle((MARGIN,fy,W-MARGIN,H-MARGIN),18,fill='#fff0c7',outline='#5a4a42',width=3)
    for j,(txt,fnt) in enumerate([('Sibling Rule: '+story['rule'],F_RULE),('Next: '+story['hook'],F_HOOK)]):
        yy=fy+16+j*58
        for ln in wrap(d,txt,fnt,W-2*MARGIN-30)[:2]:
            d.text((MARGIN+15,yy),ln,font=fnt,fill='#3b2f2f'); yy+=30
    img.save(outpath,'JPEG',quality=90,optimize=True)

def slugify(s): return re.sub(r'[^a-z0-9]+','-',s.lower()).strip('-')

def main():
    OUT.mkdir(exist_ok=True)
    stories=json.loads(STORIES.read_text(encoding='utf-8'))
    history=json.loads(HISTORY.read_text(encoding='utf-8')) if HISTORY.exists() else []
    today=datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
    existing=next((h for h in history if h.get('date')==today),None)
    if existing:
        story=next(s for s in stories if s['theme']==existing['theme'])
    else:
        used=[h.get('theme') for h in history]
        story=next((s for s in stories if s['theme'] not in used),stories[len(history)%len(stories)])
        history.append({'date':today,'theme':story['theme'],'title':story['title']})
        HISTORY.write_text(json.dumps(history,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    filename=f"{today}-{slugify(story['theme'])}.jpg"
    render(story,OUT/filename)
    caption=(f"{story['caption']}\n\nSibling Rule: {story['rule']}\n{story['hook']}\n\n"
             "#VishuChronicles #DidiAndVishu #SiblingMischief #FamilyComics #SiblingLove #ChildhoodAdventures")
    manifest={'id':f"auto-{today}-{slugify(story['theme'])}",'date':today,'theme':story['theme'],'title':story['title'],'caption':caption,
              'media_url':f"{REPO_RAW}/generated/{filename}",'approved':True,'published':False,'status':'ready','auto_generated':True,'renderer':'zero-cost-template-v1'}
    LATEST.write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))

if __name__=='__main__': main()
