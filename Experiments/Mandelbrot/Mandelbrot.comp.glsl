#version 450
#extension GL_ARB_separate_shader_objects : enable

#define WIDTH 512
#define HEIGHT 512
#define DEPTH 512
#define WORKGROUP_SIZE 8
layout (local_size_x = WORKGROUP_SIZE, local_size_y = WORKGROUP_SIZE, local_size_z = WORKGROUP_SIZE ) in;

struct Pixel{
  vec4 value;
};

layout(std140, binding = 0) buffer buf
{
   Pixel imageData[];
};

void main() {

  /*
  In order to fit the work into workgroups, some unnecessary threads are launched.
  We terminate those threads here.
  */
  if(gl_GlobalInvocationID.x >= WIDTH
      || gl_GlobalInvocationID.y >= HEIGHT
      || gl_GlobalInvocationID.z >= DEPTH) {
    return;
  }

  float x = float(gl_GlobalInvocationID.x) / float(WIDTH);
  float y = float(gl_GlobalInvocationID.y) / float(HEIGHT);
  float zoom = 2. * float(1 + gl_GlobalInvocationID.z) / float(DEPTH);

  // What follows is code for rendering the mandelbrot set.
  vec2 uv = zoom * vec2(x,y);
  float n = 0.0;
  vec2 c = vec2(-.445, 0.0) +  (uv - 0.5)*(2.0+ 1.7*0.2  ),
  z = vec2(0.0);
  const int M =128;
  for (int i = 0; i<M; i++)
  {
    z = vec2(z.x*z.x - z.y*z.y, 2.*z.x*z.y) + c;
    if (dot(z, z) > 2) break;
    n++;
  }

  // store the rendered mandelbrot set into a storage buffer:
  uint offset = HEIGHT * WIDTH * gl_GlobalInvocationID.z
                       + WIDTH * gl_GlobalInvocationID.y
                               + gl_GlobalInvocationID.x;
  imageData[offset].value = vec4(n);
}
