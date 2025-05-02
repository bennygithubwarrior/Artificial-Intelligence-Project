import copy
import json
import logging
import os
import threading
import time
import urllib.request
from collections import deque
from typing import Dict, Set, Tuple, List, Optional, Callable

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(_name_)

CONFIG_FILE = "sudoku_config.json"
DEFAULT_CONFIG = {"delay": 0.1, "theme": "light"}

def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            return json.load(open(CONFIG_FILE))
        except Exception as e:
            logger.error(f"Error loading config: {e}")
    return DEFAULT_CONFIG.copy()

def save_config(cfg: dict) -> None:
    try:
        json.dump(cfg, open(CONFIG_FILE, 'w'), indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {e}")

config = load_config()

class PuzzleLoader:
    drive_cache: Dict[str, str] = {}

    @classmethod
    def download_from_drive(cls, file_id: str) -> str:
        if file_id in cls.drive_cache:
            return cls.drive_cache[file_id]
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        with urllib.request.urlopen(url) as resp:
            text = resp.read().decode('utf-8')
        cls.drive_cache[file_id] = text
        return text

    @staticmethod
    def parse_text(text: str) -> List[List[int]]:
        board: List[List[int]] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) != 9:
                raise ValueError("Each row must have exactly 9 numbers.")
            board.append([int(tok) for tok in parts])
        if len(board) != 9:
            raise ValueError("Puzzle must have exactly 9 rows.")
        return board

    @staticmethod
    def load_local(path: str) -> List[List[int]]:
        return PuzzleLoader.parse_text(open(path).read())

Cell = Tuple[int, int]
Assignment = Dict[Cell, int]
Domain = Dict[Cell, Set[int]]

class SudokuSolver:
    def _init_(self, board: List[List[int]]):
        self.board = board
        self.variables = [(r, c) for r in range(9) for c in range(9)]
        self.domains: Domain = {}
        self._init_domains()
        self.neighbors = {v: self._compute_neighbors(v) for v in self.variables}
        self.paused = False
        self.step_mode = False
        self.pause_cond = threading.Condition()

    def _init_domains(self) -> None:
        for r, c in self.variables:
            v = self.board[r][c]
            self.domains[(r, c)] = {v} if v else set(range(1, 10))

    def _compute_neighbors(self, cell: Cell) -> Set[Cell]:
        r, c = cell
        n: Set[Cell] = set()
        for k in range(9):
            if k != c:
                n.add((r, k))
            if k != r:
                n.add((k, c))
        br, bc = 3 * (r // 3), 3 * (c // 3)
        for i in range(br, br + 3):
            for j in range(bc, bc + 3):
                if (i, j) != cell:
                    n.add((i, j))
        return n

    def enforce_node_consistency(self) -> None:
        for cell in self.variables:
            if self.board[cell[0]][cell[1]] == 0:
                for nb in self.neighbors[cell]:
                    val = self.board[nb[0]][nb[1]]
                    if val:
                        self.domains[cell].discard(val)

    def revise(self, xi: Cell, xj: Cell) -> bool:
        remove = {a for a in self.domains[xi]
                  if all(a == b for b in self.domains[xj])}
        if remove:
            self.domains[xi] -= remove
            return True
        return False

    def ac3(self) -> bool:
        queue = deque((xi, xj) for xi in self.variables for xj in self.neighbors[xi])
        while queue:
            xi, xj = queue.popleft()
            if self.revise(xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.neighbors[xi]:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def assignment_complete(self, a: Assignment) -> bool:
        return len(a) == 81

    def consistent(self, a: Assignment) -> bool:
        for cell, val in a.items():
            for nb in self.neighbors[cell]:
                if a.get(nb) == val:
                    return False
        return True

    def order_domain_values(self, var: Cell, a: Assignment) -> List[int]:
        lst = []
        for v in sorted(self.domains[var]):
            c = sum(1 for nb in self.neighbors[var]
                    if nb not in a and v in self.domains[nb])
            lst.append((v, c))
        lst.sort(key=lambda x: x[1])
        return [v for v, _ in lst]

    def select_unassigned_variable(self, a: Assignment) -> Cell:
        un = [v for v in self.variables if v not in a]
        un.sort(key=lambda v: (len(self.domains[v]), -len(self.neighbors[v])))
        return un[0]

    def _wait(self, d: float) -> None:
        with self.pause_cond:
            while self.paused:
                self.pause_cond.wait()
            if self.step_mode:
                self.paused = True
                self.pause_cond.wait()
        time.sleep(d)

    def backtrack(
        self,
        a: Assignment,
        cb: Optional[Callable[[Cell, int, str], None]] = None,
        delay: float = 0.0
    ) -> Optional[Assignment]:
        if self.assignment_complete(a):
            return a
        var = self.select_unassigned_variable(a)
        for val in self.order_domain_values(var, a):
            na = a.copy()
            na[var] = val
            if cb:
                cb(var, val, "assign")
                self._wait(delay)
            if self.consistent(na):
                saved = copy.deepcopy(self.domains)
                self.domains[var] = {val}
                if self.ac3():
                    res = self.backtrack(na, cb, delay)
                    if res:
                        return res
                self.domains = saved
            if cb:
                cb(var, 0, "backtrack")
                self._wait(delay)
        return None

    def solve(
        self,
        cb: Optional[Callable[[Cell, int, str], None]] = None,
        delay: float = 0.0
    ) -> Optional[Assignment]:
        self.enforce_node_consistency()
        if not self.ac3():
            return None
        initial = {
            c: next(iter(self.domains[c]))
            for c in self.variables
            if len(self.domains[c]) == 1
        }
        sol = self.backtrack(initial, cb, delay)
        if sol:
            for (r, c), v in sol.items():
                self.board[r][c] = v
        return sol
