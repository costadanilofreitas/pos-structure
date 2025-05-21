import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import { connect } from 'react-redux'
import injectSheet, { jss } from 'react-jss'
import { I18N } from '../core'
import StartupWarning from './StartupWarning'

jss.setup({ insertionPoint: 'posui-css-insertion-point' })

const styles = {
  loadingScreenRoot: {
    composes: 'loading-screen-root',
    display: 'table',
    width: '100%',
    height: '100%',
    position: 'absolute',
    backgroundColor: 'white',
    zIndex: 10000
  },
  loadingScreenSpinner: {
    composes: 'fa fa-spinner fa-spin fa-4x loading-screen-spinner',
    color: '#777777',
    width: '64px',
    height: '64px',
    position: 'fixed',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
    margin: 'auto',
    maxWidth: '100%',
    maxHeight: '100%',
    overflow: 'hidden'
  }
}

/**
 * Helper component that displays a spinner while the POS is loading, or
 * there is a conflict or a configuration problem that prevents the system from
 * being used yet.
 * If there is a conflict or a configuration error, a message is displayed to the user.
 *
 * `LoadingScreen` uses font-awesome for the spinner, so you need to add this library to
 * your package.json, and then include the corresponding css:
 * ```
 * import 'font-awesome/css/font-awesome.css'
 * ```
 *
 * ![LoadingScreen conflict screen](./loading-screen-conflict.png)
 * ![LoadingScreen invalid POS id screen](./loading-screen-invalid-pos-id.png)
 *
 * In order to use this component, your app state must expose the following state:
 * - `loading` using `loadingReducer` reducer
 * And one of the following states:
 * - `posId` using `posIdReducer` reducer
 * - `kdsId` using `kdsIdReducer` reducer
 * - `codId` using `codIdReducer` reducer
 *
 * Available class names:
 * - root element: `loading-screen-root`
 * - spinner element: `loading-screen-spinner`
 */
class LoadingScreen extends PureComponent {
  render() {
    const {
      posId, kdsId, codId, loading, classes, style, styleSpinner, customLoadingFlag, type
    } = this.props
    let validId
    switch (type) {
      case 'POS':
        validId = !isNaN(posId)
        break
      case 'KDS':
        validId = !isNaN(kdsId)
        break
      case 'COD':
        validId = !isNaN(codId)
        break
      default:
        validId = true
    }
    if (loading.synched && loading.localeLoaded &&
        !loading.conflict && validId && !customLoadingFlag) {
      // everything is ok, no need to render loading screen
      return <div style={style}>{this.props.children}</div>
    }
    const showSpinner = (
      !loading.synched || !loading.localeLoaded || loading.conflict || !validId || customLoadingFlag
    )

    return (
      <div className={classes.loadingScreenRoot} style={style}>
        { showSpinner &&
          <div className={classes.loadingScreenSpinner} style={styleSpinner} />
        }
        { validId && loading.conflict &&
          <StartupWarning msg={<I18N id="$CONFLICT_DETECTED" defaultMessage="A possible conflict was detected. Please check if this {type} is not opened anywhere else." values={{ type }} />} />
        }
        { validId && !loading.conflict && !loading.synched &&
          <StartupWarning msg={<I18N id="$CONNECTING_TO_SERVER" defaultMessage="Connecting to server, please wait." />} />
        }
        { !validId &&
          <StartupWarning msg={<I18N id="$SELECT_POS_ID" defaultMessage="Please select a valid {type} id on the URL." values={{ type }} />} />
        }
      </div>
    )
  }
}

LoadingScreen.propTypes = {
  /**
   * An object representing the loading current state from `loadingReducer` app state
   * @ignore
   */
  loading: PropTypes.shape({
    /**
     * Indicates if the even loop has a valid synchronization id
     * @ignore
     */
    synched: PropTypes.bool,
    /**
     * Indicates if the even loop is conflicting (another browser opened on the same
     * machine with same POS id)
     * @ignore
     */
    conflict: PropTypes.bool,
    /**
     * Indicates if the locale data is loaded
     * @ignore
     */
    localeLoaded: PropTypes.bool
  }),
  /**
   * POS id from `posIdReducer` app state
   * @ignore
   */
  posId: PropTypes.number,
  /**
   * KDS id from `kdsIdReducer` app state
   * @ignore
   */
  kdsId: PropTypes.number,
  /**
   * COD id from `codIdReducer` app state
   * @ignore
   */
  codId: PropTypes.number,
  /**
   * The content to display if everything is ok
   * @ignore
   */
  children: PropTypes.node,
  /**
   * Injected classes
   * @ignore
   */
  classes: PropTypes.object,
  /**
   * Component's root style override
   */
  style: PropTypes.object,
  /**
   * Component's spinner style override
   */
  styleSpinner: PropTypes.object,
  /**
   * Custom loading flag. User can set this to true to show the loading spinner, regardless
   * of the internal loading state. It is useful when a custom implementation needs to load
   * additional data before letting the user use the UI.
   */
  customLoadingFlag: PropTypes.bool,
  /**
   * Device type (POS, KDS or COD)
   */
  type: PropTypes.string
}

LoadingScreen.defaultProps = {
  style: {},
  styleSpinner: {},
  customLoadingFlag: false,
  type: 'POS'
}

function mapStateToProps(state) {
  return {
    posId: state.posId,
    kdsId: state.kdsId,
    codId: state.codId,
    loading: state.loading
  }
}

export default connect(mapStateToProps)(injectSheet(styles)(LoadingScreen))
