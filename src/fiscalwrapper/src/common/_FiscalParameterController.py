from typing import Dict, Tuple, Optional


class FiscalParameterNotFound(Exception):
    def __init__(self, part_code, parameter_name):
        # type: (int, unicode) -> None
        super(FiscalParameterNotFound, self).__init__("FiscalParameterNotFound")
        self.part_code = part_code
        self.parameter_name = parameter_name

    def __str__(self):
        return "FiscalParameterNotFound: partCode: {0} - parameterName: {1}".format(self.part_code, self.parameter_name)


class FiscalParameterController(object):
    def __init__(self, fiscal_parameters):
        self.fiscal_parameters = fiscal_parameters  # type: Dict[Tuple[int, unicode],unicode]

    def get_optional_parameter(self, part_code, parameter_name):
        # type: (int, unicode) -> Optional[unicode]
        key = (part_code, parameter_name)
        if key not in self.fiscal_parameters:
            return None
        else:
            return self.fiscal_parameters[key]

    def get_parameter(self, part_code, parameter_name):
        # type: (int, unicode) -> unicode
        key = (part_code, parameter_name)
        if key not in self.fiscal_parameters:
            raise FiscalParameterNotFound(part_code, parameter_name)
        else:
            return self.fiscal_parameters[key]

    def has_parameter(self, part_code, parameter_name):
        # type: (int, unicode) -> bool
        key = (part_code, parameter_name)
        return key in self.fiscal_parameters

    def get_all_products_csts(self):
        # type: () -> unicode
        return str({(x, y): self.fiscal_parameters.get((x, y)) for x, y in self.fiscal_parameters if "CST" in y})

    def get_all_products_base_reductions(self):
        # type: () -> unicode
        return str({x: self.fiscal_parameters.get((x, "BASE_REDUCTION")) for x, y in self.fiscal_parameters})
