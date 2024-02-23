import re
import requests
from bs4 import BeautifulSoup
import numpy as np

URL = "https://www.binarypuzzle.com/"


def parse():
    soup = BeautifulSoup(requests.get(URL).text, features='lxml')
    grid = [match.text.strip()
            for match in soup.find_all('p', id=re.compile('celpar_'))]
    grid = np.array([int(num) if num.isdigit() else -1 for num in grid])
    return grid.reshape(int(len(grid)**0.5), -1)
