/**
 * 碰撞检测系统
 */
class CollisionDetector {
    /**
     * 检测两个矩形是否碰撞
     * @param {Object} rect1 - 第一个矩形 {x, y, width, height}
     * @param {Object} rect2 - 第二个矩形 {x, y, width, height}
     * @returns {boolean} 是否碰撞
     */
    static checkRectCollision(rect1, rect2) {
        return rect1.x < rect2.x + rect2.width &&
               rect1.x + rect1.width > rect2.x &&
               rect1.y < rect2.y + rect2.height &&
               rect1.y + rect1.height > rect2.y;
    }
    
    /**
     * 检测两个圆形是否碰撞
     * @param {Object} circle1 - 第一个圆形 {x, y, radius}
     * @param {Object} circle2 - 第二个圆形 {x, y, radius}
     * @returns {boolean} 是否碰撞
     */
    static checkCircleCollision(circle1, circle2) {
        const dx = circle1.x - circle2.x;
        const dy = circle1.y - circle2.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        return distance < circle1.radius + circle2.radius;
    }
    
    /**
     * 检测矩形和圆形是否碰撞
     * @param {Object} rect - 矩形 {x, y, width, height}
     * @param {Object} circle - 圆形 {x, y, radius}
     * @returns {boolean} 是否碰撞
     */
    static checkRectCircleCollision(rect, circle) {
        // 找到矩形上离圆心最近的点
        let closestX = Math.max(rect.x, Math.min(circle.x, rect.x + rect.width));
        let closestY = Math.max(rect.y, Math.min(circle.y, rect.y + rect.height));
        
        // 计算该点到圆心的距离
        const dx = circle.x - closestX;
        const dy = circle.y - closestY;
        const distance = Math.sqrt(dx * dx + dy * dy);
        
        return distance < circle.radius;
    }
    
    /**
     * 使用分离轴定理(SAT)检测两个凸多边形是否碰撞
     * @param {Array} poly1 - 第一个多边形顶点数组 [{x, y}, ...]
     * @param {Array} poly2 - 第二个多边形顶点数组 [{x, y}, ...]
     * @returns {boolean} 是否碰撞
     */
    static checkPolygonCollision(poly1, poly2) {
        const polygons = [poly1, poly2];
        
        for (let p = 0; p < polygons.length; p++) {
            const polygon = polygons[p];
            
            for (let i = 0; i < polygon.length; i++) {
                const currentPoint = polygon[i];
                const nextPoint = polygon[(i + 1) % polygon.length];
                
                // 计算边的法向量
                const edge = {
                    x: nextPoint.x - currentPoint.x,
                    y: nextPoint.y - currentPoint.y
                };
                const normal = { x: -edge.y, y: edge.x };
                
                // 投影两个多边形到法向量上
                let min1 = Infinity, max1 = -Infinity;
                let min2 = Infinity, max2 = -Infinity;
                
                for (const point of poly1) {
                    const projected = point.x * normal.x + point.y * normal.y;
                    min1 = Math.min(min1, projected);
                    max1 = Math.max(max1, projected);
                }
                
                for (const point of poly2) {
                    const projected = point.x * normal.x + point.y * normal.y;
                    min2 = Math.min(min2, projected);
                    max2 = Math.max(max2, projected);
                }
                
                // 检查投影是否重叠
                if (max1 < min2 || max2 < min1) {
                    return false;
                }
            }
        }
        
        return true;
    }
}