import { Component } from 'react'

export default class FakeDevice extends Component {
  constructor(props) {
    super(props)

    if (window.mwapi == null) {
      window.mwapi = {
        print: function (callback, buffer) {
          // eslint-disable-next-line no-eval
          eval(`${callback}("0");`)
        },
        processPayment: function (callback, value, tenderType, extraData, step) {
          const localPaymentData = JSON.stringify({
            'CNPJAuth': '68.536.379/0001-92',
            'TransactionProcessor': '00051',
            'Bandeira': '4',
            'IdAuth': '1234',
            'AuthCode': '5678',
            'CardNumber': '1234',
            'ReceiptMerchant': 'UmVjZWlwdCBtZXJjaGFudA==',
            'ReceiptCustomer': 'UmVjZWlwdCBjdXN0b21lcg=='
          })
            .replace(new RegExp('"', 'g'), '\\"')

          // eslint-disable-next-line no-eval
          eval(`${callback}("0", "", "${localPaymentData}");`)
        },
        getDeviceType: function (callback) {
          // eslint-disable-next-line no-eval
          eval(`${callback}("0", "", "APOS_A8");`)
        }
      }
    }
  }

  // eslint-disable-next-line class-methods-use-this
  render() {
    return null
  }

  // eslint-disable-next-line class-methods-use-this
  componentWillUnmount() {
    window.mwapi = null
  }
}
