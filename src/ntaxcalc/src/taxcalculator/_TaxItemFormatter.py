from pos_model import TaxItem, SaleItem


class TaxItemFormatter(object):
    pattern = "<TaxItem lineNumber=\"{line_number}\" " \
              "level=\"{level}\" " \
              "itemId=\"{item_id}\" " \
              "partCode=\"{part_code}\" " \
              "taxRuleId=\"{tax_rule_id}\" " \
              "taxName=\"{tax_name}\" " \
              "taxIndex=\"{tax_index}\" " \
              "baseAmountBD=\"{base_ammount_bd}\" " \
              "taxAmountBD=\"{tax_ammount_bd}\" " \
              "baseAmountAD=\"{base_ammount_ad}\" " \
              "taxAmountAD=\"{tax_ammount_ad}\" " \
              "taxIncluded=\"{tax_included}\" " \
              "taxRate=\"{tax_rate}\"/>"

    def __init__(self):
        return

    def format_tax_item(self, tax_item, sale_item):
        # type: (TaxItem, SaleItem) -> str
        if tax_item is None:
            raise ValueError("tax_item cannot be None")

        return self.pattern.format(line_number=sale_item.line_number,
                                   level=sale_item.level,
                                   item_id=sale_item.item_id,
                                   part_code=sale_item.part_code,
                                   tax_rule_id=tax_item.tax_rule_id,
                                   tax_name=tax_item.tax_name,
                                   tax_index=tax_item.tax_name + "|" + tax_item.tax_index,
                                   base_ammount_bd=tax_item.base_amount_bd,
                                   tax_ammount_bd=tax_item.tax_amount_bd,
                                   base_ammount_ad=tax_item.base_amount_ad,
                                   tax_ammount_ad=tax_item.tax_amount_ad,
                                   tax_included=tax_item.tax_included,
                                   tax_rate=tax_item.tax_rate)
