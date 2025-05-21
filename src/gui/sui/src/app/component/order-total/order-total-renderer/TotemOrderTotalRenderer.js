import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'
import { FlexChild, FlexGrid } from '3s-widgets'
import Label from '../../../../component/label'

export default class TotemOrderTotalRenderer extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { classes, totalOrder } = this.props

    return (
      <FlexGrid
        direction={'row'}
        gridRef={this.setRef}
        className={`${classes.container} ${classes.textBounce}`}
      >
        <FlexChild size={5}>
          <FlexGrid direction={'row'}>
            <FlexChild size={1}>
              <FlexGrid direction={'row'}>
                <FlexChild size={2} innerClassName={`${this.props.classes.totalGross} test_OrderTotalRenderer_TOTAL`}>
                  {totalOrder !== -1 &&
                    <div>
                      <I18N id={'$TOTAL_PAYABLE'}/> <Label style={'currency'} text={totalOrder}/>
                    </div>
                  }
                </FlexChild>
              </FlexGrid>
            </FlexChild>
          </FlexGrid>
        </FlexChild>
      </FlexGrid>
    )
  }
}

TotemOrderTotalRenderer.propTypes = {
  totalOrder: PropTypes.number,
  classes: PropTypes.object
}
