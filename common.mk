#
# Reset PATH and LD_LIBRARY_PATH as needed to use correct python distribution
#

MACHINE := $(shell uname -m)
OPSYS := $(shell uname -s)
BASEDIR := $(CURDIR)
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

$(info OS: $(OPSYS))
$(info Platform: $(MACHINE))
$(info Base directory: $(BASEDIR))

export PYTHONHOME := $(BASEDIR)/mwappsdk/$(OPSYS)-$(MACHINE)/python
export LD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(LD_LIBRARY_PATH)
export DYLD_LIBRARY_PATH := $(PYTHONHOME)/lib:$(DYLD_LIBRARY_PATH)
export PATH := $(PYTHONHOME):$(PYTHONHOME)/bin:$(PATH)

GENPYPKG := tools/genpypkg/genpypkg.py

define NL


endef

OUTPUT_PLATFORMS := \
	darwin-x86_64 \
	linux-redhat-x86_64 \
	linux-ubuntu-x86_64 \
	linux-ubuntu-i686 \
	windows-x86


#
# Configurable variables
#
COMMON_COMPONENTS_OBJS := \
	bkcuploader.pypkg \
	bkofficeuploader.pypkg \
	blacklist.pypkg \
	cappta.pypkg \
	chatcontroller.pypkg \
	dailygoals.pypkg \
	discount.pypkg \
	edpcommon.pypkg \
	fingerprintreadercomp.pypkg \
	fiscalwrapper.pypkg \
	kdsredirect.pypkg \
	kioskmediamgr.pypkg \
	maintenancecomp.pypkg \
	ntaxcalc.pypkg \
	pickupdisplay.pypkg \
	pigeoncomp.pypkg \
	price-interface-api.pypkg \
	remoteorder.pypkg \
	remoteorderapi.pypkg \
	ruptura.pypkg \
	sapiensuploader.pypkg \
	satcomp.pypkg \
	scanner.pypkg \
	sitef.pypkg \
	totemapi.pypkg \
	totemupdater.pypkg


#
# build rules
#

COMMON_COMPONENTS_OBJS := $(join $(addsuffix /,$(addprefix src/,$(basename $(COMMON_COMPONENTS_OBJS)))), $(COMMON_COMPONENTS_OBJS))

all: common-components
	$(info $@: Done!)

#
# Common Components build rules
#

common-components: $(COMMON_COMPONENTS_OBJS)
	$(foreach f,$^,$(foreach d,$(addsuffix /bin,$(OUTPUT_PLATFORMS)),cp "$(f)" "mwappsdk/$(d)"$(NL)))
	$(info $@: Done!)

src/bkcuploader/bkcuploader.pypkg: $(shell find src/bkcuploader -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/bkofficeuploader/bkofficeuploader.pypkg: $(shell find src/bkofficeuploader -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/blacklist/blacklist.pypkg: $(shell find src/blacklist -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/cappta/cappta.pypkg: $(shell find src/cappta -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) dll
	$(info $@: Done!)

src/chatcontroller/chatcontroller.pypkg: $(shell find src/chatcontroller -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/dailygoals/dailygoals.pypkg: $(shell find src/dailygoals -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/discount/discount.pypkg: $(shell find src/discount -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/edpcommon/edpcommon.pypkg: $(shell find src/edpcommon -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/fingerprintreadercomp/fingerprintreadercomp.pypkg: $(shell find src/fingerprintreadercomp -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) "x32;x64"
	$(info $@: Done!)

src/fiscalwrapper/fiscalwrapper.pypkg: $(shell find src/fiscalwrapper -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/kdsredirect/kdsredirect.pypkg: $(shell find src/kdsredirect -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/kioskmediamgr/kioskmediamgr.pypkg: $(shell find src/kioskmediamgr -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/maintenancecomp/maintenancecomp.pypkg: $(shell find src/maintenancecomp -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/ntaxcalc/ntaxcalc.pypkg: $(shell find src/ntaxcalc -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/pickupdisplay/pickupdisplay.pypkg: $(shell find src/pickupdisplay -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/pigeoncomp/pigeoncomp.pypkg: $(shell find src/pigeoncomp -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/price-interface-api/price-interface-api.pypkg: $(shell find src/price-interface-api -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/remoteorder/remoteorder.pypkg: $(shell find src/remoteorder -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/remoteorderapi/remoteorderapi.pypkg: $(shell find src/remoteorderapi -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/ruptura/ruptura.pypkg: $(shell find src/ruptura -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/sapiensuploader/sapiensuploader.pypkg: $(shell find src/sapiensuploader -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)

src/satcomp/satcomp.pypkg: $(shell find src/satcomp -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) dll
	$(info $@: Done!)

src/scanner/scanner.pypkg: $(shell find src/scanner -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/sitef/sitef.pypkg: $(shell find src/sitef -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/totemapi/totemapi.pypkg: $(shell find src/totemapi -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@) lib
	$(info $@: Done!)

src/totemupdater/totemupdater.pypkg: $(shell find src/totemupdater -name "*.py")
	PYTHONHOME=$(PYTHONHOME) python $(GENPYPKG) $(basename $(notdir $@)) $(dir $@) $(dir $@)
	$(info $@: Done!)


#
# Clean rule
#

clean:
	@rm -f $(COMMON_COMPONENTS_OBJS)
	$(foreach d,$(basename $(notdir $(COMMON_COMPONENTS_OBJS))),find src/$(d) -type f -iname "*.pyc" | xargs rm -f$(NL))
	$(foreach f,$(COMMON_COMPONENTS_OBJS),$(foreach d,$(addsuffix mwappsdk/bin,$(OUTPUT_PLATFORMS)),rm -f $(d)/$(f)$(NL)))
	$(info $@: Done!)

