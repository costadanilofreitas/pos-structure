import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import _ from 'lodash'
import { Button } from 'posui/button'
import { NumPad } from 'posui/widgets'

const styles = {
  containerStyle: {
    position: 'relative',
    borderRadius: '7px',
    border: '2px solid rgba(0, 0, 0, 0.5)',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    width: '56%',
    height: '70%',
    left: '22%',
    top: '15%'
  },
  numPadContainer: {
    position: 'absolute',
    margin: '10% 8%',
    width: '50%',
    height: '75%'
  },
  buttonContainer: {
    position: 'absolute',
    display: 'flex',
    flexGrow: 1,
    flexDirection: 'column',
    width: '25%',
    height: '75%',
    left: '67%',
    margin: '10% 0%'
  },
  buttonStyle: {
    margin: '5px 0'
  },
  spacer: {
    height: '100%'
  }
}

class SignInScreen extends Component {
  state = {
    inputValue: ''
  }

  handleInputChange = (value) => {
    this.setState({ inputValue: value })
  }

  signIn = () => {
    return ['signIn', this.state.inputValue]
  }

  render() {
    const busy = !_.isEmpty(this.props.actionRunning)
    const { inputValue } = this.state
    return (
      <div style={styles.containerStyle}>
        <div style={styles.numPadContainer}>
          <NumPad
            value={inputValue}
            onTextChange={this.handleInputChange}
            password={true}
            rounded={false}
            forceFocus={true}
          />
        </div>
        <div style={styles.buttonContainer}>
          <Button
            style={styles.buttonStyle}
            disabled={true}
            executeAction={[]}>
            Clock In
          </Button>
          <Button
            style={styles.buttonStyle}
            disabled={true}
            executeAction={[]}>
            Clock Out
          </Button>
          <div style={styles.spacer}></div>
          <Button
            key={`ordering_${busy}`}
            style={styles.buttonStyle}
            disabled={busy}
            executeAction={this.signIn}>
            Ordering
          </Button>
          <Button
            key={`funcs_${busy}`}
            style={styles.buttonStyle}
            disabled={busy}
            onClick={() => this.props.onShowFunctionScreen()}>
            Functions
          </Button>
        </div>
      </div>
    )
  }
}

SignInScreen.propTypes = {
  /**
   * Called when the user clicks the 'Functions' button
   */
  onShowFunctionScreen: PropTypes.func.isRequired,
  /**
   * App state holding actions currently in progress
   * @ignore
   */
  actionRunning: PropTypes.object
}

function mapStateToProps(state) {
  return {
    actionRunning: state.actionRunning
  }
}

export default connect(mapStateToProps)(SignInScreen)
