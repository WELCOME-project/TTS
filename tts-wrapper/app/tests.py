import unittest
import language_utils

class Tests(unittest.TestCase):

    def test_eng(self):
        lang = 'eng_male'
        new_lang = language_utils.convert_language_config_key(lang)
        self.assertEqual(new_lang, "en_male")
        
    def test_ajp(self):
        lang = 'ajp'
        new_lang = language_utils.convert_language_config_key(lang)
        self.assertEqual(new_lang, "ar")
        
    def test_cat(self):
        lang = 'cat_female'
        new_lang = language_utils.convert_language_config_key(lang)
        self.assertEqual(new_lang, "ca_female")

if __name__ == '__main__':
    unittest.main()