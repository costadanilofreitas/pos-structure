import React from 'react'
import PropTypes from 'prop-types'
import FormItem from '../../../util/form-item/JssFormItem'

import Label from '../../../../component/label'
import { Grid, Row, Col } from '../../../../component/grid'


export default function LoginInfoRenderer(props) {
  const { posNumber, workingMode, currentDate, businessDate, storeCode, operatorId, operatorName, classes } = props
  const operator = operatorId != null ? (`${operatorId} - ${operatorName}`) : '\u00A0'

  let businessPeriod = '\u00A0'
  if (businessDate != null) {
    businessPeriod = <Label style={'date'} text={businessDate}/>
  }

  let currentPeriod = '\u00A0'
  if (currentDate != null) {
    currentPeriod = <Label style={'date'} text={currentDate}/>
  }

  const loginType = workingMode.usrCtrlType === 'TS' ? 'TS' : 'QS'
  const podType = `#${posNumber} ${loginType} - ${workingMode.podType} - ${workingMode.posFunction}`

  return (
    <div className={classes.container}>
      <Grid fluid={true}>
        <Row>
          <Col xs={12}><FormItem label={'$LABEL_USER'} value={operator} position={'below'}/></Col>
        </Row>
        <Row>
          <Col xs={6}><FormItem label={'$LABEL_BUSINESS_DATE'} value={businessPeriod} position={'below'}/></Col>
          <Col xs={6}><FormItem label={'$LABEL_CURRENT_DATE'} value={currentPeriod} position={'below'}/></Col>
        </Row>
        <Row>
          <Col xs={6}><FormItem label={'$LABEL_STORE'} value={storeCode} position={'below'}/></Col>
          <Col xs={6}><FormItem label={'$LABEL_POS'} value={podType} position={'below'}/></Col>
        </Row>
      </Grid>
    </div>)
}


LoginInfoRenderer.propTypes = {
  classes: PropTypes.object,
  posNumber: PropTypes.string,
  workingMode: PropTypes.object,
  currentDate: PropTypes.object,
  businessDate: PropTypes.object,
  storeCode: PropTypes.string,
  operatorId: PropTypes.string,
  operatorName: PropTypes.string
}
