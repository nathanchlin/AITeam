class LODManager {
  constructor() {
    this.models = [];
  }

  addModel(modelName, distances, models) {
    this.models.push({ name: modelName, distances, models });
  }

  getModelForDistance(distance) {
    for (let i = 0; i < this.models.length; i++) {
      if (distance < this.models[i].distances[i]) {
        return this.models[i].models[i];
      }
    }
    return this.models[this.models.length - 1].models[this.models.length - 1];
  }
}