# POS UI

This is the base project for a customized and componentized POS UI using ES6 / ES2015, React.js, Redux and [more](#libraries).
Copy the entire directory and use it as a base for a new UI; remember to update the makefile's output file name.

For more information about `posui` library see [posui repository](https://central.mwneo.com:7990/mw/posui).

## Environment setup

```
$ npm install
```

## Build

In order to build the UI run:

```
make
```

This will generate an output file called `gui_pos_example.zip` that is ready for distribution on MW:App's bin directory.

## Debug

During development, it is recommended to work with uncompressed files and also to copy the files directly into to apache's htdocs directory so it is not needed to restart any component.

```
npm run dev && cp -R dist/* ../../../mwdatas/$MWAPP_CONFIG/server/htdocs/pos/
```

## Base architecture

- :link: [ES6 / ES2015](http://es6-features.org/) - ECMAScript 6
- :link: [react](https://facebook.github.io/react) - A javascript library for building user interfaces
- :link: [redux](https://github.com/reactjs/redux) - Predictable state container for javascript apps
- :link: [babel](https://babeljs.io/) - A javascript compiler
- :link: [webpack](https://webpack.github.io/) - Module bundler

## Libraries

`posui` provides a set of common components that can be used as a base for a point of sale user interface.
It uses other libraries that needs to be added to the project's dependencies:

- :link: [posui](https://central.mwneo.com:7990/mw/posui) - A set of common POS components developed by MW
- :link: [axios](https://github.com/mzabriskie/axios) - Promise based HTTP client for the browser and node.js
- :link: [font-awesome](http://fontawesome.io/) - Iconic font and CSS toolkit
- :link: [lodash](https://lodash.com/) - A modern JavaScript utility library delivering modularity, performance & extras
- :link: [prop-types](https://www.npmjs.com/package/prop-types) - Runtime type checking for React props and similar objects
- :link: [react](https://facebook.github.io/react) - A javascript library for building user interfaces
- :link: [react-dom](https://facebook.github.io/react/docs/react-dom.html) - React dependency
- :link: [react-intl](https://github.com/yahoo/react-intl) - Provides React components and an API to format dates, numbers, and strings, including pluralization and handling translations
- :link: [react-modal-dialog](https://github.com/qimingweng/react-modal-dialog) - A modal dialog for ReactJS
- :link: [react-redux](https://github.com/reactjs/react-redux) - React bindings for Redux
- :link: [redux](http://redux.js.org/) - Predictable state container for JavaScript apps
- :link: [redux-promise](https://github.com/acdlite/redux-promise) - FSA-compliant promise middleware for Redux
- :link: [redux-saga](https://github.com/redux-saga/redux-saga) - An alternative side effect model for Redux apps
- :link: [react-jss](https://github.com/cssinjs/react-jss) - Components for JSS

