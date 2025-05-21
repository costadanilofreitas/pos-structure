import { FlexGrid } from '3s-widgets'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import ImageRenderer from '../common/ImageRenderer'
import { ArrowUp, ArrowUpContainer, ButtonContent, MainContainer } from '../common/StyledCommonRenderer'
import TextRenderer from '../common/TextRenderer'

export default class NavigationButton extends Component {
  render() {
    const {
      showImage, addBgColor, onClick, selected, imageContainerSize, text, textContainerSize, buttonSpacing,
      buttonStyle, mainContainerStyle, showText, direction, imageContainerStyle, faIcon, code, theme, showSelectionArrow
    } = this.props
    const color = addBgColor ? theme.navigationBgColor : 'transparent'
    const navigationImage = code != null ? `NAV${code.toString()
      .padStart(8, '0')}` : ''

    return (
      <ButtonContent
        className={`test_SubMenu_${text}`}
        onClick={() => onClick()}
        showImage={showImage}
        buttonSpacing={buttonSpacing}
        color={color}
        style={buttonStyle}
      >
        <MainContainer
          selected={selected}
          showImage={showImage}
          theme={theme}
          style={mainContainerStyle}
          showSelectedBorderBottom={true}
        >
          <FlexGrid direction={direction}>
            <ImageRenderer
              showImage={showImage}
              imageName={navigationImage}
              imageContainerSize={imageContainerSize}
              imageContainerStyle={imageContainerStyle}
              faIcon={faIcon}
            />
            <TextRenderer
              showText={showText}
              text={text}
              textContainerSize={textContainerSize}
            />
          </FlexGrid>
        </MainContainer>
        {showSelectionArrow && selected && <ArrowUpContainer><ArrowUp/></ArrowUpContainer>}
      </ButtonContent>
    )
  }
}

NavigationButton.propTypes = {
  faIcon: PropTypes.string,
  imageContainerSize: PropTypes.number,
  showImage: PropTypes.bool,

  text: PropTypes.string,
  textContainerSize: PropTypes.number,
  showText: PropTypes.bool,

  code: PropTypes.string,
  addBgColor: PropTypes.bool,
  selected: PropTypes.bool,
  showSelectionArrow: PropTypes.bool,
  onClick: PropTypes.func,
  theme: PropTypes.object,

  buttonSpacing: PropTypes.string,
  direction: PropTypes.string,
  buttonStyle: PropTypes.object,
  mainContainerStyle: PropTypes.object,
  imageContainerStyle: PropTypes.object,
  textContainerStyle: PropTypes.object
}

NavigationButton.defaultProps = {
  imageName: null,
  faIcon: null,
  imageContainerSize: 6,
  showImage: false,

  text: null,
  textContainerSize: 4,
  showText: true,

  addBgColor: true,
  selected: false,
  showSelectionArrow: false,

  buttonSpacing: '0px',
  direction: 'column',
  buttonStyle: {},
  mainContainerStyle: {},
  imageContainerStyle: {},
  textContainerStyle: {}
}
