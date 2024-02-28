import random
import re
from enum import Enum

import numpy as np
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.binarypuzzle.com/"


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    VERY_HARD = 4


def get(idx: int = random.randint(0, 199), size: int = 10, difficulty: Difficulty = Difficulty.MEDIUM):
    if idx < 0 or idx > 199:
        raise ValueError("Idx must be between 0 and 199")

    if size not in [6, 8, 10, 12, 14]:
        raise ValueError("Only size 6, 8, 10, 12, 14 are supported")

    url = f"{BASE_URL}/puzzles.php?size={size}&level={difficulty.value}&nr={idx+1}"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    grid = [match.text.strip()
            for match in soup.find_all('p', id=re.compile('celpar_'))]
    grid = np.array([int(num) if num.isdigit() else -1 for num in grid])
    return grid.reshape(int(len(grid)**0.5), -1)
