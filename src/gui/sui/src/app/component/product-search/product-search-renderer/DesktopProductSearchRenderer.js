import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { MessageBus } from '3s-posui/core'
import { FlexChild, FlexGrid, ScrollTable, Column } from '3s-widgets'

import Label from '../../../../component/label/Label'

import KeyboardWrapper from '../../../../component/dialogs/keyboard-dialog/keyboard-dialog/KeyboardWrapper'

export default class DesktopProductSearchRenderer extends Component {
  constructor(props) {
    super(props)
    this.msgBus = new MessageBus(this.props.posId)

    this.columns = [
      <Column
        key={1}
        width={200}
        flexGrow={2}
        label="Código de Barras"
        dataKey="barcode"
      />,
      <Column
        key={2}
        width={100}
        flexGrow={1}
        label="PLU"
        dataKey="plu"
      />,
      <Column
        key={3}
        width={300}
        flexGrow={3}
        label="Nome do Produto"
        dataKey="name"
      />,
      <Column
        key={4}
        width={100}
        flexGrow={1}
        label="Preço"
        dataKey="price"
        cellRenderer={
          ({ cellData }) => {
            if (cellData != null) {
              return <Label text={cellData[1] || cellData.null} style="currency" />
            }

            return null
          }
        }
      />,
      <Column
        key={5}
        width={100}
        flexGrow={1}
        label="Ação"
        dataKey="action"
        cellRenderer={ this.props.actionRenderer }
      />
    ]

    this.state = {
      keyboardVisible: false
    }

    this.handleShowHideKeyboardButton = this.handleShowHideKeyboardButton.bind(this)
  }

  render() {
    const { classes, filteredProducts, filter, handleSearch } = this.props

    return (
      <div className={classes.container}>
        <FlexGrid direction={'column'}>
          <FlexChild size={1}>
            <FlexGrid direction={'column'}>
              <FlexChild size={9}>
                <KeyboardWrapper
                  value={filter}
                  handleOnInputChange={handleSearch}
                  keyboardVisible={this.state.keyboardVisible}
                  handleShowHideKeyboardButton={this.handleShowHideKeyboardButton}
                  showHideKeyboardButton={true}
                  flat={true}
                />
              </FlexChild>
            </FlexGrid>
          </FlexChild>
          <FlexChild size={this.state.keyboardVisible ? 1 : 9}>
            <ScrollTable
              data={Object.values(filteredProducts)}
              columns={this.columns}
              rowsQuantity={this.state.keyboardVisible ? 4 : 8}
              tableFlex={this.state.keyboardVisible ? 4 : 8}
            />
          </FlexChild>
        </FlexGrid>
      </div>
    )
  }

  handleShowHideKeyboardButton() {
    const keyboardVisible = !this.state.keyboardVisible
    this.setState({ keyboardVisible })
  }
}

DesktopProductSearchRenderer.propTypes = {
  classes: PropTypes.object,
  posId: PropTypes.number,
  actionRenderer: PropTypes.func,
  handleSearch: PropTypes.func,
  filteredProducts: PropTypes.array,
  filter: PropTypes.string
}
