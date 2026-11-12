"""Compatibility command: select native frames; slow retiming was removed."""
import subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
raise SystemExit(subprocess.run([sys.executable,str(ROOT/'scripts/select-native-clips.py'),*sys.argv[1:]],cwd=ROOT).returncode)
