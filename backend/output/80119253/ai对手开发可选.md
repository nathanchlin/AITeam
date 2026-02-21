# AI对手开发（可选）

**Agent**: coder

**Time**: 2026-02-18T13:33:34.871616

---

# AI对手开发方案

我将为五子棋游戏设计一个具有不同难度的AI对手系统。这个系统将使用评估函数和搜索算法来做出决策，并通过优化确保流畅的游戏体验。

## 1. AI架构设计

### 基本结构
```python
class GomokuAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        self.max_depth = self._get_max_depth(difficulty)
        self.board_size = 15  # 标准五子棋棋盘大小
        
    def _get_max_depth(self, difficulty):
        """根据难度设置搜索深度"""
        depth_map = {
            'easy': 2,
            'medium': 4,
            'hard': 6,
            'expert': 8
        }
        return depth_map.get(difficulty, 4)
        
    def get_move(self, board):
        """根据当前棋盘状态返回AI的下一步移动"""
        if self.difficulty == 'easy':
            return self._get_random_move(board)
        else:
            return self._minimax_move(board)
            
    def _get_random_move(self, board):
        """简单难度：随机选择一个合法位置"""
        empty_positions = [(i, j) for i in range(self.board_size) 
                         for j in range(self.board_size) if board[i][j] == 0]
        return random.choice(empty_positions) if empty_positions else None
        
    def _minimax_move(self, board):
        """使用Minimax算法选择最佳移动"""
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # 获取所有可能的移动（只考虑已有棋子周围的空位）
        possible_moves = self._get_possible_moves(board)
        
        for move in possible_moves:
            i, j = move
            board[i][j] = 2  # AI的棋子
            score = self._minimax(board, self.max_depth - 1, False, alpha, beta)
            board[i][j] = 0  # 撤销移动
            
            if score > best_score:
                best_score = score
                best_move = move
                
            alpha = max(alpha, best_score)
            
        return best_move
        
    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        """Minimax算法与Alpha-Beta剪枝"""
        if depth == 0 or self._is_game_over(board):
            return self._evaluate_board(board)
            
        possible_moves = self._get_possible_moves(board)
        
        if is_maximizing:
            max_eval = float('-inf')
            for move in possible_moves:
                i, j = move
                board[i][j] = 2  # AI的棋子
                eval = self._minimax(board, depth - 1, False, alpha, beta)
                board[i][j] = 0  # 撤销移动
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = float('inf')
            for move in possible_moves:
                i, j = move
                board[i][j] = 1  # 玩家的棋子
                eval = self._minimax(board, depth - 1, True, alpha, beta)
                board[i][j] = 0  # 撤销移动
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            return min_eval
```

## 2. 棋盘评估函数

```python
def _evaluate_board(self, board):
    """评估当前棋盘状态，返回AI的得分"""
    ai_score = 0
    player_score = 0
    
    # 评估所有方向的棋型
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线
    
    for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] != 0:
                for dx, dy in directions:
                    pattern = self._get_pattern(board, i, j, dx, dy)
                    if pattern:
                        score = self._evaluate_pattern(pattern)
                        if board[i][j] == 2:  # AI的棋子
                            ai_score += score
                        else:  # 玩家的棋子
                            player_score += score
                            
    # 返回AI相对于玩家的得分
    return ai_score - player_score * 1.1  # 稍微重视防守

def _get_pattern(self, board, i, j, dx, dy):
    """获取某个方向上的棋型"""
    pattern = []
    player = board[i][j]
    
    # 向前和向后各取4个位置
    for step in range(-4, 5):
        x, y = i + step * dx, j + step * dy
        if 0 <= x < self.board_size and 0 <= y < self.board_size:
            pattern.append(board[x][y])
        else:
            pattern.append(-1)  # 边界外标记为-1
            
    return pattern

def _evaluate_pattern(self, pattern):
    """评估棋型并返回分数"""
    # 定义各种棋型的分数
    scores = {
        'five': 100000,    # 五连
        'open_four': 10000,  # 活四
        'four': 1000,      # 冲四
        'open_three': 1000,  # 活三
        'three': 100,      # 眠三
        'open_two': 100,   # 活二
        'two': 10,         # 眠二
        'one': 1           # 单子
    }
    
    # 检查五连
    if self._check_five(pattern):
        return scores['five']
        
    # 检查活四
    if self._check_open_four(pattern):
        return scores['open_four']
        
    # 检查冲四
    if self._check_four(pattern):
        return scores['four']
        
    # 检查活三
    if self._check_open_three(pattern):
        return scores['open_three']
        
    # 检查眠三
    if self._check_three(pattern):
        return scores['three']
        
    # 检查活二
    if self._check_open_two(pattern):
        return scores['open_two']
        
    # 检查眠二
    if self._check_two(pattern):
        return scores['two']
        
    # 检查单子
    if self._check_one(pattern):
        return scores['one']
        
    return 0

def _check_five(self, pattern):
    """检查是否有五连"""
    return 1 in pattern[5:10] and pattern[5] == 1 and all(p == 1 for p in pattern[5:10])

def _check_open_four(self, pattern):
    """检查是否有活四"""
    # 活四: 011110 或变体
    for i in range(1, 9):
        if pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and \
           pattern[i+2] == 1 and pattern[i+3] == 1 and pattern[i+4] == 0:
            return True
    return False

def _check_four(self, pattern):
    """检查是否有冲四"""
    # 冲四: 011112, 211110, 011101 等
    for i in range(1, 9):
        if (pattern[i] == 1 and pattern[i+1] == 1 and pattern[i+2] == 1 and 
            pattern[i+3] == 1 and pattern[i-1] != 0 and pattern[i+4] != 0):
            return True
    return False

def _check_open_three(self, pattern):
    """检查是否有活三"""
    # 活三: 01110, 011010, 010110 等
    for i in range(1, 9):
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i+2] == 1 and pattern[i+3] == 0):
            return True
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 0 and 
            pattern[i+2] == 1 and pattern[i+3] == 1 and pattern[i+4] == 0):
            return True
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i+2] == 0 and pattern[i+3] == 1 and pattern[i+4] == 0):
            return True
    return False

def _check_three(self, pattern):
    """检查是否有眠三"""
    # 眠三: 11100, 00111, 11010, 01011 等
    for i in range(1, 9):
        if (pattern[i] == 1 and pattern[i+1] == 1 and pattern[i+2] == 1 and 
            pattern[i-1] != 0 and pattern[i+3] != 0):
            return True
    return False

def _check_open_two(self, pattern):
    """检查是否有活二"""
    # 活二: 01100, 00110, 01010 等
    for i in range(1, 9):
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i+2] == 0 and pattern[i+3] == 0):
            return True
        if (pattern[i-1] == 0 and pattern[i] == 1 and pattern[i+1] == 0 and 
            pattern[i+2] == 1 and pattern[i+3] == 0):
            return True
    return False

def _check_two(self, pattern):
    """检查是否有眠二"""
    # 眠二: 11000, 00110, 10100 等
    for i in range(1, 9):
        if (pattern[i] == 1 and pattern[i+1] == 1 and 
            pattern[i-1] != 0 and pattern[i+2] != 0):
            return True
    return False

def _check_one(self, pattern):
    """检查是否有单子"""
    return 1 in pattern
```

