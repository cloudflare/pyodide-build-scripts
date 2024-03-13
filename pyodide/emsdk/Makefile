PYODIDE_ROOT=$(abspath ..)
include ../Makefile.envs

all: emsdk/.complete

emsdk/.complete: ../Makefile.envs $(wildcard patches/*.patch)
	if [ -d emsdk ]; then rm -rf emsdk; fi
	git clone --depth 1 https://github.com/emscripten-core/emsdk.git
	cd emsdk && ./emsdk install --build=Release $(PYODIDE_EMSCRIPTEN_VERSION)
	cd emsdk/upstream/emscripten/ && cat ../../../patches/*.patch | patch -p1 --verbose
	cd emsdk && ./emsdk activate --embedded --build=Release $(PYODIDE_EMSCRIPTEN_VERSION)

	touch emsdk/.complete


update_struct_info:
	rm -f ../src/js/generated_struct_info32.json
	cd ../src/js && wget "https://raw.githubusercontent.com/emscripten-core/emscripten/$(PYODIDE_EMSCRIPTEN_VERSION)/src/generated_struct_info32.json"


clean:
	rm -rf emsdk
