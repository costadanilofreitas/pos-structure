from basereport import TableReport, ReportColumnDefinition, AlignTypes, SimpleReport
from report import Presenter, Part
from report.command import NewLineCommand, AlignCommand, RepeatCommand


class IFoodOrderPresenter(Presenter):
    def __init__(self, columns):
        self.columns = columns

        self.item_table_column_definitions = [
            ReportColumnDefinition(width=4),
            ReportColumnDefinition(width=self.columns - 15),
            ReportColumnDefinition(width=10)
        ]

        self.sub_item_table_column_definitions = [
            ReportColumnDefinition(width=7, align=AlignTypes.RIGHT, after_text=u" "),
            ReportColumnDefinition(width=self.columns - 7),
        ]

        self.total_table_column_definitions = [
            ReportColumnDefinition(width=20, align=AlignTypes.LEFT),
            ReportColumnDefinition(width=self.columns - 20, align=AlignTypes.RIGHT)
        ]

        self.order = None
        self.report = None

    def present(self, dto):

        self.order = dto

        parts = []
        parts.extend(self.build_header())
        parts.extend(self.build_customer_data())
        parts.extend(self.build_items_header())
        parts.extend(self.build_items())
        parts.extend(self.build_totals_payments())
        parts.extend(self.build_localize())
        parts.extend(self.build_merchandise())

        return SimpleReport(parts, self.columns)

    def build_header(self):
        return [
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(u"$STORE", [AlignCommand(AlignCommand.Alignment.center)]),
            Part(u": {}".format(self.order[u"merchant"][u"name"]), [AlignCommand(AlignCommand.Alignment.center)]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(u"$ORDER", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": #{}".format(self.order[u"shortReference"]), [AlignCommand(AlignCommand.Alignment.left)]),
            Part(None, [NewLineCommand()]),
            Part(u"$DATE", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": #DATETIME({})".format(
                self.order[u"preparationStartDateTime"]
            ), [AlignCommand(AlignCommand.Alignment.left)]),
            Part(None, [NewLineCommand()]),
            Part(u"$ESTIMATED_DELIVERY_TIME", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": #DATETIME({})".format(self.order[u"deliveryDateTime"]), [
                AlignCommand(AlignCommand.Alignment.left)
            ]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
        ]

    def build_customer_data(self):
        customer = [
            Part(u"$CUSTOMER_DATA", [AlignCommand(AlignCommand.Alignment.center)]),
            Part(None, [NewLineCommand()]),
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
            Part(u"$NAME", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": {}".format(self.order[u"customer"][u"name"]), [AlignCommand(AlignCommand.Alignment.left)]),
            Part(None, [NewLineCommand()])
        ]

        if u"customer" in self.order and u"taxPayerIdentificationNumber" in self.order[u"customer"]:
            customer.extend([
                Part(u"$CPF", [AlignCommand(AlignCommand.Alignment.left)]),
                Part(u": {}".format(self.order[u"customer"][u"taxPayerIdentificationNumber"]), [
                    AlignCommand(AlignCommand.Alignment.left),
                ]),
                Part(None, [NewLineCommand()])
            ])
        else:
            customer.extend([
                Part(u"$CPF", [AlignCommand(AlignCommand.Alignment.left)]),
                Part(u": $NOT_INFORMED", [
                    AlignCommand(AlignCommand.Alignment.left),
                ]),
                Part(None, [NewLineCommand()])
            ])

        if "localizer" in self.order:
            customer.append(Part(u"$PHONE", [AlignCommand(AlignCommand.Alignment.left)]))
            customer.append(
                Part(u": 0800 007 0110 ID: {}".format(self.order[u"localizer"][u"id"]), [
                    AlignCommand(AlignCommand.Alignment.left)
                ]))
            customer.append(Part(None, [NewLineCommand()]))

        customer.append(Part(u"$ADDRESS", [AlignCommand(AlignCommand.Alignment.left)]))
        customer.append(
            Part(u": {}".format(self.order[u"deliveryAddress"][u"formattedAddress"]), [
                AlignCommand(AlignCommand.Alignment.left)
            ]))
        customer.append(Part(None, [NewLineCommand()]))

        if "complement" in self.order["deliveryAddress"]:
            customer.append(Part(u"$COMPLEMENT", [AlignCommand(AlignCommand.Alignment.left)]))
            customer.append(
                Part(u": {}".format(self.order[u"deliveryAddress"][u"complement"]), [
                    AlignCommand(AlignCommand.Alignment.left),
                ]))
            customer.append(Part(None, [NewLineCommand()]))

        if "reference" in self.order["deliveryAddress"]:
            customer.append(Part(u"$ADDRESS_REFERENCE", [AlignCommand(AlignCommand.Alignment.left)]))
            customer.append(
                Part(u": {}".format(self.order[u"deliveryAddress"][u"reference"]), [
                    AlignCommand(AlignCommand.Alignment.left),
                ]))
            customer.append(Part(None, [NewLineCommand()]))

        customer.extend([
            Part(u"$NEIGHBORHOOD", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": {}".format(self.order[u"deliveryAddress"][u"neighborhood"]), [
                AlignCommand(AlignCommand.Alignment.left)
            ]),
            Part(None, [NewLineCommand()]),
            Part(u"$CITY", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": {}".format(self.order[u"deliveryAddress"][u"city"]), [AlignCommand(AlignCommand.Alignment.left)]),
            Part(None, [NewLineCommand()]),
            Part(u"$ZIP_CODE", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(u": {}".format(self.order[u"deliveryAddress"][u"postalCode"]), [
                AlignCommand(AlignCommand.Alignment.left)
            ]),
            Part(None, [NewLineCommand()]),
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
        ])

        return customer

    def build_items_header(self):
        return [
            Part(None, [RepeatCommand(self.columns, u"#"), NewLineCommand()]),
            TableReport([[u"$QTD", u"$DESCRIPTION", u"$VALUE"]], self.item_table_column_definitions),
            Part(None, [RepeatCommand(self.columns, u"#"), NewLineCommand()])
        ]

    def build_items(self):
        items = []
        for item in self.order[u"items"]:
            item_line = [str(item[u"quantity"]), item[u"name"], self.get_price(item)]
            items.append(TableReport([item_line], self.item_table_column_definitions))
            if u"observations" in item and item[u"observations"] is not None and item[u"observations"] != "":
                items.extend([Part(u"       " + item[u"observations"]), Part(None, [NewLineCommand()])])
            if u"subItems" in item:
                for sub_item in item[u"subItems"]:
                    qty = ""
                    if sub_item[u"quantity"] > 1:
                        qty = str(sub_item[u"quantity"])
                    sub_item_line = [qty, sub_item[u"name"]]
                    items.append(TableReport([sub_item_line], self.sub_item_table_column_definitions))

        items.append(Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]))

        return items

    def build_totals_payments(self):
        totals = [
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
        ]

        total_values = [
            [u"$SUBTOTAL", u"#CURRENCY({})".format(self.order[u"subTotal"])],
            [u"$DELIVERY_FEE", u"#CURRENCY({})".format(self.order[u"deliveryFee"])]
        ]
        total_value = float(self.order[u"totalPrice"])
        if "benefits" in self.order:
            total_discount = 0
            for benefit in self.order["benefits"]:
                if "sponsorshipValues" in benefit:
                    values = benefit["sponsorshipValues"]
                    if "MERCHANT" in values and float(values["MERCHANT"]) > 0:
                        total_discount += float(values["MERCHANT"])
                    if "IFOOD" in values and float(values["IFOOD"]) > 0:
                        total_discount += float(values["IFOOD"])
            if total_discount > 0:
                total_values.append([u"$DISCOUNT", u"#CURRENCY({})".format(total_discount)])
                total_value -= total_discount
        totals_table = TableReport(total_values, self.total_table_column_definitions)

        totals.extend([
            totals_table,
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
            TableReport([
                [u"$TOTAL", u"#CURRENCY({})".format(total_value)],
            ], self.total_table_column_definitions),
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()])
        ])
        total_to_pay = total_value
        payments = []
        external_payment = False
        for payment in self.order["payments"]:
            if payment["prepaid"]:
                total_to_pay = 0.0
                description = u"$PREPAID_ORDER"
            else:
                external_payment = True
                description = payment["name"]
            payments.extend([Part(description, [AlignCommand(AlignCommand.Alignment.left)]),
                             Part(None, [NewLineCommand()]),
                             Part(None, [NewLineCommand()])])
            if payment["code"] == "DIN":
                if "changeFor" in payment:
                    change = float(payment["changeFor"] - float(total_to_pay))
                    if change >0:
                        payments.extend([Part(u"$CHANGE_NEEDED : ", [AlignCommand(AlignCommand.Alignment.left)]),
                                         Part(u"#CURRENCY({})".format(change), [NewLineCommand()]),
                                         Part(None, [NewLineCommand()]),
                                         Part(None, [NewLineCommand()])])
            elif external_payment:
                payments.extend([Part(u"$EXTERNAL_POS", [AlignCommand(AlignCommand.Alignment.left)]),
                                 Part(None, [NewLineCommand()]),
                                 Part(None, [NewLineCommand()])])

        totals.extend([
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            TableReport([
                [u"$TOTAL_TO_PAY", u"#CURRENCY({})".format(total_to_pay)],
            ], self.total_table_column_definitions),
            Part(None, [NewLineCommand()]),
            Part(None, [RepeatCommand(self.columns, "-"), NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
        ])
        totals.extend([
            Part(u"$PAYMENT", []),
            Part(u":", [AlignCommand(AlignCommand.Alignment.left)]),
            Part(None, [NewLineCommand()]),
        ])
        totals.extend(payments),

        return totals

    def build_localize(self):
        localizer = []
        if "localizer" in self.order:
            localizer = [
                Part(None, [NewLineCommand()]),
                Part(u"$IFOOD_LOCALIZER_TEXT", [AlignCommand(AlignCommand.Alignment.left)]),
                Part(None, [NewLineCommand()]),
                Part(u"$LOCALIZER : {}".format(self.order[u"localizer"][u"id"]), [
                    AlignCommand(AlignCommand.Alignment.left)]),
                Part(None, [NewLineCommand()])
            ]
        return localizer

    def build_merchandise(self):
        return [
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(u"$BRAND", [
                AlignCommand(AlignCommand.Alignment.left),
                NewLineCommand()
            ]),
            Part(u"$SITE", [
                AlignCommand(AlignCommand.Alignment.left),
                NewLineCommand()
            ]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
            Part(None, [NewLineCommand()]),
        ]

    def get_price(self, item):
        if item["totalPrice"] > 0:
            return u"#CURRENCY({})".format(item["quantity"] * item["totalPrice"])
        else:
            return ""
