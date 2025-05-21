import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { I18N } from '3s-posui/core'
import injectSheet, { jss } from 'react-jss'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  saleSummaryLineRoot: {
    composes: 'sale-summary-line-root',
    fontSize: '2vmin',
    display: 'flex',
    flexDirection: 'row-reverse',
    alignItems: 'center',
    padding: '0 2%'
  },
  totemSaleSummaryLineRoot: {
    composes: 'sale-summary-line-root',
    height: '100%',
    fontSize: '3vmin',
    padding: '0 2%',
    display: 'flex',
    flexDirection: 'row-reverse',
    alignItems: 'center'
  },
  saleSummaryLineLabel: {
    composes: 'sale-summary-line-label',
    flexGrow: '1'
  },
  saleSummaryLineValue: {
    composes: 'sale-summary-line-value'
  }
}

class SaleSummaryLine extends PureComponent {
  render() {
    const { classes, label, value, className, defaultMessage, saleSummaryStyle } = this.props
    const valueStr = `${value}`
    const classLabel = label.replace(/\$|LABEL_|_AMOUNT/g, '').toUpperCase()

    if (value == null || valueStr === '' || valueStr === 'NaN') {
      return <div/>
    }

    return (
      <div className={`${classes[saleSummaryStyle]} ${className}`}>
        <div className={`${classes.saleSummaryLineValue} test_SaleSummaryLine_${classLabel}`}>
          {value}
        </div>
        <div className={classes.saleSummaryLineLabel}>
          {this.props.translate &&
          <I18N
            id={label}
            defaultMessage={defaultMessage}
            values={{ 0: '' }}
          />
          }
          {!this.props.translate && label}
        </div>
      </div>
    )
  }
}

SaleSummaryLine.propTypes = {
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Label to display on the left side of the line
   */
  label: PropTypes.string,
  /**
   * Default message in case i18n is not found
   */
  defaultMessage: PropTypes.string.isRequired,
  /**
   * Value to display on the right side of the line
   */
  value: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  /**
   * Class to add to this summary line
   */
  className: PropTypes.string,
  /**
   * Whether the message should be translated using `I18N` or not
   */
  translate: PropTypes.bool,
  /**
   * SaleSummaryLine root class
   */
  saleSummaryStyle: PropTypes.string
}

SaleSummaryLine.defaultProps = {
  translate: true,
  className: ''
}

export default injectSheet(styles)(SaleSummaryLine)
