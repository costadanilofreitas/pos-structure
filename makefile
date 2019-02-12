#
# Configurable variables
#

PACKAGE_PREFIX := client
STANDARD_DATA_DIR := mwdatas/data.client
STANDARD_BOH_DATA_DIR := mwdatas/data.mwboh
STANDARD_COMMON_DIR := $(STANDARD_DATA_DIR)/server/common
STANDARD_COMMON_OBJS :=
STANDARD_COMMON_UI_OBJS := ui/gui_client_pos.zip
DDL_FILES := $(STANDARD_DATA_DIR)/server/bundles/persistcomp/normal/i18ncustom.ddl
# OUTPUT_PLATFORMS := darwin-x86_64 linux-redhat-x86_64 linux-ubuntu-i686 linux-ubuntu-x86_64 windows-x86
OUTPUT_PLATFORMS := linux-redhat-x86_64 windows-x86

FLAKE_EXCLUDED_PATHS := \
	$(STANDARD_BOH_DATA_DIR)/server/bundles/dashboard/python/pygal/* \
	$(STANDARD_DATA_DIR)/server/lib/* \
	$(STANDARD_DATA_DIR)/server/bundles/reports/lib/* \
	$(STANDARD_DATA_DIR)/server/bundles/pyscripts/dev_lib/* \
	$(STANDARD_DATA_DIR)/server/bundles/pyscripts/tests/* \
	$(STANDARD_DATA_DIR)/server/bundles/reports/tests/* \
	$(STANDARD_DATA_DIR)/server/bundles/reports/python/lib/* \
	$(STANDARD_DATA_DIR)/server/bundles/pyscripts/python/lib/* \
	$(STANDARD_DATA_DIR)/server/bundles/fiscalwrapper/python/lib/* \
	$(STANDARD_DATA_DIR)/* \
	src/fiscalwrapper/lib/* \
	src/bkcuploader/lib/* \
	src/chatcontroller/lib/* \
	src/fiscalwrapper/lib/* \
	src/pickupdisplay/lib/* \
	src/pigeoncomp/lib/* \
	src/price-interface-api/lib/* \
	src/remoteorder/lib/* \
	src/remoteorderapi/lib/* \
	src/scanner/lib/* \
	src/totemapi/lib/* \
	src/edpcommon/dateutil/* \
	src/edpcommon/iso8601/* \
	wmappsdk/tools/flake8/*

ifndef BUILD_VERSION
	BUILD_VERSION := $(shell date +"%Y%m")
endif

ifndef BUILD_NUMBER
	BUILD_NUMBER := $(CI_PIPELINE_ID)
endif

#
# Reset PATH and LD_LIBRARY_PATH as needed to use correct python distribution
#

MACHINE=$(shell uname -m)
OPSYS=$(shell uname -s)
BASEDIR=$(CURDIR)
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

export PYTHONHOME := $(BASEDIR)/wmappsdk/$(OPSYS)-$(MACHINE)/python
export LD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(LD_LIBRARY_PATH)
export DYLD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(DYLD_LIBRARY_PATH)
export PATH := $(PYTHONHOME):$(PYTHONHOME)/bin:$(PATH)

GENPYPKG := mwappsdk/tools/genpypkg/genpypkg.py

FLAKE_OUT_DIR := .flake
FLAKE_EXCLUDES := $(foreach notpath,$(FLAKE_EXCLUDED_PATHS),-not -path "$(notpath)")
FLAKE_PY_FILES := $(shell find mwdatas $(FLAKE_EXCLUDES) -name "*.py")
FLAKE_PY_FILES := $(FLAKE_PY_FILES) $(shell find src/edpcommon $(FLAKE_EXCLUDES) -name "*.py")
FLAKE_PY_FILES := $(FLAKE_PY_FILES) $(shell find mwappsdk/tools $(FLAKE_EXCLUDES) -name "*.py")
FLAKE_APP_FILES := $(addprefix $(FLAKE_OUT_DIR)/, $(FLAKE_PY_FILES:.py=.flake))
FLAKE := echo
DUMMY := $(shell test -d $(FLAKE_OUT_DIR) || mkdir -p $(FLAKE_OUT_DIR))

DDLHASHSCRIPT := "import sys, re, hashlib; a=re.compile(r'CREATE\s+TABLE\s+schema_version.*Revision;',re.S|re.I).split(open(sys.argv[1], 'r').read()); h=(hashlib.sha1(a[-1]).hexdigest() if len(a)>1 else ''); print re.sub('\0134\044Revision:\s*[a-z:A-Z0-9]*\s*\0134\044', '\044Revision: '+h+'\044', open(sys.argv[1], 'r').read()),;"

BUILD_EXCLUSIONS := $(shell find . -name "cef*" && find . -name "libcef*" && find . -name "libQt*" && find . -name "Qt*.dll")
BUILD_EXCLUSIONS := $(subst ./,,$(BUILD_EXCLUSIONS))
TMPDIR := $(shell mktemp -d)
BUILDDIR := $(CURDIR)

$(info Temporary dir: $(TMPDIR))
$(info Build dir: $(BUILDDIR))


#
# build rules
#

STANDARD_COMMON_OBJS := $(addprefix $(STANDARD_COMMON_DIR)/,$(STANDARD_COMMON_OBJS))
STANDARD_COMMON_UI_OBJS := $(addprefix $(STANDARD_COMMON_DIR)/,$(STANDARD_COMMON_UI_OBJS))

DATA_POS_EXCLUSIONS :=

ifdef NOLOADERS
	DATA_POS_EXCLUSIONS := $(DATA_POS_EXCLUSIONS) -not -name "*.cfg"
endif

define NL


endef

GENESIS_DATA_POS_FILES := $(shell find $(STANDARD_DATA_DIR) -type f -not -name "*.git*" -not -name "*.md" -not -name "*.log" -not -name "*.pyc" -not -name "product.db" -not -name "users.db" -not -path "mwdatas/data.vanilla/server/lib/*" $(DATA_POS_EXCLUSIONS) | sed 's: :\\ :g')
GENESIS_DATA_BOH_FILES := $(shell find $(STANDARD_BOH_DATA_DIR)/server -type f -not -name "*.git*" -not -name "*.md" -not -name "*.log" -not -name "*.pyc")

all: $(FLAKE_APP_FILES) ddl-hash standard-common-objs standard-common-ui-objs
	@rm -rf $(TMPDIR)
	$(info $@: Done!)

genesis-packages: data-genesis-package binary-genesis-package
	@rm -rf $(TMPDIR)
	@rm -f manifest.xml
	$(info $@: Done!)

data-genesis-package: $(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_data.genpkg
	$(info $@: Done!)

$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_data.genpkg: manifest.xml data-genesis-pos data-genesis-boh data-config-adjustments
	cd $(TMPDIR) && \
	tar -cvf $(BUILDDIR)/genesis.tar * && \
	cd $(BUILDDIR) && \
	rm -rf $(TMPDIR) && \
	zip $@ genesis.tar manifest.xml && \
	rm -f genesis.tar

data-genesis-pos: $(GENESIS_DATA_POS_FILES)
	@mkdir -p $(TMPDIR)/data
	@rm -f $(TMPDIR)/data/tmp.tar
	@touch $(TMPDIR)/data/tmp.tar
	$(foreach f,$(patsubst $(STANDARD_DATA_DIR)/%,%,$^),cd $(STANDARD_DATA_DIR) && tar rvf $(TMPDIR)/data/tmp.tar "$(f)"$(NL))
	@cd $(TMPDIR)/data && tar xvf tmp.tar && rm -f tmp.tar

data-genesis-boh: $(GENESIS_DATA_BOH_FILES)
	mkdir -p $(TMPDIR)/data/bohserver
	cd $(STANDARD_BOH_DATA_DIR)/server && rsync -Ravzh --delete $(patsubst $(STANDARD_BOH_DATA_DIR)/server/%,./%,$^) $(TMPDIR)/data/bohserver

data-config-adjustments:
ifndef NOLOADERS
#	sed -i -- "s/..\/..\/src\/posui\/gui_pos.zip/..\/data\/common\/ui\/gui_pos.zip/g" $(TMPDIR)/data/server/bundles/apachecomp/loader.cfg
#	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/escpos-danfe-printer/loader.cfg
#	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/fiscalwrapper/loader.cfg
	sed -i -- "s/>..\/..\/mwdatas\/data.client\//>..\/data\//g" $(TMPDIR)/data/server/bundles/fiscalwrapper/loader.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/peripherals/loader_fiscal_printer_ecf.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/peripherals/loader_printer_virtual_printer1.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/peripherals/loader_printer_virtual_printerpl-1.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/peripherals/loader_printer_virtual_printerpl-2.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_1.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_2.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_3.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_4.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_5.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_9.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_10.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/sitef/loader_11.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/hvmon/loader.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/server/bundles/reports/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/auditlogger/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/mwcentral/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/remotesupport/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/wshubclient/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/genserver/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/autoupd/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/bohpump/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/server/bundles/mwboh/loader.cfg
	sed -i -- "s/>7777</>7890</g" $(TMPDIR)/data/server/bundles/loader.cfg
	sed -i -- "s/>225.200.24.139</>225.99.9.97</g" $(TMPDIR)/data/server/bundles/loader.cfg
	sed -i -- "s/>true</>false</g" $(TMPDIR)/data/server/bundles/loader.cfg
	sed -i -- "s/>7788</>7890</g" $(TMPDIR)/data/bohserver/bundles/loader.cfg
	sed -i -- "s/>225.0.0.1</>225.99.9.97</g" $(TMPDIR)/data/bohserver/bundles/loader.cfg
	sed -i -- "s/>true</>false</g" $(TMPDIR)/data/bohserver/bundles/loader.cfg
	sed -i -- "s/>automatic</>manual</g" $(TMPDIR)/data/bohserver/bundles/hvmon/loader.cfg
	sed -i -- "s/>automatic</>disabled</g" $(TMPDIR)/data/bohserver/bundles/pgsqlcomp/loader.cfg
	sed -i -- "s/>manual</>automatic</g" $(TMPDIR)/data/bohserver/bundles/pgsqlcomp/loader_local.cfg
else
	$(info No loaders to cdjust. Continuing ...)
endif


binary-genesis-package: $(addsuffix .genpkg,$(addprefix $(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_,$(OUTPUT_PLATFORMS)))
	$(info $@: Done!)


#
# Function: build_genesis_tar(platform, binaries, type: [bin, apache, python, pgsql], op: [c: create, r: append])
#
define build_genesis_tar
	@echo -e '$(addsuffix \n,$(2))' > filelst.tmp
	tail -c +3 filelst.tmp | xargs tar --transform s@$(1)/$(3)@$(3)/$(1)@g -$(4)vf genesis.tar
endef


manifest.xml: TIMESTAMP=$(shell date +"%Y%m%d%H%M%S")
manifest.xml:
	@echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<GenesisPackage version=\"1.0\" type=\"update\" timestamp=\"$(TIMESTAMP)\" newVersion=\"$(BUILD_VERSION)-$(BUILD_NUMBER)\">\n       <Description lang=\"en\">Commit SHA=$(CI_COMMIT_SHA); Pipeline=$(CI_PIPELINE_ID)</Description>\n</GenesisPackage>" > manifest.xml

# darwin-x86_64
APACHE_DARWIN_x86_64 := $(shell find -L mwappsdk/darwin-x86_64/apache -type f)
PGSQL_DARWIN_x86_64 := $(shell find -L mwappsdk/darwin-x86_64/pgsql -type f)
PYTHON_DARWIN_x86_64 := $(shell find -L mwappsdk/darwin-x86_64/python -type f -not -name "*.pyc")
BINARY_DARWIN_x86_64 := $(shell find -L mwappsdk/darwin-x86_64/bin -type f)
pgsql_darwin-x86_64: $(PGSQL_DARWIN_x86_64)
python_darwin-x86_64: $(PYTHON_DARWIN_x86_64)
apache_darwin-x86_64: $(APACHE_DARWIN_x86_64)
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_darwin-x86_64.genpkg: MARCH=darwin-x86_64
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_darwin-x86_64.genpkg: manifest.xml $(BINARY_DARWIN_x86_64) apache_darwin-x86_64 python_darwin-x86_64 pgsql_darwin-x86_64
	$(call build_genesis_tar,$(MARCH),$(filter-out manifest.xml $(BUILD_EXCLUSIONS) pgsql% python% apache% %.a %.lib,$^),bin,c)
	$(call build_genesis_tar,$(MARCH),$(APACHE_DARWIN_x86_64),apache,r)
	$(call build_genesis_tar,$(MARCH),$(PYTHON_DARWIN_x86_64),python,r)
	$(call build_genesis_tar,$(MARCH),$(PGSQL_DARWIN_x86_64),pgsql,r)
	zip $@ genesis.tar manifest.xml && rm -f genesis.tar filelst.tmp

# linux-redhat-x86_64
APACHE_REDHAT_x86_64 := $(shell find -L mwappsdk/linux-redhat-x86_64/apache -type f)
PGSQL_REDHAT_x86_64 := $(shell find -L mwappsdk/linux-redhat-x86_64/pgsql -type f)
PYTHON_REDHAT_x86_64 := $(shell find -L mwappsdk/linux-redhat-x86_64/python -type f -not -name "*.pyc")
BINARY_REDHAT_x86_64 := $(shell find -L mwappsdk/linux-redhat-x86_64/bin -type f)
pgsql_linux-redhat-x86_64: $(PGSQL_REDHAT_x86_64)
python_linux-redhat-x86_64: $(PYTHON_REDHAT_x86_64)
apache_linux-redhat-x86_64: $(APACHE_REDHAT_x86_64)
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_linux-redhat-x86_64.genpkg: MARCH=linux-redhat-x86_64
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_linux-redhat-x86_64.genpkg: manifest.xml $(BINARY_REDHAT_x86_64) apache_linux-redhat-x86_64 python_linux-redhat-x86_64 pgsql_linux-redhat-x86_64
	$(call build_genesis_tar,$(MARCH),$(filter-out manifest.xml $(BUILD_EXCLUSIONS) pgsql% python% apache% %.a %.lib,$^),bin,c)
	$(call build_genesis_tar,$(MARCH),$(APACHE_REDHAT_x86_64),apache,r)
	$(call build_genesis_tar,$(MARCH),$(PYTHON_REDHAT_x86_64),python,r)
	$(call build_genesis_tar,$(MARCH),$(PGSQL_REDHAT_x86_64),pgsql,r)
	zip $@ genesis.tar manifest.xml && rm -f genesis.tar filelst.tmp

# linux-ubuntu-x86_64
APACHE_UBUNTU_x86_64 := $(shell find -L mwappsdk/linux-ubuntu-x86_64/apache -type f)
PGSQL_UBUNTU_x86_64 := $(shell find -L mwappsdk/linux-ubuntu-x86_64/pgsql -type f)
PYTHON_UBUNTU_x86_64 := $(shell find -L mwappsdk/linux-ubuntu-x86_64/python -type f -not -name "*.pyc")
BINARY_UBUNTU_x86_64 := $(shell find -L mwappsdk/linux-ubuntu-x86_64/bin -type f)
pgsql_linux-ubuntu-x86_64: $(PGSQL_UBUNTU_x86_64)
python_linux-ubuntu-x86_64: $(PYTHON_UBUNTU_x86_64)
apache_linux-ubuntu-x86_64: $(APACHE_UBUNTU_x86_64)
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_linux-ubuntu-x86_64.genpkg: MARCH=linux-ubuntu-x86_64
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_linux-ubuntu-x86_64.genpkg: manifest.xml $(BINARY_UBUNTU_x86_64) apache_linux-ubuntu-x86_64 python_linux-ubuntu-x86_64 pgsql_linux-ubuntu-x86_64
	$(call build_genesis_tar,$(MARCH),$(filter-out manifest.xml $(BUILD_EXCLUSIONS) pgsql% python% apache% %.a %.lib,$^),bin,c)
	$(call build_genesis_tar,$(MARCH),$(APACHE_UBUNTU_x86_64),apache,r)
	$(call build_genesis_tar,$(MARCH),$(PYTHON_UBUNTU_x86_64),python,r)
	$(call build_genesis_tar,$(MARCH),$(PGSQL_UBUNTU_x86_64),pgsql,r)
	zip $@ genesis.tar manifest.xml && rm -f genesis.tar filelst.tmp

# linux-ubuntu-i686
APACHE_UBUNTU_i686 := $(shell find -L mwappsdk/linux-ubuntu-i686/apache -type f)
PGSQL_UBUNTU_i686 := $(shell find -L mwappsdk/linux-ubuntu-i686/pgsql -type f)
PYTHON_UBUNTU_i686 := $(shell find -L mwappsdk/linux-ubuntu-i686/python -type f -not -name "*.pyc")
BINARY_UBUNTU_i686 := $(shell find -L mwappsdk/linux-ubuntu-i686/bin -type f)
pgsql_linux-ubuntu-i686: $(PGSQL_UBUNTU_i686)
python_linux-ubuntu-i686: $(PYTHON_UBUNTU_i686)
apache_linux-ubuntu-i686: $(APACHE_UBUNTU_i686)
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_linux-ubuntu-i686.genpkg: MARCH=linux-ubuntu-i686
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_linux-ubuntu-i686.genpkg: manifest.xml $(BINARY_UBUNTU_i686) apache_linux-ubuntu-i686 python_linux-ubuntu-i686 pgsql_linux-ubuntu-i686
	$(call build_genesis_tar,$(MARCH),$(filter-out manifest.xml $(BUILD_EXCLUSIONS) pgsql% python% apache% %.a %.lib,$^),bin,c)
	$(call build_genesis_tar,$(MARCH),$(APACHE_UBUNTU_i686),apache,r)
	$(call build_genesis_tar,$(MARCH),$(PYTHON_UBUNTU_i686),python,r)
	$(call build_genesis_tar,$(MARCH),$(PGSQL_UBUNTU_i686),pgsql,r)
	zip $@ genesis.tar manifest.xml && rm -f genesis.tar filelst.tmp

# windows-x86
APACHE_WINDOWS_x86 := $(shell find -L mwappsdk/windows-x86/apache -type f)
# PGSQL_WINDOWS_x86 := $(shell find -L mwappsdk/windows-x86/pgsql -type f)
PYTHON_WINDOWS_x86 := $(shell find -L mwappsdk/windows-x86/python -type f -not -name "*.pyc")
BINARY_WINDOWS_x86 := $(shell find -L mwappsdk/windows-x86/bin -type f)
pgsql_windows-x86: $(PGSQL_WINDOWS_x86)
python_windows-x86: $(PYTHON_WINDOWS_x86)
apache_windows-x86: $(APACHE_WINDOWS_x86)
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_windows-x86.genpkg: MARCH=windows-x86
$(PACKAGE_PREFIX)_$(BUILD_VERSION)_$(BUILD_NUMBER)_windows-x86.genpkg: manifest.xml $(BINARY_WINDOWS_x86) apache_windows-x86 python_windows-x86 pgsql_windows-x86
	$(call build_genesis_tar,$(MARCH),$(filter-out manifest.xml $(BUILD_EXCLUSIONS) pgsql% python% apache% %.a %.lib,$^),bin,c)
	$(call build_genesis_tar,$(MARCH),$(APACHE_WINDOWS_x86),apache,r)
	$(call build_genesis_tar,$(MARCH),$(PYTHON_WINDOWS_x86),python,r)
#	$(call build_genesis_tar,$(MARCH),$(PGSQL_WINDOWS_x86),pgsql,r)
	zip $@ genesis.tar manifest.xml && rm -f genesis.tar filelst.tmp


#
# Standard build
#

standard-common-objs: $(STANDARD_COMMON_OBJS)
	if [ -e common.mk ]; then \
		$(MAKE) -f common.mk; \
	fi
	$(info $@: Done!)

standard-common-ui-objs: $(STANDARD_COMMON_UI_OBJS)
	$(info $@: Done!)
	
$(STANDARD_COMMON_DIR)/ui/gui_client_pos.zip: $(shell find $(STANDARD_DATA_DIR)/server/bundles/gui/pos/src -type f -iname "*.js" -o -iname "*.json" -o -iname "*css" -o -iname "*.html")
	cd $(STANDARD_DATA_DIR)/server/bundles/gui/pos && $(MAKE) && mkdir -p ../../../$(dir $@) &&  mv $(notdir $@) ../../../../../../$(dir $@)

$(FLAKE_APP_FILES): $(FLAKE_OUT_DIR)/%.flake: %.py
	test -d $(dir $@) || mkdir -p $(dir $@)
	$(FLAKE) --ignore=E501,E127,E128,E241,E731,W601 $< && touch $@

ddl-hash: $(DDL_FILES)
	echo $(DDLHASHSCRIPT) > ./ddlhash.py
	for f in $?; do\
		python ./ddlhash.py $$f > $$f.new; \
		cp $$f.new $$f; \
		rm $$f.new; \
	done
	rm -f ./ddlhash.py


#
# Clean rule
#

clean-common:
	if [ -e common.mk ]; then \
		$(MAKE) -f common.mk clean; \
	fi

clean: clean-common
	rm -rf $(TMPDIR)
	rm -f manifest.xml
	rm -f genesis.tar
	cd $(STANDARD_DATA_DIR)/server/bundles/gui/pos && $(MAKE) clean
	rm -rf $(FLAKE_OUT_DIR)
	rm -rf $(dir $(STANDARD_COMMON_OBJS))
	rm -rf $(dir $(STANDARD_COMMON_UI_OBJS))
	rm -f $(PACKAGE_PREFIX)_*.genpkg
