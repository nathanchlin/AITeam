// 碰撞检测测试用例
void testCollisionDetection() {
    Player player;
    Platform platform(100, 300, 200, 20);
    
    // 测试站在平台上
    player.setPosition(150, 280);
    auto collision = checkAABBCollisionWithDirection(player.getBoundingBox(), platform.getBoundingBox());
    assert(collision.bottom);
    
    // 测试从上方撞到平台
    player.setPosition(150, 200);
    collision = checkAABBCollisionWithDirection(player.getBoundingBox(), platform.getBoundingBox());
    assert(collision.top);
    
    // 测试侧面碰撞
    player.setPosition(50, 320);
    collision = checkAABBCollisionWithDirection(player.getBoundingBox(), platform.getBoundingBox());
    assert(collision.right);
}