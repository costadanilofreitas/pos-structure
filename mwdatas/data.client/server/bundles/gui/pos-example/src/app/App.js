import React from 'react'
import { LoadingScreen, ScreenSize, Footer } from 'posui/widgets'
import { DialogList } from 'posui/dialogs'
import { MainScreen } from '.'

const App = () => {
  return (
    <LoadingScreen style={{ height: '100%' }}>
      <MainScreen />
      <Footer />
      <ScreenSize />
      <DialogList />
    </LoadingScreen>
  )
}

export default App
