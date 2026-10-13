"""Validate this Chinese visual revision without retraining or rerunning evaluation."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unicodedata
import zipfile

import imageio.v2 as imageio
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw
from pptx import Presentation
import pymupdf

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def chars(t):return Counter(re.sub(r'\s','',unicodedata.normalize('NFKC',t)))


def main():
    original=HERE.parent/'assignment_solutions_20261013'
    assert sha(HERE/'results.json')==sha(original/'results.json')
    original_check=read(original/'verification.json')
    for n in original_check['notebooks']:
        assert sha(ROOT/'notebooks/solutions_20261013'/n['file'])==n['sha256']
    replay=read(HERE/'replay_provenance.json')
    assert replay['new_training_runs']==replay['new_policy_evaluations']==0
    for name,case in replay['cases'].items():
        assert max(case['max_absolute_state_errors'].values())==0.0
        assert case['all_logged_booleans_match']
        assert sha(HERE/'evidence'/f'{name}_trace.npz')==sha(original/'evidence'/f'{name}_trace.npz')
    for name,h in replay['asset_sha256'].items():assert sha(HERE/'assets'/name)==h
    trace=np.load(HERE/'evidence/failure_trace.npz')
    assert trace['gripper_contact'][49:57].all() and not trace['gripper_contact'][57:].any()
    assert abs((trace['object_position'][:,2].max()-trace['object_position'][0,2])*1000-5.722)<.001
    result=read(HERE/'results.json')
    for v,count in [('lr_a',3),('lr_b',5)]:
        for condition in ['standard','shifted']:
            rows=[r for r in result['variants'][v]['eval']['episodes'] if r['condition']==condition]
            assert len(rows)==5 and sum(r['stable_success'] for r in rows)==count
    notes=read(HERE/'slides.json');deck=Presentation(HERE/'Manipulation_Lab_Solutions_ZH.pptx')
    assert len(deck.slides)==len(notes['slides'])==15
    pdf=pymupdf.open(HERE/'Manipulation_Lab_Solutions_ZH.pdf');assert len(pdf)==15
    font_names=sorted({f[3] for page in pdf for f in page.get_fonts()})
    assert any('LabClassroomSans' in n for n in font_names),font_names
    assert any('LabClassroomSerif' in n for n in font_names),font_names
    assert notes['visible_language']=='Chinese explanations; English mathematical notation'
    assert notes['equations'][0]['latex'].startswith(r'\mathcal{L}_{BC}')
    equation=HERE/notes['equations'][0]['asset']
    assert Image.open(equation).width>1500
    assert any(sh.shape_type==13 and hashlib.sha256(sh.image.blob).hexdigest()==sha(equation)
               for sh in deck.slides[5].shapes)
    sheet=Image.new('RGB',(1600,1750),'#E4EAF1');texts=[]
    for i,(s,page) in enumerate(zip(deck.slides,pdf)):
        t='\n'.join(sh.text for sh in s.shapes if sh.has_text_frame);texts.append(t)
        assert len(re.findall(r'[\u4e00-\u9fff]',t))>40
        assert notes['slides'][i]['notes_zh'] in s.notes_slide.notes_text_frame.text
        assert not list(page.annots() or [])
        missing=chars(t)-chars(page.get_text());assert not missing,(i+1,dict(missing))
        for sh in s.shapes:
            assert sh.left>=0 and sh.top>=0
            assert sh.left+sh.width<=deck.slide_width+10 and sh.top+sh.height<=deck.slide_height+10,(i+1,sh.name)
        dest=HERE/f'preview/slide_{i+1:02d}.png';page.get_pixmap(matrix=pymupdf.Matrix(1.5,1.5)).save(dest)
        im=Image.open(dest).convert('RGB');im.thumbnail((533,300));sheet.paste(im,((i%3)*533,(i//3)*350));ImageDraw.Draw(sheet).text(((i%3)*533+12,(i//3)*350+310),str(i+1),fill='#14283D')
    sheet.save(HERE/'preview/contact_sheet.png')
    (HERE/'visible_slide_text.txt').write_text('\n\n'.join(texts)+'\n')
    media=[]
    for label in ['failure','success']:
        path=HERE/'assets'/f'{label}_hd.mp4'
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-v','error','-i',str(path),'-f','null','-'],check=True,capture_output=True)
        with imageio.get_reader(path) as r:meta=r.get_meta_data();frames=r.count_frames()
        assert frames==len(replay['cases'][label]['video_control_steps'])
        assert tuple(meta['size'])==(960,544)
        media.append({'file':path.name,'frames':frames,'duration_seconds':meta['duration'],'size':meta['size'],'playback_speed':.5})
    with zipfile.ZipFile(HERE/'Manipulation_Lab_Solutions_ZH.pptx') as z:
        names=[n for n in z.namelist() if n.endswith('.mp4')];assert len(names)==2
        assert {hashlib.sha256(z.read(n)).hexdigest() for n in names}=={sha(HERE/'assets'/f'{x}_hd.mp4') for x in ['failure','success']}
    verification={'passed':True,'slides':15,'language':'Chinese explanations and notes; English mathematical notation','speaker_notes_seconds':notes['seconds'],
        'style':notes['style'],'equation_source_and_embedded_image_match':True,
        'native_editable_diagrams':True,'source_experiment_unchanged':True,'executed_notebooks_unchanged':True,
        'new_training_runs':0,'new_policy_evaluations':0,'saved_action_replays':replay['cases'],
        'all_replayed_numeric_states_exactly_match':True,'all_logged_booleans_match':True,
        'pdf_native_text_coverage_including_character_counts':True,'pdf_fonts':font_names,'media':media,'embedded_video_hashes_match':True,
        'original_failed_replay_retained':replay.get('excluded_attempt'),
        'limits':['Native PowerPoint playback on the teaching computer remains untested. Install the bundled SC fonts for the intended typography.',
                  'Camera replays visualize saved actions, not new independent policy evaluations. The failure clip covers only states 1 through 101 of the original 500-step rollout.',
                  'One training seed and five matched cases per condition. Failure causes and proposed interventions remain untested.']}
    verification['deliverable_sha256']={name:sha(HERE/name) for name in ['Manipulation_Lab_Solutions_ZH.pptx','Manipulation_Lab_Solutions_ZH.pdf','speaker_notes_zh.txt']}
    (HERE/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'passed':True,'slides':15,'all_replay_state_errors':0.0,'new_experiments':0,'media':media,'pdf_fonts':font_names},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
