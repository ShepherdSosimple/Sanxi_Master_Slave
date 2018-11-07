from ctypes import *

type_p_int = POINTER(c_int)
v = c_int(4)
p_int = type_p_int(v)
print(type(p_int))

print(p_int[0])
print('p_int[0]类型', type(p_int[0]))

print(p_int.contents)
print('p_int.contents类型为', type(p_int.contents))

# # -------
# p_int = pointer(v)
# print
# type(p_int)
# print
# p_int[0]
# print
# p_int.contents