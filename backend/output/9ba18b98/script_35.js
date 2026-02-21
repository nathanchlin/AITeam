const resources = {};

function preloadResources() {
  const tetrominoImages = ['I', 'O', 'T', 'S', 'Z', 'J', 'L'];
  tetrominoImages.forEach(type => {
    const img = new Image();
    img.src = `assets/${type}.png`;
    resources[type] = img;
  });
}