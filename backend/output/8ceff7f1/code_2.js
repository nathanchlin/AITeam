const mongoose = require('mongoose');

const ScoreSchema = new mongoose.Schema({
  username: {
    type: String,
    required: true,
    trim: true,
    maxlength: 50
  },
  score: {
    type: Number,
    required: true,
    min: 0
  },
  level: {
    type: Number,
    required: true,
    min: 1
  },
  timeSpent: {
    type: Number, // 单位：秒
    required: true,
    min: 0
  },
  completedAt: {
    type: Date,
    default: Date.now
  },
  avatar: {
    type: String,
    default: 'default'
  }
}, {
  timestamps: true
});

// 创建索引以提高查询性能
ScoreSchema.index({ score: -1, completedAt: -1 });
ScoreSchema.index({ username: 1 });

module.exports = mongoose.model('Score', ScoreSchema);