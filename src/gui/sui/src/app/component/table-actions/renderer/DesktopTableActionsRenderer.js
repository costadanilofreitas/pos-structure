import React from 'react'
import PropTypes from 'prop-types'
import ButtonGrid from '../../button-grid/ButtonGrid'


export default function DesktopTableActionsRenderer({ tableActions }) {
  const buttons = {}

  const cols = 2
  const rows = 6

  const start = (cols * rows) - tableActions.length
  tableActions.forEach((action, index) => (buttons[start + index] = action))

  return (
    <div style={{ height: '100%', width: '100%', backgroundColor: 'white', position: 'absolute' }}>
      <ButtonGrid
        direction="row"
        cols={cols}
        rows={rows}
        buttons={buttons}
        style={{ position: 'relative' }}
      />
    </div>
  )
}

DesktopTableActionsRenderer.propTypes = {
  tableActions: PropTypes.array,
  classes: PropTypes.object
}
