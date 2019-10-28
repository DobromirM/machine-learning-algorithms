import sys
import unittest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from src.application import MainWindow

app = QApplication(sys.argv)


class MargaritaMixerTest(unittest.TestCase):

    def setUp(self):
        '''Create the GUI'''
        self.window = MainWindow()

    def test_turn_delay_slider(self):
        '''Test the turn delay slider'''

        self.window.central_widget.delay_slider.setValue(20)
        self.assertEqual(self.window.central_widget.delay_slider.value(), 20)
