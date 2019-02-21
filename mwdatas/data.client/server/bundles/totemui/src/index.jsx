import React from 'react';
import { render } from 'react-dom';
import { Provider } from 'react-redux'
import App from './common/main/app';
import configureStore from './store/configureStore'
import { START_SCREEN, MODAL_STATE, MAIN_SCREEN } from "./common/constants"

const store = configureStore({
	selectedScreen: START_SCREEN,
	order: {
		cpf: "",
		clientName: "",
		couponCode: "",
		type: null,
		items: []
	},
	title: "",
	modalState: MODAL_STATE,
	selectedSubScreen: MAIN_SCREEN,
	acumulateValue: 0
})

render(
	<Provider store={store}>
		<App />
	</Provider>,
	document.getElementById("app")
);
