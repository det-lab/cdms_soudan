KSY_FILE = scdms_soudan.ksy
BUILD_DIR = build
OUTPUT_FILE = soudan.cpp

all: $(OUTPUT_FILE)

$(OUTPUT_FILE): $(KSY_FILE)
	ksc -t awkward $(KSY_FILE)
	awkward-kaitai-build -b $(BUILD_DIR) $(OUTPUT_FILE)

clean:
	rm -rf $(BUILD_DIR) $(OUTPUT_FILE)