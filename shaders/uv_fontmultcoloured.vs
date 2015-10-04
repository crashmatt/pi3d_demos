precision mediump float;

attribute vec3 vertex;
attribute vec3 normal;
attribute vec2 texcoord;

uniform mat4 modelviewmatrix[2]; // [0] model movement in real coords, [1] in camera coords
uniform vec3 unib[4];
//uniform float ntiles => unib[0][0]
//uniform vec2 umult, vmult => unib[2]
//uniform vec2 u_off, v_off => unib[3]

varying float dist;
varying mat2 rotn;
varying vec2 corner;
varying vec4 colour;

void main(void) {
  dist = vertex[2];
  gl_Position = modelviewmatrix[1] * vec4(vertex,1.0);
  rotn = mat2(cos(normal[0]), sin(normal[0]),
             -sin(normal[0]), cos(normal[0])); 
  gl_PointSize = unib[2][2] * fract(dist);
  corner = texcoord;

  // alpha	= frac(normal[1])
  // red 	= normal[1]/256
  // green 	= frac(normal[2])
  // blue 	= normal[2]/256
  colour = vec4(normal[1]/256.0, fract(normal[2]), normal[2]/256.0, fract(normal[1]) );
}
