import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import { I18N } from 'posui/core'
import { Button } from 'posui/button'
import { ButtonGrid, ContextButton } from 'posui/widgets'
import injectSheet, { jss } from 'react-jss'
import _ from 'lodash'
import { MENU_PAYMENT } from '../reducers/menuReducer'
import setMenuAction from '../actions/setMenuAction'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  buttonsBox: {
    flexGrow: 15,
    flexShrink: 0,
    flexBasis: 0,
    position: 'relative',
    marginBottom: '0.5vh'
  },
  footerGridPadding: {
    boxSizing: 'border-box'
  },
  footerCont: {
  },
  footerInProgressTop: {
    display: 'flex',
    height: '100%'
  },
  footerInProgressBottom: {
    display: 'flex',
    height: '100%'
  },
  functionButton: {
    flexGrow: 1,
    flexShrink: 0,
    flexBasis: 'calc(33% - 8px)'
  },
  payButton: {
    fontSize: '2vh !important'
  },
  contextButton: {
    backgroundColor: '#d2691e',
    color: 'white',
    '& i.button-menu-arrow': {
      color: 'white !important'
    }
  },
  redButton: {
    backgroundColor: '#cc0001',
    color: 'white',
    marginRight: '4px',
    marginBottom: '0.3vh'
  },
  orangeButton: {
    backgroundColor: '#d2691e',
    color: 'white',
    marginRight: '4px',
    marginTop: '0.3vh'
  },
  contextButtonStyle: {
    height: '100%',
    marginRight: '4px',
    marginBottom: '0.3vh'
  },
  clearOrderButton: {
    width: '14vh',
    height: '7vh',
    margin: '1vh 1vh 3vh',
    fontSize: '1.3vh',
    backgroundColor: '#cc0001',
    color: 'white'
  },
  specialInstructionsButton: {
    width: '14vh',
    height: '7vh',
    margin: '1vh',
    fontSize: '1.3vh'
  },
  repeatItemButton: {
    width: '14vh',
    height: '7vh',
    margin: '1vh 1vh 3vh',
    fontSize: '1.3vh'
  },
  miacButton: {
    width: '14vh',
    height: '7vh',
    margin: '1vh',
    fontSize: '1.3vh',
    backgroundColor: '#0066b2',
    color: 'white'
  },
  contextMenu: {
    left: 'calc(50% - 8vh)',
    backgroundColor: '#f1eeea'
  },
  arrow: {
    fill: '#f1eeea'
  },
  modifyButton: {
    backgroundColor: '#fdbd10',
    color: 'black',
    marginBottom: '0.3vh'
  },
  totalButton: {
    backgroundColor: '#59980d',
    color: 'white',
    marginTop: '0.3vh'
  }
}

class OrderFunctions extends PureComponent {

  optionsButton = <I18N id="$OPTIONS" defaultMessage="Options" />

  voidOrClearOption = (selectedLine) => {
    const level = parseInt((selectedLine || {}).level || '0', 10)
    const { itemId, partCode, lineNumber } = selectedLine || {}
    if (level > 0) {
      let fullItemId = ''
      if (itemId && partCode) {
        fullItemId = `${itemId}.${partCode}`
      }
      return ['doClearOptionItem', lineNumber, fullItemId]
    }
    return ['doVoidLine', lineNumber]
  }

  afterVoid = (selectedLine) => {
    // unselect line after delete
    const level = parseInt((selectedLine || {}).level || '0', 10)
    if (level === 0) {
      this.props.onUnselectLine()
    }
  }

  getCommentId = (selectedLine) => () => {
    const { order } = this.props
    let commentId = '-1'
    // check if we have a comment already
    const line = _.find(
      order.SaleLine || [],
      (lineItem) => _.isEqual(lineItem['@attributes'], selectedLine)
    )
    if (line) {
      const comment = _.find(
        line.Comment || [],
        (commentItem) => {
          const commentStr = (commentItem['@attributes'] || {}).comment
          return !_.startsWith(commentStr, '[') || !_.endsWith(commentStr, ']')
        }
      )
      if (comment) {
        commentId = comment['@attributes'].commentId
      }
    }
    return commentId
  }

