from enum import Enum
from typing import List, Tuple, Optional
import copy

class Player(Enum):
    BLACK = 1
    WHITE = 2
    
class GameStatus(Enum):
    IN_PROGRESS = "进行中"
    BLACK_WIN = "黑棋胜利"
    WHITE_WIN = "白棋胜利"
    DRAW = "平局"
    PAUSED = "暂停"
    TERMINATED = "终止"

class GameState:
    def __init__(self, board_size: int = 15):
        """
        初始化游戏状态
        
        Args:
            board_size: 棋盘大小，默认为15x15
        """
        self.board_size = board_size
        self.reset_game()
    
    def reset_game(self):
        """重置游戏状态"""
        # 初始化棋盘，0表示空，1表示黑棋，2表示白棋
        self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.current_player = Player.BLACK
        self.game_status = GameStatus.IN_PROGRESS
        self.move_history = []
        self.winning_line = []  # 存储获胜的五子连线
        self.last_move = None  # 存储最后一步的位置
        self.captures = {Player.BLACK: 0, Player.WHITE: 0}  # 记录吃子数（如果需要）
    
    def make_move(self, row: int, col: int) -> bool:
        """
        在指定位置落子
        
        Args:
            row: 行索引
            col: 列索引
            
        Returns:
            bool: 落子是否成功
        """
        # 检查游戏是否在进行中
        if self.game_status != GameStatus.IN_PROGRESS:
            return False
        
        # 检查位置是否有效
        if not self.is_valid_move(row, col):
            return False
        
        # 落子
        self.board[row][col] = self.current_player.value
        self.last_move = (row, col)
        
        # 记录历史
        self.move_history.append({
            'player': self.current_player,
            'position': (row, col),
            'board_state': copy.deepcopy(self.board)
        })
        
        # 检查是否获胜
        if self.check_win(row, col):
            self.game_status = GameStatus.BLACK_WIN if self.current_player == Player.BLACK else GameStatus.WHITE_WIN
            return True
        
        # 检查是否平局
        if self.is_board_full():
            self.game_status = GameStatus.DRAW
            return True
        
        # 切换玩家
        self.current_player = Player.WHITE if self.current_player == Player.BLACK else Player.BLACK
        return True
    
    def is_valid_move(self, row: int, col: int) -> bool:
        """
        检查落子是否有效
        
        Args:
            row: 行索引
            col: 列索引
            
        Returns:
            bool: 落子是否有效
        """
        # 检查是否在棋盘范围内
        if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
            return False
        
        # 检查位置是否已有棋子
        return self.board[row][col] == 0
    
    def check_win(self, row: int, col: int) -> bool:
        """
        检查是否获胜
        
        Args:
            row: 最后落子的行索引
            col: 最后落子的列索引
            
        Returns:
            bool: 是否获胜
        """
        player = self.board[row][col]
        directions = [
            [(0, 1), (0, -1)],    # 水平
            [(1, 0), (-1, 0)],    # 垂直
            [(1, 1), (-1, -1)],   # 对角线1
            [(1, -1), (-1, 1)]    # 对角线2
        ]
        
        for direction_pair in directions:
            count = 1  # 包括当前位置
            winning_positions = [(row, col)]
            
            # 检查两个方向
            for dx, dy in direction_pair:
                r, c = row + dx, col + dy
                while (0 <= r < self.board_size and 0 <= c < self.board_size and 
                       self.board[r][c] == player):
                    count += 1
                    winning_positions.append((r, c))
                    r += dx
                    c += dy
            
            # 如果有连续5个或更多棋子，则获胜
            if count >= 5:
                self.winning_line = winning_positions
                return True
        
        return False
    
    def is_board_full(self) -> bool:
        """
        检查棋盘是否已满
        
        Returns:
            bool: 棋盘是否已满
        """
        for row in self.board:
            if 0 in row:
                return False
        return True
    
    def undo_move(self) -> bool:
        """
        撤销上一步操作
        
        Returns:
            bool: 是否成功撤销
        """
        if not self.move_history:
            return False
        
        # 恢复上一步状态
        last_move = self.move_history.pop()
        self.board = last_move['board_state']
        self.current_player = last_move['player']
        self.last_move = None if not self.move_history else self.move_history[-1]['position']
        
        # 重置游戏状态
        self.game_status = GameStatus.IN_PROGRESS
        self.winning_line = []
        
        return True
    
    def get_board_state(self) -> List[List[int]]:
        """
        获取当前棋盘状态
        
        Returns:
            List[List[int]]: 棋盘状态
        """
        return copy.deepcopy(self.board)
    
    def get_game_info(self) -> dict:
        """
        获取游戏信息
        
        Returns:
            dict: 游戏信息
        """
        return {
            'current_player': self.current_player,
            'game_status': self.game_status,
            'move_count': len(self.move_history),
            'last_move': self.last_move,
            'winning_line': self.winning_line,
            'captures': self.captures
        }
    
    def pause_game(self):
        """暂停游戏"""
        if self.game_status == GameStatus.IN_PROGRESS:
            self.game_status = GameStatus.PAUSED
    
    def resume_game(self):
        """恢复游戏"""
        if self.game_status == GameStatus.PAUSED:
            self.game_status = GameStatus.IN_PROGRESS
    
    def terminate_game(self):
        """终止游戏"""
        self.game_status = GameStatus.TERMINATED
    
    def get_possible_moves(self) -> List[Tuple[int, int]]:
        """
        获取所有可能的落子位置
        
        Returns:
            List[Tuple[int, int]]: 所有可能的落子位置
        """
        possible_moves = []
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] == 0:
                    possible_moves.append((row, col))
        return possible_moves