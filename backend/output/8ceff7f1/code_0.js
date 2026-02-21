// 使用CSS 3D变换实现流畅的卡片翻转效果
.card {
  width: 100px;
  height: 100px;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.6s cubic-bezier(0.4, 0.0, 0.2, 1);
}

.card.flipped {
  transform: rotateY(180deg);
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.card-front {
  background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
  transform: rotateY(180deg);
}

.card-back {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
}