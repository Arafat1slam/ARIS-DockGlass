import unittest
from src.domain.dock_layout import calculate_layout

class TestDockLayout(unittest.TestCase):
    def test_total_width(self):
        items = [{'width': 50, 'scale': 1.0}, {'width': 50, 'scale': 2.0}]
        layout = calculate_layout(items, spacing=10)
        self.assertEqual(layout['total_width'], 50*1.0 + 50*2.0 + 10)

    def test_no_overlap(self):
        items = [{'width': 50, 'scale': 1.0}, {'width': 50, 'scale': 1.0}]
        layout = calculate_layout(items, spacing=10)
        self.assertEqual(layout['items'][1]['x'], layout['items'][0]['x'] + 50 + 10)

    def test_symmetric_around_center(self):
        items = [{'width': 50, 'scale': 1.0}, {'width': 50, 'scale': 1.0}]
        layout = calculate_layout(items, spacing=10, position='BOTTOM_CENTER')
        self.assertEqual(layout['items'][0]['x'], -55) # Half of total_width 110
        self.assertEqual(layout['items'][1]['x'], 5)

if __name__ == '__main__':
    unittest.main()
