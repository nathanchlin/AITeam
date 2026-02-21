import axios from 'axios';

// 获取排行榜
export const getLeaderboard = async (page = 1, limit = 10) => {
  try {
    const response = await axios.get(`/api/scores?page=${page}&limit=${limit}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching leaderboard:', error);
    throw error;
  }
};

// 提交分数
export const submitScore = async (scoreData) => {
  try {
    const response = await axios.post('/api/scores', scoreData);
    return response.data;
  } catch (error) {
    console.error('Error submitting score:', error);
    throw error;
  }
};

// 获取用户排名
export const getUserRank = async (username) => {
  try {
    const response = await axios.get(`/api/scores/user/${username}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching user rank:', error);
    throw error;
  }
};