export const themes = [
  {
    /* shared with posui */
    name: 'default',
    backgroundColor: 'white',
    color: 'black',
    footer: {
      backgroundColor: 'white',
      color: 'black',
      fontSize: '1.4vh'
    },
    footerLeftPanel: {
      fontSize: '1.2vh',
      border: '1px solid rgba(204, 204, 204, 1)'
    },
    footerRightPanel: {
      fontSize: '1.7vh',
      borderTop: '1px solid rgba(204, 204, 204, 1)',
      borderRight: '1px solid rgba(204, 204, 204, 1)',
      borderBottom: '1px solid rgba(204, 204, 204, 1)'
    },
    clock: {
      color: 'black',
      fontSize: '1.4vh'
    },
    /* local widgets */
    mainMenu: {
      backgroundColor: 'white',
      color: 'black',
      fontSize: '2vh',
      textTransform: 'uppercase',
      borderBottom: '1px solid #cccccc'
    },
    mainMenuActive: {
      backgroundColor: '#eeeeee',
      color: 'black'
    },
    mainMenuNotLast: {
      borderRight: '1px solid #cccccc'
    },
    submenu: {
      backgroundColor: 'white',
      color: 'black',
      borderBottom: '1px solid #cccccc'
    },
    submenuActive: {
      backgroundColor: '#eeeeee',
      color: 'black'
    },
    submenuNotLast: {
      borderRight: '1px solid #cccccc'
    },
    qtyButton: {
      backgroundColor: 'white',
      border: '1px solid #cccccc'
    },
    qtyButtonSelected: {
      color: 'black',
      backgroundColor: '#eeeeee',
      border: '1px solid #cccccc'
    }
  },
  {
    name: 'dark',
    backgroundColor: '#3c3c3c',
    color: '#888888',
    footer: {
      backgroundColor: '#222222',
      border: 'none'
    },
    footerRightPanel: {
      borderTop: 'none',
      borderRight: 'none',
      borderBottom: 'none'
    },
    /* local widgets */
    mainMenu: {
      backgroundColor: '#222222',
      color: '#888888',
      textTransform: 'uppercase',
      borderBottom: 'none'
    },
    mainMenuActive: {
      backgroundColor: '#eeeeee',
      color: 'black'
    },
    mainMenuNotLast: {
      borderRight: 'none'
    },
    submenu: {
      backgroundColor: '#444444',
      color: '#888888',
      borderBottom: 'none'
    },
    submenuActive: {
      backgroundColor: '#eeeeee',
      color: 'black'
    },
    submenuNotLast: {
      borderRight: 'none'
    },
    qtyButton: {
      backgroundColor: '#444444',
      color: '#888888',
      border: 'none'
    },
    qtyButtonSelected: {
      color: 'black',
      backgroundColor: '#eeeeee',
      border: 'none'
    }
  },
  {
    name: 'king',
    backgroundColor: '#f1eeea',
    color: '#444444',
    /* local widgets */
    mainMenu: {
      backgroundColor: '#0066b2',
      color: 'white',
      textTransform: 'uppercase',
      borderBottom: '1px solid #333333'
    },
    mainMenuActive: {
      backgroundColor: '#ed7801',
      color: '#762823'
    },
    mainMenuNotLast: {
      borderRight: '1px solid #333333'
    },
    submenu: {
      backgroundColor: '#ffffff',
      color: '#ec1c24',
      borderBottom: '1px solid #aaaaaa'
    },
    submenuActive: {
      backgroundColor: '#ed7801',
      color: '#762823'
    },
    submenuNotLast: {
      borderRight: '1px solid #aaaaaa'
    },
    qtyButton: {
      backgroundColor: '#0066b2',
      border: 'none'
    },
    qtyButtonSelected: {
      color: '#762823',
      backgroundColor: '#ed7801',
      border: 'none'
    }
  }
]
