import React, { Component } from 'react'
import PropTypes from 'prop-types'

import { I18N } from '3s-posui/core'

import ButtonGrid from '../button-grid/ButtonGrid'
import { CommonStyledButton, IconStyle } from '../../../constants/commonStyles'

class TableSeatsActions extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const { selectedTable, onChangeSeats, onSplitItems, onMergeItems, setSeatScreen } = this.props
    const onAuthorize = this.props.onChangeEnabledToReorganizeItems
    const isAuthorized = this.props.enabledToReorganizeItems

    const buttons = {
      0: <CommonStyledButton
        className={'test_TableSeatsActions_LOCK-OPEN'}
        key={'authorize'}
        onClick={() => onAuthorize()}
        disabled={isAuthorized}
        border={true}
      >
        <IconStyle
          className="fas fa-lock-open fa-2x"
          aria-hidden="true"
          disabled={isAuthorized}
        />
        <br/>
        <I18N id="$AUTHORIZE"/>
      </CommonStyledButton>,
      1: <CommonStyledButton
        className={'test_TableSeatsActions_LOCK'}
        key={'finish'}
        onClick={() => onAuthorize()}
        disabled={!isAuthorized}
        border={true}
      >
        <IconStyle
          className="fas fa-lock fa-2x"
          aria-hidden="true"
          disabled={!isAuthorized}
        />
        <br/>
        <I18N id="$FINISH"/>
      </CommonStyledButton>,
      2: <CommonStyledButton
        className={'test_TableSeatsActions_SPLIT'}
        key={'splitItem'}
        onClick={() => onSplitItems(false)}
        disabled={!isAuthorized}
        border={true}
      >
        <IconStyle
          className="fas fa-divide fa-2x"
          aria-hidden="true"
          disabled={!isAuthorized}
        />
        <br/>
        <I18N id="$SPLIT_ITEM"/>
      </CommonStyledButton>,
      3: <CommonStyledButton
        className={'test_TableSeatsActions_MERGE'}
        key={'mergeItem'}
        onClick={() => onMergeItems(false)}
        disabled={!isAuthorized}
        border={true}
      >
        <IconStyle
          className="fas fa-plus fa-2x"
          aria-hidden="true"
          disabled={!isAuthorized}
        />
        <br/>
        <I18N id="$MERGE_ITEM"/>
      </CommonStyledButton>,
      4: <CommonStyledButton
        className={'test_TableSeatsActions_BACK'}
        key={'back'}
        onClick={() => setSeatScreen(false)}
        border={true}
      >
        <IconStyle
          className="fa fa-arrow-circle-left fa-2x"
          aria-hidden="true"
        />
        <br/>
        <I18N id="$BACK"/>
      </CommonStyledButton>,
      5: <CommonStyledButton
        className={'test_TableSeatsActions_CHANGE-SEATS'}
        key={'changeTableSeats'}
        onClick={() => onChangeSeats(selectedTable.id)}
        border={true}
      >
        <IconStyle
          className="fa fa-users fa-2x"
          aria-hidden="true"
        />
        <br/>
        <I18N id="$CHANGE_SEATS"/>
      </CommonStyledButton>
    }

    return (
      <div style={{ width: '100%', height: '100%', backgroundColor: 'white', position: 'absolute' }}>
        <ButtonGrid
          direction="row"
          cols={2}
          rows={3}
          buttons={buttons}
          style={{ position: 'relative' }}
        />
      </div>
    )
  }
}

TableSeatsActions.propTypes = {
  selectedTable: PropTypes.shape({
    id: PropTypes.string,
    linkedTables: PropTypes.arrayOf(PropTypes.string),
    status: PropTypes.number.isRequired,
    dueAmount: PropTypes.number,
    orders: PropTypes.array
  }),
  enabledToReorganizeItems: PropTypes.bool,
  setSeatScreen: PropTypes.func,
  onSplitItems: PropTypes.func,
  onMergeItems: PropTypes.func,
  onChangeSeats: PropTypes.func,
  onChangeEnabledToReorganizeItems: PropTypes.func
}

export default (TableSeatsActions)
