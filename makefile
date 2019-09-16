#
# Configurable variables
#
PACKAGE_PREFIX := client
STANDARD_DATA_DIR := mwdatas/data.client
STANDARD_COMMON_DIR := $(STANDARD_DATA_DIR)/server/common
STANDARD_COMMON_UI_OBJS := ui/gui_client_prep.zip ui/gui_client_sui.zip ui/gui_client_kiosk.zip ui/gui_client_pickup.zip
DDL_FILES := $(STANDARD_DATA_DIR)/server/bundles/persistcomp/tblservice/tblservice.ddl
DDLHASHSCRIPT := "import sys, re, hashlib; a=re.compile(r'CREATE\s+TABLE\s+schema_version.*Revision;',re.S|re.I).split(open(sys.argv[1], 'r').read()); h=(hashlib.sha1(a[-1]).hexdigest() if len(a)>1 else ''); print re.sub('\0134\044Revision:\s*[a-z:A-Z0-9]*\s*\0134\044', '\044Revision: '+h+'\044', open(sys.argv[1], 'r').read()),;"
# OUTPUT_PLATFORMS := darwin-x86_64 linux-redhat-x86_64 linux-ubuntu-i686 linux-ubuntu-x86_64 windows-x86
OUTPUT_PLATFORMS := linux-redhat-x86_64 windows-x86

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
	MAKE := $(BASEDIR)/mwsdk/tools/windows-x86/make.exe
endif
ifeq ($(OPSYS),linux)
ifneq ($(shell cat /etc/lsb-release | grep -i ubuntu),)
	OPSYS := linux-ubuntu
else
	OPSYS := linux-redhat
endif
endif

export PYTHONHOME := $(BASEDIR)/mwsdk/$(OPSYS)-$(MACHINE)/python
export LD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(LD_LIBRARY_PATH)
export DYLD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(DYLD_LIBRARY_PATH)
export PATH := $(PYTHONHOME):$(PYTHONHOME)/bin:$(PATH)

GENPYPKG := mwsdk/tools/genpypkg/genpypkg.py

#
# build rules
.PHONY: all

all: ddl-hash common-comp pos-comp apache-conf
	$(info $@: Done!)

common-comp:
	if [ -e $(BASEDIR)/src/common.mk ]; then \
		cd src && $(MAKE) -f $(BASEDIR)/src/common.mk && cd -; \
	fi
	$(info $@: Done!)

pos-comp:
	if [ -e $(BASEDIR)/components/common.mk ]; then \
		cd components && $(MAKE) -f common.mk && cd -; \
	fi
	$(info $@: Done!)

ddl-hash: $(DDL_FILES)
	@echo $(DDLHASHSCRIPT) > ./ddlhash.py
	@PYTHONHOME=$(PYTHONHOME)
	for f in $?; do \
	python ./ddlhash.py $$f > $$f.new; \
		cp $$f.new $$f; \
		rm $$f.new; \
	done
	rm -f ./ddlhash.p
	$(info $@: Done!)

apache-conf:
	@if [ -d win.zip ]; then rm win.zip; fi
	curl -s -O http://nuget.e-deploy.com.br/apache/win.zip
	@if [ -d components/apache ]; then rm -rf components/apache; fi
	@mkdir components/apache
	unzip -q win.zip -d components/apache
	@mv components/apache/Apache24/* components/apache
	@rm -rf components/apache/Apache24
	curl -s -O http://nuget.e-deploy.com.br/apache/httpd.txt
	@mv httpd.txt components/apache/conf/httpd.in
	@rm components/apache/conf/httpd.conf
	sed 's,\\[\\[SRVROOT\\]\\],$(BASEDIR)/components/apache,g' components/apache/conf/httpd.in > components/apache/conf/httpd.conf
	sed -i 's,\\[\\[DOCUMENT_ROOT\\]\\],$(BASEDIR)/$(STANDARD_DATA_DIR)/server/htdocs,g' components/apache/conf/httpd.conf
	$(info $@: Done!)

#
# Clean rule
#
clean-common:
	if [ -e src/common.mk ]; then \
		cd src && $(MAKE) -f $(BASEDIR)/src/common.mk clean && cd -; \
	fi
	$(info $@: Done!)

clean-pos-comp:
	if [ -e $(BASEDIR)/components/common.mk ]; then \
		cd components && $(MAKE) -f common.mk clean && cd -; \
	fi
	$(info $@: Done!)

clean-apache:
	if [ -d win.zip ]; then rm win.zip; fi
	if [ -d components/apache ]; then rm -rf components/apache; fi
	$(info $@: Done!)

clean: clean-common clean-pos-comp clean-apache
	@rm -rf $(dir $(STANDARD_COMMON_UI_OBJS))
	$(info $@: Done!)
