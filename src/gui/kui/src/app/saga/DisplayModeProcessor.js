import DisplayMode from '../model/DisplayMode'

export default class DisplayModeProcessor {
  constructor(currentDisplayMode) {
    this.currentDisplayMode = currentDisplayMode
  }

  getNewDisplayMode(newDisplayMode) {
    if (this.currentDisplayMode === newDisplayMode) {
      return DisplayMode.Normal
    }
    return newDisplayMode
  }
}
