// 按需加载游戏模块
function loadGameModule(moduleName) {
    return import(`./js/${moduleName}.js`);
}