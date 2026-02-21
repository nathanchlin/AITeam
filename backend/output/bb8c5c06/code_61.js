checkSelfCollision() {
    const head = this.body[0];
    for (let i = 1; i < this.body.length; i++) {
        if (head.x === this.body[i].x && head.y === this.body[i].y) {
            return true;
        }
    }
    return false;
}