import re, json, sys
T=__import__('os').path.dirname(__file__)+'/'; P=sys.argv[1]
s=open(T+'index.src.tmpl').read()
sprite=open(T+'sprite.html').read().replace('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">','<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0" aria-hidden="true">')
LOGO=('<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="11" fill="#1d4373"/>'
 '<path d="M13 11.5h6.2a8.5 8.5 0 0 1 0 17H13z" fill="none" stroke="#fff" stroke-width="3.2" stroke-linejoin="round"/><circle cx="29.2" cy="11.2" r="3.3" fill="#F4B942"/></svg>')
W=json.load(open(P+'/transcript.json'))
sfx=[('impact-bass-1.mp3',0.05,1.2,0.5)]
sfx+=[('whoosh.mp3',t,0.57,0.5) for t in (4.4,10.0,14.25,24.45,27.95)]
sfx+=[('pop.mp3',t,0.7,0.45) for t in (15.95,16.35,16.88,18.5,24.6,27.5,30.4,30.82,31.24,31.66)]
sfx+=[('impact-bass-1.mp3',21.24,1.2,0.65),('click.mp3',12.9,0.6,0.6),('ping.mp3',26.25,1.0,0.5),('notification.mp3',28.0,2.0,0.45),('typing.mp3',32.9,0.9,0.4),('click.mp3',33.9,0.6,0.8),('whoosh-short.mp3',34.55,0.6,0.5),('ping.mp3',35.05,1.0,0.5)]
import subprocess
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',P+'/assets/sfx/'+f]).decode())
tags=[]
for k,(f,t,d,v) in enumerate(sfx):
    d=min(d,dur(f))
    tags.append(f'<audio id="sfx-{k:02d}" src="assets/sfx/{f}" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{30+k}" data-volume="{v*0.6:.2f}" data-audio-group="sfx"></audio>')
s=s.replace('[[SFX]]','\n      '.join(tags)).replace('[[SPRITE]]',sprite).replace('[[LOGO]]',LOGO)
s=s.replace('[[WORDS]]',json.dumps([[x['text'],x['start'],x['end']] for x in W],ensure_ascii=False))
s=re.sub(r'\[\[i:([a-z0-9-]+)\]\]',r'<svg class="icon" aria-hidden="true"><use href="#i-\1"/></svg>',s)
s=re.sub(r'\[\[b:([a-z0-9-]+)\]\]',r'<svg class="icon" aria-hidden="true"><use href="#b-\1"/></svg>',s)
assert not re.findall(r'\[\[[a-zA-Z]', s), re.findall(r'\[\[[^\]]*\]\]',s)
open(P+'/index.html','w').write(s); print('ok', len(s))
