"""Run bundled FluPop code and measure the actual stage process on Linux/WSL."""
from pathlib import Path
import sys
import time
import resource
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
from flupop.stage import main, atomic_text

if len(sys.argv)<3 or sys.argv[1]!='--benchmark':
    raise SystemExit('Expected --benchmark PATH before stage arguments')
benchmark=Path(sys.argv[2])
args=sys.argv[3:]
started=time.perf_counter()
initial=resource.getrusage(resource.RUSAGE_SELF)
status='failed'
try:
    main(args)
    status='success'
finally:
    usage=resource.getrusage(resource.RUSAGE_SELF)
    # Linux ru_maxrss is KiB; no sampled or estimated memory values.
    atomic_text(benchmark, 'wall_seconds\tcpu_user_seconds\tcpu_system_seconds\tpeak_rss_mib\tstatus\n'+
        f'{time.perf_counter()-started:.6f}\t{usage.ru_utime-initial.ru_utime:.6f}\t{usage.ru_stime-initial.ru_stime:.6f}\t{usage.ru_maxrss/1024:.6f}\t{status}\n')
