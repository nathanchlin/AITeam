# 后端API开发

**Agent**: coder

**Time**: 2026-02-18T14:24:20.948826

---

我将为您开发一个完整的RESTful API后端，用于处理测试请求和结果存储。我会使用Node.js和Express框架来实现这个API。

以下是完整的后端代码实现：

```javascript
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
```

接下来，我将为您提供一个简单的HTML前端界面，用于与这个API交互：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>测试管理API</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            padding: 30px;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .section {
            margin-bottom: 30px;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
        .section h2 {
            color: #3498db;
            margin-top: 0;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input, textarea, select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #3498db;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #2980b9;
        }
        button.secondary {
            background-color: #95a5a6;
        }
        button.secondary:hover {
            background-color: #7f8c8d;
        }
        .test-list {
            margin-top: 20px;
        }
        .test-item {
            background-color: #f9f9f9;
            border: 1px solid #eee;
            border-radius: 4px;
            padding: 15px;
            margin-bottom: 15px;
        }
        .test-item h3 {
            margin-top: 0;
            color: #2c3e50;
        }
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-left: 10px;
        }
        .status.pending {
            background-color: #f39c12;
            color: white;
        }
        .status.running {
            background-color: #3498db;
            color: white;
        }
        .status.completed {
            background-color: #2ecc71;
            color: white;
        }
        .status.failed {
            background-color: #e74c3c;
            color: white;
        }
        .test-details {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
        }
        .test-details p {
            margin: 5px 0;
        }
        .test-details table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .test-details th, .test-details td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .test-details th {
            background-color: #f2f2f2;
        }
        .notification {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
            display: none;
        }
        .notification.success {
            background-color: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .notification.error {
            background-color: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>测试管理API</h1>
        
        <div id="notification" class="notification"></div>
        
        <!-- 创建新测试 -->
        <div class="section">
            <h2>创建新测试</h2>
            <form id="createTestForm">
                <div class="form-group">
                    <label for="testId">测试ID:</label>
                    <input type="text" id="testId" required>
                </div>
                <div class="form-group">
                    <label for="nodeVersion">Node.js 版本:</label>
                    <input type="text" id="nodeVersion" placeholder="例如: v14.17.0">
                </div>
                <div class="form-group">
                    <label for="platform">平台:</label>
                    <input type="text" id="platform" placeholder="例如: Linux, Windows, macOS">
                </div>
                <button type="submit">创建测试</button>
            </form>
        </div>
        
        <!-- 更新测试结果 -->
        <div class="section">
            <h2>更新测试结果</h2>
            <form id="updateTestForm">
                <div class="form-group">
                    <label for="updateTestId">测试ID:</label>
                    <input type="text" id="updateTestId" required>
                </div>
                <div class="form-group">
                    <label for="status">状态:</label>
                    <select id="status">
                        <option value="pending">待处理</option>
                        <option value="running">运行中</option>
                        <option value="completed">已完成</option>
                        <option value="failed">失败</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="passed">通过数量:</label>
                    <input type="number" id="passed" min="0">
                </div>
                <div class="form-group">
                    <label for="failed">失败数量:</label>
                    <input type="number" id="failed" min="0">
                </div>
                <div class="form-group">
                    <label for="total">总数量:</label>
                    <input type="number" id="total" min="0">
                </div>
                <div class="form-group">
                    <label for="executionTime">执行时间 (毫秒):</label>
                    <input type="number" id="executionTime" min="0">
                </div>
                <div class="form-group">
                    <label for="details">测试详情 (JSON格式):</label>
                    <textarea id="details" rows="4" placeholder='[{"testCase": "测试用例1", "result": "通过", "message": "测试通过", "duration": 100}]'></textarea>
                </div>
                <button type="submit">更新测试</button>
                <button type="button" class="secondary" id="deleteTestBtn">删除测试</button>
            </form>
        </div>
        
        <!-- 测试列表 -->
        <div class="section">
            <h2>测试列表</h2>
            <button id="refreshTestsBtn">刷新测试列表</button>
            <div id="testList" class="test-list"></div>
        </div>
    </div>

    <script>
        // API 基础URL
        const API_BASE_URL = 'http://localhost:3000/api';
        
        // DOM 元素
        const notification = document.getElementById('notification');
        const createTestForm = document.getElementById('createTestForm');
        const updateTestForm = document.getElementById('updateTestForm');
        const refreshTestsBtn = document.getElementById('refreshTestsBtn');
        const testList = document.getElementById('testList');
        const deleteTestBtn = document.getElementById('deleteTestBtn');
        
        // 显示通知
        function showNotification(message, type = 'success') {
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.style.display = 'block';
            
            setTimeout(() => {
                notification.style.display = 'none';
            }, 3000);
        }
        
        // 创建新测试
        createTestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const testId = document.getElementById('testId').value;
            const nodeVersion = document.getElementById('nodeVersion').value || process.version;
            const platform = document.getElementById('platform').value || process.platform;
            
            try {
                const response = await fetch(`${API_BASE_URL}/tests`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        testId,
                        environment: {
                            nodeVersion,
                            platform
                        }
                    })
                });
                
                if (response.ok) {
                    showNotification('测试创建成功！');
                    createTestForm.reset();
                    loadTests();
                } else {
                    const error = await response.json();
                    showNotification(error.error, 'error');
                }
            } catch (error) {
                showNotification('创建测试失败: ' + error.message, 'error');
            }
        });
        
        // 更新测试
        updateTestForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const testId = document.getElementById('updateTestId').value;
            const status = document.getElementById('status').value;
            const passed = parseInt(document.getElementById('passed').value) || 0;
            const failed = parseInt(document.getElementById('failed').value) || 0;
            const total = parseInt(document.getElementById('total').value) || 0;
            const executionTime = parseInt(document.getElementById('executionTime').value) || 0;
            
            let details = [];
            try {
                const detailsText = document.getElementById('details').value;
                if (detailsText) {
                    details = JSON.parse(detailsText);
                }
            } catch (error) {
                showNotification('测试详情格式错误，请使用有效的JSON格式', 'error');
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/tests/${testId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        status,
                        results: {
                            passed,
                            failed,
                            total
                        },
                        details,
                        executionTime
                    })
                });
                
                if (response.ok) {
                    showNotification('测试更新成功！');
                    updateTestForm.reset();
                    loadTests();
                } else {
                    const error = await response.json();
                    showNotification(error.error, 'error');
                }
            } catch (error) {
                showNotification('更新测试失败: ' + error.message, 'error');
            }
        });
        
        // 删除测试
        deleteTestBtn.addEventListener('click', async () => {
            const testId = document.getElementById('updateTestId').value;
            
            if (!testId) {
                showNotification('请输入要删除的测试ID', 'error');
                return;
            }
            
            if (!confirm(`确定要删除测试ID为 ${testId} 的测试吗？`)) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE_URL}/tests/${testId}`, {
                    method: 'DELETE'
                });
                
                if (response.ok) {
                    showNotification('测试删除成功！');
                    updateTestForm.reset();
                    loadTests();
                } else {
                    const error = await response.json();
                    showNotification(error.error, 'error');
                }
            } catch (error) {
                showNotification('删除测试失败: ' + error.message, 'error');
            }
        });
        
        // 加载测试列表
        async function loadTests() {
            try {
                const response = await fetch(`${API_BASE_URL}/tests`);
                
                if (response.ok) {
                    const tests = await response.json();
                    displayTests(tests);
                } else {
                    const error = await response.json();
                    showNotification(error.error, 'error');
                }
            } catch (error) {
                showNotification('加载测试列表失败: ' + error.message, 'error');
            }
        }
        
        // 显示测试列表
        function displayTests(tests) {
            testList.innerHTML = '';
            
            if (tests.length === 0) {
                testList.innerHTML = '<p>暂无测试记录</p>';
                return;
            }
            
            tests.forEach(test => {
                const testItem = document.createElement('div');
                testItem.className = 'test-item';
                
                let statusClass = test.status;
                let statusText = '';
                
                switch (test.status) {
                    case 'pending':
                        statusText = '待处理';
                        break;
                    case 'running':
                        statusText = '运行中';
                        break;
                    case 'completed':
                        statusText = '已完成';
                        break;
                    case 'failed':
                        statusText = '失败';
                        break;
                }
                
                testItem.innerHTML = `
                    <h3>${test.testId} <span class="status ${statusClass}">${statusText}</span></h3>
                    <p>创建时间: ${new Date(test.timestamp).toLocaleString()}</p>
                    <p>执行时间: ${test.executionTime ? test.executionTime + ' 毫秒' : '未执行'}</p>
                    <p>测试结果: ${test.results.total} 个测试用例 (${test.results.passed} 通过, ${test.results.failed} 失败)</p>
                    <div class="test-details">
                        <h4>测试详情:</h4>
                        ${test.details && test.details.length > 0 ? `
                            <table>
                                <thead>
                                    <tr>
                                        <th