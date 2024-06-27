import unittest
from unittest.mock import patch

import numpy as np

from memo import menu, setup_game, launch_game


class TestMenu(unittest.TestCase):
    @patch('cv2.VideoCapture')
    def test_menu_starts_game_when_s_pressed(self, mock_vid):
        mock_vid.read.return_value = (True, np.zeros((500, 500, 3),
                                                     dtype=np.uint8))
        with patch('cv2.waitKey', return_value=ord('s')):
            with patch('memo.launch_game') as mock_launch:
                menu(mock_vid)
                mock_launch.assert_called_once()

    @patch('cv2.VideoCapture')
    def test_menu_quits_when_q_pressed(self, mock_vid):
        mock_vid.read.return_value = (True, np.zeros((500, 500, 3),
                                                     dtype=np.uint8))
        with patch('cv2.waitKey', return_value=ord('q')):
            with patch('cv2.destroyAllWindows') as mock_destroy:
                menu(mock_vid)
                mock_destroy.assert_called_once()


class TestSetupGame(unittest.TestCase):
    def test_setup_game_creates_correct_grid(self):
        rows, cols = 4, 5
        result = setup_game(rows, cols)
        self.assertEqual(len(result), rows)
        self.assertEqual(len(result[0]), cols)
        self.assertEqual(len(set(sum(result, []))), (rows * cols) // 2)

    def test_setup_game_creates_random_grid(self):
        rows, cols = 4, 5
        result1 = setup_game(rows, cols)
        result2 = setup_game(rows, cols)
        self.assertNotEqual(result1, result2)


class LaunchGameTests(unittest.TestCase):
    @patch('cv2.flip')
    @patch('cv2.VideoCapture')
    def test_game_quits_when_q_pressed(self, mock_vid, mock_flip):
        mock_vid.read.return_value = (
            True, np.zeros((500, 500, 3), dtype=np.uint8))
        mock_flip.return_value = np.zeros((500, 500, 3),
                                          dtype=np.uint8)
        with patch('cv2.waitKey', return_value=ord('q')):
            with patch('cv2.destroyAllWindows') as mock_destroy:
                launch_game(mock_vid, [[-1] * 5] * 4)
                mock_destroy.assert_called_once()


if __name__ == '__main__':
    unittest.main()
