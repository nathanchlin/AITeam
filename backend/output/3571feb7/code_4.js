class Entity {
  constructor(x, y) {
    this.id = Entity.generateId();
    this.x = x;
    this.y = y;
    this.width = 0;
    this.height = 0;
    this.rotation = 0;
    this.visible = true;
    this.components = new Map();
  }

  static generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  // 添加组件
  addComponent(component) {
    component.entity = this;
    this.components.set(component.constructor.name, component);
    return this;
  }

  // 获取组件
  getComponent(componentName) {
    return this.components.get(componentName);
  }

  // 移除组件
  removeComponent(componentName) {
    this.components.delete(componentName);
  }

  // 更新所有组件
  update(deltaTime) {
    for (const component of this.components.values()) {
      if (component.update) {
        component.update(deltaTime);
      }
    }
  }
}