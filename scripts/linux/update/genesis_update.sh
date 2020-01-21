#!/bin/bash
cd mwpos_server
cd genesis
if [ -d data ]; then
  rm -rf data
fi
mkdir data
cd data
cp -r ../../../../pos-structure/mwdatas/data.client/* .
cd server/databases
# rm discountcalc.db
# rm fiscal_params.db
# rm ntaxcalc.db
# rm product.db
# rm taxcalc.db
cd ../../../../data/databases
if [ -f i18ncustom.db ];then
  rm i18ncustom.db
fi
