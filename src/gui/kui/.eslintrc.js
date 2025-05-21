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
    "indent": ["error", 2, { "SwitchCase": 1 }],
    "jsx-quotes": ["error", "prefer-double"],
    "no-console": ["error", { allow: ["warn", "error"] }],
    "max-len": ["error", { "code": 120, "ignoreStrings": true }],
    "no-param-reassign": ["error", { "props": false }],
    "prefer-const": ["error", { "destructuring": "all", "ignoreReadBeforeAssign": true }],
    "prefer-template": "error",
    "template-curly-spacing": ["error", "never"],
    "brace-style": ["error", "1tbs"],
    "curly": ["error", "all"],
    "class-methods-use-this": "off",
    "global-require": 0
  }
}
