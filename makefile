#
# Configurable variables
#

PACKAGE_PREFIX := client
STANDARD_DATA_DIR := mwdatas/data.client
STANDARD_COMMON_DIR := $(STANDARD_DATA_DIR)/server/common
STANDARD_COMMON_UI_OBJS :=  ui/gui_client_prep.zip ui/gui_client_sui.zip ui/gui_client_kiosk.zip ui/gui_client_pickup.zip
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
#

STANDARD_COMMON_UI_OBJS := $(addprefix $(STANDARD_COMMON_DIR)/,$(STANDARD_COMMON_UI_OBJS))


#
# Standard build
#
.PHONY: all

all: ddl-hash standard-common-ui-objs standard-common-objs apache-conf pos-comp
	$(info $@: Done!)

standard-common-ui-objs: $(STANDARD_COMMON_UI_OBJS)
	$(info $@: Done!)

$(STANDARD_COMMON_DIR)/ui/gui_client_prep.zip:
	cd $(BASEDIR)/src/gui/prep && $(MAKE) && mkdir -p $(BASEDIR)/$(dir $@) &&  mv $(notdir $@) $(BASEDIR)/$(dir $@)
	$(info $@: Done!)

$(STANDARD_COMMON_DIR)/ui/gui_client_sui.zip:
	cd $(BASEDIR)/src/gui/newgui && $(MAKE) && mkdir -p $(BASEDIR)/$(dir $@) &&  mv $(notdir $@) $(BASEDIR)/$(dir $@)
	$(info $@: Done!)

$(STANDARD_COMMON_DIR)/ui/gui_client_kiosk.zip: $(shell find $(BASEDIR)/src/gui/kiosk/src -type f -iname "*.js" -o -iname "*.json" -o -iname "*css" -o -iname "*.html")
	cd $(BASEDIR)/src/gui/kiosk && $(MAKE) && mkdir -p $(BASEDIR)/$(dir $@) &&  mv $(notdir $@) $(BASEDIR)/$(dir $@)

$(STANDARD_COMMON_DIR)/ui/gui_client_pickup.zip:
	cd $(BASEDIR)/src/gui/pickup && $(MAKE) && mkdir -p $(BASEDIR)/$(dir $@) &&  mv $(notdir $@) $(BASEDIR)/$(dir $@)
	$(info $@: Done!)

standard-common-objs:
	if [ -e $(BASEDIR)/src/common.mk ]; then \
		$(MAKE) -f $(BASEDIR)/src/common.mk; \
	fi
	$(info $@: Done!)


ddl-hash: $(DDL_FILES)
	echo $(DDLHASHSCRIPT) > ./ddlhash.py
	PYTHONHOME=$(PYTHONHOME)
	for f in $?; do \
	python ./ddlhash.py $$f > $$f.new; \
		cp $$f.new $$f; \
		rm $$f.new; \
	done
	rm -f ./ddlhash.py

apache-conf:
	if [ -d win.zip ]; then rm win.zip; fi
	curl -O http://nuget.e-deploy.com.br/apache/win.zip
	if [ -d components/apache ]; then rm -rf components/apache; fi
	mkdir components/apache
	unzip win.zip -d components/apache
	rm win.zip
	mv components/apache/Apache24/* components/apache
	rm -rf components/apache/Apache24
	curl -O http://nuget.e-deploy.com.br/apache/httpd.txt
	mv httpd.txt components/apache/conf/httpd.in
	rm components/apache/conf/httpd.conf
	sed 's,\\[\\[SRVROOT\\]\\],$(BASEDIR)/components/apache,g' components/apache/conf/httpd.in > components/apache/conf/httpd.conf
	sed -i 's,\\[\\[DOCUMENT_ROOT\\]\\],$(BASEDIR)/$(STANDARD_DATA_DIR)/server/htdocs,g' components/apache/conf/httpd.conf

pos-comp:
	if [ -e $(BASEDIR)/components/common.mk ]; then \
		$(MAKE) -f $(BASEDIR)/components/common.mk; \
	fi
	$(info $@: Done!)
#
# Clean rule
#

clean-common:
	if [ -e src/common.mk ]; then \
		$(MAKE) -f src/common.mk clean; \
	fi

clean: clean-common
	cd $(BASEDIR)/src/gui/prep && $(MAKE) clean
	cd $(BASEDIR)/src/gui/newgui && $(MAKE) clean
	cd $(BASEDIR)/src/gui/kiosk && $(MAKE) clean
	cd $(BASEDIR)/src/gui/pickup && $(MAKE) clean
	rm -rf $(dir $(STANDARD_COMMON_UI_OBJS))
