SOURCE := src/*
COMPILED := build/index.html build/manifest.json build/service-worker.js build/static
OUTPUT := pickupdisplayui.zip

.PHONY: all build

all: $(OUTPUT)

$(COMPILED): $(SOURCE) node_modules build

build:
	npm run build

node_modules:
	npm install

$(OUTPUT): $(COMPILED)
	python ../../../../../tools/genzip/genzip.py $(OUTPUT) build

clean:
	rm -rf build
	rm -rf node_modules
	rm -rf $(HOME)/node_modules

