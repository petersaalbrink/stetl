import mock
import os

from stetl.etl import ETL
from stetl.filters.fileextractor import ZipFileExtractor
from tests.stetl_test_case import StetlTestCase

class ZipFileExtractorTest(StetlTestCase):
    """Unit tests for ZipFileExtractor plus deprecation"""

    def setUp(self):
        super(ZipFileExtractorTest, self).setUp()

        # Initialize Stetl
        self.curr_dir = os.path.dirname(os.path.realpath(__file__))
        cfg_dict = {'config_file': os.path.join(self.curr_dir, 'configs/zipfileextractor.cfg')}
        self.etl = ETL(cfg_dict)
    
    def test_class(self):
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')
        self.assertEqual('stetl.filters.fileextractor.ZipFileExtractor', class_name)
    
    def test_legacy_class(self):
        cfg_dict = {'config_file': os.path.join(self.curr_dir, 'configs/zipfileextractordeprecated.cfg')}
        self.etl = ETL(cfg_dict)
        chain = StetlTestCase.get_chain(self.etl)
        section = StetlTestCase.get_section(chain, 1)
        class_name = self.etl.configdict.get(section, 'class')

        # Deprecated class name in config
        self.assertEqual('stetl.filters.zipfileextractor.ZipFileExtractor', class_name)

        # Assigned to new version in fileextractor module!
        self.assertTrue(isinstance(chain.first_comp.next, ZipFileExtractor))

    def test_instance(self):
        chain = StetlTestCase.get_chain(self.etl)

        self.assertTrue(isinstance(chain.first_comp.next, ZipFileExtractor))
        
    @mock.patch('stetl.filters.fileextractor.ZipFileExtractor.after_chain_invoke', autospec=True)
    def test_execute(self, mock_after_chain_invoke):
        chain = StetlTestCase.get_chain(self.etl)
        chain.run()

        # ZIP file contains two GML files, both should be extracted; count is 3 because of final
        # call, so the ZipFileExtractor can indicate that no more files can be found.
        self.assertTrue(mock_after_chain_invoke.called)
        self.assertEqual(3, mock_after_chain_invoke.call_count)

        # Check if temp file exists
        section = StetlTestCase.get_section(chain, 1)
        file_path = self.etl.configdict.get(section, 'file_path')
        self.assertTrue(os.path.exists(file_path))
        os.remove(file_path)
