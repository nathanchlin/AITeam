// 脏矩形渲染示例
const dirtyRegions = [];

function markDirty(x, y, width, height) {
  dirtyRegions.push({x, y, width, height});
}

function render() {
  dirtyRegions.forEach(region => {
    mainCtx.clearRect(region.x, region.y, region.width, region.height);
    drawGameRegion(region.x, region.y, region.width, region.height);
  });
  dirtyRegions.length = 0; // 清空脏区域列表
}