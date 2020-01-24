# Configurable variables
STANDARD_DATA_DIR := ../datas/data.client
STANDARD_COMMON_DIR := $(STANDARD_DATA_DIR)/server/common
STANDARD_COMMON_UI_OBJS := ui/gui_client_prep.zip ui/gui_client_sui.zip ui/gui_client_kiosk.zip ui/gui_client_pickup.zip
OUTPUT_PLATFORMS := linux-redhat-x86_64 windows-x86

MACHINE=$(shell uname -m)
OPSYS=$(shell uname -s)
BASEDIR=$(CURDIR)/..
ifeq ($(OPSYS),Linux)
	OPSYS := linux-redhat
else
	OPSYS := windows
	MACHINE := x86
	MAKE := $(CURDIR)/tools/make.exe
endif

# Build Rules
.PHONY: all

all: sdkcore common-comp apache-conf
	$(info $@: Done!)

sdkcore:
	python -m pip install mwsdk==2.0.84 -t ../ --extra-index-url=http://mwsdk.hmledp.com.br/ --trusted-host mwsdk.hmledp.com.br

common-comp:
	if [ -e $(BASEDIR)/src/common.mk ]; then \
		cd ../src && $(MAKE) -f $(BASEDIR)/src/common.mk && cd -; \
	fi
	$(info $@: Done!)

ifeq ($(OPSYS),windows)
apache-conf:
	@if [ -d win.zip ]; then rm win.ip; fi
	curl -LO -o win.zip https://s3.amazonaws.com/pos-install.e-deploy.com.br/httpd-2.4.41-win64-VS16.zip
	@if [ -d $(BASEDIR)/apache ]; then rm -rf $(BASEDIR)/apache; fi
	@mkdir $(BASEDIR)/apache
	@rm -rf temp
	unzip -q win.zip -d temp
	@mv temp/Apache24/* $(BASEDIR)/apache
	@rm -rf temp
	sed -i.bak 's,^\(Define SRVROOT \)".*",\1"$(BASEDIR)/apache",g' $(BASEDIR)/apache/conf/httpd.conf
	sed -i.bak 's,^\(DocumentRoot \)".*htdocs",\1"$(BASEDIR)/datas/server/htdocs",g' $(BASEDIR)/apache/conf/httpd.conf
	sed -i.bak 's,^\(<Directory \)".*htdocs"\(>\),\1"$(BASEDIR)/datas/server/htdocs"\2,g' $(BASEDIR)/apache/conf/httpd.conf
	sed -i.bak 's,^\(Listen \).*,\18080,g' $(BASEDIR)/apache/conf/httpd.conf
	sed -i.bak 's,^#\(LoadModule proxy_module modules/mod_proxy.so\),\1,g' $(BASEDIR)/apache/conf/httpd.conf
	sed -i.bak 's,^#\(LoadModule proxy_http_module modules/mod_proxy_http.so\),\1,g' $(BASEDIR)/apache/conf/httpd.conf
	sed -i.bak 's,^\(<Directory \/>\),ProxyTimeout 60000000\nProxyPreserveHost On\nProxyPass /mwapp http://127.0.0.1:9494/mwapp\nProxyPassReverse /mwapp http://127.0.0.1:9494/mwapp\n\n\1,g' $(BASEDIR)/apache/conf/httpd.conf
else
apache-conf:
endif
	$(info $@: Done!)

# Clean Rules
clean-common:
	if [ -e src/common.mk ]; then \
		cd ../src && $(MAKE) -f $(BASEDIR)/src/common.mk clean && cd -; \
	fi
	$(info $@: Done!)

clean-apache:
	if [ -d httpd-2.4.41-win64-VS16.zip.zip ]; then rm httpd-2.4.41-win64-VS16.zip.zip; fi
	if [ -d $(BASEDIR)/apache ]; then rm -rf $(BASEDIR)/apache; fi
	$(info $@: Done!)

clean: clean-common clean-apache
	@rm -rf $(dir $(STANDARD_COMMON_UI_OBJS))
	$(info $@: Done!)
