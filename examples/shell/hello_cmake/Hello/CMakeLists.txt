add_library (Hello SHARED
  Speaker.h
  Speaker.cpp)

install (TARGETS Hello DESTINATION lib)
install (FILES Speaker.h DESTINATION include)
