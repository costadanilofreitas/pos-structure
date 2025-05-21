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
    "react/no-unused-prop-types": [1],
    "import/first": "error",
    "react/jsx-key": [1],
    "react/jsx-no-duplicate-props": [1, { "ignoreCase": true }],
    "react/jsx-closing-tag-location": [1],
    "react/jsx-closing-bracket-location": [1]
  }
}
