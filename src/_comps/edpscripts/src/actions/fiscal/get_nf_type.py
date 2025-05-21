import persistence

from msgbus import TK_SYS_ACK, FM_PARAM
from sysactions import action
from bustoken import TK_FISCALWRAPPER_GET_NF_TYPE
from .. import logger, mb_context


nf_type = None


@action
def get_nf_type(posid=0, *args):
    global nf_type
    if not nf_type:
        ret = mb_context.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_GET_NF_TYPE, format=FM_PARAM, data=None)
        # Processamento Finalizado com Sucesso
        if ret.token == TK_SYS_ACK:
            nf_type = ret.data.upper()
            # Populate taxes for combos
            if nf_type == "PAF":
                populate_combo_taxes()
    return nf_type


def populate_combo_taxes():
    BEGIN_TRANSACTION = ["BEGIN TRANSACTION", "UPDATE fiscalinfo.FiscalDEnabled SET Enabled=0"]
    COMMIT_TRANSACTION = ["UPDATE fiscalinfo.FiscalDEnabled SET Enabled=1", "COMMIT TRANSACTION"]

    query = """
        INSERT OR REPLACE INTO taxcalc.ProductTaxCategory(ItemId, TaxCgyId)
        SELECT PI.ItemId, V1.TaxCgyId
            FROM (
                SELECT P.ItemId, P.ProductCode, PTC.TaxCgyId
                FROM sysproddb.ProductItem P
                LEFT JOIN taxcalc.ProductTaxCategory PTC ON PTC.ItemId=P.ItemId
                WHERE P.RecursionLevel=1 AND PTC.TaxCgyId IS NOT NULL
            ) V1
        JOIN sysproddb.ProductItem PI ON PI.ProductCode=V1.ProductCode
        WHERE PI.RecursionLevel>1;
        INSERT OR REPLACE INTO fiscalinfo.FiscalProductCatalogChangesCounter SELECT * FROM productdb.ProductCatalogChangesCounter;

        DELETE FROM fiscalinfo.FiscalProductDB
        WHERE EXISTS (
            SELECT 1 FROM productdb.ProductCatalogChangesCounter A
            LEFT JOIN fiscalinfo.FiscalProductCatalogChangesCounter B
            WHERE A.ChangesCount!=COALESCE(B.ChangesCount,-1) OR A.ChangesDateTime!=COALESCE(B.ChangesDateTime,''));

        INSERT OR REPLACE INTO fiscalinfo.FiscalProductDB(ProductCode,ProductName,UnitPrice,TaxFiscalIndex,FiscalCategory,TaxRate,IAT,IPPT,MeasureUnit)
        SELECT ProductCode,ProductName,UnitPrice,TaxFiscalIndex,FiscalCategory,TaxRate,IAT,IPPT,MeasureUnit
        FROM
            (SELECT
                    Price.ProductCode AS ProductCode,
                    Product.ProductName AS ProductName,
                    Price.DefaultUnitPrice as UnitPrice,
                    TaxRule.TaxFiscalIndex AS TaxFiscalIndex,
                    TaxCategory.TaxCgyDescr AS FiscalCategory,
                    tdscale(TaxRule.TaxRate,2,0) AS TaxRate,
                    COALESCE(IAT.CustomParamValue,'T') AS IAT,
                    COALESCE(IPPT.CustomParamValue,'P') AS IPPT,
                    COALESCE(PKP.MeasureUnit,'UN') AS MeasureUnit
                FROM
                    Price Price
                LEFT JOIN taxcalc.ProductTaxCategory ProductTaxCategory
                    ON ProductTaxCategory.ItemId=(Price.Context || "." || Price.ProductCode)
                LEFT JOIN taxcalc.TaxCategory TaxCategory
                    ON TaxCategory.TaxCgyId=ProductTaxCategory.TaxCgyId
                LEFT JOIN taxcalc.TaxRule TaxRule
                    ON TaxRule.TaxCgyId=ProductTaxCategory.TaxCgyId
                LEFT JOIN Product
                    ON Price.ProductCode=Product.ProductCode
                LEFT JOIN productdb.ProductKernelParams PKP
                    ON PKP.ProductCode=Product.ProductCode
                LEFT JOIN productdb.ProductCustomParams IAT
                    ON IAT.ProductCode=Product.ProductCode AND IAT.CustomParamId='IAT'
                LEFT JOIN productdb.ProductCustomParams IPPT
                    ON IPPT.ProductCode=Product.ProductCode AND IPPT.CustomParamId='IPPT'
                WHERE CURRENT_TIMESTAMP BETWEEN Price.ValidFrom AND Price.ValidThru
            ) FiscalProductsView
        WHERE EXISTS (
            SELECT 1 FROM productdb.ProductCatalogChangesCounter A
            LEFT JOIN fiscalinfo.FiscalProductCatalogChangesCounter B
            WHERE A.ChangesCount!=COALESCE(B.ChangesCount,-1) OR A.ChangesDateTime!=COALESCE(B.ChangesDateTime,'')
        );

        INSERT INTO fiscalinfo.FiscalProductCatalogChangesCounter SELECT * FROM productdb.ProductCatalogChangesCounter;
    """

    queries = [query]
    conn = None
    try:
        conn = persistence.Driver().open(mb_context)
        queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
        conn.query("\0".join(queries))
    except Exception:
        logger.exception("ERRO CRIANDO FISCALINFO DATABASE INFORMATION")
    finally:
        if conn:
            conn.close()
