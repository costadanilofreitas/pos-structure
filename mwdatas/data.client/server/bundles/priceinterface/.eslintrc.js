module.exports = {
  "extends": ["eslint:recommended", "plugin:react/recommended", "airbnb-base-hf"],
  "plugins": [
    "import",
    "react"
  ],
  "parser": "babel-eslint",
  "parserOptions": {
    "ecmaVersion": 6,
    "sourceType": "module",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "rules": {
    "semi": [2, "never"],
    "indent": ["error", 2],
    "jsx-quotes": ["error", "prefer-double"],
    "no-console": ["error", { allow: ["warn", "error"] }],
    "class-methods-use-this": [2, {
      "exceptMethods": [
        "render",
        "getInitialState",
        "getDefaultProps",
        "getChildContext",
        "componentWillMount",
        "componentDidMount",
        "componentWillReceiveProps",
        "shouldComponentUpdate",
        "componentWillUpdate",
        "componentDidUpdate",
        "componentWillUnmount",
      ],
    }],
  },
  "excludes": ["*/*.html"]
}
