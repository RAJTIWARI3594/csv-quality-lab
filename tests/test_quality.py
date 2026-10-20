import unittest,tempfile,csv,json
from pathlib import Path
from quality import analyze,kind,main,export_csv
class Tests(unittest.TestCase):
 def setUp(self):self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.p=Path(self.t.name)/'in.csv'
 def text(self,s):self.p.write_text(s);return self.p
 def test_counts(self):
  r,h,rows=analyze(self.text('id,x\n1, 2 \n1,\n'),'id');self.assertEqual(r['row_count'],2);self.assertEqual(r['columns']['x']['blank'],1);self.assertEqual(len(r['duplicate_keys']),1);self.assertEqual(rows[0],['1','2'])
 def test_duplicate_headers(self):
  with self.assertRaises(ValueError):analyze(self.text('id,id\n1,2'))
 def test_blank_header(self):
  with self.assertRaises(ValueError):analyze(self.text('id,\n1,2'))
 def test_shape(self):
  with self.assertRaises(ValueError):analyze(self.text('id,x\n1,2,3'))
 def test_empty(self):
  with self.assertRaises(ValueError):analyze(self.text(''))
 def test_key(self):
  with self.assertRaises(ValueError):analyze(self.text('id\n1'),'missing')
 def test_types(self):self.assertEqual([kind(x) for x in ('','2026-01-02','1.2','nan','hello')],['blank','date','number','text','text'])
 def test_export_safe(self):
  out=Path(self.t.name)/'o.csv';export_csv(out,['x'],[['=1+1']],True);self.assertIn("'=1+1",out.read_text())
 def test_overwrite_guard(self):
  self.text('x\n1');self.assertEqual(main([str(self.p),'--out',str(self.p)]),2);self.assertEqual(self.p.read_text(),'x\n1')
 def test_cli(self):
  self.text('id\n1');out=Path(self.t.name)/'r.json';self.assertEqual(main([str(self.p),'--out',str(out)]),0);self.assertEqual(json.loads(out.read_text())['row_count'],1)
 def test_quoted_multiline(self):
  r,_,rows=analyze(self.text('id,note\n1,"a\nb"\n'));self.assertEqual(r['row_count'],1);self.assertEqual(rows[0][1],'a\nb')
if __name__=='__main__':unittest.main()
