import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('sync',Path(__file__).resolve().parents[1]/'scripts/sync_publications.py')
sync=importlib.util.module_from_spec(spec);spec.loader.exec_module(sync)
class Publications(unittest.TestCase):
 def setUp(self):
  self.config={'from_date':'2025-01-01','types':['article','preprint'],'required_coauthor_orcid':'0000-0001-9481-6956','exclude':{}}
  self.work={'id':'https://openalex.org/W1','doi':'https://doi.org/10.1234/EXAMPLE','display_name':'Ocean Kite Control','publication_date':'2025-02-01','publication_year':2025,'type':'article','authorships':[{'author':{'display_name':'Chris Vermillion','orcid':'https://orcid.org/0000-0001-9481-6956'}}],'primary_location':{'source':{'display_name':'Example Journal'}},'biblio':{}}
 def discover(self,works,existing=None,legacy=None):return sync.discover(works,existing or [],legacy or set(),self.config,'2026-10-09')
 def test_deduplicate_doi_and_author_queries(self):
  other=copy.deepcopy(self.work);other['id']='https://openalex.org/W2';other['doi']='http://dx.doi.org/10.1234/example';other['display_name']='Altered title'
  result,added=self.discover([self.work,other,self.work]);self.assertEqual(len(result),1);self.assertEqual(len(added),1)
 def test_legacy_unicode_title_matching(self):
  self.work['display_name']='Ocean—Kite Control'
  self.assertEqual(self.discover([self.work],legacy=sync.legacy_titles('<p>Chris, “Ocean-Kite Control,” Journal.</p>'))[1],[])
 def test_scope_retractions_and_future_dates(self):
  for field,value in [('authorships',[]),('is_retracted',True),('publication_date','2027-01-01')]:
   work=copy.deepcopy(self.work);work[field]=value;self.assertEqual(self.discover([work])[1],[])
 def test_exclusions(self):
  self.config['exclude']={'dois':['10.1234/example']};self.assertEqual(self.discover([self.work])[1],[])
 def test_keep_manual_corrections_and_missing_records(self):
  reviewed=sync.entry(self.work);reviewed['title']='Corrected title';reviewed['note']='Keep'
  self.assertEqual(self.discover([self.work],[reviewed]),([reviewed],[]));self.assertEqual(self.discover([],[reviewed])[0],[reviewed])
 def test_prefer_published_to_preprint(self):
  preprint=copy.deepcopy(self.work);preprint['type']='preprint';preprint['id']='https://openalex.org/W0'
  self.assertEqual(self.discover([preprint,self.work])[0][0]['type'],'article')
 def test_cursor_pagination(self):
  client=sync.OpenAlex();params=[]
  def get(p):
   params.append(dict(p));return {'results':[self.work] if len(params)==1 else [],'meta':{'next_cursor':'NEXT' if len(params)==1 else None}}
  client.get=get;self.assertEqual(len(client.works({'name':'Chris','orcid':'0000-0001-9481-6956'},'2025-01-01')),1);self.assertEqual(params[1]['cursor'],'NEXT')
 def test_atomic_write_no_churn(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'data.json';self.assertTrue(sync.atomic_json(path,[1]));self.assertFalse(sync.atomic_json(path,[1]))
 def test_fetch_failure_preserves_file(self):
  with tempfile.TemporaryDirectory() as folder:
   path=Path(folder)/'data.json';path.write_text('[]\n');old=sync.OpenAlex.works
   def fail(*args):raise RuntimeError('source unavailable')
   sync.OpenAlex.works=fail
   try:
    with self.assertRaises(RuntimeError):sync.main(['--output',str(path)])
   finally:sync.OpenAlex.works=old
   self.assertEqual(path.read_text(),'[]\n')
if __name__=='__main__':unittest.main()
