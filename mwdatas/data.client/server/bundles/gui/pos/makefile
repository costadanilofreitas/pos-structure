#
# Reset PATH and LD_LIBRARY_PATH as needed to use correct python distribution
#

MACHINE=$(shell uname -m)
OPSYS=$(shell uname -s)
BASEDIR=$(abspath $(CURDIR)/../../../../../../)

ifeq ($(OPSYS),Linux)
	OPSYS := linux
else ifeq ($(OPSYS),Darwin)
	OPSYS := darwin
else
	OPSYS := windows
	MACHINE := x86
endif

ifeq ($(OPSYS),linux)
ifneq ($(shell cat /etc/lsb-release | grep -i ubuntu),)
	OPSYS := linux-ubuntu
else
	OPSYS := linux-redhat
endif
endif

export PYTHONHOME := $(BASEDIR)/mwappsdk/$(OPSYS)-$(MACHINE)/python
export LD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(LD_LIBRARY_PATH)
export DYLD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(DYLD_LIBRARY_PATH)
export PATH := $(PYTHONHOME):$(PYTHONHOME)/bin:$(PATH)

GENZIP := $(BASEDIR)/tools/genzip/genzip.py
SOURCE := $(shell find ./src -type f -iname "*.js" -or -iname "*.html" -or -iname "*.css")
COMPILED := dist/bundle.js dist/styles.css dist/index.html
OUTPUT := gui_client_pos.zip

.PHONY: all

all: $(OUTPUT)

$(COMPILED): $(SOURCE)
	npm run build

$(OUTPUT): pre-build $(COMPILED)
	PYTHONHOME=$(PYTHONHOME) python $(GENZIP) $(OUTPUT) dist static

clean:
	$(RM) $(OUTPUT) $(COMPILED)
	rm -rf node_modules
	rm -rf $(HOME)/node_modules

pre-build:
	npm install

