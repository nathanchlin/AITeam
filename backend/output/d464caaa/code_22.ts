// src/store/reducers/gameReducer.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

export interface GameState {
  board: number[][];
  currentPiece: any;
  score: number;
  level: number;
  lines: number;
  isGameOver: boolean;
  isPaused: boolean;
}

const initialState: GameState = {
  board: Array(20).fill(null).map(() => Array(10).fill(0)),
  currentPiece: null,
  score: 0,
  level: 1,
  lines: 0,
  isGameOver: false,
  isPaused: false,
}

const gameSlice = createSlice({
  name: 'game',
  initialState,
  reducers: {
    updateBoard: (state, action: PayloadAction<number[][]>) => {
      state.board = action.payload
    },
    // 添加其他reducer...
  },
})

export const { updateBoard } = gameSlice.actions
export default gameSlice.reducer