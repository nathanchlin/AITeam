function checkTankCollision(tank1, tank2) {
    const dx = tank1.x - tank2.x;
    const dy = tank1.y - tank2.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const minDistance = tank1.radius + tank2.radius;
    
    return distance < minDistance;
}