import unittest
from ..observer import Observer

class ObserverTest(unittest.TestCase):
    def test_find_consoles(self):
        """Find valid console plugins"""
        obs = Observer(console_path='test/valid_plugins', find_cnsl=False)
        self.assertFalse(obs.console)
        obs.find_console()
        self.assertTrue(obs.console)
        self.assertTrue(hasattr(obs.console, 'discover'))
        self.assertTrue(hasattr(obs.console, 'measure'))
        
    def test_find_emitters(self):
        """Find valid emitter plugins"""
        obs = Observer(emitter_path='test/valid_plugins', find_emitters=False)
        self.assertFalse(obs.emitters)
        obs.find_emitters()
        self.assertTrue(obs.emitters)
        self.assertEqual(len(obs.emitters), 2)
        for emitter in obs.emitters:
            self.assertTrue(hasattr(emitter, 'connect'))
            self.assertTrue(hasattr(emitter, 'send'))
        
    def test_polling(self):
        """Test polling"""
        pass

    
