// 实现多边形碰撞检测
function checkPolygonCollision(ship, asteroid) {
  // 将飞船和陨石顶点转换为世界坐标
  const shipVertices = getWorldVertices(ship);
  const asteroidVertices = getWorldVertices(asteroid);
  
  // 使用SAT算法检测碰撞
  return satCollision(shipVertices, asteroidVertices);
}

function satCollision(poly1, poly2) {
  const polygons = [poly1, poly2];
  
  for (let p = 0; p < polygons.length; p++) {
    const polygon = polygons[p];
    
    for (let i = 0; i < polygon.length; i++) {
      const current = polygon[i];
      const next = polygon[(i + 1) % polygon.length];
      
      // 计算边的法线
      const edge = { x: next.x - current.x, y: next.y - current.y };
      const normal = { x: -edge.y, y: edge.x };
      
      // 投射两个多边形到法线上
      const proj1 = projectPolygon(poly1, normal);
      const proj2 = projectPolygon(poly2, normal);
      
      // 检查投影是否重叠
      if (proj1.max < proj2.min || proj2.max < proj1.min) {
        return false; // 找到分离轴，无碰撞
      }
    }
  }
  
  return true; // 没有找到分离轴，有碰撞
}