  render() {
    const { classes, inProgress, setMenu, onShowModifierScreen, modifierScreenOpen } = this.props
    if (!inProgress) {
      // TODO: implement buttons to be displayed when there is no order in progress
      return (
        <div className={classes.footerCont}>
        </div>
      )
    }
    return (
      <div className={classes.buttonsBox}>
        <ButtonGrid
          className={classes.footerGridPadding}
          direction="row"
          cols={1}
          rows={2}
          buttons={{
            0: (
              <div className={classes.footerInProgressTop}>
                <Button
                  className={classes.functionButton}
                  style={styles.redButton}
                  selectedLine={this.props.selectedLine || {}}
                  executeAction={() => this.voidOrClearOption(this.props.selectedLine)}
                  onActionFinish={() => this.afterVoid(this.props.selectedLine)}
                  text="$DELETE_LINE"
                  defaultText="Delete Line"
                />
                <ContextButton
                  className={classes.functionButton}
                  style={styles.contextButtonStyle}
                  classNameButton={classes.contextButton}
                  styleContextMenu={styles.contextMenu}
                  styleArrow={styles.arrow}
                  buttonText={this.optionsButton}>
                  <Button
                    style={styles.clearOrderButton}
                    executeAction={function () {
                      this.closeContextMenu()
                      return ['doVoidSale']
                    }}
                    text="$CLEAR_ORDER"
                    defaultText="Clear Order"
                  />
                  <Button
                    style={styles.specialInstructionsButton}
                    selectedLine={this.props.selectedLine || {}}
                    getCommentId={this.getCommentId(this.props.selectedLine || {})}
                    executeAction={function () {
                      const { lineNumber, level, itemId, partCode } = this.selectedLine
                      this.closeContextMenu()
                      return ['doComment', lineNumber || '', level || '', itemId || '', partCode || '', this.getCommentId()]
                    }}
                    onActionFinish={() => this.afterVoid(this.props.selectedLine) }
                    text="$SPECIAL_INSTRUCTION"
                    defaultText="Special Instruction"
                  />
                  <Button
                    style={styles.repeatItemButton}
                    selectedLine={this.props.selectedLine || {}}
                    executeAction={function () {
                      this.closeContextMenu()
                      return ['doDuplicateLine', this.selectedLine.lineNumber]
                    }}
                    text="$REPEAT_ITEM"
                    defaultText="Repeat Item"
                  />
                  <Button
                    style={styles.miacButton}
                    selectedLine={this.props.selectedLine || {}}
                    selectedQty={this.props.selectedQty || 1}
                    executeAction={function () {
                      const { lineNumber, selectedQty } = this.selectedLine
                      this.closeContextMenu()
                      return ['doMakeCombo', lineNumber || '', 'M', selectedQty]
                    }}
                    text="$MAKE_IT_A_COMBO"
                    defaultText="Make it a Combo"
                  />
                  <Button
                    style={styles.miacButton}
                    selectedLine={this.props.selectedLine || {}}
                    selectedQty={this.props.selectedQty || 1}
                    executeAction={function () {
                      const { lineNumber, selectedQty } = this.selectedLine
                      this.closeContextMenu()
                      return ['doUpsize', 1, lineNumber || '', '', selectedQty]
                    }}
                    text="$UPSIZE"
                    defaultText="Up Size"
                  />
                  <Button
                    style={styles.miacButton}
                    selectedLine={this.props.selectedLine || {}}
                    selectedQty={this.props.selectedQty || 1}
                    executeAction={function () {
                      const { lineNumber, selectedQty } = this.selectedLine
                      this.closeContextMenu()
                      return ['doUpsize', 0, lineNumber || '', '', selectedQty]
                    }}
                    text="$DOWNSIZE"
                    defaultText="Down Size"
                  />
                </ContextButton>
                <Button
                  className={classes.functionButton}
                  style={styles.modifyButton}
                  onClick={onShowModifierScreen}
                  text={(modifierScreenOpen) ? '$DONE' : '$MODIFY'}
                  defaultText={(modifierScreenOpen) ? 'Done' : 'Modify'}
                />
              </div>
            ),
            1: (
              <div className={classes.footerInProgressBottom}>
                <Button
                  className={classes.functionButton}
                  style={styles.orangeButton}
                  executeAction={() => ['doStoreOrder']}
                  text="$SAVE"
                  defaultText="Save"
                />
                <Button
                  className={classes.functionButton}
                  style={styles.orangeButton}
                  executeAction={() => ['doSetCustomerName']}
                  text="$CUSTOMER_NAME"
                  defaultText="Customer Name"
                />
                <Button
                  className={`${classes.functionButton} ${classes.payButton}`}
                  style={styles.totalButton}
                  executeAction={() => ['doTotal']}
                  onActionFinish={(resp) => {
                    if (resp === 'True') {
                      setMenu(MENU_PAYMENT)
                    }
                  }}
                  text="$TOTAL"
                  defaultText="Total"
                />
              </div>
            )
          }}
        />
      </div>
    )
  }
}

OrderFunctions.propTypes = {
  /**
   * @ignore
   */
  setMenu: PropTypes.func,
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Current order
   */
  order: PropTypes.object,
  /**
   * True when a sale is in progress
   */
  inProgress: PropTypes.bool.isRequired,
  /**
   * Currently selected line on sale panel
   */
  selectedLine: PropTypes.object,
  /**
   * Currently selected quantity
   */
  selectedQty: PropTypes.number,
  /**
   * Called when Modifier button is clicked
   */
  onShowModifierScreen: PropTypes.func.isRequired,
  /**
   * Called when sale panel must be unselected, after a void
   */
  onUnselectLine: PropTypes.func.isRequired,
  /**
   * Indicates if the modifier screen is currently open
   */
  modifierScreenOpen: PropTypes.bool
}

OrderFunctions.defaultProps = {
  selectedLine: {}
}

function mapDispatchToProps(dispatch) {
  return bindActionCreators({
    setMenu: setMenuAction
  }, dispatch)
}

export default connect(null, mapDispatchToProps)(injectSheet(styles)(OrderFunctions))
