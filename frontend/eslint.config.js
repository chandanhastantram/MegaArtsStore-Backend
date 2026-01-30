import js from '@eslint/js'
import globals from 'globals'

export default [
  { ignores: ['dist', 'node_modules', '.vercel'] },
  {
    files: ['**/*.{js,jsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      // Downgrade all to warnings
      ...Object.keys(js.configs.recommended.rules).reduce((acc, rule) => {
        acc[rule] = 'warn'
        return acc
      }, {}),
    },
  },
]
