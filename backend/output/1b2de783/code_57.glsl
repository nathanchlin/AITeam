#version 330 core
in vec4 vColor;

out vec4 FragColor;

void main() {
    vec2 coord = gl_PointCoord - vec2(0.5);
    if (length(coord) > 0.5) {
        discard;
    }
    
    float alpha = 1.0 - length(coord) * 2.0;
    FragColor = vec4(vColor.rgb, vColor.a * alpha);
}