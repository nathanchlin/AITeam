// Node.js Express示例
const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(bodyParser.json());

const FEEDBACK_FILE = path.join(__dirname, 'feedback.json');

// 保存反馈
app.post('/feedback', (req, res) => {
    const feedback = req.body;
    
    // 读取现有反馈
    let feedbacks = [];
    if (fs.existsSync(FEEDBACK_FILE)) {
        feedbacks = JSON.parse(fs.readFileSync(FEEDBACK_FILE));
    }
    
    // 添加新反馈
    feedbacks.push(feedback);
    
    // 保存反馈
    fs.writeFileSync(FEEDBACK_FILE, JSON.stringify(feedbacks, null, 2));
    
    res.json({ success: true, id: feedbacks.length });
});

// 获取反馈（管理员功能）
app.get('/admin/feedback', (req, res) => {
    if (!req.headers.authorization || req.headers.authorization !== 'Bearer admin-token') {
        return res.status(401).json({ error: 'Unauthorized' });
    }
    
    const feedbacks = fs.existsSync(FEEDBACK_FILE) 
        ? JSON.parse(fs.readFileSync(FEEDBACK_FILE)) 
        : [];
    
    res.json(feedbacks);
});

app.listen(3000, () => console.log('Feedback API running on port 3000'));