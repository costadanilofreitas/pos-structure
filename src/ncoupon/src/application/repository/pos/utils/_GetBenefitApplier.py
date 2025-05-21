import json
from logging import Logger
from xml.etree import cElementTree as eTree

from application.model import DefaultBenefitApplierRepository, BenefitAppliers
from application.model.customexception import BenefitApplierNotFound
from typing import Optional, Dict, List

BENEFIT_APPLIERS_REPOSITORIES = None  # type: Optional[Dict[BenefitAppliers: DefaultBenefitApplierRepository]]


def find_benefit_applier(pos_id, voucher_id):
    # type: (int, str) -> BenefitAppliers
    
    for benefit_applier in sorted(BENEFIT_APPLIERS_REPOSITORIES, reverse=True):
        if BENEFIT_APPLIERS_REPOSITORIES[benefit_applier].check_voucher(pos_id, voucher_id):
            return benefit_applier

    raise BenefitApplierNotFound("NDISCOUNT_BENEFIT_NOT_FOUND")


def find_benefit_id_by_custom_property(order_picture):
    # type: (eTree) -> Optional[str]

    for benefit_applier in BENEFIT_APPLIERS_REPOSITORIES:
        benefit_id = BENEFIT_APPLIERS_REPOSITORIES[benefit_applier].get_benefit_id_by_custom_property(order_picture)
        if benefit_id:
            return benefit_applier, benefit_id


def find_order_benefits_id(logger, order_picture, validate_voided_lines=False):
    # type: (Logger, eTree, Optional[bool]) -> Optional[List[str]]

    order_id = order_picture.get("orderId")
    logger.info("Finding order benefits to orderId: {}".format(order_id))

    order_benefits_id = []
    try:
        benefit_prop = order_picture.find(".//OrderProperty[@key='BENEFIT_LIST']")
        if benefit_prop is None:
            return order_benefits_id

        voided_sale_lines = _get_removed_sale_lines(order_picture)

        applied_benefits = json.loads(benefit_prop.get("value", ""))

        for applied_benefit in applied_benefits:
            if validate_voided_lines:
                added_sale_lines = applied_benefit.get("added_sale_lines")
                has_voided_sale_lines = [sale_line for sale_line in added_sale_lines if sale_line in voided_sale_lines]

                if not has_voided_sale_lines:
                    continue

            benefit = json.loads(applied_benefit.get("benefit"))
            benefit_id = str(benefit.get("id"))
            if benefit_id not in order_benefits_id:
                order_benefits_id.append(benefit_id)

        return order_benefits_id
    finally:
        logger.info("Found [{}] benefits on orderId: {}".format(len(order_benefits_id), order_id))


def _get_removed_sale_lines(order_picture):
    # type: (eTree) -> List

    sale_lines = order_picture.findall(".//SaleLine")
    removed_sale_lines = []
    for sale_line in sale_lines:
        if sale_line.get("level") == "0" and sale_line.get("qty") == "0":
            removed_sale_lines.append(int(sale_line.get("lineNumber")))

    return removed_sale_lines


def fill_benefit_appliers_repositories(benefit_appliers_repositories):
    # type: (Dict[BenefitAppliers: DefaultBenefitApplierRepository]) -> None

    global BENEFIT_APPLIERS_REPOSITORIES

    BENEFIT_APPLIERS_REPOSITORIES = benefit_appliers_repositories


def get_originator_id(order_picture):
    # type: (eTree) -> int
    
    return int(order_picture.get("originatorId").split("POS")[-1])


def replace_pos_id_by_originator_id(logger, pos_id, order_picture):
    # type: (Logger, int, eTree) -> int
    
    originator_pos_id = get_originator_id(order_picture)
    if originator_pos_id != pos_id:
        logger.info("Replacing PosID by OriginatorID")
        return originator_pos_id
    return pos_id
