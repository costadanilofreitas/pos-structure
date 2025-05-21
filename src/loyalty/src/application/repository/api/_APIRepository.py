import requests
from application.model.configuration import Configurations
from application.model.customexception import NotFound, ResponseError, ValidationError
from helper import json_serialize, retry
from typing import Optional


class APIRepository(object):

    def __init__(self, configs):
        # type: (Configurations) -> None

        self.logger = configs.logger
        self.configs = configs

    def retrieve_loyalty_customer_info(self, loyalty_customer_id):
        # type: (str) -> Optional[str]

        url = self._get_customer_url(loyalty_customer_id)
        headers = self._get_headers()
        errors_status_code = []

        response = retry(
                logger=self.logger,
                method_name="retrieve_loyalty_customer_info",
                n=1,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("GET", url=url, headers=headers, timeout=5),
                is_success=lambda resp: resp.status_code == 200,
                success=lambda resp: resp,
                failed=lambda resp: errors_status_code.append((resp.status_code, resp))
        )

        if response:
            return response.content
        else:
            if not errors_status_code:
                raise NotFound()

            last_received_error = errors_status_code[-1]
            last_error_status_code = last_received_error[0]
            response = last_received_error[1]
            self.logger.error("Error retrieving loyalty id: {}".format(json_serialize(response)))

            if last_error_status_code == 404:
                raise NotFound()
            elif last_error_status_code == 422:
                raise ValidationError()

    def retrieve_benefit(self, pos_id, voucher_id):
        # type: (int, str) -> Optional[str]

        url = self._get_benefit_url(voucher_id)
        headers = self._get_headers()
        params = {"posId": pos_id, "storeId": self.configs.store_id}
        errors_status_code = []

        response = retry(
                logger=self.logger,
                method_name="retrieve_benefit",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("PUT", url=url, headers=headers, params=params, timeout=5),
                is_success=lambda resp: resp.status_code == 200,
                success=lambda resp: resp,
                failed=lambda resp: errors_status_code.append((resp.status_code, resp))
        )

        if response:
            return response.content
        else:
            if not errors_status_code:
                raise NotFound()

            last_received_error = errors_status_code[-1]
            error_response = last_received_error[1]

            if error_response.status_code == 404:
                raise NotFound()

            raise ResponseError(self.logger, error_response)

    def burn_benefit(self, benefit_id):
        # type: (str) -> None

        url = self._get_burn_url(benefit_id)
        headers = self._get_headers()
        errors_status_code = []

        response = retry(
                logger=self.logger,
                method_name="burn_benefit",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("PUT", url=url, headers=headers, timeout=5),
                is_success=lambda resp: resp.status_code == 204,
                success=lambda resp: resp,
                failed=lambda resp: errors_status_code.append((resp.status_code, resp))
        )

        if response:
            return response.content
        else:
            if not errors_status_code:
                raise NotFound()

            last_received_error = errors_status_code[-1]
            error_response = last_received_error[1]

            if error_response.status_code == 404:
                raise NotFound()

            raise ResponseError(self.logger, error_response)

    def unlock_benefit(self, benefit_id):
        # type: (str) -> None

        url = self._get_unlock_url(benefit_id)
        headers = self._get_headers()
        errors_status_code = []

        response = retry(
                logger=self.logger,
                method_name="unlock_benefit",
                n=3,
                sleep_seconds=5,
                trying_to_do=lambda: requests.request("PUT", url=url, headers=headers, timeout=5),
                is_success=lambda resp: resp.status_code == 204,
                success=lambda resp: resp,
                failed=lambda resp: errors_status_code.append((resp.status_code, resp))
        )

        if response:
            return response.content
        else:
            if not errors_status_code:
                raise NotFound()

            last_received_error = errors_status_code[-1]
            error_response = last_received_error[1]

            if error_response.status_code == 404:
                raise NotFound()

            raise ResponseError(self.logger, error_response)
    
    def _get_customer_url(self, loyalty_customer_id):
        # type: (str) -> str

        end_point_url = self.configs.endpoints.retrieve_loyalty_customer_info.format(customerId=loyalty_customer_id)
        return self.configs.base_url + end_point_url
    
    def _get_benefit_url(self, voucher_id):
        # type: (str) -> str

        end_point_url = self.configs.endpoints.retrieve_benefit.format(voucherId=voucher_id)
        return self.configs.base_url + end_point_url
    
    def _get_burn_url(self, benefit_id):
        # type: (str) -> str

        end_point_url = self.configs.endpoints.burn_benefit.format(benefitId=benefit_id)
        return self.configs.base_url + end_point_url
    
    def _get_unlock_url(self, benefit_id):
        # type: (str) -> str

        end_point_url = self.configs.endpoints.unlock_benefit.format(benefitId=benefit_id)
        return self.configs.base_url + end_point_url
    
    def _get_headers(self):
        # type: () -> str

        return {"X-Api-Key": self.configs.api_key,
                "Content-type": "application/json"}
