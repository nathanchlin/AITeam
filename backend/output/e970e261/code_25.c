// 精确像素级碰撞检测
int checkPixelPerfectCollision(Entity* a, Entity* b, unsigned char* aPixels, unsigned char* bPixels) {
    // 计算重叠区域
    int left = (a->x > b->x) ? a->x : b->x;
    int right = (a->x + a->width < b->x + b->width) ? a->x + a->width : b->x + b->width;
    int top = (a->y > b->y) ? a->y : b->y;
    int bottom = (a->y + a->height < b->y + b->height) ? a->y + a->height : b->y + b->height;
    
    // 检查重叠区域内的像素
    for (int y = top; y < bottom; y++) {
        for (int x = left; x < right; x++) {
            int aIndex = ((y - a->y) * a->width) + (x - a->x);
            int bIndex = ((y - b->y) * b->width) + (x - b->x);
            
            if (aPixels[aIndex] != 0 && bPixels[bIndex] != 0) {
                return 1; // 碰撞发生
            }
        }
    }
    
    return 0; // 无碰撞
}