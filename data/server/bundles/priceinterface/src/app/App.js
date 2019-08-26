import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'

import PriceLogin from '../components/PriceLogin'
import Navbar from '../components/Navbar'
import Content from '../components/Content'
import TitleBar from '../components/TitleBar'

class App extends Component {

  render() {
    return (
      <div className="app">
        <TitleBar/>
        <div className="mainApp">
          <PriceLogin>
            <div className="row">
              <div className="col-md-3 col-xs-3 col-lg-3 optionsMenu">
                <Navbar />
              </div>
              <div className="col-md-9 col-xs-9 col-lg-9 itemsMenu" >
                <Content/>
              </div>
            </div>
          </PriceLogin>
        </div>
      </div>
    )
  }
}

const mapStateToProps = state => (
  {
    user: state.user
  })

export default withRouter(connect(mapStateToProps)(App))
