# Interface for Python Interaction

The command _automate_run_ can be used to script board and 
compiler interaction in python. 


    Usage: automate-run [--core-opts] <subcommand> [--subcommand-opts] ...
     
    Core options:
     
      -d, --debug                        Enable debug output.
      -l [STRING], --list[=STRING]       List available tasks, optionally limited to a namespace.
      -V, --version                      Show version and exit.


The tasks provided by automate-run are defined in a file called _autofile.py_ . 
Which should be placed in the current working directory. 

Tasks are then defined using the _pyinvoke_ tasks syntax (http://docs.pyinvoke.org/en/stable/concepts/invoking-tasks.html). The only differences 
is, that tasks get handed in a [AutomateContext](#automate.context) object instead of pyinvokes contexts, this allows tasks to interact with the boards and compilers from 
the Metadata repository. 



## Examples 


## Run hello on All boards:

Put the following in _autofile.py_

    from invoke import task
          
    @task
    def say_hello(c):
        for board in c.boards():
            with board.connect() as con:
                con.run('echo "Hello from $(hostname)!"')

The command _echo "Hello from $(hostname)!"_ will be run on each board,
and return the corresponding return values.

To run use:
   
     $automate-run say-hello
	 
	 Hello from jetsonagx!
	 Hello from jetsontx2!
	 Hello from raspberrypi4b-jh1!
	 Hello from zynqberry!


## Access cross compiler information:

If one wants to see the default compiler flags for each compiler one could use:

    @task
    def compiler_info(c, board="", toolchain=""):
        board = c.board(board)
     
        for compiler in board.compilers(toolchain=toolchain):
            print("compiler:", compiler.name)
            print("  CC =", compiler.cc)
            print("  CFLAGS = ", compiler.cflags)
            print("  CXX =", compiler.cxx)
            print("  CXXFLAGS =", compiler.cxxflags)
            print("  LDFLAGS =", compiler.ldflags)
            print("  LDLIBS = ", compiler.libs)
            print("")

To run use: 


    $ automate-run compiler-info -b zynqberry -t gcc
    compiler: aarch32hf-gcc74
      CC = arm-linux-gnueabihf-gcc
      CFLAGS =  -mcpu=cortex-a9 --sysroot=/nfs/es-genial/schrank/boards/zynqberry/sysroot -O2
      CXX = arm-linux-gnueabihf-g++
      CXXFLAGS = -mcpu=cortex-a9 --sysroot=/nfs/es-genial/schrank/boards/zynqberry/sysroot -O2
      LDFLAGS = -mcpu=cortex-a9 --sysroot=/nfs/es-genial/schrank/boards/zynqberry/sysroot -O2
      LDLIBS = 
	  
# Further examples

  The examples from this tutorial and further more advanced examples are available 
  from the folder _examples/python/_ in this repository.
