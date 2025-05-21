import * as types from '3s-posui/constants/actionTypes'
import isEqual from 'lodash/isEqual'

const DEFAULT_KDS_MODEL = {}

export default function (state = DEFAULT_KDS_MODEL, action = {}) {
  switch (action.type) {
    case types.KDS_TITLE:
      if (state.title === action.payload) {
        break
      }
      return { ...state, title: action.payload }
    case types.KDS_VIEW_TITLE:
      if (state.viewTitle === action.payload) {
        break
      }
      return { ...state, viewTitle: action.payload }
    case types.KDS_CELL_FORMAT:
      if (isEqual(state.cellFormat, action.payload)) {
        break
      }
      return { ...state, cellFormat: action.payload }
    case types.KDS_LAYOUT:
      if (isEqual(state.layout, action.payload)) {
        break
      }
      return { ...state, layout: action.payload }
    case types.KDS_THRESHOLDS:
      if (isEqual(state.thresholds, action.payload)) {
        break
      }
      return { ...state, thresholds: action.payload }
    case types.KDS_BUMPBARS:
      if (isEqual(state.bumpbar, action.payload)) {
        break
      }
      return { ...state, bumpbar: action.payload.bumpbar }
    case types.KDS_TITLES: // not found
      return { ...state, titles: action.payload }
    case types.KDS_ENABLE_TAGGING: // not found
      return { ...state, enableTagging: action.payload }
    case types.KDS_STATUS: // not found
      return { ...state, kdsEnabled: action.payload }
    case types.KDS_MODIFIER_PREFIXES:
      if (isEqual(state.modifierPrefixes, action.payload)) {
        break
      }
      return { ...state, modifierPrefixes: action.payload }
    case types.KDS_STATISTICS:
      if (isEqual(state.statistics, action.payload)) {
        break
      }
      return { ...state, statistics: action.payload }
    case types.KDS_CAROUSEL:
      if (state.carousel === action.payload) {
        break
      }
      return { ...state, carousel: action.payload }
    case types.KDS_VIEWS_MODEL:
      if (isEqual(state.views, action.payload)) {
        break
      }
      return { ...state, views: action.payload }
    case types.KDS_SHOW_ITEMS:
      if (state.showItems === action.payload) {
        break
      }
      return { ...state, showItems: action.payload }
    case types.KDS_SETTINGS:
      if (isEqual(state.settings, action.payload)) {
        break
      }
      return { ...state, settings: action.payload }
    case types.KDS_SELECTED_ZOOM:
      if (state.selectedZoom === action.payload) {
        break
      }
      return { ...state, selectedZoom: action.payload }
    case types.KDS_AUTO_ORDER_COMMANDS:
      if (isEqual(state.autoOrderCommand, action.payload)) {
        break
      }
      return { ...state, autoOrderCommand: action.payload }
    case types.KDS_DISPLAY_MODE:
      if (state.displayMode === action.payload) {
        break
      }
      return { ...state, displayMode: action.payload }
    case types.KDS_COLORED_AREA:
      if (state.coloredArea === action.payload) {
        break
      }
      return { ...state, coloredArea: action.payload }
    case types.VIEW_WITH_ACTIONS:
      if (state.ViewWithActions === action.payload) {
        break
      }
      return { ...state, viewWithActions: action.payload === 'true' }
    default:
  }

  return state
}
