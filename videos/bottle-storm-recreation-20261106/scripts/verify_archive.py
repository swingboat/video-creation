"""Check the portable archive against its own file hashes without external dependencies."""
from pathlib import Path,PurePosixPath
import zipfile,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
archive=ROOT/'outputs/bottle-storm-bunny-fish-project.zip'
with zipfile.ZipFile(archive) as z:
    names=z.namelist();prefix=ROOT.name+'/'
    for name in names:
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or not name.startswith(prefix):raise RuntimeError('Unsafe archive path '+name)
    manifest=json.loads(z.read(prefix+'docs/package-manifest.json'))
    for rel,meta in manifest.items():
        data=z.read(prefix+rel)
        if len(data)!=meta['bytes'] or hashlib.sha256(data).hexdigest()!=meta['sha256']:raise RuntimeError('Manifest mismatch '+rel)
    if z.testzip():raise RuntimeError('CRC failed')
    required=['public/bottle-storm.blend','public/bunny-fish-picture.mp4','public/storm-soundscape.wav','src/Composition.tsx','package.json','package-lock.json','scripts/upgrade_fish.py','docs/fish-paths.json','outputs/versions/bunny-v2/bottle-storm.blend','outputs/bottle-storm-bunny-fish-20s.mp4']
    missing=[x for x in required if prefix+x not in names]
    if missing:raise RuntimeError('Missing '+repr(missing))
report={'passed':True,'manifest_hashes_verified':len(manifest),'files':len(names),'bytes':archive.stat().st_size,'crc_ok':True,'all_paths_inside_video':True,'required_deliverables_present':True}
(ROOT/'outputs/checks/fish/archive-check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
