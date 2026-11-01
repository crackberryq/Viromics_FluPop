import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
class WorkflowTests(unittest.TestCase):
    def test_run_resume_recovery_and_validation(self):
        with tempfile.TemporaryDirectory(prefix='flupop test ') as tmp:
            root=Path(tmp)
            config={'output_dir':str(root/'output with spaces'),'synthetic_demo':True,'samples':{'DEMO':{
                'consensus':str(ROOT/'examples/consensus.fasta'),
                'haplotypes':str(ROOT/'examples/haplotypes.tsv')}}}
            path=root/'run.json';path.write_text(json.dumps(config))
            cmd=[sys.executable,'-m','snakemake','-s',str(ROOT/'workflow/Snakefile'),'--directory',tmp,'--configfile',str(path),'--cores','1','--rerun-incomplete']
            def run():return subprocess.run(cmd,capture_output=True,text=True,timeout=120)
            result=run();self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            output=root/'output with spaces/DEMO'
            report=output/'report/viral-cloud.html'
            self.assertIn('SYNTHETIC',report.read_text())
            stamp=report.stat().st_mtime_ns
            result=run();self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(stamp,report.stat().st_mtime_ns)
            report.unlink()
            result=run();self.assertEqual(result.returncode,0,result.stderr)
            self.assertTrue(report.is_file())
            for name in ['validate','cfasta','report']:
                self.assertTrue((output/f'benchmarks/{name}.tsv').stat().st_size)
            bad=root/'bad.tsv';bad.write_text('wrong\n')
            config['samples']['DEMO']['haplotypes']=str(bad)
            config['output_dir']=str(root/'invalid-results')
            path.write_text(json.dumps(config))
            result=run();self.assertNotEqual(result.returncode,0)
            self.assertFalse((root/'invalid-results/DEMO/report/viral-cloud.html').exists())
