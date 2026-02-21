const foodElement = document.createElement('div');
foodElement.className = 'food';
foodElement.style.left = `${food.x * CELL_SIZE}px`;
foodElement.style.top = `${food.y * CELL_SIZE}px`;
foodElement.style.width = `${CELL_SIZE - 5}px`;
foodElement.style.height = `${CELL_SIZE - 5}px`;
gameBoard.appendChild(foodElement);