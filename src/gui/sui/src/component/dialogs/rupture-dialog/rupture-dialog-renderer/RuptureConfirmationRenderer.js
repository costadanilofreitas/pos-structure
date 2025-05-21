import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { FlexChild, FlexGrid, ScrollPanel } from '3s-widgets'
import { I18N } from '3s-posui/core'
import {
  BottomButtonsContainer,
  ButtonGridContainer,
  Ingredient,
  IngredientContainer,
  RuptureBackground,
  RuptureContainer,
  RuptureContainerLine,
  RuptureLabel,
  RuptureLabelLine,
  RuptureLabelsContainer,
  RuptureMainContainer,
  RuptureTitle,
  Spinner
} from './StyledRuptureDialog'
import { IconStyle, PopupStyledButton } from '../../../../constants/commonStyles'
import MessageBusPropTypes from '../../../../prop-types/MessageBusPropTypes'
import ButtonGrid from '../../../../app/component/button-grid/ButtonGrid'


class RuptureConfirmationRenderer extends Component {
  constructor(props) {
    super(props)

    this.handleSaveRupture = this.handleSaveRupture.bind(this)
  }

  renderIngredients(ingredients) {
    if (ingredients == null) {
      return <Spinner className={'fa fa-spinner fa-spin fa-4x loading-screen-spinner'} />
    }

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
      return (
        <IngredientContainer key={ingredient.product_code}>
          <Ingredient>
            {`${ingredient.product_code} - ${ingredient.product_name}`}
          </Ingredient>
        </IngredientContainer>
      )
    })
  }

  renderButtons() {
    const { toggleRenderer } = this.props
    const buttonsComponents = {}

    buttonsComponents[0] = (
      <PopupStyledButton
        active={true}
        flexButton={true}
        borderRight={true}
        className={'test_RuptureConfirmation_BACK'}
        onClick={() => toggleRenderer('0')}
      >
        <IconStyle className={'fas fa-arrow-circle-left fa-2x'} style={{ margin: '0.5vmin' }} secondaryColor={true}/>
        <I18N id={'$BACK'}/>
      </PopupStyledButton>
    )
    buttonsComponents[1] = (
      <PopupStyledButton
        active={true}
        flexButton={true}
        className={'test_RuptureConfirmation_OK'}
        onClick={() => this.handleSaveRupture()}
      >
        <IconStyle className={'fas fa-check fa-2x'} style={{ margin: '0.5vmin' }} secondaryColor={true}/>
        <I18N id={'$OK'}/>
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

  render() {
    const { enterRuptureItems, exitRuptureItems } = this.props

    return (
      <RuptureBackground>
        <RuptureMainContainer>
          <FlexGrid direction={'column'}>
            <FlexChild size={1}>
              <RuptureTitle>
                <I18N id={'$CONFIRM_RUPTURE'}/>
              </RuptureTitle>
            </FlexChild>
            <FlexChild size={10}>
              <FlexGrid direction={'column'}>
                <FlexChild size={1}>
                  <RuptureLabelsContainer>
                    <FlexGrid direction={'row'}>
                      <FlexChild size={3}>
                        <RuptureLabelLine>
                          <I18N id={'$EXIT_RUPTURE'}/>
                        </RuptureLabelLine>
                      </FlexChild>
                      <FlexChild size={3}>
                        <RuptureLabel>
                          <I18N id={'$ENTER_RUPTURE'}/>
                        </RuptureLabel>
                      </FlexChild>
                    </FlexGrid>
                  </RuptureLabelsContainer>
                </FlexChild>
                <FlexChild size={9}>
                  <FlexGrid direction={'row'}>
                    <FlexChild size={3}>
                      <RuptureContainer className={'test_RuptureConfirmation_EXIT-ITEMS'}>
                        <ScrollPanel>
                          {this.renderIngredients(exitRuptureItems)}
                        </ScrollPanel>
                      </RuptureContainer>
                    </FlexChild>
                    <FlexChild size={3}>
                      <RuptureContainerLine className={'test_RuptureConfirmation_ENTER-ITEMS'}>
                        <ScrollPanel>
                          {this.renderIngredients(enterRuptureItems)}
                        </ScrollPanel>
                      </RuptureContainerLine>
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

  handleSaveRupture() {
    const { updatedEnabledIngredients, updatedDisabledIngredients } = this.props
    const { msgBus, closeDialog } = this.props

    msgBus.parallelSyncAction('save_rupture', JSON.stringify(updatedEnabledIngredients),
      JSON.stringify(updatedDisabledIngredients))

    closeDialog('1')
  }
}

RuptureConfirmationRenderer.propTypes = {
  msgBus: MessageBusPropTypes,
  enterRuptureItems: PropTypes.array,
  exitRuptureItems: PropTypes.array,
  updatedEnabledIngredients: PropTypes.array,
  updatedDisabledIngredients: PropTypes.array,
  closeDialog: PropTypes.func,
  toggleRenderer: PropTypes.func
}

export default RuptureConfirmationRenderer
