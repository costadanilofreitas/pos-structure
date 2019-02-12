SOURCE := src/*
COMPILED := dist/bundle.js dist/styles.css dist/index.html
OUTPUT := gui_pos_example.zip

.PHONY: all

all: $(OUTPUT)

$(COMPILED): $(SOURCE)
	npm run build

$(OUTPUT): $(COMPILED)
	python ../../../tools/genzip/genzip.py $(OUTPUT) dist

clean:
	$(RM) $(OUTPUT) $(COMPILED)
