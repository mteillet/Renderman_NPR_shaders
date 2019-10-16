# SE Expressions

An Se Expression is a node which mixes patterns, textures, shapes, normals and vectors
No need to compile before use
But slow compared to OSL or C++

Initially developped by Disney, for an internal paint program

Based on Disney Animations's open source SeExpr system, giving a scriptable pattern generator and combiner node


# References

https://rmanwiki.pixar.com/display/REN/PxrSeExpr+Quick+Reference
https://www.disneyanimation.com/technology/seexpr.html




# Examples

# You can reference the 8 inputs of the SeExpression by referencing to them as follows
res = floatInput1;
res

# It is possible to plug textures/procedurals into the color inputs of the SeExpression nodes and refer to them later
res = colorInput1;
res

# It is also possible to load textures through the SeExpression Node directly, although it is of limited use

# Cell noise from SeExpression node. From surface point position (P) - red = X - green = Y - blue = Z (here generated from camera space)
# You would need to modify the floatInput1 value in order to scale the noise by changing how the cvoronoi function would read the surface point position data
# The norm function normalizes the luminance from what is generated
res = P;
res = cvoronoi(P*floatInput1)*2-1 ;
res = res*floatInput2;
res = norm(res);
res

# By defaut, the P will generate the function, and is in camera space - meaning it won't stick to the object
#   use instead Pobj
res = P;
res = cvoronoi(Pobj*floatInput1)*2-1 ;
res = res*floatInput2;
res = norm(res);
res


# Classic noise generation
# The value should oscillate around 0.5 luminance
res = noise(P*freq)
res

# Remapped noise
# The mid value is offsetted according to the new variable (here -0.5)
res = noise(P*freq) - 0.5
res

# Stretching/scaling the noise
# The mid value is extended / shrinked  according to the new variable (here 2)
res = noise(P*freq) * 2
res

# Possible to do both at the same time
res = noise(P*freq) * 2 - 1
res

# Remapped and mapped to object space cVoronoi example
![](/.imgs/SeExpr_cVoronoi_001.JPG)