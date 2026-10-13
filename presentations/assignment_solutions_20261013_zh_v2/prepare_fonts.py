"""Extract SC faces; rename both outer and internal names without changing glyphs."""
import hashlib
import json
from pathlib import Path
from fontTools.ttLib import TTCollection, TTFont

HERE=Path(__file__).resolve().parent


def glyph_hash(font):
    chars=font['CFF '].cff.topDictIndex[0].CharStrings
    digest=hashlib.sha256()
    for name in sorted(chars.keys()):
        digest.update(name.encode());digest.update(chars[name].bytecode)
    return digest.hexdigest()


def main():
    records=[]
    for kind,weight in [('Sans','Regular'),('Sans','Bold'),('Serif','Regular')]:
        source=Path(f'/usr/share/fonts/opentype/noto/Noto{kind}CJK-{weight}.ttc')
        collection=TTCollection(source)
        font=next(f for f in collection.fonts if f['name'].getDebugName(1)==f'Noto {kind} CJK SC')
        original_hash=glyph_hash(font);cmap=font.getBestCmap().copy()
        family=f'Lab Classroom {kind}';ps=f'LabClassroom{kind}-{weight}'
        replacements={1:family,4:f'{family} {weight}',6:ps,16:family}
        for item in font['name'].names:
            if item.nameID in replacements:
                item.string=replacements[item.nameID].encode(item.getEncoding())
        cff=font['CFF '].cff;cff.fontNames=[ps];top=cff.topDictIndex[0]
        top.FamilyName=family;top.FullName=f'{family} {weight}'
        # Shared CJK glyph subfonts retain JP labels even in the authentic SC face.
        # Rename these internal labels too so PDF embedding identifies this package.
        for sub in top.FDArray:sub.FontName=ps+'-'+sub.FontName.split(f'-{weight}-',1)[1]
        dest=HERE/'fonts'/f'{ps}.otf';font.save(dest)
        check=TTFont(dest)
        assert check.getBestCmap()==cmap and glyph_hash(check)==original_hash
        records.append({'file':dest.name,'source':str(source),'selected_face':f'Noto {kind} CJK SC',
                        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                        'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                        'cmap_and_all_glyph_programs_unchanged':True,'glyph_program_sha256':original_hash})
    (HERE/'fonts/provenance.json').write_text(json.dumps(records,indent=2)+'\n')
    print('Three Simplified Chinese faces extracted; all character maps and glyph programs unchanged.')


if __name__=='__main__':main()
