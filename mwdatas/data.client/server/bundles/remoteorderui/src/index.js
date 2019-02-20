import React from 'react';
import ReactDOM from 'react-dom';
import App from './App';
import registerServiceWorker from './registerServiceWorker';
import './css/bootstrap.css'
import './css/bootstrap-theme.css'
import './index.css';
import './Keyboard.css'

if (!String.prototype.trim) {
    // eslint-disable-next-line
    String.prototype.trim = function () {
        return this.replace(/^[\s\uFEFF\xA0]+|[\s\uFEFF\xA0]+$/g, '');
    };
}

ReactDOM.render(<App />, document.getElementById('root'));
registerServiceWorker();
