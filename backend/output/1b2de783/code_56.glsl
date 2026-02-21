#version 330 core
layout (location = 0) in vec2 aPosition;
layout (location = 1) in vec4 aColor;
layout (location = 2) in float aSize;

out vec4 vColor;

uniform mat4 projection;

void main() {
    gl_Position = projection * vec4(aPosition, 0.0, 1.0);
    gl_PointSize = aSize;
    vColor = aColor;
}