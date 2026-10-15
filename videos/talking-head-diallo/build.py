import re, json, sys
T=__import__('os').path.dirname(__file__)+'/'; P=sys.argv[1]
s=open(T+'index.src.html').read()
sprite=open(T+'sprite.html').read().replace('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">','<svg xmlns="http://www.w3.org/2000/svg" style="position:absolute;width:0;height:0" aria-hidden="true">')
LOGO=('<svg viewBox="0 0 40 40" aria-hidden="true"><rect width="40" height="40" rx="11" fill="#1d4373"/>'
 '<path d="M13 11.5h6.2a8.5 8.5 0 0 1 0 17H13z" fill="none" stroke="#fff" stroke-width="3.2" stroke-linejoin="round"/><circle cx="29.2" cy="11.2" r="3.3" fill="#F4B942"/></svg>')
W=json.load(open(P+'/transcript.json'))
sfx=[('impact-bass-1.mp3',0.05,1.2,0.5)]
sfx+=[('whoosh.mp3',t,0.57,0.55) for t in (6.4,9.6,14.7,17.8,24.2,27.7,33.3,40.1)]
sfx+=[('pop.mp3',t,0.7,0.45) for t in (12.6,19.5,22.3,30.4,31.1)]
sfx+=[('impact-bass-1.mp3',25.6,1.2,0.6),('click.mp3',35.3,0.6,0.8),('notification.mp3',36.6,2.0,0.5),('ping.mp3',40.85,1.0,0.5)]
import subprocess
def dur(f): return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',P+'/assets/sfx/'+f]).decode())
tags=[]
for k,(f,t,d,v) in enumerate(sfx):
    d=min(d,dur(f))
    tags.append(f'<audio id="sfx-{k:02d}" src="assets/sfx/{f}" data-start="{t:.2f}" data-duration="{d:.2f}" data-track-index="{30+k}" data-volume="{v}" data-audio-group="sfx"></audio>')
s=s.replace('[[SFX]]','\n      '.join(tags)).replace('[[SPRITE]]',sprite).replace('[[LOGO]]',LOGO)
s=s.replace('[[WORDS]]',json.dumps([[x['text'],x['start'],x['end']] for x in W],ensure_ascii=False))
s=re.sub(r'\[\[i:([a-z0-9-]+)\]\]',r'<svg class="icon" aria-hidden="true"><use href="#i-\1"/></svg>',s)
s=re.sub(r'\[\[b:([a-z0-9-]+)\]\]',r'<svg class="icon" aria-hidden="true"><use href="#b-\1"/></svg>',s)
assert not re.findall(r'\[\[[a-zA-Z]', s), re.findall(r'\[\[[^\]]*\]\]',s)
open(P+'/index.html','w').write(s); print('ok', len(s))
