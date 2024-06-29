import unittest

from games_file.python.cv2_utils import Rectangle
from memo import setup_game


class TestSetupGame(unittest.TestCase):
    def test_setup_game_creates_correct_number_of_cards(self):
        cards = setup_game(4, 5)
        self.assertEqual(len(cards), 20)

    def test_setup_game_creates_cards_with_correct_values(self):
        cards = setup_game(2, 2)
        card_values = [card.text for card in cards]
        self.assertCountEqual(card_values, ['1', '1', '2', '2'])

    def test_setup_game_creates_cards_with_correct_positions(self):
        cards = setup_game(2, 2)
        expected_positions = [(0, 0), (200, 0), (0, 250), (200, 250)]
        card_positions = [(card.x, card.y) for card in cards]
        self.assertCountEqual(card_positions, expected_positions)

    def test_setup_game_creates_cards_of_type_rectangle(self):
        cards = setup_game(2, 2)
        for card in cards:
            self.assertIsInstance(card, Rectangle)


if __name__ == '__main__':
    unittest.main()