## 3. 可能移动的优化

```python
def _get_possible_moves(self, board):
    """获取所有可能的移动，只考虑已有棋子周围的空位"""
    moves = set()
    
    # 遍历棋盘，找到所有已有棋子
    for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] != 0:  # 如果有棋子
                # 检查周围2格内的空位
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        x, y = i + dx, j + dy
                        if (0 <= x < self.board_size and 0 <= y < self.board_size and 
                            board[x][y] == 0):
                            moves.add((x, y))
                            
    # 如果棋盘为空，返回中心位置
    if not moves:
        center = self.board_size // 2
        return [(center, center)]
        
    return list(moves)
```

## 4. 游戏结束检查

```python
def _is_game_over(self, board):
    """检查游戏是否结束"""
    # 检查是否有五连
    for i in range(self.board_size):
        for j in range(self.board_size):
            if board[i][j] != 0:
                if self._check_win(board, i, j):
                    return True
    return False

def _check_win(self, board, i, j):
    """检查从位置(i,j)出发是否有五连"""
    player = board[i][j]
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线
    
    for dx, dy in directions:
        count = 1  # 当前位置已经有一个棋子
        
        # 正方向检查
        x, y = i + dx, j + dy
        while 0 <= x < self.board_size and 0 <= y < self.board_size and board[x][y] == player:
            count += 1
            x += dx
            y += dy
            
        # 反方向检查
        x, y = i - dx, j - dy
        while 0 <= x < self.board_size and 0 <= y < self.board_size and board[x][y] == player:
            count += 1
            x -= dx
            y -= dy
            
        if count >= 5:
            return True
            
    return False
```

## 5. 性能优化策略

1. **移动窗口优化**：只考虑已有棋子周围的空位，而不是整个棋盘
2. **Alpha-Beta剪枝**：在Minimax搜索中剪掉不可能的分支
3. **迭代深化**：对于高难度AI，可以逐步增加搜索深度
4. **置换表**：缓存已评估的棋盘状态，避免重复计算
5. **启发式评估**：优先考虑更有可能获胜的移动

```python
def _iterative_deepening_minimax(self, board):
    """迭代深化Minimax搜索"""
    best_move = None
    for depth in range(1, self.max_depth + 1):
        _, move = self._minimax_with_depth(board, depth)
        if move:
            best_move = move
    return best_move

def _minimax_with_depth(self, board, depth):
    """带深度限制的Minimax搜索"""
    best_score = float('-inf')
    best_move = None
    alpha = float('-inf')
    beta = float('inf')
    
    possible_moves = self._get_possible_moves(board)
    
    for move in possible_moves:
        i, j = move
        board[i][j] = 2  # AI的棋子
        score = self._minimax(board, depth - 1, False, alpha, beta)
        board[i][j] = 0  # 撤销移动
        
        if score > best_score:
            best_score = score
            best_move = move
            
        alpha = max(alpha, best_score)
        
    return best_score, best_move
```

## 6. 使用示例

```python
# 初始化AI
ai = GomokuAI(difficulty='medium')  # 可以是 'easy', 'medium', 'hard', 'expert'

# 在游戏循环中使用
board = [[0] * 15 for _ in range(15)]  # 15x15空棋盘

# 玩家下棋
player_move = (7, 7)  # 玩家下在中心
board[player_move[0]][player_move[1]] = 1

# AI下棋
ai_move = ai.get_move(board)
board[ai_move[0]][ai_move[1]] = 2
```

## 7. 难度调整策略

1. **简单难度**：
   - 随机选择合法位置
   - 只考虑防守，不考虑进攻
   - 搜索深度为1-2层

2. **中等难度**：
   - 基础Minimax算法
   - 考虑攻防平衡
   - 搜索深度为3-4层

3. **困难难度**：
   - 带Alpha-Beta剪枝的Minimax
   - 重视进攻
   - 搜索深度为5-6层

4. **专家难度**：
   - 迭代深化+置换表
   - 高级评估函数
   - 搜索深度为7-8层

这个AI系统提供了不同难度的对手，能够评估棋局并做出合理的决策，同时通过多种优化策略确保流畅的游戏体验。