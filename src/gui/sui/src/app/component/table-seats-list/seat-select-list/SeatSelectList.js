import React from 'react'
import PropTypes from 'prop-types'
import Button from '../../../../component/action-button/Button'


export default function SeatSelectList({ seats, onSeatSelect }) {
  return (
    <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)' }}>
      {
        seats.map(seat =>
          <Button
            key={`buttonSeat${seat}`}
            text={`$SEAT|${seat}`}
            onClick={() => onSeatSelect(seat)}
          />)
      }
    </div>
  )
}

SeatSelectList.propTypes = {
  seats: PropTypes.arrayOf(PropTypes.number).isRequired,
  onSeatSelect: PropTypes.func.isRequired
}
