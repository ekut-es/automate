all: hello

hello: hello.o
	$(CXX) $(LDFLAGS) -o $@ $+ $(LDLIBS)

.PHONY: clean
clean:
	rm -f hello
	rm -f *.o
