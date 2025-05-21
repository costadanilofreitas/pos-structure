import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'
import { I18N } from '3s-posui/core'
import {
  BlankLabelContainer,
  BottomButtonsContainer,
  ButtonGridContainer,
  Ingredient,
  IngredientContainer,
  RuptureBackground,
  RuptureButton,
  RuptureButtonsContainer,
  RuptureContainer,
  RuptureKeyboard,
  RuptureLabel,
  RuptureLabelsContainer,
  RuptureMainContainer,
  RuptureTitle
} from './StyledRuptureDialog'
import { IconStyle, PopupStyledButton } from '../../../../constants/commonStyles'
import KeyboardWrapper from '../../keyboard-dialog/keyboard-dialog/KeyboardWrapper'
import MessageBusPropTypes from '../../../../prop-types/MessageBusPropTypes'
import RuptureConfirmationRenderer from './RuptureConfirmationRenderer'
import ButtonGrid from '../../../../app/component/button-grid/ButtonGrid'
import { deepEquals } from '../../../../util/renderUtil'

class RuptureDialogRenderer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      filter: '',
      allIngredients: [],
      enabledIngredients: [],
      disabledIngredients: [],
      updatedEnabledIngredients: [],
      updatedDisabledIngredients: [],
      enterRuptureItems: [],
      outRuptureItems: [],
      selectedIngredientList: [],
      showKeyboard: false,
      confirmationScreen: false
    }

    this.handleOnCancel = this.handleOnCancel.bind(this)
    this.handleEnableItem = this.handleEnableItem.bind(this)
    this.handleDisableItem = this.handleDisableItem.bind(this)
    this.handleShowHideKeyboardButton = this.handleShowHideKeyboardButton.bind(this)
  }

  ingredientIsSelected(ingredientCode) {
    const { selectedIngredientList } = this.state

    return selectedIngredientList.includes(ingredientCode)
  }

  handleIngredientClick(ingredientCode) {
    const { selectedIngredientList } = this.state
    const newSelectedIngredientList = selectedIngredientList

    if (this.ingredientIsSelected(ingredientCode)) {
      for (let i = 0; i < selectedIngredientList.length; i++) {
        if (selectedIngredientList[i] === ingredientCode) {
          newSelectedIngredientList.splice(i, 1)
          break
        }
      }
    } else {
      newSelectedIngredientList.push(ingredientCode)
    }

    this.setState({ selectedIngredientList: newSelectedIngredientList })
  }

  renderIngredients(ingredients) {
    const { filter } = this.state
    const orderedIngredients = ingredients.sort(function (a, b) {
      if (Number(a.product_code) > Number(b.product_code)) {
        return 1
      }
      if (Number(a.product_code) < Number(b.product_code)) {
        return -1
      }
      return 0
    })

    return orderedIngredients.map((ingredient) => {
      if (ingredient.product_code.includes(filter) ||
        ingredient.product_name.toLowerCase().includes(filter.toLowerCase())) {
        return (
          <IngredientContainer
            key={ingredient.product_code}
            className={this.ingredientIsSelected(ingredient.product_code) ? 'selected' : ''}
            onClick={() => this.handleIngredientClick(ingredient.product_code)}
          >
            <Ingredient>
              {`${ingredient.product_code} - ${ingredient.product_name}`}
            </Ingredient>
          </IngredientContainer>
        )
      }

      return false
    })
  }

  renderButtons() {
    const { updatedEnabledIngredients, enabledIngredients } = this.state

    const buttonsComponents = {}

    buttonsComponents[0] = (
      <PopupStyledButton
        active={true}
        flexButton={true}
        borderRight={true}
        className={'test_RuptureDialog_CLOSE'}
        onClick={() => this.handleOnCancel('0')}
      >
        <IconStyle
          className={'fas fa-times fa-2x'}
          secondaryColor={true}
        />
        <I18N id={'$CANCEL'}/>
      </PopupStyledButton>
    )
    buttonsComponents[1] = (
      <PopupStyledButton
        flexButton={true}
        active={!(deepEquals(enabledIngredients, updatedEnabledIngredients))}
        className={'test_RuptureDialog_SAVE'}
        disabled={deepEquals(enabledIngredients, updatedEnabledIngredients)}
        onClick={() => this.toggleRenderer()}
        textTransform={'uppercase'}
      >
        <IconStyle
          className={'fas fa-save fa-2x'}
          secondaryColor={!(deepEquals(enabledIngredients, updatedEnabledIngredients))}
          disabled={deepEquals(enabledIngredients, updatedEnabledIngredients)}
        />
        <I18N id={'$SAVE'}/>
      </PopupStyledButton>
    )

    return (
      <ButtonGridContainer>
        <ButtonGrid
          direction="row"
          cols={Object.keys(buttonsComponents).length}
          rows={1}
          buttons={buttonsComponents}
          style={{ height: '100%' }}
        />
      </ButtonGridContainer>
    )
  }

  changeFilter = (filter) => {
    this.setState({ filter: filter })
  }

  handleShowHideKeyboardButton() {
    const { showKeyboard } = this.state

    this.setState({ showKeyboard: !showKeyboard })
  }

  toggleRenderer = () => {
    const { confirmationScreen } = this.state
    this.setState({
      confirmationScreen: !confirmationScreen,
      outRuptureItems: null,
      enterRuptureItems: null
    })

    if (!confirmationScreen) {
      this.getRupturedItems()
    }
  }

  getRupturedItems() {
    const { msgBus } = this.props
    const { allIngredients, disabledIngredients, updatedDisabledIngredients } = this.state

    const disabledJson = JSON.stringify(disabledIngredients)
    const updatedDisabledJson = JSON.stringify(updatedDisabledIngredients)
    const promise = msgBus.parallelSyncAction('get_ruptured_products', disabledJson, updatedDisabledJson)
    promise.then(result => {
      if (result.ok) {
        this.setState({
          outRuptureItems: allIngredients.filter(x => result.data.enabledProducts.includes(x.product_code)),
          enterRuptureItems: allIngredients.filter(x => result.data.disabledProducts.includes(x.product_code))
        })
      } else {
        this.setState({ confirmationScreen: false })
      }
    })
  }

  renderConfirmationScreen() {
    const {
      updatedDisabledIngredients, updatedEnabledIngredients, enterRuptureItems, outRuptureItems
    } = this.state

    return (
      <RuptureConfirmationRenderer
        msgBus={this.props.msgBus}
        enterRuptureItems={enterRuptureItems}
        exitRuptureItems={outRuptureItems}
        closeDialog={this.props.closeDialog}
        toggleRenderer={this.toggleRenderer}
        updatedDisabledIngredients={updatedDisabledIngredients}
        updatedEnabledIngredients={updatedEnabledIngredients}
      />
    )
  }

  renderRuptureScreen() {
    const { filter, updatedEnabledIngredients, updatedDisabledIngredients, showKeyboard } = this.state

    return (
      <RuptureBackground>
        <RuptureMainContainer>
          <FlexGrid direction={'column'}>
            <FlexChild size={1}>
              <RuptureTitle>
                <I18N id={'$ITEMS_RUPTURE'}/>
              </RuptureTitle>
            </FlexChild>
            <FlexChild size={10}>
              <FlexGrid direction={'column'}>
                <FlexChild size={showKeyboard ? 9 : 1}>
                  <RuptureKeyboard>
                    <KeyboardWrapper
                      value={filter}
                      handleOnInputChange={this.changeFilter}
                      keyboardVisible={showKeyboard}
                      handleShowHideKeyboardButton={this.handleShowHideKeyboardButton}
                      showHideKeyboardButton={true}
                      flat={true}
                    />
                  </RuptureKeyboard>
                </FlexChild>
                <FlexChild size={1}>
                  <RuptureLabelsContainer>
                    <FlexGrid direction={'row'}>
                      <FlexChild size={3}>
                        <RuptureLabel>
                          <I18N id={'$AVAILABLE'}/>
                        </RuptureLabel>
                      </FlexChild>
                      <FlexChild size={1}>
                        <BlankLabelContainer/>
                      </FlexChild>
                      <FlexChild size={3}>
                        <RuptureLabel>
                          <I18N id={'$IN_RUPTURE'}/>
                        </RuptureLabel>
                      </FlexChild>
                    </FlexGrid>
                  </RuptureLabelsContainer>
                </FlexChild>
                <FlexChild size={8}>
                  <FlexGrid direction={'row'}>
                    <FlexChild size={3}>
                      <RuptureContainer className={'test_RuptureDialog_ENABLED-ITEMS'}>
                        <ScrollPanel>
                          {this.renderIngredients(updatedEnabledIngredients)}
                        </ScrollPanel>
                      </RuptureContainer>
                    </FlexChild>
                    <FlexChild size={1}>
                      <RuptureButtonsContainer>
                        <RuptureButton
                          className={'test_RuptureDialog_DISABLE'}
                          onClick={() => this.handleDisableItem()}
                        >
                          <IconStyle
                            className="fas fa-chevron-right fa-2x"
                            aria-hidden="true"
                            secondaryColor={true}
                          />
                        </RuptureButton>
                        <RuptureButton
                          className={'test_RuptureDialog_ENABLE'}
                          onClick={() => this.handleEnableItem()}
                        >
                          <IconStyle
                            className="fas fa-chevron-left fa-2x"
                            aria-hidden="true"
                            secondaryColor={true}
                          />
                        </RuptureButton>
                      </RuptureButtonsContainer>
                    </FlexChild>
                    <FlexChild size={3}>
                      <RuptureContainer className={'test_RuptureDialog_DISABLED-ITEMS'}>
                        <ScrollPanel>
                          {this.renderIngredients(updatedDisabledIngredients)}
                        </ScrollPanel>
                      </RuptureContainer>
                    </FlexChild>
                  </FlexGrid>
                </FlexChild>
              </FlexGrid>
            </FlexChild>
            <FlexChild size={1}>
              <BottomButtonsContainer>
                {this.renderButtons()}
              </BottomButtonsContainer>
            </FlexChild>
          </FlexGrid>
        </RuptureMainContainer>
      </RuptureBackground>
    )
  }

  render() {
    const { confirmationScreen } = this.state

    return (confirmationScreen ? this.renderConfirmationScreen() : this.renderRuptureScreen())
  }

  componentDidMount() {
    const { info, products } = this.props
    const ingredients = this.getIngredients(info, products)

    const allIngredients = ingredients.enabledIngredients.concat(ingredients.disabledIngredients)

    this.setState({
      allIngredients: allIngredients,
      enabledIngredients: ingredients.enabledIngredients,
      updatedEnabledIngredients: ingredients.enabledIngredients,
      disabledIngredients: ingredients.disabledIngredients,
      updatedDisabledIngredients: ingredients.disabledIngredients
    })
  }

  getIngredients(info, products) {
    const ingredients = JSON.parse(info)
    this.removeCFH(products, ingredients)
    return ingredients
  }

  removeCFH(products, ingredients) {
    const CFHList = this.getCFHList(products)
    ingredients.enabledIngredients = ingredients.enabledIngredients.filter(x => !CFHList.includes(x.product_code))
    ingredients.disabledIngredients = ingredients.disabledIngredients.filter(x => !CFHList.includes(x.product_code))
  }

  getCFHList(products) {
    const CFHList = []
    const keys = Object.keys(products)
    keys.forEach(function (key) {
      if (products[key].CFH === 'true') {
        CFHList.push(key)
      }
    })

    return CFHList
  }

  handleOnCancel(selectedOption) {
    this.props.closeDialog(selectedOption)
  }

  handleEnableItem() {
    const { selectedIngredientList, updatedDisabledIngredients, updatedEnabledIngredients } = this.state
    const newEnabledIngredients = Object.assign([], updatedEnabledIngredients)
    const newDisabledIngredients = Object.assign([], updatedDisabledIngredients)
    const excludeList = []

    for (let i = 0; i < updatedDisabledIngredients.length; i++) {
      if (selectedIngredientList.includes(updatedDisabledIngredients[i].product_code)) {
        newEnabledIngredients.push(updatedDisabledIngredients[i])
        excludeList.push(updatedDisabledIngredients[i])
      }
    }

    for (let i = 0; i < excludeList.length; i++) {
      const excludeIndex = newDisabledIngredients.indexOf(excludeList[i])
      newDisabledIngredients.splice(excludeIndex, 1)
    }

    this.setState({
      updatedEnabledIngredients: newEnabledIngredients,
      updatedDisabledIngredients: newDisabledIngredients,
      selectedIngredientList: []
    })
  }

  handleDisableItem() {
    const { selectedIngredientList, updatedEnabledIngredients, updatedDisabledIngredients } = this.state
    const newEnabledIngredients = Object.assign([], updatedEnabledIngredients)
    const newDisabledIngredients = Object.assign([], updatedDisabledIngredients)
    const excludeList = []

    for (let i = 0; i < updatedEnabledIngredients.length; i++) {
      if (selectedIngredientList.includes(updatedEnabledIngredients[i].product_code)) {
        newDisabledIngredients.push(updatedEnabledIngredients[i])
        excludeList.push(updatedEnabledIngredients[i])
      }
    }

    for (let i = 0; i < excludeList.length; i++) {
      const excludeIndex = newEnabledIngredients.indexOf(excludeList[i])
      newEnabledIngredients.splice(excludeIndex, 1)
    }

    this.setState({
      updatedEnabledIngredients: newEnabledIngredients,
      updatedDisabledIngredients: newDisabledIngredients,
      selectedIngredientList: []
    })
  }
}

RuptureDialogRenderer.propTypes = {
  closeDialog: PropTypes.func,
  info: PropTypes.string,
  msgBus: MessageBusPropTypes,
  products: PropTypes.array
}

export default RuptureDialogRenderer
