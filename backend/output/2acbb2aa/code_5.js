// server.js
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = process.env.PORT || 3000;

// 中间件
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// MongoDB 连接
mongoose.connect('mongodb://localhost:27017/testResultsDB', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('MongoDB 连接成功'))
.catch(err => console.error('MongoDB 连接失败:', err));

// 定义测试结果模型
const TestResultSchema = new mongoose.Schema({
  testId: { type: String, required: true, unique: true },
  timestamp: { type: Date, default: Date.now },
  status: { type: String, enum: ['pending', 'running', 'completed', 'failed'], default: 'pending' },
  results: {
    passed: { type: Number, default: 0 },
    failed: { type: Number, default: 0 },
    total: { type: Number, default: 0 }
  },
    details: [{
        testCase: String,
        result: String,
        message: String,
        duration: Number
    }],
    executionTime: Number,
    environment: {
        nodeVersion: String,
        platform: String,
        timestamp: Date
    }
});

const TestResult = mongoose.model('TestResult', TestResultSchema);

// API 路由

// 创建新的测试
app.post('/api/tests', async (req, res) => {
    try {
        const { testId, environment } = req.body;
        
        // 检查测试ID是否已存在
        const existingTest = await TestResult.findOne({ testId });
        if (existingTest) {
            return res.status(409).json({ error: '测试ID已存在' });
        }
        
        const newTest = new TestResult({
            testId,
            environment: {
                nodeVersion: process.version,
                platform: process.platform,
                timestamp: new Date(),
                ...environment
            }
        });
        
        await newTest.save();
        res.status(201).json(newTest);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 获取所有测试
app.get('/api/tests', async (req, res) => {
    try {
        const tests = await TestResult.find().sort({ timestamp: -1 });
        res.json(tests);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 获取特定测试
app.get('/api/tests/:testId', async (req, res) => {
    try {
        const test = await TestResult.findOne({ testId: req.params.testId });
        if (!test) {
            return res.status(404).json({ error: '测试未找到' });
        }
        res.json(test);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 更新测试状态和结果
app.put('/api/tests/:testId', async (req, res) => {
    try {
        const { status, results, details, executionTime } = req.body;
        
        const updateData = {};
        if (status) updateData.status = status;
        if (results) updateData.results = results;
        if (details) updateData.details = details;
        if (executionTime) updateData.executionTime = executionTime;
        
        const test = await TestResult.findOneAndUpdate(
            { testId: req.params.testId },
            updateData,
            { new: true, runValidators: true }
        );
        
        if (!test) {
            return res.status(404).json({ error: '测试未找到' });
        }
        
        res.json(test);
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 删除测试
app.delete('/api/tests/:testId', async (req, res) => {
    try {
        const test = await TestResult.findOneAndDelete({ testId: req.params.testId });
        if (!test) {
            return res.status(404).json({ error: '测试未找到' });
        }
        res.json({ message: '测试已成功删除' });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// 启动服务器
app.listen(PORT, () => {
    console.log(`服务器运行在端口 ${PORT}`);
});

// 导出模型以供其他模块使用
module.exports = { app, TestResult };